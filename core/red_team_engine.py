"""
Red Team Engine – orchestrates DeepTeam scans.

This module ties together:
  - LLM Factory (attacker & target models)
  - Attack Registry (vulnerabilities, attacks, frameworks)
  - Database (persist results)
"""

from __future__ import annotations

import logging
import traceback
from typing import Any, Dict, List, Optional
import asyncio

from deepteam.red_teamer import RedTeamer

from core.llm_factory import create_deepeval_model, create_target_callback, create_async_target_callback
from core.attack_registry import resolve_vulnerabilities, resolve_attacks, resolve_framework
from database import db_manager
from utils.logger import get_logger
from utils.helpers import safe_float

logger = get_logger(__name__, level=logging.DEBUG)  # Enable DEBUG logging


def run_red_team_scan(
    scan_id: int,
    attacker_provider: str,
    attacker_model: str,
    target_provider: str,
    target_model: str,
    target_purpose: str = "",
    vulnerability_ids: List[str] | None = None,
    attack_ids: List[str] | None = None,
    framework_id: str | None = None,
    attacks_per_vuln: int = 5,
    attacker_kwargs: dict | None = None,
    target_kwargs: dict | None = None,
) -> Dict[str, Any]:
    """
    Execute a full red-team scan and persist results.

    Returns a summary dict: {status, total_tests, passed, failed, score, results}.
    """
    attacker_kwargs = attacker_kwargs or {}
    target_kwargs = target_kwargs or {}

    # Mark scan as running
    db_manager.update_scan_status(scan_id, "running")
    logger.info(f"Scan {scan_id} started — attacker={attacker_provider}/{attacker_model}, target={target_provider}/{target_model}")

    try:
        # 1. Build models
        # Use temperature=1.0 for simulator to generate diverse attacks
        sim_kwargs = {**attacker_kwargs, "temperature": attacker_kwargs.get("temperature", 1.0)}
        simulator_model = create_deepeval_model(attacker_provider, attacker_model, **sim_kwargs)
        
        # Use temperature=0.0 for evaluation to ensure consistent, deterministic JSON output
        eval_kwargs = {**attacker_kwargs, "temperature": 0.0}
        evaluation_model = create_deepeval_model(attacker_provider, attacker_model, **eval_kwargs)
        
        target_callback = create_async_target_callback(target_provider, target_model, **target_kwargs)
        
        logger.info(f"Models created - Simulator: {attacker_provider}/{attacker_model} (temp={sim_kwargs.get('temperature')}), Evaluation: {attacker_provider}/{attacker_model} (temp=0.0)")

        # 2. Resolve vulnerabilities, attacks, framework
        vulns = resolve_vulnerabilities(vulnerability_ids) if vulnerability_ids else None
        atks = resolve_attacks(attack_ids) if attack_ids else None
        fw = resolve_framework(framework_id)
        
        # Debug logging
        logger.info(f"Resolved {len(vulns) if vulns else 0} vulnerabilities: {[type(v).__name__ for v in vulns] if vulns else []}")
        logger.info(f"Resolved {len(atks) if atks else 0} attacks: {[type(a).__name__ for a in atks] if atks else []}")
        logger.info(f"Resolved framework: {type(fw).__name__ if fw else 'None'}")
        logger.info(f"Attacks per vulnerability type: {attacks_per_vuln}")

        # 3. Create RedTeamer
        red_teamer = RedTeamer(
            simulator_model=simulator_model,
            evaluation_model=evaluation_model,
            target_purpose=target_purpose,
            async_mode=True,
            max_concurrent=5,
        )

        # 4. Execute red_team scan
        logger.info("Starting red team scan...")
        risk_assessment = red_teamer.red_team(
            model_callback=target_callback,
            vulnerabilities=vulns,
            attacks=atks,
            framework=fw,
            attacks_per_vulnerability_type=attacks_per_vuln,
            ignore_errors=True,  # Ignore errors to continue scan even if some tests fail
            _print_assessment=False,  # Don't print to avoid cluttering output
            _upload_to_confident=False,
        )
        
        logger.info(f"Red team scan completed. Risk assessment type: {type(risk_assessment)}")

        # 5. Parse results
        results = _parse_risk_assessment(risk_assessment)
        
        # Filter out tests that failed due to errors (no input or output)
        valid_results = []
        failed_attack_generation = 0
        rate_limit_errors = 0
        json_errors = 0
        
        for r in results:
            error_msg = r.get("error", "") if isinstance(r, dict) else getattr(r, "error", "")
            if error_msg:
                if "rate_limit" in str(error_msg).lower():
                    rate_limit_errors += 1
                elif "json" in str(error_msg).lower():
                    json_errors += 1
                else:
                    failed_attack_generation += 1
                logger.debug(f"Skipping failed test: {error_msg[:100]}")
                continue
            
            # Only include tests that have valid input/output
            input_prompt = r.get("input_prompt", "") if isinstance(r, dict) else ""
            target_response = r.get("target_response", "") if isinstance(r, dict) else ""
            
            if input_prompt or target_response:
                valid_results.append(r)
        
        if rate_limit_errors > 0:
            logger.warning(f"⚠️  {rate_limit_errors} tests failed due to rate limits on the attacker model")
        if json_errors > 0:
            logger.warning(f"⚠️  {json_errors} tests failed due to JSON generation errors")
        if failed_attack_generation > 0:
            logger.warning(f"⚠️  {failed_attack_generation} tests failed during attack generation")
        
        results = valid_results
        total = len(results)
        passed = sum(1 for r in results if r["passed"])
        failed = total - passed
        score = (passed / total * 100) if total > 0 else 0.0

        # 6. Persist results
        db_manager.add_scan_results(scan_id, results)
        db_manager.update_scan_status(
            scan_id,
            status="completed",
            total_tests=total,
            passed=passed,
            failed=failed,
            overall_score=round(score, 2),
        )

        logger.info(f"Scan {scan_id} completed — {total} tests, {passed} passed, {failed} failed, score={score:.1f}%")
        return {
            "status": "completed",
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "score": round(score, 2),
            "results": results,
        }

    except Exception as e:
        logger.error(f"Scan {scan_id} failed: {e}\n{traceback.format_exc()}")
        db_manager.update_scan_status(scan_id, "failed")
        return {
            "status": "failed",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


def _parse_risk_assessment(risk_assessment: Any) -> List[Dict[str, Any]]:
    """
    Parse the DeepTeam RiskAssessment object into a flat list of result dicts.
    Handles various return shapes from different DeepTeam versions.
    """
    results: List[Dict[str, Any]] = []

    try:
        # Debug: log the structure of the risk_assessment object
        logger.info(f"Risk assessment type: {type(risk_assessment)}")
        logger.info(f"Risk assessment attributes: {dir(risk_assessment)}")
        
        # Try to get test_runs (common in newer DeepTeam versions)
        if hasattr(risk_assessment, "test_runs"):
            logger.info(f"Found test_runs attribute with {len(risk_assessment.test_runs)} runs")
            for idx, test_run in enumerate(risk_assessment.test_runs):
                logger.info(f"Test run #{idx+1} type: {type(test_run)}")
                if hasattr(test_run, '__dict__'):
                    logger.info(f"Test run #{idx+1} dict keys: {list(test_run.__dict__.keys())}")
                    # Log first test run's full content for debugging
                    if idx == 0:
                        logger.info(f"First test run full content: {test_run.__dict__}")
                results.append(_extract_test_case(test_run))
        
        # Try vulnerabilities_score (another common structure)
        if hasattr(risk_assessment, "vulnerabilities_score"):
            logger.info(f"Found vulnerabilities_score: {risk_assessment.vulnerabilities_score}")
        
        # risk_assessment is typically a RiskAssessment object
        # with .score_breakdown or .test_cases or similar attribute
        if hasattr(risk_assessment, "score_breakdown"):
            logger.info("Found score_breakdown attribute")
            for vuln_type, breakdown in risk_assessment.score_breakdown.items():
                if isinstance(breakdown, dict):
                    for attack_type, cases in breakdown.items():
                        if isinstance(cases, list):
                            for case in cases:
                                results.append(_extract_case(case, vuln_type, attack_type))
                        else:
                            results.append({
                                "vulnerability_type": vuln_type,
                                "attack_type": attack_type,
                                "score": safe_float(cases, 0.0),
                                "passed": True,
                                "input_prompt": "",
                                "target_response": "",
                                "reason": str(cases),
                            })

        if hasattr(risk_assessment, "test_cases"):
            logger.info(f"Found test_cases attribute with {len(risk_assessment.test_cases)} cases")
            for idx, tc in enumerate(risk_assessment.test_cases):
                # Log the first test case's complete structure
                if idx == 0:
                    logger.info(f"First test case type: {type(tc)}")
                    if hasattr(tc, '__dict__'):
                        logger.info(f"First test case __dict__: {tc.__dict__}")
                    if hasattr(tc, 'model_dump'):
                        logger.info(f"First test case model_dump: {tc.model_dump()}")
                results.append(_extract_test_case(tc))

        # Fallback: try iterating the object itself
        if not results and hasattr(risk_assessment, "__iter__"):
            logger.info("Trying to iterate risk_assessment directly")
            for item in risk_assessment:
                logger.info(f"Item type: {type(item)}, attributes: {dir(item)}")
                if hasattr(item, "vulnerability"):
                    results.append(_extract_test_case(item))

        # If we still have no results, log detailed info
        if not results:
            logger.warning(f"No results found. Risk assessment repr: {repr(risk_assessment)[:500]}")
            logger.warning(f"Risk assessment str: {str(risk_assessment)[:500]}")
            
            # Try to extract any useful data
            if hasattr(risk_assessment, "__dict__"):
                logger.warning(f"Risk assessment __dict__: {risk_assessment.__dict__}")

    except Exception as e:
        logger.error(f"Error parsing risk assessment: {e}\n{traceback.format_exc()}")

    logger.info(f"Parsed {len(results)} results from risk assessment")
    return results


def _extract_case(case: Any, vuln_type: str, attack_type: str) -> dict:
    """Extract a single case from DeepTeam score breakdown."""
    return {
        "vulnerability_type": vuln_type,
        "attack_type": attack_type,
        "input_prompt": getattr(case, "input", "") or getattr(case, "prompt", "") or str(case.get("input", "")) if isinstance(case, dict) else "",
        "target_response": getattr(case, "actual_output", "") or getattr(case, "response", "") or str(case.get("actual_output", "")) if isinstance(case, dict) else "",
        "score": safe_float(getattr(case, "score", 0.0), 0.0),
        "passed": bool(getattr(case, "success", True)) if hasattr(case, "success") else True,
        "reason": getattr(case, "reason", "") or "",
        "risk_category": getattr(case, "risk_category", "") or "",
    }


def _extract_test_case(tc: Any) -> dict:
    """Extract data from a DeepTeam test case object."""
    # Try using Pydantic's model_dump if available (most reliable)
    if hasattr(tc, 'model_dump'):
        try:
            data = tc.model_dump()
            logger.debug(f"Extracted via model_dump: vuln={data.get('vulnerability', 'N/A')}, has_input={bool(data.get('input'))}, has_output={bool(data.get('actual_output'))}, has_error={bool(data.get('error'))}")
            return {
                "vulnerability_type": data.get("vulnerability", "") or data.get("vulnerability_type", "") or "",
                "attack_type": data.get("attack", "") or data.get("attack_type", "") or data.get("attack_method", "") or data.get("attack_enhancement", "") or "",
                "input_prompt": data.get("input", "") or data.get("prompt", "") or data.get("enhanced_attack", "") or "",
                "target_response": data.get("actual_output", "") or data.get("output", "") or data.get("response", "") or data.get("target_response", "") or "",
                "score": safe_float(data.get("score", 0.0), 0.0),
                "passed": bool(data.get("success", True) if data.get("score") is not None else False),
                "reason": data.get("reason", "") or "",
                "risk_category": data.get("risk_category", "") or "",
                "error": data.get("error", "") or "",
            }
        except Exception as e:
            logger.warning(f"model_dump failed: {e}, falling back to getattr")
    
    # Fallback to attribute access
    # Log all attributes to understand the structure
    if hasattr(tc, '__dict__'):
        logger.debug(f"Test case attributes: {list(tc.__dict__.keys())}")
    
    # Try multiple possible attribute names for each field
    vuln = (
        getattr(tc, "vulnerability", "") or 
        getattr(tc, "vulnerability_type", "") or
        getattr(tc, "vuln", "") or ""
    )
    
    attack = (
        getattr(tc, "attack", "") or 
        getattr(tc, "attack_type", "") or
        getattr(tc, "attack_method", "") or
        getattr(tc, "attack_enhancement", "") or ""
    )
    
    input_prompt = (
        getattr(tc, "input", "") or 
        getattr(tc, "prompt", "") or
        getattr(tc, "input_prompt", "") or
        getattr(tc, "enhanced_attack", "") or ""
    )
    
    target_response = (
        getattr(tc, "actual_output", "") or 
        getattr(tc, "target_output", "") or
        getattr(tc, "output", "") or
        getattr(tc, "response", "") or
        getattr(tc, "target_response", "") or ""
    )
    
    error = getattr(tc, "error", "") or ""
    
    # If still empty, check if it's a dict
    if isinstance(tc, dict):
        vuln = vuln or tc.get("vulnerability", "") or tc.get("vulnerability_type", "")
        attack = attack or tc.get("attack", "") or tc.get("attack_type", "") or tc.get("attack_method", "")
        input_prompt = input_prompt or tc.get("input", "") or tc.get("prompt", "")
        target_response = target_response or tc.get("actual_output", "") or tc.get("output", "")
        error = error or tc.get("error", "")
    
    logger.debug(f"Extracted - Vuln: {str(vuln)[:50] if vuln else 'N/A'}, Attack: {str(attack)[:50] if attack else 'N/A'}, Has Input: {bool(input_prompt)}, Has Response: {bool(target_response)}, Has Error: {bool(error)}")
    
    return {
        "vulnerability_type": str(vuln) if vuln else "",
        "attack_type": str(attack) if attack else "",
        "input_prompt": input_prompt,
        "target_response": target_response,
        "score": safe_float(getattr(tc, "score", 0.0), 0.0),
        "passed": bool(getattr(tc, "success", True) if getattr(tc, "score", None) is not None else False),
        "reason": getattr(tc, "reason", "") or "",
        "risk_category": getattr(tc, "risk_category", "") or "",
        "error": error,
    }
