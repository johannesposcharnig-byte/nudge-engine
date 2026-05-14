# Orchestrator Pseudocode fuer die Nudge Engine

## Zweck

Dieses Dokument beschreibt die technische Kernlogik des Orchestrators in Pseudocode.

Es modelliert:
- Routing
- Feedback-Gating
- Rueckspiel
- Eskalation
- Modellwahl
- Done-Entscheidung

## Kernprinzip

Der Orchestrator ist nicht nur Verteiler, sondern aktiver Qualitaetsknoten.

Er fragt immer:
- Ist die Arbeit erledigt?
- Ist die Qualitaet ausreichend?
- Was sagt der Critic?
- Was sagt der Devil's Advocate?
- Muss die Arbeit zur Revision zurueck?
- Kann der Output weitergegeben werden?

## Datentypen

```python
class AgentResult:
    agent: str
    phase: str
    jtbd: str
    summary: str
    done_status: str  # done | partial | blocked
    confidence: float
    assumptions: list[str]
    evidence: list[str]
    risks: list[str]
    open_questions: list[str]
    requested_feedback: list[str]
    feedback_to: list[str]
    next_action: str  # approve | revise | reject | hold


class Task:
    phase: str
    agent: str
    prompt: str
    model: str
    requires_critic: bool = False
    requires_devil_advocate: bool = False
    requires_governance: bool = False
```

## Orchestrator Ablauf

```python
def run_orchestration(task: Task):
    while True:
        agent_result = dispatch(task.agent, task.prompt, model=task.model)

        self_check = request_self_check(task.agent, agent_result)
        peer_feedback = []

        if task.requires_critic:
            peer_feedback.append(review_with_critic(task, agent_result))

        if task.requires_devil_advocate:
            peer_feedback.append(review_with_devil_advocate(task, agent_result))

        if task.requires_governance:
            peer_feedback.append(review_with_governance(task, agent_result))

        orchestrator_decision = evaluate_feedback(
            agent_result=agent_result,
            self_check=self_check,
            peer_feedback=peer_feedback,
        )

        if orchestrator_decision == "approve":
            mark_done(task.agent, agent_result)
            return agent_result

        if orchestrator_decision == "revise":
            task = route_revision(task, agent_result, peer_feedback)
            continue

        if orchestrator_decision == "reject":
            task = reframe_task(task, agent_result, peer_feedback)
            continue

        if orchestrator_decision == "hold":
            pause_for_blocker_resolution(task, agent_result, peer_feedback)
            continue
```

## Feedback-Gating

```python
def evaluate_feedback(agent_result, self_check, peer_feedback):
    if agent_result.done_status == "blocked":
        return "hold"

    if self_check["quality"] == "insufficient":
        return "revise"

    if any(fb["decision"] == "reject" for fb in peer_feedback):
        return "reject"

    if any(fb["decision"] == "revise" for fb in peer_feedback):
        return "revise"

    if all(fb["decision"] == "approve" for fb in peer_feedback) and agent_result.next_action == "approve":
        return "approve"

    return "hold"
```

## Routinglogik

```python
def route_revision(task, agent_result, peer_feedback):
    if task.agent == "data":
        return task
    if task.agent == "statistical":
        return task
    if task.agent == "ml":
        return task
    if task.agent == "policy":
        return task
    return task
```

## Rechenreihenfolge fuer den MVP

```python
workflow = [
    "problem_definition",
    "research",
    "data_readiness",
    "statistical_design",
    "ml_training",
    "policy_design",
    "offline_evaluation",
    "governance_review",
    "online_monitoring",
]
```

## Modellwahl

```python
def choose_model(task):
    if task.phase in {"problem_definition", "routing", "simple_refactor"}:
        return "GPT-5.4-Mini"

    if task.phase in {"statistical_design", "policy_design", "governance_review"}:
        return "GPT-5.4"

    if task.phase in {"deep_architecture", "conflict_resolution", "long_context_analysis"}:
        return "GPT-5.4"  # oder groesseres Modell je nach Verfuegbarkeit

    return "GPT-5.4-Mini"
```

## Done-Kriterien des Orchestrators

Der Orchestrator ist fuer einen Schritt erst done, wenn:
- der Agent selbst seine Arbeit als erledigt markiert
- mindestens der notwendige Peer-Check erfolgt ist
- kritische Blocker aufgeloest oder dokumentiert sind
- der Output im Standard-Format vorliegt
- die naechste Aktion klar ist

## Praktische Regel

- kleine, klare Tasks -> `GPT-5.4-Mini`
- tiefe Analyse, viele Abhaengigkeiten, hoher Risiko-Impact -> groesseres Modell

