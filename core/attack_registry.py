"""
Attack & Vulnerability registry – single source of truth for all
available DeepTeam attacks, vulnerabilities, and compliance frameworks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Vulnerability catalogue
# ---------------------------------------------------------------------------

from deepteam.vulnerabilities import (
    Bias,
    Toxicity,
    PIILeakage,
    Misinformation,
    IntellectualProperty,
    PromptLeakage,
    Robustness,
    Fairness,
    IllegalActivity,
    GraphicContent,
    PersonalSafety,
    ChildProtection,
    Ethics,
    Competition,
    SQLInjection,
    ShellInjection,
    SSRF,
    BOLA,
    BFLA,
    RBAC,
    DebugAccess,
    ExcessiveAgency,
    IndirectInstruction,
    GoalTheft,
    AgentIdentityAbuse,
    AutonomousAgentDrift,
    InsecureInterAgentCommunication,
    RecursiveHijacking,
    ToolMetadataPoisoning,
    ToolOrchestrationAbuse,
    UnexpectedCodeExecution,
)

# ---------------------------------------------------------------------------
# Single-turn attacks
# ---------------------------------------------------------------------------

from deepteam.attacks.single_turn import (
    PromptInjection,
    Roleplay,
    Base64,
    ROT13,
    Leetspeak,
    GrayBox,
    Multilingual,
    MathProblem,
    ContextPoisoning,
    GoalRedirection,
    InputBypass,
    PermissionEscalation,
    PromptProbing,
    SystemOverride,
    AdversarialPoetry,
    LinguisticConfusion,
)

# ---------------------------------------------------------------------------
# Multi-turn attacks
# ---------------------------------------------------------------------------

from deepteam.attacks.multi_turn import (
    CrescendoJailbreaking,
    TreeJailbreaking,
    LinearJailbreaking,
    BadLikertJudge,
    SequentialJailbreak,
)

# ---------------------------------------------------------------------------
# Compliance frameworks
# ---------------------------------------------------------------------------

from deepteam.frameworks import (
    OWASPTop10,
    NIST,
    MITRE,
    Aegis,
    BeaverTails,
)

# Try importing OWASP_ASI_2026 (may not exist in all deepteam versions)
try:
    from deepteam.frameworks import OWASP_ASI_2026
except ImportError:
    OWASP_ASI_2026 = None


# ======================================================================
# Registry data-classes
# ======================================================================

@dataclass
class VulnerabilityInfo:
    id: str
    display_name: str
    category: str
    cls: Any  # DeepTeam vulnerability class


@dataclass
class AttackInfo:
    id: str
    display_name: str
    category: str  # "single_turn" | "multi_turn"
    cls: Any  # DeepTeam attack class


@dataclass
class FrameworkInfo:
    id: str
    display_name: str
    cls: Any


# ======================================================================
# Vulnerability registry
# ======================================================================

VULNERABILITIES: Dict[str, VulnerabilityInfo] = {
    # --- Content Safety ---
    "bias": VulnerabilityInfo("bias", "Bias", "Content Safety", Bias),
    "toxicity": VulnerabilityInfo("toxicity", "Toxicity", "Content Safety", Toxicity),
    "graphic_content": VulnerabilityInfo("graphic_content", "Graphic Content", "Content Safety", GraphicContent),
    "personal_safety": VulnerabilityInfo("personal_safety", "Personal Safety", "Content Safety", PersonalSafety),
    "child_protection": VulnerabilityInfo("child_protection", "Child Protection", "Content Safety", ChildProtection),
    "illegal_activity": VulnerabilityInfo("illegal_activity", "Illegal Activity", "Content Safety", IllegalActivity),

    # --- Data Privacy ---
    "pii_leakage": VulnerabilityInfo("pii_leakage", "PII Leakage", "Data Privacy", PIILeakage),
    "prompt_leakage": VulnerabilityInfo("prompt_leakage", "Prompt Leakage", "Data Privacy", PromptLeakage),
    "intellectual_property": VulnerabilityInfo("intellectual_property", "Intellectual Property", "Data Privacy", IntellectualProperty),

    # --- Reliability ---
    "misinformation": VulnerabilityInfo("misinformation", "Misinformation", "Reliability", Misinformation),
    "robustness": VulnerabilityInfo("robustness", "Robustness", "Reliability", Robustness),
    "fairness": VulnerabilityInfo("fairness", "Fairness", "Reliability", Fairness),
    "ethics": VulnerabilityInfo("ethics", "Ethics", "Reliability", Ethics),
    "competition": VulnerabilityInfo("competition", "Competition", "Reliability", Competition),

    # --- Security ---
    "sql_injection": VulnerabilityInfo("sql_injection", "SQL Injection", "Security", SQLInjection),
    "shell_injection": VulnerabilityInfo("shell_injection", "Shell Injection", "Security", ShellInjection),
    "ssrf": VulnerabilityInfo("ssrf", "SSRF", "Security", SSRF),
    "bola": VulnerabilityInfo("bola", "BOLA", "Security", BOLA),
    "bfla": VulnerabilityInfo("bfla", "BFLA", "Security", BFLA),
    "rbac": VulnerabilityInfo("rbac", "RBAC", "Security", RBAC),
    "debug_access": VulnerabilityInfo("debug_access", "Debug Access", "Security", DebugAccess),

    # --- Agentic Risks ---
    "excessive_agency": VulnerabilityInfo("excessive_agency", "Excessive Agency", "Agentic", ExcessiveAgency),
    "indirect_instruction": VulnerabilityInfo("indirect_instruction", "Indirect Instruction", "Agentic", IndirectInstruction),
    "goal_theft": VulnerabilityInfo("goal_theft", "Goal Theft", "Agentic", GoalTheft),
    "agent_identity_abuse": VulnerabilityInfo("agent_identity_abuse", "Agent Identity Abuse", "Agentic", AgentIdentityAbuse),
    "autonomous_agent_drift": VulnerabilityInfo("autonomous_agent_drift", "Autonomous Agent Drift", "Agentic", AutonomousAgentDrift),
    "insecure_inter_agent_communication": VulnerabilityInfo("insecure_inter_agent_communication", "Insecure Inter-Agent Comm", "Agentic", InsecureInterAgentCommunication),
    "recursive_hijacking": VulnerabilityInfo("recursive_hijacking", "Recursive Hijacking", "Agentic", RecursiveHijacking),
    "tool_metadata_poisoning": VulnerabilityInfo("tool_metadata_poisoning", "Tool Metadata Poisoning", "Agentic", ToolMetadataPoisoning),
    "tool_orchestration_abuse": VulnerabilityInfo("tool_orchestration_abuse", "Tool Orchestration Abuse", "Agentic", ToolOrchestrationAbuse),
    "unexpected_code_execution": VulnerabilityInfo("unexpected_code_execution", "Unexpected Code Execution", "Agentic", UnexpectedCodeExecution),
}


# ======================================================================
# Attack registry
# ======================================================================

ATTACKS: Dict[str, AttackInfo] = {
    # --- Single-turn ---
    "prompt_injection": AttackInfo("prompt_injection", "Prompt Injection", "single_turn", PromptInjection),
    "roleplay": AttackInfo("roleplay", "Roleplay", "single_turn", Roleplay),
    "base64": AttackInfo("base64", "Base64 Encoding", "single_turn", Base64),
    "rot13": AttackInfo("rot13", "ROT13", "single_turn", ROT13),
    "leetspeak": AttackInfo("leetspeak", "Leetspeak", "single_turn", Leetspeak),
    "gray_box": AttackInfo("gray_box", "Gray Box", "single_turn", GrayBox),
    "multilingual": AttackInfo("multilingual", "Multilingual", "single_turn", Multilingual),
    "math_problem": AttackInfo("math_problem", "Math Problem", "single_turn", MathProblem),
    "context_poisoning": AttackInfo("context_poisoning", "Context Poisoning", "single_turn", ContextPoisoning),
    "goal_redirection": AttackInfo("goal_redirection", "Goal Redirection", "single_turn", GoalRedirection),
    "input_bypass": AttackInfo("input_bypass", "Input Bypass", "single_turn", InputBypass),
    "permission_escalation": AttackInfo("permission_escalation", "Permission Escalation", "single_turn", PermissionEscalation),
    "prompt_probing": AttackInfo("prompt_probing", "Prompt Probing", "single_turn", PromptProbing),
    "system_override": AttackInfo("system_override", "System Override", "single_turn", SystemOverride),
    "adversarial_poetry": AttackInfo("adversarial_poetry", "Adversarial Poetry", "single_turn", AdversarialPoetry),
    "linguistic_confusion": AttackInfo("linguistic_confusion", "Linguistic Confusion", "single_turn", LinguisticConfusion),

    # --- Multi-turn ---
    "crescendo_jailbreaking": AttackInfo("crescendo_jailbreaking", "Crescendo Jailbreaking", "multi_turn", CrescendoJailbreaking),
    "tree_jailbreaking": AttackInfo("tree_jailbreaking", "Tree Jailbreaking", "multi_turn", TreeJailbreaking),
    "linear_jailbreaking": AttackInfo("linear_jailbreaking", "Linear Jailbreaking", "multi_turn", LinearJailbreaking),
    "bad_likert_judge": AttackInfo("bad_likert_judge", "Bad Likert Judge", "multi_turn", BadLikertJudge),
    "sequential_jailbreak": AttackInfo("sequential_jailbreak", "Sequential Jailbreak", "multi_turn", SequentialJailbreak),
}


# ======================================================================
# Framework registry
# ======================================================================

FRAMEWORKS: Dict[str, FrameworkInfo] = {
    "owasp_top10": FrameworkInfo("owasp_top10", "OWASP Top 10 for LLMs", OWASPTop10),
    "nist": FrameworkInfo("nist", "NIST AI RMF", NIST),
    "mitre": FrameworkInfo("mitre", "MITRE ATLAS", MITRE),
    "aegis": FrameworkInfo("aegis", "Aegis AI Safety", Aegis),
    "beavertails": FrameworkInfo("beavertails", "BeaverTails", BeaverTails),
}

if OWASP_ASI_2026 is not None:
    FRAMEWORKS["owasp_asi_2026"] = FrameworkInfo(
        "owasp_asi_2026", "OWASP ASI 2026", OWASP_ASI_2026
    )


# ======================================================================
# Helper accessors
# ======================================================================

def get_vulnerability_categories() -> Dict[str, List[VulnerabilityInfo]]:
    """Group vulnerabilities by category."""
    cats: Dict[str, List[VulnerabilityInfo]] = {}
    for v in VULNERABILITIES.values():
        cats.setdefault(v.category, []).append(v)
    return cats


def get_attack_categories() -> Dict[str, List[AttackInfo]]:
    """Group attacks by category (single_turn / multi_turn)."""
    cats: Dict[str, List[AttackInfo]] = {}
    for a in ATTACKS.values():
        cats.setdefault(a.category, []).append(a)
    return cats


def resolve_vulnerabilities(ids: List[str]) -> list:
    """Convert vulnerability string IDs to DeepTeam class instances."""
    return [VULNERABILITIES[vid].cls() for vid in ids if vid in VULNERABILITIES]


def resolve_attacks(ids: List[str]) -> list:
    """Convert attack string IDs to DeepTeam class instances."""
    return [ATTACKS[aid].cls() for aid in ids if aid in ATTACKS]


def resolve_framework(fid: str | None):
    """Return a DeepTeam framework instance or None."""
    if fid and fid in FRAMEWORKS:
        return FRAMEWORKS[fid].cls()
    return None
