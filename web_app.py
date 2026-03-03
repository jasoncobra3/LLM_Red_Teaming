"""
FastAPI Web Application for LLM Red Teaming Platform.
Replaces the Streamlit UI with a full HTML/CSS/JS front-end.
"""

from __future__ import annotations

# Fix for Windows async event loop cleanup issues
import sys
import warnings

if sys.platform == 'win32':
    import asyncio
    # Use SelectorEventLoop instead of ProactorEventLoop on Windows
    # This prevents "Event loop is closed" errors during httpx cleanup
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # Suppress async cleanup warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*Event loop is closed.*")

import asyncio
import datetime
import json
import threading
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import uvicorn

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
from config.settings import settings
from config.providers import PROVIDERS, get_configured_providers
from core.attack_registry import (
    VULNERABILITIES,
    ATTACKS,
    FRAMEWORKS,
    get_vulnerability_categories,
    get_attack_categories,
    resolve_vulnerabilities,
    resolve_attacks,
    resolve_framework,
)
from core.llm_factory import create_deepeval_model, create_async_target_callback
from core.red_team_engine import run_red_team_scan
from core.custom_red_team_engine import run_custom_attack, run_static_attack
from core.jailbreak_strategies import STRATEGIES, list_strategies
from core.attack_library import (
    ATTACK_LIBRARY,
    list_attack_prompts,
    get_attack_categories as get_static_attack_categories,
)
from database import db_manager
from database.models import init_db
from reports.pdf_generator import generate_pdf_report
from utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="LLM Red Teaming Platform", version="1.0.0")
app.add_middleware(SessionMiddleware, secret_key=settings.APP_SECRET_KEY)

# Mount static files if directory exists
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# ---------------------------------------------------------------------------
# DB init on startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup():
    import os
    init_db()
    logger.info("Database initialized")
    
    # Load saved API keys from database into environment
    saved_keys = db_manager.list_api_keys()
    for entry in saved_keys:
        if entry.extra_config:
            for key, value in entry.extra_config.items():
                if value:
                    os.environ[key] = str(value)
    
    if saved_keys:
        logger.info(f"Loaded {len(saved_keys)} provider API keys from database")


# ---------------------------------------------------------------------------
# Active scans tracker (in-memory)
# ---------------------------------------------------------------------------
active_scans: Dict[int, Dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# HTML Pages
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    configured = get_configured_providers()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "configured_count": len(configured),
        "total_providers": len(PROVIDERS),
        "vuln_count": len(VULNERABILITIES),
        "attack_count": len(ATTACKS),
        "framework_count": len(FRAMEWORKS),
    })


@app.get("/attack", response_class=HTMLResponse)
async def attack_page(request: Request):
    vuln_cats = get_vulnerability_categories()
    atk_cats = get_attack_categories()
    providers = PROVIDERS
    configured = get_configured_providers()
    return templates.TemplateResponse("attack.html", {
        "request": request,
        "vuln_categories": {cat: [{"id": v.id, "name": v.display_name} for v in vs]
                           for cat, vs in vuln_cats.items()},
        "attack_categories": {cat: [{"id": a.id, "name": a.display_name} for a in ats]
                              for cat, ats in atk_cats.items()},
        "frameworks": {fid: f.display_name for fid, f in FRAMEWORKS.items()},
        "providers": {pid: {
            "display_name": p.display_name,
            "default_models": p.default_models,
            "configured": pid in configured,
        } for pid, p in providers.items()},
    })


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/results/{scan_id}", response_class=HTMLResponse)
async def results_page(request: Request, scan_id: int):
    return templates.TemplateResponse("results.html", {
        "request": request,
        "scan_id": scan_id,
    })


@app.get("/config", response_class=HTMLResponse)
async def config_page(request: Request):
    try:
        providers = PROVIDERS
        configured = get_configured_providers()
        ctx = {
            "request": request,
            "providers": {pid: {
                "display_name": p.display_name,
                "env_keys": p.env_keys,
                "default_models": p.default_models,
                "configured": pid in configured,
            } for pid, p in providers.items()},
        }
        tmpl = templates.get_template("config.html")
        html = tmpl.render(ctx)
        return HTMLResponse(html)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Config page error: {tb}")
        return HTMLResponse(f"<pre>{tb}</pre>", status_code=500)


@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request})


@app.get("/custom-attack", response_class=HTMLResponse)
async def custom_attack_page(request: Request):
    providers = PROVIDERS
    configured = get_configured_providers()
    return templates.TemplateResponse("custom_attack.html", {
        "request": request,
        "strategies": list_strategies(),
        "strategy_details": {sid: {
            "display_name": s.display_name,
            "description": s.description,
            "system_suffix": s.system_suffix,
            "phases": [{"name": p.name, "objective": p.objective} for p in s.phases],
        } for sid, s in STRATEGIES.items()},
        "static_attacks": get_static_attack_categories(),
        "static_attack_list": list_attack_prompts(),
        "providers": {pid: {
            "display_name": p.display_name,
            "default_models": p.default_models,
            "configured": pid in configured,
        } for pid, p in providers.items()},
    })


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def api_health():
    configured = get_configured_providers()
    return {
        "status": "ok",
        "configured_providers": len(configured),
        "total_providers": len(PROVIDERS),
        "vulnerabilities": len(VULNERABILITIES),
        "attacks": len(ATTACKS),
        "frameworks": len(FRAMEWORKS),
    }


@app.get("/api/providers")
async def api_providers():
    configured = get_configured_providers()
    result = {}
    for pid, p in PROVIDERS.items():
        result[pid] = {
            "display_name": p.display_name,
            "default_models": p.default_models,
            "configured": pid in configured,
            "supports_custom_model": p.supports_custom_model,
        }
    return result


@app.get("/api/vulnerabilities")
async def api_vulnerabilities():
    cats = get_vulnerability_categories()
    return {cat: [{"id": v.id, "name": v.display_name} for v in vs]
            for cat, vs in cats.items()}


@app.get("/api/attacks")
async def api_attacks():
    cats = get_attack_categories()
    return {cat: [{"id": a.id, "name": a.display_name} for a in ats]
            for cat, ats in cats.items()}


@app.get("/api/frameworks")
async def api_frameworks():
    return {fid: f.display_name for fid, f in FRAMEWORKS.items()}


# ---------------------------------------------------------------------------
# Scan CRUD API
# ---------------------------------------------------------------------------

@app.post("/api/scans")
async def create_scan(request: Request):
    """Create and start a new red-team scan."""
    data = await request.json()

    # Validate required fields
    required = ["scan_name", "attacker_provider", "attacker_model",
                "target_provider", "target_model"]
    for field in required:
        if not data.get(field):
            raise HTTPException(400, f"Missing required field: {field}")

    # Create DB record
    scan_run = db_manager.create_scan_run(
        name=data["scan_name"],
        attacker_provider=data["attacker_provider"],
        attacker_model=data["attacker_model"],
        target_provider=data["target_provider"],
        target_model=data["target_model"],
        target_purpose=data.get("target_purpose", ""),
        vulnerabilities=data.get("vulnerabilities", []),
        attacks=data.get("attacks", []),
        framework=data.get("framework"),
        attacks_per_vuln=data.get("attacks_per_vuln", 5),
    )

    scan_id = scan_run.id

    # Track active scan
    active_scans[scan_id] = {
        "status": "starting",
        "started_at": datetime.datetime.utcnow().isoformat(),
        "scan_name": data["scan_name"],
    }

    # Run in background thread (DeepTeam uses its own async loop)
    def _run():
        try:
            active_scans[scan_id]["status"] = "running"
            result = run_red_team_scan(
                scan_id=scan_id,
                attacker_provider=data["attacker_provider"],
                attacker_model=data["attacker_model"],
                target_provider=data["target_provider"],
                target_model=data["target_model"],
                target_purpose=data.get("target_purpose", ""),
                vulnerability_ids=data.get("vulnerabilities"),
                attack_ids=data.get("attacks"),
                framework_id=data.get("framework"),
                attacks_per_vuln=data.get("attacks_per_vuln", 5),
            )
            active_scans[scan_id]["status"] = result.get("status", "completed")
            active_scans[scan_id]["result"] = result
        except Exception as e:
            active_scans[scan_id]["status"] = "failed"
            active_scans[scan_id]["error"] = str(e)
            logger.error(f"Scan {scan_id} thread error: {e}")
        finally:
            # Remove from active after a delay so the UI can fetch final status
            def _cleanup():
                import time
                time.sleep(30)
                active_scans.pop(scan_id, None)
            threading.Thread(target=_cleanup, daemon=True).start()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    return {"scan_id": scan_id, "status": "started"}


@app.get("/api/scans")
async def list_scans(limit: int = 50):
    """List recent scans."""
    scans = db_manager.list_scan_runs(limit=limit)
    return [
        {
            "id": s.id,
            "name": s.name,
            "status": s.status,
            "scan_type": getattr(s, 'scan_type', 'deepteam') or 'deepteam',
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            "attacker_provider": s.attacker_provider,
            "attacker_model": s.attacker_model,
            "target_provider": s.target_provider,
            "target_model": s.target_model,
            "target_purpose": s.target_purpose,
            "vulnerabilities": s.vulnerabilities,
            "attacks": s.attacks,
            "framework": s.framework,
            "attacks_per_vuln": s.attacks_per_vuln,
            "strategy_id": getattr(s, 'strategy_id', None),
            "topic": getattr(s, 'topic', None),
            "max_turns": getattr(s, 'max_turns', None),
            "total_tests": s.total_tests,
            "passed": s.passed,
            "failed": s.failed,
            "overall_score": s.overall_score,
        }
        for s in scans
    ]


@app.get("/api/scans/{scan_id}")
async def get_scan(scan_id: int):
    """Get a single scan with summary."""
    scan = db_manager.get_scan_run(scan_id)
    if not scan:
        raise HTTPException(404, "Scan not found")

    # Check if it's currently active
    active_info = active_scans.get(scan_id, {})

    return {
        "id": scan.id,
        "name": scan.name,
        "status": active_info.get("status", scan.status),
        "scan_type": getattr(scan, 'scan_type', 'deepteam') or 'deepteam',
        "created_at": scan.created_at.isoformat() if scan.created_at else None,
        "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
        "attacker_provider": scan.attacker_provider,
        "attacker_model": scan.attacker_model,
        "target_provider": scan.target_provider,
        "target_model": scan.target_model,
        "target_purpose": scan.target_purpose,
        "vulnerabilities": scan.vulnerabilities,
        "attacks": scan.attacks,
        "framework": scan.framework,
        "attacks_per_vuln": scan.attacks_per_vuln,
        "strategy_id": getattr(scan, 'strategy_id', None),
        "topic": getattr(scan, 'topic', None),
        "max_turns": getattr(scan, 'max_turns', None),
        "total_tests": scan.total_tests,
        "passed": scan.passed,
        "failed": scan.failed,
        "overall_score": scan.overall_score,
        "is_active": scan_id in active_scans,
    }


@app.get("/api/scans/{scan_id}/results")
async def get_scan_results(scan_id: int):
    """Get detailed results for a scan."""
    results = db_manager.get_scan_results(scan_id)
    return [
        {
            "id": r.id,
            "vulnerability_type": r.vulnerability_type,
            "attack_type": r.attack_type,
            "risk_category": r.risk_category,
            "input_prompt": r.input_prompt,
            "target_response": r.target_response,
            "score": r.score,
            "passed": r.passed,
            "reason": r.reason,
        }
        for r in results
    ]


@app.delete("/api/scans/{scan_id}")
async def delete_scan(scan_id: int):
    """Delete a scan run and its results."""
    db_manager.delete_scan_run(scan_id)
    return {"status": "deleted"}


@app.get("/api/active_scans")
async def get_active_scans():
    """Get currently running scans."""
    return active_scans


# ---------------------------------------------------------------------------
# Custom Attack API
# ---------------------------------------------------------------------------

@app.get("/api/strategies")
async def api_strategies():
    """List all jailbreaking strategies."""
    return list_strategies()


@app.get("/api/strategies/{strategy_id}")
async def api_strategy_detail(strategy_id: str):
    """Get details for a specific strategy including phases."""
    s = STRATEGIES.get(strategy_id)
    if not s:
        raise HTTPException(404, "Strategy not found")
    return {
        "id": s.id,
        "display_name": s.display_name,
        "description": s.description,
        "system_suffix": s.system_suffix,
        "phases": [{"name": p.name, "objective": p.objective} for p in s.phases],
    }


@app.get("/api/static_attacks")
async def api_static_attacks():
    """List all static attack library prompts."""
    return list_attack_prompts()


@app.post("/api/custom_attack")
async def create_custom_attack(request: Request):
    """Start a custom multi-turn adaptive jailbreaking attack."""
    data = await request.json()

    required = ["attacker_provider", "attacker_model",
                "target_provider", "target_model", "strategy_id", "topic"]
    for field in required:
        if not data.get(field):
            raise HTTPException(400, f"Missing required field: {field}")

    max_turns = int(data.get("max_turns", 10))
    compliance_threshold = int(data.get("compliance_threshold", 70))
    strategy_id = data["strategy_id"]
    topic = data["topic"]

    if strategy_id not in STRATEGIES:
        raise HTTPException(400, f"Unknown strategy: {strategy_id}")

    scan_name = data.get("scan_name") or f"Custom: {STRATEGIES[strategy_id].display_name} - {topic[:50]}"

    # Create DB record
    scan_run = db_manager.create_scan_run(
        name=scan_name,
        attacker_provider=data["attacker_provider"],
        attacker_model=data["attacker_model"],
        target_provider=data["target_provider"],
        target_model=data["target_model"],
        target_purpose=data.get("target_system_prompt", ""),
        scan_type="custom_multi_turn",
        strategy_id=strategy_id,
        topic=topic,
        max_turns=max_turns,
    )

    scan_id = scan_run.id

    active_scans[scan_id] = {
        "status": "starting",
        "scan_type": "custom_multi_turn",
        "started_at": datetime.datetime.utcnow().isoformat(),
        "scan_name": scan_name,
        "strategy_id": strategy_id,
        "topic": topic,
        "current_turn": 0,
        "max_turns": max_turns,
        "turns": [],
    }

    def _on_turn_complete(turn, state):
        """Callback to update active_scans with live turn data."""
        if scan_id in active_scans:
            active_scans[scan_id]["current_turn"] = turn.turn_number
            active_scans[scan_id]["turns"].append({
                "turn_number": turn.turn_number,
                "phase": turn.phase,
                "attack_prompt": turn.attack_prompt[:300],
                "target_response": turn.target_response[:300],
                "compliance_level": turn.analysis.get("compliance_level", 0),
                "jailbreak_achieved": turn.analysis.get("jailbreak_achieved", False),
            })

    def _run():
        try:
            active_scans[scan_id]["status"] = "running"
            result = run_custom_attack(
                scan_id=scan_id,
                attacker_provider=data["attacker_provider"],
                attacker_model=data["attacker_model"],
                target_provider=data["target_provider"],
                target_model=data["target_model"],
                strategy_id=strategy_id,
                topic=topic,
                max_turns=max_turns,
                compliance_threshold=compliance_threshold,
                target_system_prompt=data.get("target_system_prompt", ""),
                on_turn_complete=_on_turn_complete,
            )
            active_scans[scan_id]["status"] = result.get("status", "completed")
            active_scans[scan_id]["result"] = result

            # Save conversation data to DB
            if result.get("conversation"):
                db_manager.update_scan_conversation(scan_id, result["conversation"])

        except Exception as e:
            active_scans[scan_id]["status"] = "failed"
            active_scans[scan_id]["error"] = str(e)
            logger.error(f"Custom attack {scan_id} failed: {e}")
        finally:
            def _cleanup():
                import time
                time.sleep(60)
                active_scans.pop(scan_id, None)
            threading.Thread(target=_cleanup, daemon=True).start()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    return {"scan_id": scan_id, "status": "started", "scan_type": "custom_multi_turn"}


@app.post("/api/static_attack")
async def create_static_attack(request: Request):
    """Run selected static attack prompts against a target."""
    data = await request.json()

    required = ["target_provider", "target_model", "attack_ids"]
    for field in required:
        if not data.get(field):
            raise HTTPException(400, f"Missing required field: {field}")

    attack_ids = data["attack_ids"]
    if not isinstance(attack_ids, list) or len(attack_ids) == 0:
        raise HTTPException(400, "attack_ids must be a non-empty list")

    scan_name = data.get("scan_name") or f"Static Library: {len(attack_ids)} attacks"

    scan_run = db_manager.create_scan_run(
        name=scan_name,
        attacker_provider=data.get("analyser_provider", "none"),
        attacker_model=data.get("analyser_model", "keyword_analysis"),
        target_provider=data["target_provider"],
        target_model=data["target_model"],
        scan_type="custom_static",
        attacks=attack_ids,
    )

    scan_id = scan_run.id

    active_scans[scan_id] = {
        "status": "starting",
        "scan_type": "custom_static",
        "started_at": datetime.datetime.utcnow().isoformat(),
        "scan_name": scan_name,
    }

    def _run():
        try:
            active_scans[scan_id]["status"] = "running"
            result = run_static_attack(
                scan_id=scan_id,
                target_provider=data["target_provider"],
                target_model=data["target_model"],
                attack_ids=attack_ids,
                analyser_provider=data.get("analyser_provider"),
                analyser_model=data.get("analyser_model"),
                target_system_prompt=data.get("target_system_prompt", ""),
            )
            active_scans[scan_id]["status"] = result.get("status", "completed")
            active_scans[scan_id]["result"] = result
        except Exception as e:
            active_scans[scan_id]["status"] = "failed"
            active_scans[scan_id]["error"] = str(e)
            logger.error(f"Static attack {scan_id} failed: {e}")
        finally:
            def _cleanup():
                import time
                time.sleep(30)
                active_scans.pop(scan_id, None)
            threading.Thread(target=_cleanup, daemon=True).start()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    return {"scan_id": scan_id, "status": "started", "scan_type": "custom_static"}


@app.post("/api/custom_attack/{scan_id}/stop")
async def stop_custom_attack(scan_id: int):
    """Signal a running custom attack to stop after the current turn."""
    if scan_id not in active_scans:
        raise HTTPException(404, "No active scan found with this ID")
    active_scans[scan_id]["status"] = "stopping"
    return {"status": "stop_requested"}


@app.get("/api/scans/{scan_id}/conversation")
async def get_scan_conversation(scan_id: int):
    """Get the conversation data for a custom attack scan."""
    # First check active scans for live data
    if scan_id in active_scans and active_scans[scan_id].get("turns"):
        return {
            "source": "live",
            "status": active_scans[scan_id].get("status"),
            "current_turn": active_scans[scan_id].get("current_turn", 0),
            "max_turns": active_scans[scan_id].get("max_turns", 0),
            "turns": active_scans[scan_id].get("turns", []),
        }

    # Otherwise check DB
    scan = db_manager.get_scan_run(scan_id)
    if not scan:
        raise HTTPException(404, "Scan not found")

    return {
        "source": "database",
        "status": scan.status,
        "conversation_data": scan.conversation_data,
    }


# ---------------------------------------------------------------------------
# Reports API
# ---------------------------------------------------------------------------

@app.get("/api/scans/{scan_id}/report/pdf")
async def download_pdf_report(scan_id: int):
    """Generate and download a PDF report for a scan."""
    try:
        scan = db_manager.get_scan_run(scan_id)
        if not scan:
            raise HTTPException(404, "Scan not found")

        results = db_manager.get_scan_results(scan_id)
        
        # Ensure we have results
        if not results:
            raise HTTPException(400, "No results found for this scan")
        
        result_dicts = [
            {
                "vulnerability_type": r.vulnerability_type or "N/A",
                "attack_type": r.attack_type or "N/A",
                "input_prompt": r.input_prompt or "",
                "target_response": r.target_response or "",
                "score": r.score if r.score is not None else 0.0,
                "passed": r.passed if r.passed is not None else False,
                "reason": r.reason or "",
            }
            for r in results
        ]

        logger.info(f"Generating PDF for scan {scan_id} with {len(result_dicts)} results")
        pdf_bytes = generate_pdf_report(scan, result_dicts)

        filename = f"red_team_report_{scan_id}_{datetime.datetime.utcnow().strftime('%Y%m%d')}.pdf"
        
        import io
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/pdf",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF for scan {scan_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"Error generating PDF: {str(e)}")


@app.get("/api/scans/{scan_id}/report/csv")
async def download_csv_report(scan_id: int):
    """Generate and download a CSV report for a scan."""
    scan = db_manager.get_scan_run(scan_id)
    if not scan:
        raise HTTPException(404, "Scan not found")

    results = db_manager.get_scan_results(scan_id)

    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["#", "Vulnerability", "Attack", "Score", "Passed", "Prompt", "Response", "Reason"])
    for i, r in enumerate(results, 1):
        writer.writerow([
            i, r.vulnerability_type, r.attack_type,
            r.score, r.passed,
            r.input_prompt[:500], r.target_response[:500], r.reason[:300],
        ])

    csv_bytes = output.getvalue().encode("utf-8")
    filename = f"red_team_results_{scan_id}_{datetime.datetime.utcnow().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        iter([csv_bytes]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.get("/api/scans/{scan_id}/report/json")
async def download_json_report(scan_id: int):
    """Download raw JSON report for a scan."""
    scan = db_manager.get_scan_run(scan_id)
    if not scan:
        raise HTTPException(404, "Scan not found")

    results = db_manager.get_scan_results(scan_id)
    report = {
        "scan": {
            "id": scan.id,
            "name": scan.name,
            "status": scan.status,
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
            "attacker": f"{scan.attacker_provider}/{scan.attacker_model}",
            "target": f"{scan.target_provider}/{scan.target_model}",
            "total_tests": scan.total_tests,
            "passed": scan.passed,
            "failed": scan.failed,
            "overall_score": scan.overall_score,
        },
        "results": [
            {
                "vulnerability_type": r.vulnerability_type,
                "attack_type": r.attack_type,
                "score": r.score,
                "passed": r.passed,
                "input_prompt": r.input_prompt,
                "target_response": r.target_response,
                "reason": r.reason,
            }
            for r in results
        ],
    }
    filename = f"red_team_report_{scan_id}.json"
    return StreamingResponse(
        iter([json.dumps(report, indent=2).encode()]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ---------------------------------------------------------------------------
# Statistics API
# ---------------------------------------------------------------------------

@app.post("/api/save_keys")
async def save_keys(request: Request):
    """Save API keys to the database and optionally to environment."""
    data = await request.json()
    provider_id = data.get("provider_id")
    keys = data.get("keys", {})

    if not provider_id or not keys:
        raise HTTPException(400, "provider_id and keys required")

    # Save to DB via db_manager
    db_manager.save_api_key(provider_id, json.dumps(keys), extra_config=keys)

    # Also set in current process environment so they take effect immediately
    import os
    for k, v in keys.items():
        os.environ[k] = v

    return {"status": "saved", "provider": provider_id}


@app.get("/api/saved_keys")
async def get_saved_keys():
    """Return provider IDs that have saved keys, with masked values."""
    import os
    all_keys = db_manager.list_api_keys()
    result = {}
    for entry in all_keys:
        extra = entry.extra_config or {}
        masked = {}
        for k, v in extra.items():
            if v and len(str(v)) > 4:
                masked[k] = str(v)[:4] + "*" * (len(str(v)) - 4)
            elif v:
                masked[k] = "****"
            else:
                masked[k] = ""
        result[entry.provider_id] = {"masked_keys": masked, "configured": True}

    # Also check env vars for providers that aren't in DB
    from config.providers import PROVIDERS
    for pid, pinfo in PROVIDERS.items():
        if pid not in result:
            env_set = {}
            all_set = True
            for ek in pinfo.env_keys:
                val = os.environ.get(ek, "")
                if val:
                    env_set[ek] = val[:4] + "*" * max(0, len(val) - 4)
                else:
                    all_set = False
                    env_set[ek] = ""
            if any(env_set.values()):
                result[pid] = {"masked_keys": env_set, "configured": all_set}

    return result


@app.post("/api/test_provider")
async def test_provider(request: Request):
    """Quick smoke-test: send a minimal prompt to the provider and check response."""
    import os
    from config.providers import PROVIDERS

    body = await request.json()
    provider_id = body.get("provider_id")
    if provider_id not in PROVIDERS:
        return JSONResponse({"success": False, "error": f"Unknown provider: {provider_id}"})

    pinfo = PROVIDERS[provider_id]

    # Make sure env vars are set (from DB if needed)
    entry = db_manager.get_api_key(provider_id)
    if entry and entry.extra_config:
        for k, v in entry.extra_config.items():
            if v:
                os.environ[k] = str(v)

    # Check all required keys are present
    missing = [ek for ek in pinfo.env_keys if not os.environ.get(ek)]
    if missing:
        return JSONResponse({"success": False, "error": f"Missing keys: {', '.join(missing)}"})

    try:
        from core.llm_factory import create_chat_model
        model_name = pinfo.default_models[0] if pinfo.default_models else None
        llm = create_chat_model(provider_id, model_name)
        # Simple invocation
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, lambda: llm.invoke("Say OK").content
        )
        return JSONResponse({
            "success": True,
            "model": model_name or provider_id,
            "response_preview": str(result)[:100],
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)[:300]})


@app.get("/api/statistics")
async def get_statistics():
    """Aggregate statistics across all scans."""
    scans = db_manager.list_scan_runs(limit=200)

    total_scans = len(scans)
    completed = [s for s in scans if s.status == "completed"]
    failed_scans = [s for s in scans if s.status == "failed"]
    running = [s for s in scans if s.status == "running"]

    total_tests = sum(s.total_tests for s in scans)
    total_passed = sum(s.passed for s in scans)
    total_failed = sum(s.failed for s in scans)
    avg_score = (sum(s.overall_score for s in completed) / len(completed)) if completed else 0

    # Provider breakdown
    provider_stats = {}
    for s in scans:
        key = s.target_provider
        if key not in provider_stats:
            provider_stats[key] = {"scans": 0, "avg_score": 0, "scores": []}
        provider_stats[key]["scans"] += 1
        if s.overall_score:
            provider_stats[key]["scores"].append(s.overall_score)
    for v in provider_stats.values():
        v["avg_score"] = round(sum(v["scores"]) / len(v["scores"]), 1) if v["scores"] else 0
        del v["scores"]

    # Vulnerability breakdown (from all results)
    vuln_stats = {}
    for s in completed[:20]:  # Limit to recent scans for performance
        results = db_manager.get_scan_results(s.id)
        for r in results:
            vt = r.vulnerability_type or "unknown"
            if vt not in vuln_stats:
                vuln_stats[vt] = {"total": 0, "passed": 0, "failed": 0}
            vuln_stats[vt]["total"] += 1
            if r.passed:
                vuln_stats[vt]["passed"] += 1
            else:
                vuln_stats[vt]["failed"] += 1

    return {
        "total_scans": total_scans,
        "completed_scans": len(completed),
        "failed_scans": len(failed_scans),
        "running_scans": len(running),
        "total_tests": total_tests,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "avg_score": round(avg_score, 1),
        "provider_stats": provider_stats,
        "vulnerability_stats": vuln_stats,
    }


# ---------------------------------------------------------------------------
# Run server
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
