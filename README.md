# Nudge Engine

## Ziel

Ein wissenschaftlich fundiertes Modell fuer eine Nudge Engine, die Verhaltensdaten, psychologische Archetypen und Interventionen kombiniert.

## Kernannahme

- Daten validieren die Wirkung von Interventionen um Verhalten von Kunden zu steuern.
- Archetypen validieren die Passung von Interventionen zu Nutzerprofilen.
- Theorie validiert den Mechanismus hinter der Wirkung.

## Grundprinzip: Hypothesen zuerst, Evidenz vor Behauptung

- Jeder Analyseprozess beginnt mit einer MECE-Hypothesenstruktur.
- Kein Agent darf Wirkung, Kausalitaet, Signifikanz oder Empfehlung als Fakt behaupten, bevor die Datenlage analysiert wurde.
- Jede zentrale Aussage wird als `observed`, `inferred`, `hypothesis`, `unknown` oder `blocked` markiert.
- Wenn die Daten eine Aussage nicht tragen, muss der Agent dies explizit sagen und Rueckfragen oder Blocker formulieren.
- Nicht testbare Hypothesen bleiben sichtbar als `not_testable_yet`; sie duerfen nicht stillschweigend in Empfehlungen umgewandelt werden.
- Calculation startet erst nach Customer Data Intake, Zielklaerung, Hypothesenstruktur und Evidence Gate.

## Token-Budget-Regel

- Agents arbeiten standardmaessig mit einem Evidence Pack statt mit Full Context.
- Der Orchestrator waehlt nur Quellen, die direkt zur JTBD des Agents passen.
- Standardlimit: maximal 3 Dokumente und maximal 2 Sections pro Dokument.
- Run State ersetzt wiederholtes Lesen alter Outputs.
- Full Context ist nur erlaubt, wenn `full_context_required` und `full_context_reason` gesetzt sind.
- Formelpruefungen nutzen zuerst die Formula Registry, Hypothesen und Unsicherheitsfelder statt komplette Markdown-Dateien.
- Token-Effizienz darf Governance, Sicherheit, Unsicherheitslogik oder statistische Validitaet niemals ueberstimmen.

## Cognitive Governance v1

- Jede Quelle im Evidence Pack erhaelt Retrieval- und Evidence-Metadaten.
- Quellen mit `blocked` oder `deprecated` werden blockiert.
- Stale governance-kritische Quellen erzeugen `hold`.
- Unaufgeloeste Konflikte zwischen Quellen blockieren Freigabe und werden eskaliert.
- Externe Inhalte gelten als untrusted und werden auf Prompt-Injection-Muster geprueft.
- Security- und Integritaetschecks laufen ueber **Leonidas**, einen verpflichtenden Security-Check vor Agenten-Reasoning und Execution.
- Leonidas prueft Prompt Injection, Governance Bypass, Reward-/Policy-Override, unsichere Quellen und auffaellige Daten-Schema-Verletzungen.
- Leonidas ist kein zusaetzlicher Entscheidungs-Agent, sondern ein hartes Gate: `safe_to_reason=false` blockiert Agentenlauf, `safe_to_execute=false` blockiert Freigabe.
- Referenz: [Security & Integrity Layer](./SECURITY_INTEGRITY_LAYER.md)
- Es wird keine Chain-of-thought persistiert; gespeichert werden nur `decision_rationale`, `compressed_memory` und auditierbare Zusammenfassungen.

## PII Vault Boundary

- Direkte PII darf nicht in Evidence Packs, Agent Context, Run State oder Reports gelangen.
- Rohdaten werden zuerst in Vault Records und pseudonymisierte Analytics Rows getrennt.
- Agents sehen nur `subject_id` und verhaltensbezogene Felder, keine E-Mail, Telefonnummer, Namen oder Roh-IDs.
- Re-Identifikation darf nur ueber eine separate Vault-Schicht mit Audit, Zweckbindung und Berechtigung erfolgen.
- Referenz: [PII Vault Architecture](./PII_VAULT_ARCHITECTURE.md)

## Decision Reporting

- Ergebnisse werden als JSON-kompatibler Decision Report und als Markdown Report ausgegeben.
- Reports enthalten Executive Summary, Evidence & Confidence, Hypothesen, Nudge Recommendations, Segment View, Security & Governance und Next Actions.
- Reports duerfen keine direkte PII, Vault Payloads oder Roh-IDs enthalten.
- Signifikanz wird nur gezeigt, wenn CI-Felder vollstaendig sind, die Null ausgeschlossen ist und `confidence_level >= 0.95`.
- Referenz: [Report Output Specification](./REPORT_OUTPUT_SPEC.md)

## Analysis Service

- `src/analysis_service.py` ist der lokale Engine-Einstieg vor API/Dashboard-Anbindung.
- `run_analysis()` nimmt Frage, Kundendaten und optionale Konfiguration entgegen.
- Der Service verbindet Leonidas, PII-Pseudonymisierung, Customer Data Intake, MECE-Hypothesen, unterstuetzte Calculations, Policy/Reward und Reporting.
- Fehlende Zielvariable, fehlende Identity, fehlende Treatment/Control-Logik oder Security-Risiken erzeugen `hold`/`reject` statt ungesicherter Aussagen.
- Referenz: [Engine Functionality Check](./ENGINE_FUNCTIONALITY_CHECK.md)

## Dashboard UX

- Ein helles Dashboard unter `dashboard/index.html` ist als Einstieg fuer Frage/Daten -> Engine Run -> Ergebnis gedacht.
- Es zeigt Status, Evidence/CI, Hypothesen, Nudge Recommendations, Security/Governance und Next Actions.
- Security/Governance laeuft im Hintergrund und ist als Systemcheck einblendbar, aber nicht der Hauptfokus.
- Ein lokaler Report-Chat-Preview kann Fragen zum geladenen Ergebnis beantworten und ist fuer eine spaetere LLM-Anbindung vorbereitet.
- Referenz: [Dashboard UX Specification](./DASHBOARD_UX_SPEC.md)

## Runtime-Agenten

Die Engine nutzt operativ 5 Kern-Agents:

1. Orchestrator
2. Data & Measurement Agent
3. Behavioral Science Agent
4. Policy & Reward Agent
5. Critic & Governance Agent

Die urspruenglichen 10 Expertisen bleiben als interne Submodes, Checklisten und Review-Perspektiven erhalten.

## Modellbausteine

1. Verhaltensdiagnose
- Analyse von Zielverhalten, Barrieren und Kontext
- Orientierung an Modellen wie COM-B
- Identifikation von Capability, Opportunity und Motivation

2. Archetypenmodell
- Bildung empirischer Verhaltenstypen und Kundensegemente statt starrer Personas
- Nutzung von Clustering, Latent Class Analysis oder Bayes-Modellen
- Zuordnung von Reaktionsprofilen mit Wahrscheinlichkeiten
- Optionales OCEAN / Big-Five Signal ueber TIPI nur als hypothesenbildendes, consent-pflichtiges Low-Precision-Signal
- OCEAN darf keine Policy, keine Reward-Logik und keine Wirkungsaussage allein freigeben
- Referenz: [OCEAN Signal Model](./OCEAN_SIGNAL_MODEL.md)

3. Interventionslogik
- Mapping von Barriere plus Archetyp plus Kontext auf Nudges
- Beispiele: Default, Framing, Social Proof, Friction Reduction, Commitment
- Auswahl der Intervention nach erwarteter Wirkung und Nebenwirkungen

4. Lernsystem
- A/B/n-Tests fuer saubere kausale Validierung
- Contextual Bandits fuer Personalisierung
- Optional spaeter Reinforcement Learning fuer Sequenzen

5. Verhaltensmethoden
- Wissenschaftlich fundierte Interventionen wie Defaults, Friction Reduction, Social Proof, Commitment, Gain / Loss Framing, Reciprocity und Cognitive Ease
- Zuordnung der Methoden zu Formelebenen, Risiken und Review-Agents
- Runtime-Methoden werden in einer Behavioral Method Registry mit Pflichtsignalen, Mechanismus, Governance-Pflicht und Manipulationsrisiko gefuehrt
- `personalization` ist ein Meta-Mechanismus fuer Auswahl und Heterogenitaet, keine direkte Nudge-Action
- Referenz: [Behavioral Method Matrix](./BEHAVIORAL_METHOD_MATRIX.md)

8. Heuristik- und Bias-Layer
- Cognitive Biases werden als erklaerende Hypothesen modelliert, nicht als Kundendiagnosen
- Aktive Heuristiken wie Availability, Present Bias, WYSIATI, Choice Overload oder Decision Fatigue koennen Method-Fit leicht beeinflussen
- Reference-only Biases beeinflussen kein Ranking
- Excluded Biases duerfen nur Governance-Risiken markieren
- Korrelationen erzeugen maximal `moderate_support`, nie Kausalitaet
- Referenz: [Heuristic Layer Plan](./HEURISTIC_LAYER_PLAN.md)

6. Unsicherheitslogik
- Jede Effektschaetzung muss neben dem Punktwert ein Konfidenzintervall oder einen gleichwertigen Unsicherheitsbereich liefern
- `confidence` im Agentenoutput bedeutet subjektive Agenten-Sicherheit und ist nicht das statistische Konfidenzniveau
- `confidence_level` ist das statistische Niveau fuer Konfidenzintervalle
- Standard fuer belastbare Freigaben ist `0.95`
- `0.90` ist nur fuer explorative oder fruehe Iterationen vorgesehen
- Das Intervall zeigt, wie stabil der Effekt unter Stichprobenunsicherheit, Segmentierung und Datenrauschen ist
- Wenn das Intervall zu breit ist oder die Null enthalten kann, geht die Formel oder Policy in `revise` oder `hold`
- Signifikanz wird erst behauptet, wenn Daten oder Simulationsergebnisse vorliegen
- Fuer aggregierte oder gruppierte Daten werden robuste oder cluster-robuste Intervalle bevorzugt
- Bei schiefen Verteilungen oder kleinen Samples sind Bootstrap-Intervalle oft geeigneter als reine Normalapproximationen
- Der Statistical Agent ist fuer die Unsicherheitslogik federfuehrend, Evaluation und Orchestrator nutzen sie fuer Freigabeentscheidungen
- Referenz: [Validation Acceptance Criteria](./VALIDATION_ACCEPTANCE.md)

7. Governance
- Sicherung von Wahlfreiheit und Transparenz
- Schutz vulnerabler Gruppen
- Vermeidung von Dark Patterns und unerwuenschten Nebenwirkungen

## Naechste Arbeitsfragen

- Welcher konkrete Use Case soll zuerst modelliert werden?
- Welche Verhaltensdaten stehen zur Verfuegung?
- Wie sollen Archetypen operationalisiert werden?
- Welche Metrik zaehlt als Erfolg?
