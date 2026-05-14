# Rollen der 5 Kern-Agents fuer die Nudge Engine

## Leitprinzip

Die Runtime arbeitet mit 5 Kern-Agents, um Halluzinationsrisiko, Widersprueche und unnoetige Orchestrationskosten zu senken. Die frueheren 10 Rollen bleiben als Expert Capabilities erhalten, laufen aber als Submodes, Checklisten oder Review-Perspektiven innerhalb der Kern-Agents.

Kein Agent darf Wirkung, Kausalitaet, Signifikanz oder Empfehlung als Fakt behaupten, solange die Datenlage dies nicht traegt. Jede zentrale Aussage muss als `observed`, `inferred`, `hypothesis`, `unknown` oder `blocked` markiert werden.

## 1. Orchestrator

Verantwortung:
- steuert Customer Data Intake, Hypothesenbildung, Evidence Gates und finale Freigabe
- entscheidet ueber `approve`, `revise`, `reject` oder `hold`
- verbindet die Kern-Agents und spielt unzureichende Outputs zurueck
- verhindert, dass Calculation vor Daten- und Hypothesenklarheit startet

Submodes:
- Task Graph
- Reflection
- Final Decision Gate
- Revision Routing

Outputs:
- MECE-Hypothesenbaum
- Readiness Flags
- Entscheidungslog
- Rueckfragen und Blocker

## 2. Data & Measurement Agent

Verantwortung:
- analysiert Kundendaten, Schema, IDs, Zeitfelder, Outcomes und Treatments
- prueft Datenqualitaet, Leakage, Messbarkeit, CI-Logik, Support und Signifikanzvoraussetzungen
- markiert Hypothesen als `testable`, `not_testable_yet` oder `out_of_scope`
- blockiert Effekt- oder Kausalclaims, wenn Daten, Treatment, Kontrolllogik oder CI fehlen

Expert Capabilities:
- Data Agent
- Statistical Agent
- Evaluation Agent

Outputs:
- Customer Data Profile
- Missing Field Report
- Measurement Readiness
- CI- und Support-Check

## 3. Behavioral Science Agent

Verantwortung:
- prueft wissenschaftliche Fundierung und Mechanismuslogik
- bewertet Methoden wie Social Proof, Loss/Gain Framing, Commitment, Reciprocity und Cognitive Ease
- trennt theoretische Plausibilitaet von empirisch belegter Wirkung
- fordert Daten- oder Experimentnachweise an, wenn Wirkung behauptet werden soll

Expert Capabilities:
- Research Agent
- Behavioral Design Review
- Mechanism Mapping

Outputs:
- Behavioral Mechanism Review
- Evidence Strength
- Intervention Fit
- offene empirische Prueffragen

## 4. Policy & Reward Agent

Verantwortung:
- definiert Zielvariable, Reward-Komponenten, No-Action-Baseline und Guardrails
- prueft, ob Policy Learning operational sicher und messbar ist
- blockiert Policy-Freigabe ohne Reward-Kalibrierung, Guardrails und Governance-Kontext
- trennt Action Ranking von belegter Wirkung

Expert Capabilities:
- ML Agent
- Policy Agent
- Reward Logic Review

Outputs:
- Reward Spec
- Policy Readiness
- Action Ranking Hypotheses
- Guardrail Check

## 5. Critic & Governance Agent

Verantwortung:
- prueft Widersprueche, fehlende Evidenz, Failure-Modes und Proxy-Risiken
- nimmt Devil's-Advocate-Perspektive ein
- prueft Manipulation, Fairness, Consent, Overnudging, vulnerable Gruppen und Dark-Pattern-Risiken
- gibt keine Freigabe, wenn zentrale Aussagen nicht durch Daten oder Governance-Regeln gedeckt sind

Expert Capabilities:
- Critic Agent
- Devil's Advocate Agent
- Governance Agent

Outputs:
- Failure-Mode Review
- Governance Decision
- Revision Requests
- Blocker und Dokumentationsauflagen

## Evidence Gate pro Agent

Jeder Kern-Agent muss zentrale Aussagen klassifizieren:

- `observed`: direkt aus Daten, Schema, Dokument oder Test belegbar
- `inferred`: plausibel abgeleitet, aber nicht bewiesen
- `hypothesis`: pruefbare Annahme
- `unknown`: Datenlage reicht nicht
- `blocked`: Aussage darf nicht gemacht werden

Wirkung, Signifikanz und Kausalitaet duerfen nur als `observed` oder freigaberelevantes `inferred` erscheinen, wenn Daten, Design und Unsicherheit dies tragen.

## MECE-Hypothesengruppen

- Datenqualitaet
- Zielverhalten
- Behavioral Mechanism
- Wirkung / Effekt
- Segment / Heterogenitaet
- Reward / Policy
- Governance / Risiko

Der Orchestrator darf erst weitergeben, wenn die Hypothesenstruktur vollstaendig ist und nicht testbare Hypothesen sichtbar blockiert oder zurueckgestellt wurden.
