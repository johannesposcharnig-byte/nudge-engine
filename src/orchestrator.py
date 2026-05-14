"""Orchestrator for the Nudge Engine with short feedback loops and reflection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional

from .agents.base import AgentMessage, BaseAgent
from .agents.critic import CriticAgent
from .agents.data import DataAgent
from .agents.devils_advocate import DevilsAdvocateAgent
from .agents.evaluation import EvaluationAgent
from .agents.governance import GovernanceAgent
from .agents.ml import MLAgent
from .agents.policy import PolicyAgent
from .agents.research import ResearchAgent
from .agents.statistical import StatisticalAgent
from .context_budget import build_evidence_pack, estimate_context_reduction, minimize_context
from .evidence import (
    MECE_HYPOTHESIS_GROUPS,
    build_mece_hypotheses,
    clarification_questions_for_missing,
    customer_data_missing_fields,
    infer_customer_data_profile,
    mece_groups_complete,
)
from .formulas import formula_context, get_formula_definition
from .ocean import ocean_context_requires_hold
from .reward import reward_policy_blockers


Decision = Literal["approve", "revise", "reject", "hold"]
DoneStatus = Literal["done", "partial", "blocked"]
AnalysisDepth = Literal["routine", "deep"]


@dataclass
class Task:
    phase: str
    agent: str
    prompt: str
    model: str = "GPT-5.4-Mini"
    analysis_depth: AnalysisDepth = "routine"
    requires_critic: bool = False
    requires_devil_advocate: bool = False
    requires_governance: bool = False
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationReflection:
    task_phase: str
    agent: str
    what_is_clear: list[str] = field(default_factory=list)
    what_is_unclear: list[str] = field(default_factory=list)
    what_is_missing: list[str] = field(default_factory=list)
    why_next_action: str = ""
    decision: Decision = "hold"


@dataclass
class OrchestrationStep:
    task: Task
    result: AgentMessage
    self_check: dict[str, Any]
    peer_feedback: list[AgentMessage] = field(default_factory=list)
    reflection: Optional[OrchestrationReflection] = None
    decision: Decision = "hold"


class Orchestrator:
    """Coordinates agents, review loops, and final quality gates."""

    def __init__(self, agents: Optional[dict[str, BaseAgent]] = None) -> None:
        self.agents: dict[str, BaseAgent] = agents or self._build_default_agents()
        self.history: list[OrchestrationStep] = []
        self.reflections: list[OrchestrationReflection] = []
        self.run_state: dict[str, Any] = {
            "decisions": [],
            "blockers": [],
            "open_questions": [],
            "last_summary": "",
        }

    def _build_default_agents(self) -> dict[str, BaseAgent]:
        return {
            "research": ResearchAgent(),
            "data": DataAgent(),
            "statistical": StatisticalAgent(),
            "ml": MLAgent(),
            "policy": PolicyAgent(),
            "evaluation": EvaluationAgent(),
            "governance": GovernanceAgent(),
            "critic": CriticAgent(),
            "devils_advocate": DevilsAdvocateAgent(),
        }

    def core_agent_roles(self) -> list[str]:
        return [
            "orchestrator",
            "data_measurement",
            "behavioral_science",
            "policy_reward",
            "critic_governance",
        ]

    def expert_capability_map(self) -> dict[str, str]:
        return {
            "data": "data_measurement",
            "statistical": "data_measurement",
            "evaluation": "data_measurement",
            "research": "behavioral_science",
            "ml": "policy_reward",
            "policy": "policy_reward",
            "critic": "critic_governance",
            "devils_advocate": "critic_governance",
            "governance": "critic_governance",
        }

    def choose_model(self, task: Task) -> str:
        if task.analysis_depth == "deep":
            return "GPT-5.4"
        if task.phase in {"formula_review", "statistical_design", "policy_design", "governance_review"}:
            return "GPT-5.4"
        return "GPT-5.4-Mini"

    def build_message(self, task: Task) -> AgentMessage:
        chosen_model = self.choose_model(task)
        model = chosen_model if task.model == "GPT-5.4-Mini" else task.model
        context = dict(task.context)
        if task.phase == "formula_review":
            context = formula_context(context)
        context.setdefault("evidence_gate_required", True)
        context.setdefault("hypotheses", build_mece_hypotheses(context))
        context.setdefault("mece_groups", list(MECE_HYPOTHESIS_GROUPS))
        context.setdefault("model", model)
        context.setdefault("analysis_depth", task.analysis_depth)
        context.setdefault("routing_phase", task.phase)
        context = self.build_agent_context(task, context)
        return AgentMessage(
            agent=task.agent,
            phase=task.phase,
            jtbd=task.prompt,
            summary=task.prompt,
            done_status="partial",
            confidence=0.5,
            context=context,
            assumptions=[],
            evidence=[],
            risks=[],
            open_questions=[],
            requested_feedback=[],
            feedback_to=[],
            next_action="hold",
            uncertainty=dict(context.get("uncertainty", {})),
            claims=[],
            claim_type="unknown",
            evidence_required=[],
            evidence_available=[],
            clarification_questions=[],
            readiness_flags={},
            source_metadata=dict(context.get("source_metadata", {})),
            conflicts=list(context.get("conflicts", [])),
            security_warnings=list(context.get("security_warnings", [])),
            lifecycle_status="active",
            compressed_memory=str(context.get("run_state", {}).get("last_summary", ""))[:500],
            decision_rationale="Pending agent output.",
        )

    def build_agent_context(self, task: Task, context: dict[str, Any]) -> dict[str, Any]:
        minimized = minimize_context(context, agent=task.agent)
        evidence_pack = build_evidence_pack(
            task_phase=task.phase,
            agent=task.agent,
            prompt=task.prompt,
            context=minimized,
            run_state=self.run_state,
        )
        reduction = estimate_context_reduction(context, minimized)
        minimized["evidence_pack"] = evidence_pack
        minimized["run_state"] = dict(self.run_state)
        minimized["context_budget"] = {
            "mode": "evidence_pack_only" if not minimized.get("full_context_used") else "full_context_exception",
            "estimated_reduction": reduction,
            "target_reduction": 0.70,
            "max_documents": evidence_pack["selected_sources"]["max_documents"],
            "max_sections_per_document": evidence_pack["selected_sources"]["max_sections_per_document"],
            "selected_documents": evidence_pack["selected_sources"]["documents"],
            "selected_sections": evidence_pack["selected_sources"]["sections"],
            "retrieval_governance": minimized.get("retrieval_governance", {}),
            "blocked_sources": list(minimized.get("blocked_sources", [])),
            "stale_sources": list(minimized.get("stale_sources", [])),
            "security_warnings": list(minimized.get("security_warnings", [])),
            "security_review": dict(minimized.get("security_review", {})),
            "security_agent": minimized.get("security_agent", "Leonidas"),
        }
        return minimized

    def dispatch(self, task: Task) -> AgentMessage:
        agent = self.agents[task.agent]
        message = self.build_message(task)
        preflight_decision = self.evaluate_evidence_gate(message)
        if preflight_decision == "hold" and (
            message.context.get("blocked_sources")
            or message.context.get("security_warnings")
            or message.context.get("conflicts")
            or not message.context.get("security_review", {}).get("safe_to_reason", True)
            or not message.context.get("retrieval_governance", {}).get("passed", True)
        ):
            return self.preflight_blocked_message(message)
        return agent.run(message)

    def preflight_blocked_message(self, message: AgentMessage) -> AgentMessage:
        blockers = []
        blockers.extend(message.context.get("blocked_sources", []))
        blockers.extend(warning.get("pattern", warning.get("reason", "security_warning")) for warning in message.context.get("security_warnings", []))
        blockers.extend(conflict.get("conflict_reason", "unresolved_conflict") for conflict in message.context.get("conflicts", []))
        if not message.context.get("retrieval_governance", {}).get("passed", True):
            blockers.append("retrieval_governance_failed")
        security_review = message.context.get("security_review", {})
        if security_review and not security_review.get("safe_to_reason", True):
            blockers.append("leonidas_security_review_failed")
        return AgentMessage(
            agent=message.agent,
            phase=message.phase,
            jtbd=message.jtbd,
            summary="Pre-dispatch governance gate blocked this agent run before reasoning. Leonidas security review was active.",
            done_status="blocked",
            confidence=0.9,
            context=message.context,
            assumptions=["Blocked, deprecated, conflicting, or unsafe context must not enter agent reasoning."],
            evidence=["Pre-dispatch governance gate evaluated context metadata.", "Leonidas security review evaluated integrity risks."],
            risks=["Unsafe or invalid context could compromise downstream decisions."],
            open_questions=["Resolve pre-dispatch blockers before retrying."],
            requested_feedback=["Orchestrator must resolve source, security, or conflict blockers."],
            feedback_to=["orchestrator"],
            next_action="hold",
            claims=[
                {
                    "statement": "Agent reasoning did not run because pre-dispatch governance failed.",
                    "claim_type": "blocked",
                    "category": "governance",
                    "evidence_available": blockers,
                }
            ],
            claim_type="blocked",
            evidence_available=blockers,
            blocked_reason=", ".join(blockers) if blockers else "pre_dispatch_governance_failed",
            source_metadata=dict(message.context.get("source_metadata", {})),
            conflicts=list(message.context.get("conflicts", [])),
            security_warnings=list(message.context.get("security_warnings", [])),
            lifecycle_status="blocked",
            compressed_memory="Pre-dispatch governance blocked unsafe context after Leonidas security review.",
            decision_rationale="Unsafe, blocked, stale, or conflicting context cannot be passed into agent reasoning.",
        )

    def request_self_check(self, task: Task, result: AgentMessage) -> dict[str, Any]:
        agent = self.agents[task.agent]
        return agent.self_check(result)

    def _peer_review_message(self, reviewer: str, task: Task, result: AgentMessage) -> AgentMessage:
        target_context = self.compact_peer_context(result.context, reviewer=reviewer)
        return AgentMessage(
            agent=reviewer,
            phase=task.phase,
            jtbd=f"Review {task.agent} output for {task.phase}",
            summary=result.summary,
            done_status="partial",
            confidence=0.5,
            context={
                "mode": "review",
                "reviewer": reviewer,
                "target_agent": task.agent,
                "task_phase": task.phase,
                "target_context": target_context,
                "evidence_pack": target_context.get("evidence_pack", {}),
                "context_budget": target_context.get("context_budget", {}),
            },
            assumptions=list(result.assumptions),
            evidence=list(result.evidence),
            risks=list(result.risks),
            open_questions=list(result.open_questions),
            requested_feedback=list(result.requested_feedback),
            feedback_to=[task.agent],
            next_action="hold",
        )

    def compact_peer_context(self, context: dict[str, Any], *, reviewer: str) -> dict[str, Any]:
        return minimize_context(context, agent=reviewer)

    def review_with_critic(self, task: Task, result: AgentMessage) -> AgentMessage:
        return self.agents["critic"].run(self._peer_review_message("critic", task, result))

    def review_with_devil_advocate(self, task: Task, result: AgentMessage) -> AgentMessage:
        return self.agents["devils_advocate"].run(self._peer_review_message("devils_advocate", task, result))

    def review_with_governance(self, task: Task, result: AgentMessage) -> AgentMessage:
        return self.agents["governance"].run(self._peer_review_message("governance", task, result))

    def peer_review_sequence(self, task: Task) -> list[str]:
        sequence = []
        if task.requires_critic:
            sequence.append("critic")
        if task.requires_devil_advocate:
            sequence.append("devils_advocate")
        if task.requires_governance:
            sequence.append("governance")

        if task.agent in sequence:
            sequence = [reviewer for reviewer in sequence if reviewer != task.agent]
        return sequence

    def formula_review_sequence(self) -> list[str]:
        return ["statistical", "data", "devils_advocate", "research"]

    def formula_review_sequence_for(self, task: Task) -> list[str]:
        context = formula_context(task.context)
        definition = get_formula_definition(context)
        if definition is not None and definition.required_review_agents:
            return list(definition.required_review_agents)
        sequence = self.formula_review_sequence()
        if context.get("ci_required") and "evaluation" not in sequence:
            sequence.append("evaluation")
        if context.get("formula_class") in {"policy", "constraint"} and "governance" not in sequence:
            sequence.append("governance")
        return sequence

    def _reviewer_result(self, reviewer: str, task: Task, result: AgentMessage) -> AgentMessage:
        if reviewer == "critic":
            return self.review_with_critic(task, result)
        if reviewer == "devils_advocate":
            return self.review_with_devil_advocate(task, result)
        if reviewer == "governance":
            return self.review_with_governance(task, result)
        return self.agents[reviewer].run(self._peer_review_message(reviewer, task, result))

    def evaluate_feedback(
        self,
        agent_result: AgentMessage,
        self_check: dict[str, Any],
        peer_feedback: list[AgentMessage],
    ) -> Decision:
        if agent_result.done_status == "blocked" or self_check.get("quality") == "blocked":
            return "hold"

        evidence_decision = self.evaluate_evidence_gate(agent_result)
        if evidence_decision in {"hold", "reject", "revise"}:
            return evidence_decision

        if agent_result.phase == "formula_review":
            formula_decision = self.evaluate_formula_gate(agent_result)
            if formula_decision in {"hold", "reject", "revise"}:
                return formula_decision

        if agent_result.phase == "policy_design":
            context = agent_result.context
            if not (
                context.get("reward_calibrated")
                and isinstance(context.get("no_action_baseline"), dict)
                and bool(context.get("guardrails"))
                and context.get("governance_review")
            ):
                return "hold"
            if reward_policy_blockers(context):
                return "hold"

        if self_check.get("quality") == "insufficient":
            return "revise"

        if any(review.next_action == "reject" for review in peer_feedback):
            return "reject"

        if any(review.next_action == "revise" for review in peer_feedback):
            return "revise"

        if any(review.next_action == "hold" for review in peer_feedback):
            return "hold"

        if agent_result.next_action == "approve" and all(review.next_action == "approve" for review in peer_feedback):
            return "approve"

        return "revise"

    def evaluate_evidence_gate(self, message: AgentMessage) -> Decision:
        if not message.context.get("evidence_gate_required"):
            return "approve"

        if message.blocked_reason:
            return "hold"

        ocean_hold_reason = ocean_context_requires_hold(message.context)
        if ocean_hold_reason and message.next_action == "approve":
            return "hold"

        if message.security_warnings or message.context.get("security_warnings"):
            critical = [
                warning
                for warning in [*message.security_warnings, *message.context.get("security_warnings", [])]
                if warning.get("severity") == "critical" or warning.get("action") == "block"
            ]
            if critical:
                return "hold"

        security_review = message.context.get("security_review", {})
        if security_review:
            if security_review.get("safe_to_reason") is False:
                return "hold"
            if message.next_action == "approve" and security_review.get("safe_to_execute") is False:
                return "hold"

        blocked_sources = message.context.get("blocked_sources", [])
        if blocked_sources:
            return "hold"

        retrieval_governance = message.context.get("retrieval_governance", {})
        if retrieval_governance and not retrieval_governance.get("passed", True):
            return "hold"

        unresolved_conflicts = [
            conflict
            for conflict in [*message.conflicts, *message.context.get("conflicts", [])]
            if conflict.get("conflict_detected") and conflict.get("resolution_status") != "resolved"
        ]
        if unresolved_conflicts:
            return "hold"

        if message.context.get("evidence_strength_warnings") and message.next_action == "approve":
            return "revise"

        unsupported = self.agents.get(message.agent, BaseAgent()).unsupported_claims(message)
        if unsupported:
            return "hold"

        for claim in message.claims:
            category = str(claim.get("category", "")).lower()
            claim_type = claim.get("claim_type", message.claim_type)
            if claim_type == "blocked":
                return "hold"
            if category in {"psychological_trait", "personality", "ocean"}:
                if message.context.get("ocean_consent") is not True:
                    return "hold"
                if claim_type in {"observed", "inferred"} and message.context.get("ocean_only_decision"):
                    return "hold"
            if category in {"effect", "significance"} and claim_type in {"observed", "inferred"}:
                if not message.uncertainty and not message.context.get("simulation_result"):
                    return "hold"
            if category == "causal" and claim_type in {"observed", "inferred"}:
                has_design = any(
                    message.context.get(key)
                    for key in ["identification_strategy", "treatment_group", "control_group"]
                )
                if not has_design:
                    return "hold"

        if message.next_action == "approve":
            readiness_flags = message.readiness_flags or {}
            hard_flags = [
                "data_ready",
                "hypotheses_mece_ready",
                "hypotheses_tested_ready",
                "measurement_ready",
                "behavioral_fit_ready",
                "reward_ready",
                "policy_ready",
                "governance_ready",
            ]
            if any(flag in readiness_flags and readiness_flags[flag] is False for flag in hard_flags):
                return "hold"

        return "approve"

    def evaluate_formula_gate(self, message: AgentMessage) -> Decision:
        context = formula_context(message.context)
        formula_class = context.get("formula_class")
        missing_required = [key for key in context.get("required_context", []) if key not in context]

        if ocean_context_requires_hold(context):
            return "hold"

        if formula_class in {"policy", "constraint"} and context.get("governance_blocked"):
            return "hold"

        if formula_class == "policy":
            if reward_policy_blockers(context):
                return "hold"

        if formula_class == "evaluation" and context.get("formula_key") == "dr_ope":
            required_support = ["overlap_check", "propensity_clipping", "cross_fitting", "support_check"]
            if any(context.get(key) is not True for key in required_support):
                return "hold"

        if context.get("ci_required"):
            uncertainty = message.uncertainty or context.get("uncertainty", {})
            has_ci = all(
                key in uncertainty
                for key in [
                    "effect_estimate",
                    "ci_lower",
                    "ci_upper",
                    "ci_method",
                    "sample_size",
                    "confidence_level",
                    "contains_null",
                ]
            )
            if not has_ci:
                return "hold"
            if float(uncertainty["ci_lower"]) > float(uncertainty["ci_upper"]):
                return "hold"
            if int(uncertainty["sample_size"]) <= 0:
                return "hold"
            if float(uncertainty["confidence_level"]) < 0.90:
                return "hold"
            null_value = float(context.get("null_value", 0.0))
            if float(uncertainty["ci_lower"]) <= null_value <= float(uncertainty["ci_upper"]):
                return "revise"

        if missing_required:
            return "revise"

        return "approve"

    def reflect(
        self,
        task: Task,
        result: AgentMessage,
        self_check: dict[str, Any],
        peer_feedback: list[AgentMessage],
        decision: Decision,
    ) -> OrchestrationReflection:
        clear = [f"Agent {result.agent} delivered {result.done_status} with confidence {result.confidence:.2f}"]
        unclear = list(self_check.get("missing", []))
        missing = list(self_check.get("missing", []))
        if result.phase == "formula_review":
            context = formula_context(result.context)
            missing.extend([key for key in context.get("required_context", []) if key not in context])
            if context.get("ci_required") and not result.uncertainty and not context.get("uncertainty"):
                missing.append("uncertainty")
        if result.context.get("evidence_gate_required"):
            unsupported = self.agents.get(result.agent, BaseAgent()).unsupported_claims(result)
            if unsupported:
                missing.append("supported_claims")
            if not result.claims:
                missing.append("claims")
            if result.clarification_questions:
                missing.extend(result.clarification_questions)
            if result.security_warnings or result.context.get("security_warnings"):
                missing.append("security_warnings")
            if result.context.get("blocked_sources"):
                missing.extend(result.context.get("blocked_sources", []))
            if result.context.get("conflicts"):
                missing.append("unresolved_conflicts")

        for review in peer_feedback:
            if review.risks:
                unclear.extend(review.risks)
            if review.open_questions:
                missing.extend(review.open_questions)

        why = {
            "approve": "Output is complete enough to move forward.",
            "revise": "Output needs tightening or a more precise follow-up review.",
            "reject": "Output is not yet structurally trustworthy enough.",
            "hold": "A blocker or unresolved risk needs to be cleared first.",
        }[decision]

        reflection = OrchestrationReflection(
            task_phase=task.phase,
            agent=task.agent,
            what_is_clear=clear,
            what_is_unclear=sorted(set(unclear)),
            what_is_missing=sorted(set(missing)),
            why_next_action=why,
            decision=decision,
        )
        self.reflections.append(reflection)
        return reflection

    def route_revision(
        self,
        task: Task,
        agent_result: AgentMessage,
        peer_feedback: list[AgentMessage],
    ) -> Task:
        feedback_text = " | ".join(
            filter(None, [agent_result.summary, *[review.summary for review in peer_feedback]])
        )
        context = dict(task.context)
        context["revision_reason"] = feedback_text

        if task.phase == "formula_review":
            if any(review.agent == "data" for review in peer_feedback):
                return Task(
                    phase=task.phase,
                    agent="data",
                    prompt=f"Revise formula inputs and measurability: {task.prompt}",
                    model=self.choose_model(task),
                    analysis_depth=task.analysis_depth,
                    requires_critic=task.requires_critic,
                    requires_devil_advocate=task.requires_devil_advocate,
                    requires_governance=task.requires_governance,
                    context=context,
                )

        return Task(
            phase=task.phase,
            agent=task.agent,
            prompt=f"Revise with feedback: {feedback_text}".strip(),
            model=self.choose_model(task),
            analysis_depth=task.analysis_depth,
            requires_critic=task.requires_critic,
            requires_devil_advocate=task.requires_devil_advocate,
            requires_governance=task.requires_governance,
            context=context,
        )

    def reframe_task(
        self,
        task: Task,
        agent_result: AgentMessage,
        peer_feedback: list[AgentMessage],
    ) -> Task:
        context = dict(task.context)
        context["reframe_reason"] = " | ".join(
            filter(None, [agent_result.summary, *[review.summary for review in peer_feedback]])
        )
        return Task(
            phase=task.phase,
            agent=task.agent,
            prompt=f"Reframe from scratch after rejection: {task.prompt}",
            model="GPT-5.4" if task.analysis_depth == "deep" else self.choose_model(task),
            analysis_depth=task.analysis_depth,
            requires_critic=task.requires_critic,
            requires_devil_advocate=task.requires_devil_advocate,
            requires_governance=task.requires_governance,
            context=context,
        )

    def pause_for_blocker_resolution(
        self,
        task: Task,
        agent_result: AgentMessage,
        peer_feedback: list[AgentMessage],
    ) -> AgentMessage:
        reflection = self.reflect(task, agent_result, self_check={"quality": "blocked", "missing": ["blocker"]}, peer_feedback=peer_feedback, decision="hold")
        held_result = AgentMessage(
            agent="orchestrator",
            phase=task.phase,
            jtbd=task.prompt,
            summary=f"Orchestration is on hold after {agent_result.agent}: {agent_result.summary}",
            done_status="blocked",
            confidence=agent_result.confidence,
            context=dict(agent_result.context),
            assumptions=list(agent_result.assumptions),
            evidence=list(agent_result.evidence),
            risks=list(agent_result.risks),
            open_questions=list(agent_result.open_questions),
            requested_feedback=["Resolve blocker before continuing."],
            feedback_to=["orchestrator"],
            next_action="hold",
            uncertainty=dict(agent_result.uncertainty),
            claims=list(agent_result.claims),
            claim_type="blocked",
            evidence_required=list(agent_result.evidence_required),
            evidence_available=list(agent_result.evidence_available),
            clarification_questions=list(agent_result.clarification_questions),
            blocked_reason=agent_result.blocked_reason or "orchestration_hold",
            readiness_flags=dict(agent_result.readiness_flags),
            source_metadata=dict(agent_result.source_metadata),
            conflicts=list(agent_result.conflicts),
            security_warnings=list(agent_result.security_warnings),
            lifecycle_status="blocked",
            compressed_memory=agent_result.compressed_memory,
            decision_rationale="The orchestrator converted a failed gate into a hold result.",
        )
        self.history.append(
            OrchestrationStep(
                task=task,
                result=held_result,
                self_check={"quality": "blocked", "missing": ["blocker"]},
                peer_feedback=peer_feedback,
                reflection=reflection,
                decision="hold",
            )
        )
        self.update_run_state(task, held_result, "hold")
        return held_result

    def record_step(
        self,
        task: Task,
        result: AgentMessage,
        self_check: dict[str, Any],
        peer_feedback: list[AgentMessage],
        decision: Decision,
    ) -> None:
        reflection = self.reflect(task, result, self_check, peer_feedback, decision)
        self.history.append(
            OrchestrationStep(
                task=task,
                result=result,
                self_check=self_check,
                peer_feedback=peer_feedback,
                reflection=reflection,
                decision=decision,
            )
        )
        self.update_run_state(task, result, decision)

    def update_run_state(self, task: Task, result: AgentMessage, decision: Decision) -> None:
        entry = {
            "phase": task.phase,
            "agent": task.agent,
            "decision": decision,
            "summary": result.summary[:300],
        }
        self.run_state["decisions"] = [*self.run_state.get("decisions", [])[-9:], entry]
        self.run_state["last_summary"] = result.summary[:500]
        blockers = list(self.run_state.get("blockers", []))
        if result.blocked_reason:
            blockers.append(result.blocked_reason)
        blockers.extend(result.risks[:3] if decision == "hold" else [])
        self.run_state["blockers"] = sorted(set(blockers))[-10:]
        questions = [*self.run_state.get("open_questions", []), *result.open_questions, *result.clarification_questions]
        self.run_state["open_questions"] = sorted(set(questions))[-10:]
        conflicts = [
            *self.run_state.get("conflicts", []),
            *result.conflicts,
            *result.context.get("conflicts", []),
        ]
        self.run_state["conflicts"] = conflicts[-10:]
        security_warnings = [
            *self.run_state.get("security_warnings", []),
            *result.security_warnings,
            *result.context.get("security_warnings", []),
        ]
        self.run_state["security_warnings"] = security_warnings[-10:]
        security_review = result.context.get("security_review", {})
        if security_review:
            self.run_state["last_security_review"] = {
                "agent": security_review.get("agent", "Leonidas"),
                "security_status": security_review.get("security_status"),
                "risk_level": security_review.get("risk_level"),
                "safe_to_reason": security_review.get("safe_to_reason"),
                "safe_to_execute": security_review.get("safe_to_execute"),
            }
        source_metadata = result.source_metadata or result.context.get("source_metadata", {})
        if source_metadata:
            self.run_state["last_source_metadata"] = source_metadata

    def run_orchestration(self, task: Task) -> AgentMessage:
        if task.phase in {"customer_data_intake", "customer_analysis", "nudge_analysis"}:
            return self.run_customer_data_intake(task)

        if task.phase == "formula_review":
            return self.run_formula_review(task)

        current_task = task
        while True:
            result = self.dispatch(current_task)
            self_check = self.request_self_check(current_task, result)

            decision = self.evaluate_feedback(result, self_check, [])
            self.record_step(current_task, result, self_check, [], decision)
            if decision != "approve":
                if decision == "revise":
                    current_task = self.route_revision(current_task, result, [])
                    continue
                if decision == "reject":
                    current_task = self.reframe_task(current_task, result, [])
                    continue
                return self.pause_for_blocker_resolution(current_task, result, [])

            peer_feedback: list[AgentMessage] = []
            for reviewer in self.peer_review_sequence(current_task):
                review = self._reviewer_result(reviewer, current_task, result)
                peer_feedback.append(review)
                decision = self.evaluate_feedback(result, self_check, [review])
                self.record_step(current_task, result, self_check, [review], decision)

                if decision == "approve":
                    continue
                if decision == "revise":
                    current_task = self.route_revision(current_task, result, [review])
                    break
                if decision == "reject":
                    current_task = self.reframe_task(current_task, result, [review])
                    break
                return self.pause_for_blocker_resolution(current_task, result, [review])
            else:
                return result

    def should_stage_hold_final_formula(self, stage_name: str, result: AgentMessage) -> bool:
        if result.next_action != "hold":
            return False
        context = result.context
        if context.get("formula_key") == "reward_policy" and stage_name == "devils_advocate":
            cleared = not reward_policy_blockers(context)
            return not cleared
        return True

    def _formula_stage_prompt(
        self,
        task: Task,
        stage_name: str,
        previous_result: Optional[AgentMessage],
    ) -> str:
        if previous_result is None:
            return task.prompt
        return (
            f"{task.prompt}\n\n"
            f"Previous stage ({previous_result.agent}) summary: {previous_result.summary}\n"
            f"Now review this from the perspective of {stage_name}."
        )

    def run_formula_review(self, task: Task) -> AgentMessage:
        stage_results: list[tuple[str, AgentMessage, dict[str, Any], Decision]] = []
        review_context = formula_context(task.context)
        review_context.setdefault("evidence_gate_required", True)
        review_context.setdefault("hypotheses", build_mece_hypotheses(review_context))
        review_context["hypotheses_mece_ready"] = mece_groups_complete(review_context["hypotheses"])
        if task.context.get("require_testable_hypothesis") and not any(
            hypothesis.get("status") == "testable" for hypothesis in review_context["hypotheses"]
        ):
            return self._blocked_hypothesis_result(task, review_context)

        for stage_index, stage_name in enumerate(self.formula_review_sequence_for(task)):
            stage_task = Task(
                phase=task.phase,
                agent=stage_name,
                prompt=self._formula_stage_prompt(
                    task,
                    stage_name,
                    None if not stage_results else stage_results[-1][1],
                ),
                model=self.choose_model(task),
                analysis_depth=task.analysis_depth,
                requires_critic=task.requires_critic,
                requires_devil_advocate=task.requires_devil_advocate,
                requires_governance=task.requires_governance,
                context={
                    **review_context,
                    "formula_review_stage": stage_name,
                    "formula_review_stage_index": stage_index,
                    "previous_stage_agent": None if not stage_results else stage_results[-1][1].agent,
                    "previous_stage_summary": None if not stage_results else stage_results[-1][1].summary,
                },
            )

            result = self.dispatch(stage_task)
            self_check = self.request_self_check(stage_task, result)
            decision = self.evaluate_feedback(result, self_check, [])
            self.record_step(stage_task, result, self_check, [], decision)
            stage_results.append((stage_name, result, self_check, decision))

            if decision == "reject":
                # The formula review should continue collecting evidence, but keep the rejection visible.
                continue
            if decision == "hold" and result.done_status == "blocked":
                continue

        stage_decisions = [decision for _, _, _, decision in stage_results]
        gate_decision = self.evaluate_formula_gate(
            AgentMessage(
                agent="orchestrator",
                phase=task.phase,
                jtbd=task.prompt,
                summary="Formula gate evaluation",
                done_status="partial",
                confidence=0.5,
                context=review_context,
                uncertainty=dict(review_context.get("uncertainty", {})),
            )
        )
        stage_hold_blocks = [
            self.should_stage_hold_final_formula(name, result)
            for name, result, _, decision in stage_results
            if decision == "hold"
        ]
        if gate_decision == "hold" or any(stage_hold_blocks):
            final_decision: Decision = "hold"
        elif gate_decision == "reject" or any(decision == "reject" for decision in stage_decisions):
            final_decision = "reject"
        elif gate_decision == "revise" or any(decision == "revise" for decision in stage_decisions):
            final_decision = "revise"
        else:
            final_decision = "approve"

        summaries = [f"{name}: {result.next_action} ({result.done_status})" for name, result, _, _ in stage_results]
        risks = sorted({risk for _, result, _, _ in stage_results for risk in result.risks})
        open_questions = sorted({question for _, result, _, _ in stage_results for question in result.open_questions})
        evidence = sorted({item for _, result, _, _ in stage_results for item in result.evidence})
        assumptions = sorted({item for _, result, _, _ in stage_results for item in result.assumptions})

        return AgentMessage(
            agent="orchestrator",
            phase=task.phase,
            jtbd=task.prompt,
            summary="Formula review completed: " + " | ".join(summaries),
            done_status="done" if final_decision == "approve" else "partial",
            confidence=min(0.95, max((result.confidence for _, result, _, _ in stage_results), default=0.0)),
            context={
                **review_context,
                "formula_review_stage_summaries": summaries,
                "formula_review_final_decision": final_decision,
                "formula_gate_decision": gate_decision,
                "core_agent_roles": self.core_agent_roles(),
            },
            assumptions=assumptions,
            evidence=evidence,
            risks=risks,
            open_questions=open_questions,
            requested_feedback=[],
            feedback_to=[],
            next_action=final_decision,
            uncertainty=dict(review_context.get("uncertainty", {})),
            claims=[
                {
                    "statement": "Formula review decision is based on staged agent evidence and formula gates.",
                    "claim_type": "observed",
                    "category": "process",
                    "evidence_available": summaries,
                }
            ],
            claim_type="observed",
            evidence_available=summaries,
            readiness_flags={
                "hypotheses_mece_ready": bool(review_context.get("hypotheses_mece_ready")),
                "measurement_ready": final_decision == "approve",
            },
        )

    def run_customer_data_intake(self, task: Task) -> AgentMessage:
        context = dict(task.context)
        profile = infer_customer_data_profile(context)
        context["customer_data_profile"] = profile
        hypotheses = build_mece_hypotheses(context)
        missing = customer_data_missing_fields(context)
        context["hypotheses"] = hypotheses
        context["missing_required_fields"] = missing
        context["evidence_gate_required"] = True
        governed_context = self.build_agent_context(task, context)
        questions = clarification_questions_for_missing(missing)
        critical_security = [
            warning
            for warning in governed_context.get("security_warnings", [])
            if warning.get("severity") == "critical" or warning.get("action") == "block"
        ]
        governance_blockers = (
            bool(governed_context.get("blocked_sources"))
            or bool(critical_security)
            or not governed_context.get("retrieval_governance", {}).get("passed", True)
        )
        data_ready = not missing and not governance_blockers
        if critical_security:
            questions.append("Der externe Inhalt enthaelt Sicherheits- oder Prompt-Injection-Risiken und muss bereinigt werden.")
        readiness_flags = {
            "data_ready": data_ready,
            "hypotheses_mece_ready": mece_groups_complete(hypotheses),
            "hypotheses_tested_ready": data_ready,
            "measurement_ready": data_ready,
            "behavioral_fit_ready": bool(context.get("behavioral_method") or context.get("behavioral_methods")),
            "reward_ready": bool(context.get("reward_calibrated")),
            "policy_ready": bool(context.get("reward_calibrated") and context.get("guardrails")),
            "governance_ready": bool(context.get("governance_review") or context.get("consent_field")),
        }
        claims = [
            {
                "statement": "Customer data profile was inferred from the provided schema context.",
                "claim_type": "observed" if profile.get("available_columns") else "unknown",
                "category": "data_quality",
                "evidence_available": list(profile.get("available_columns", [])),
            },
            {
                "statement": "Effect, causality, significance and policy recommendations are blocked until required data gates pass.",
                "claim_type": "blocked" if not data_ready else "hypothesis",
                "category": "effect",
                "evidence_available": [],
            },
        ]
        result = AgentMessage(
            agent="orchestrator",
            phase="customer_data_intake",
            jtbd=task.prompt,
            summary="Customer data intake completed." if data_ready else "Customer data intake is blocked by missing fields.",
            done_status="done" if data_ready else "blocked",
            confidence=0.86 if data_ready else 0.6,
            context={
                **governed_context,
                "hypotheses": hypotheses,
                "missing_required_fields": missing,
                "core_agent_roles": self.core_agent_roles(),
            },
            assumptions=["Customer data must be understood before calculation or recommendation."],
            evidence=list(profile.get("available_columns", [])),
            risks=[] if data_ready else ["Unsupported recommendations are blocked until missing fields are clarified."],
            open_questions=questions,
            requested_feedback=["Please answer clarification questions before calculation starts."] if questions else [],
            feedback_to=["orchestrator"],
            next_action="approve" if data_ready else "hold",
            claims=claims,
            claim_type="observed" if data_ready else "blocked",
            evidence_required=missing,
            evidence_available=list(profile.get("available_columns", [])),
            clarification_questions=questions,
            blocked_reason=", ".join(missing) if missing else ("governance_blocker" if governance_blockers else None),
            readiness_flags=readiness_flags,
            source_metadata=dict(governed_context.get("source_metadata", {})),
            conflicts=list(governed_context.get("conflicts", [])),
            security_warnings=list(governed_context.get("security_warnings", [])),
            lifecycle_status="active",
            compressed_memory=str(governed_context.get("run_state", {}).get("last_summary", ""))[:500],
            decision_rationale="Customer data intake is approved only when schema and governance gates pass.",
        )
        self.record_step(task, result, self.request_self_check(task, result), [], result.next_action)
        return result

    def _blocked_hypothesis_result(self, task: Task, context: dict[str, Any]) -> AgentMessage:
        questions = ["Welche Hypothese soll mit welchen Daten getestet werden?"]
        return AgentMessage(
            agent="orchestrator",
            phase=task.phase,
            jtbd=task.prompt,
            summary="Formula review is on hold because no testable hypothesis is available.",
            done_status="blocked",
            confidence=0.6,
            context=context,
            assumptions=["Formula review requires at least one testable hypothesis when strict hypothesis gating is requested."],
            evidence=[],
            risks=["A formula can look valid while answering no testable business or behavioral hypothesis."],
            open_questions=questions,
            requested_feedback=["Provide a testable hypothesis or the required data fields."],
            feedback_to=["orchestrator"],
            next_action="hold",
            claims=[
                {
                    "statement": "No testable hypothesis is available for this formula review.",
                    "claim_type": "blocked",
                    "category": "hypothesis",
                    "evidence_available": [],
                }
            ],
            claim_type="blocked",
            clarification_questions=questions,
            blocked_reason="no_testable_hypothesis",
            readiness_flags={"hypotheses_mece_ready": True, "hypotheses_tested_ready": False},
        )
