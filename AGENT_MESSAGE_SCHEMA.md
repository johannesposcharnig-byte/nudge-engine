# Agent Message Schema

## Zweck

Dieses Dokument definiert das einheitliche Kommunikationsformat zwischen Orchestrator und Agents.

## JSON Schema

```json
{
  "agent": "research",
  "phase": "problem_definition",
  "jtbd": "science-backed mechanism review",
  "summary": "short summary of the output",
  "done_status": "done",
  "confidence": 0.86,
  "claims": [
    {
      "statement": "The intervention effect is positive.",
      "claim_type": "hypothesis",
      "category": "effect",
      "evidence_required": ["effect_estimate", "ci_lower", "ci_upper", "ci_method"],
      "evidence_available": [],
      "hypothesis_id": "H4"
    }
  ],
  "claim_type": "hypothesis",
  "evidence_required": [
    "effect_estimate",
    "ci_lower",
    "ci_upper",
    "ci_method"
  ],
  "evidence_available": [],
  "hypothesis_id": "H4",
  "hypothesis_status": "not_testable_yet",
  "clarification_questions": [
    "Welche Zielvariable soll optimiert oder erklaert werden?"
  ],
  "blocked_reason": "missing_outcome_variable",
  "readiness_flags": {
    "data_ready": false,
    "hypotheses_mece_ready": true,
    "hypotheses_tested_ready": false,
    "measurement_ready": false,
    "behavioral_fit_ready": false,
    "reward_ready": false,
    "policy_ready": false,
    "governance_ready": false
  },
  "context_budget": {
    "mode": "evidence_pack_only",
    "estimated_reduction": 0.78,
    "target_reduction": 0.7,
    "max_documents": 3,
    "max_sections_per_document": 2,
    "selected_documents": ["formula_registry", "validation_acceptance"],
    "selected_sections": ["formula_definition", "ci_rule"]
  },
  "evidence_pack": {
    "task_phase": "formula_review",
    "agent": "statistical",
    "selected_sources": {
      "documents": ["formula_registry", "validation_acceptance"],
      "sections": ["formula_definition", "ci_rule"],
      "source_metadata": {
        "formula_registry": {
          "relevance_score": 0.9,
          "selection_reason": "Formula metadata is required for formula review.",
          "retrieval_timestamp": "2026-05-09T12:00:00+00:00",
          "retrieval_method": "agent_source_policy",
          "retrieval_query": "statistical evidence pack",
          "source_confidence": 0.9,
          "validation_status": "approved",
          "evidence_level": "high",
          "owner": "orchestrator",
          "last_reviewed": "2026-05-09T12:00:00+00:00",
          "lifecycle_status": "active"
        }
      }
    },
    "retrieval_governance": {
      "blocked_sources": [],
      "stale_sources": [],
      "warnings": [],
      "passed": true
    },
    "security_warnings": [],
    "security_agent": "Leonidas",
    "security_review": {
      "agent": "Leonidas",
      "security_status": "approve",
      "risk_level": "low",
      "detected_risks": [],
      "blocked_content": [],
      "required_mitigations": [],
      "safe_to_reason": true,
      "safe_to_execute": true,
      "decision_rationale": "Leonidas found no security or integrity blockers."
    },
    "conflicts": [],
    "run_state": {
      "last_summary": "Customer data intake found missing outcome."
    }
  },
  "source_metadata": {},
  "conflicts": [],
  "security_warnings": [],
  "security_review": {
    "agent": "Leonidas",
    "security_status": "approve",
    "risk_level": "low",
    "safe_to_reason": true,
    "safe_to_execute": true
  },
  "lifecycle_status": "active",
  "compressed_memory": "short audit summary",
  "decision_rationale": "why this action is approved, revised, rejected, or held",
  "uncertainty": {
    "effect_estimate": 0.42,
    "ci_lower": 0.18,
    "ci_upper": 0.66,
    "ci_method": "bootstrap",
    "sample_size": 240,
    "confidence_level": 0.95,
    "contains_null": false,
    "decision_rule": "approve only if interval excludes the null and support checks pass"
  },
  "assumptions": [
    "assumption one"
  ],
  "evidence": [
    "evidence one"
  ],
  "risks": [
    "risk one"
  ],
  "open_questions": [
    "question one"
  ],
  "requested_feedback": [
    "please review evidence strength"
  ],
  "feedback_to": [
    "orchestrator",
    "statistical"
  ],
  "next_action": "approve",
  "model_policy": {
    "default_model": "GPT-5.4-Mini",
    "analysis_model": "GPT-5.4",
    "reason": "deep conflict analysis"
  }
}
```

## Pflichtfelder

- `agent`
- `phase`
- `jtbd`
- `summary`
- `done_status`
- `confidence`
- `claims`
- `claim_type`
- `assumptions`
- `evidence`
- `risks`
- `open_questions`
- `requested_feedback`
- `feedback_to`
- `next_action`

## Zulässige Werte

## Claim- und Evidence-Konvention

- Jede zentrale Aussage muss als Claim dokumentiert werden.
- `observed`: direkt aus Daten, Schema, Dokumenten, Tests oder Simulation ableitbar.
- `inferred`: plausibel abgeleitet, aber nicht bewiesen; muss Evidenz und Annahmen nennen.
- `hypothesis`: pruefbare Annahme; darf nicht als Ergebnis oder Empfehlung formuliert werden.
- `unknown`: Datenlage reicht nicht; der Agent muss Rueckfragen stellen.
- `blocked`: Aussage darf nicht gemacht werden, bis ein Blocker geloest ist.
- Wirkung, Kausalitaet und Signifikanz duerfen nur freigaberelevant werden, wenn Datenlage, Design und Unsicherheitsfelder dies tragen.
- Wenn Daten eine Aussage nicht tragen, muss der Agent dies explizit sagen.

## Hypothesen-Konvention

- Jeder Analyseprozess startet mit MECE-Hypothesen.
- Zulaessige `hypothesis_status` Werte sind `testable`, `not_testable_yet` und `out_of_scope`.
- Standardgruppen sind Datenqualitaet, Zielverhalten, Behavioral Mechanism, Effekt, Segment/Heterogenitaet, Reward/Policy und Governance/Risiko.
- Nicht testbare Hypothesen bleiben sichtbar und duerfen nicht in Empfehlungen umgewandelt werden.

## OCEAN / Psychological-Signal-Konvention

- Psychologische Traits sind optionale Signale, keine Fakten ueber zukuenftiges Verhalten.
- `ocean_consent` muss `true` sein, bevor `tipi_responses`, `ocean_scores` oder `ocean_signal` fuer Personalisierung genutzt werden.
- OCEAN/TIPI Claims muessen als `hypothesis` oder vorsichtig begruendetes `inferred` markiert werden; sie duerfen keine Wirkung, Signifikanz oder Policy-Freigabe allein tragen.
- `ocean_only_decision=true` erzwingt `hold`, wenn ein Agent `approve` anstrebt.
- Relevante Kontextfelder sind `tipi_responses`, `ocean_scores`, `ocean_signal`, `ocean_consent`, `ocean_instrument`, `ocean_source`, `psychological_signal` und `uses_ocean_for_personalization`.

## Readiness Flags

- `data_ready`
- `hypotheses_mece_ready`
- `hypotheses_tested_ready`
- `measurement_ready`
- `behavioral_fit_ready`
- `reward_ready`
- `policy_ready`
- `governance_ready`

Ein `false` in einem freigaberelevanten Flag erzwingt `hold`, sofern der aktuelle Schritt `approve` anstrebt.

## Context-Budget-Konvention

- Agents erhalten standardmaessig ein `evidence_pack`.
- `context_budget.mode` ist normalerweise `evidence_pack_only`.
- Maximal 3 Dokumente und 2 Sections pro Dokument duerfen pro Agentenlauf ausgewaehlt werden.
- Full Context ist verboten, ausser `full_context_required` und `full_context_reason` sind gesetzt.
- Wiederholtes Lesen alter Outputs wird durch `run_state` ersetzt.
- Ein Agent, dem Kontext fehlt, soll eine konkrete Rueckfrage stellen statt breit zu lesen.

## Cognitive-Governance-Konvention

Jede Quelle im Evidence Pack muss folgende Felder fuehren:

- `relevance_score`
- `selection_reason`
- `retrieval_timestamp`
- `retrieval_method`
- `retrieval_query`
- `source_confidence`
- `validation_status`
- `evidence_level`
- `owner`
- `last_reviewed`
- `lifecycle_status`

Zulaessige `validation_status` Werte:

- `draft`
- `revise`
- `approved`
- `deprecated`
- `blocked`

Zulaessige `evidence_level` Werte:

- `low`
- `medium`
- `high`
- `experimentally_validated`

Zulaessige `lifecycle_status` Werte:

- `active`
- `stale`
- `archived`
- `deprecated`
- `blocked`

Unaufgeloeste Konflikte, kritische Security-Warnungen sowie `blocked` oder `deprecated` Quellen erzwingen `hold`.

Reasoning wird nicht als Chain-of-thought persistiert. Erlaubt sind nur auditierbare Felder wie `decision_rationale` und `compressed_memory`.

## Leonidas Security-Konvention

- `security_agent` ist standardmaessig `Leonidas`.
- `security_review.security_status` kann `approve`, `revise`, `hold` oder `reject` sein.
- `security_review.risk_level` kann `low`, `medium`, `high` oder `critical` sein.
- `safe_to_reason=false` blockiert Agenten-Reasoning vor Dispatch.
- `safe_to_execute=false` blockiert Approval, Policy-Rollout oder aktive Intervention.
- `detected_risks` muessen Risikoart, Schwere, Evidenz, Aktion und Begruendung enthalten.
- Leonidas prueft Prompt Injection, Governance Bypass, Reward-/Policy-Override, unsichere Quellen und auffaellige Daten-Schema-Verletzungen.

## Unsicherheitskonvention

- `confidence` ist die subjektive Sicherheit des Agents zwischen `0.0` und `1.0`.
- `confidence_level` ist das statistische Konfidenzniveau fuer Intervalle.
- Standard fuer belastbare Effektauswertungen ist `0.95`.
- `0.90` ist fuer explorative Iterationen erlaubt.
- Signifikanz darf nur aus `effect_estimate`, `ci_lower`, `ci_upper`, `ci_method`, `sample_size` und `confidence_level` abgeleitet werden.
- Wenn eine Wirkungsschaetzung keine `uncertainty`-Felder hat, muss der Orchestrator `hold` oder `revise` setzen.

### `done_status`

- `done`
- `partial`
- `blocked`

### `next_action`

- `approve`
- `revise`
- `reject`
- `hold`

## Feedback-Konvention

- Jede Nachricht muss an mindestens einen Empfaenger gerichtet sein.
- Feedback muss immer eine konkrete Entscheidung enthalten.
- Feedback muss fachlich begruendet sein.
- Feedback darf nie implizit sein.

## Modellkonvention

- `GPT-5.4-Mini` ist der Default fuer Standardarbeit.
- Ein groesseres Modell wird fuer tiefe Analyse, Konfliktaufloesung und komplexe Architekturfragen verwendet.
