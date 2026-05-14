# Agentic Workflow fuer die Nudge Engine

## Ziel

Dieser Workflow beschreibt ein mehrstufiges, iteratives Agentensystem, mit dem die Nudge Engine wissenschaftlich entwickelt, berechnet, geprueft und validiert werden kann.

Der Fokus liegt auf:
- kausaler Effektschaetzung statt reiner Vorhersage
- wissenschaftlicher Validierung auf User-, Company- und Policy-Ebene
- klaren Rollen fuer mehrere spezialisierte Agents
- iterativen Review- und Korrekturschleifen
- reproduzierbarer Implementierung in Code, Statistik und Evaluation

## Leitprinzipien

- Kausalitaet vor Optimierung: Erst Effekte sauber schätzen, dann Policy lernen.
- Trennung von Ebenen: User-Level, Company-Aggregation, Company-Outcomes und Policy bleiben getrennt.
- Jede Annahme wird explizit dokumentiert: Identifikation, Positivitaet, SUTVA, Interferenz, Logging.
- Jeder Modellschritt bekommt mindestens einen Validierungs-Check.
- Kein Deployment ohne Offline- und Online-Evaluation.
- Jede Iteration produziert ein pruefbares Artefakt: Datensatz, Modell, Metrik, Plot, Decision-Rule oder Test.

## Agentenrolle

### 1. Orchestrator Agent

Aufgabe:
- plant den Gesamtprozess
- verteilt Aufgaben an Spezialagenten
- sammelt Ergebnisse
- erkennt Widersprueche und startet Korrekturschleifen
- entscheidet, wann ein Modell reif fuer naechste Stufe ist

Outputs:
- Task-Plan
- Status pro Layer
- offene Risiken
- Entscheidung, ob iteriert oder fortgefahren wird

### 2. Research Agent

Aufgabe:
- prueft wissenschaftliche Literatur zu Nudging, Verhaltensaenderung, Kausalmodellierung, Uplift, Bandits und Evaluation
- leitet methodische Hypothesen fuer die Nudge Engine ab
- sammelt theoretische Mechanismen fuer Interventionen und Archetypen

Outputs:
- Literature Summary
- Hypothesenliste
- Evidenzgrad je Intervention
- methodische Empfehlungen

### 3. Data Agent

Aufgabe:
- definiert Datenschema, Logging und Feature-Pipeline
- prueft Datenqualitaet, Leakage, Missingness und Zeitlogik
- validiert die Verfuegbarkeit von Inputs fuer User- und Company-Layer

Outputs:
- Tabellen- und Event-Schema
- Feature-Spezifikation
- Data-Quality-Report
- Leakage-Check

### 4. Statistical Agent

Aufgabe:
- spezifiziert Kausalmodelle und statistische Modelle
- prueft Identifikationsannahmen
- definiert A/B-Test-Design, CUPED, DR-OPE, Mixed Models und Unsicherheiten
- kontrolliert, ob die Ergebnisse statistisch haltbar sind

Outputs:
- Modellformeln
- Schätzstrategie
- Testdesign
- Unsicherheits- und Robustheitschecks

### 5. ML Agent

Aufgabe:
- implementiert User-Level Outcome-Modelle
- schätzt CATE/Uplift
- trainiert Company-Level Prognosemodelle
- kalibriert Scores und Wahrscheinlichkeiten

Outputs:
- trainierte Modelle
- Feature Importance oder Erklärungen
- Kalibrierungsplots
- Performance-Metriken

### 6. Policy Agent

Aufgabe:
- uebersetzt Modelloutputs in eine Entscheidungslogik
- optimiert Reward-Funktion und Guardrails
- prueft Kontaktbudget, Fairness, Frequency Capping und No-Action-Baseline

Outputs:
- Policy-Regeln
- Reward-Funktion
- Auswahllogik pro Aktion
- Guardrail-Validierung

### 7. Evaluation Agent

Aufgabe:
- bewertet Offline- und Online-Wirkung
- vergleicht Baselines, Modelle und Policies
- beobachtet Drift, Nebenwirkungen und Segmentunterschiede

Outputs:
- Evaluationsreport
- Experimentergebnisse
- Lift- und Calibration-Analysen
- OPE-Resultate

### 8. Governance Agent

Aufgabe:
- prueft Ethik, Transparenz, Wahlfreiheit und Risiko
- verhindert Dark Patterns
- kontrolliert vulnerable Gruppen, Einwilligung und Dokumentation

Outputs:
- Governance-Checklist
- Risiko-Register
- Freigabe oder Blocker

## Gesamtprozess in Phasen

### Phase 0: Problemdefinition

Ziel:
- einen konkreten Use Case festlegen
- Zielverhalten und Business-Ziel definieren
- Erfolgsmessung und Zeithorizont festlegen

Arbeitsschritte:
- Orchestrator sammelt Ziel, Zielgruppe und Kontext.
- Research Agent uebersetzt das Problem in wissenschaftlich pruefbare Hypothesen.
- Governance Agent prueft, ob der Use Case ethisch und rechtlich vertretbar ist.

Gate:
- Kein Start ohne klar definierte Outcome-Variable und Kontrollbedingung.

### Phase 1: Daten- und Messdesign

Ziel:
- ein belastbares Logging- und Datenschema aufbauen

Arbeitsschritte:
- Data Agent definiert `users`, `events`, `interventions`, `decisions` und `company_daily_features`.
- Data Agent definiert Zeitfenster, Cutoffs und Versionierung.
- Statistical Agent prüft Identifikationsrisiken und Messfehler.

Gate:
- Kein Training ohne sauberes Event-Logging, Treatment-Logging und Outcome-Logging.

### Phase 2: User-Level Modellierung

Ziel:
- den kausalen Effekt von Interventionen auf Nutzerverhalten schätzen

Arbeitsschritte:
- ML Agent trainiert Baseline-Outcome-Modelle.
- Statistical Agent validiert A/B-Test- oder Beobachtungsdesign.
- Evaluation Agent misst AUC, Log Loss, Calibration, Lift und Uplift.

Gate:
- Wenn Calibration oder Uplift instabil sind, geht der Prozess in eine neue Iteration zur Feature- oder Designkorrektur.

### Phase 3: Archetypen und Segmentlogik

Ziel:
- Verhaltenstypen empirisch ableiten und mit Interventionen verbinden

Arbeitsschritte:
- Research Agent definiert theoretische Archetypen.
- ML Agent prueft Clustering, Latent-Class-Modelle oder probabilistische Segmente.
- Statistical Agent validiert Segmentstabilitaet und Interpretierbarkeit.

Gate:
- Segmente muessen stabil, nachvollziehbar und operationalisierbar sein.

### Phase 4: Company-Aggregation

Ziel:
- User-Signale in Unternehmensmetriken uebersetzen

Arbeitsschritte:
- Data Agent berechnet `U_ct`, `F_ct`, `C_ct`, `E_ct`, `H_ct`, `J_ct`.
- Statistical Agent prueft Aggregationslogik und Kausalgrenzen.
- Evaluation Agent checkt, ob Aggregation die Zielmetriken sinnvoll vorhersagt.

Gate:
- Keine Company-Modelle ohne klar definierte Aggregationsformeln und Zeitfenster.

### Phase 5: Company-Level Outcome-Modelle

Ziel:
- Renewal, NPS und Upsell modellieren

Arbeitsschritte:
- ML Agent trainiert getrennte Modelle fuer Renewal, NPS und Upsell.
- Statistical Agent prueft mixed-effects, Kollinearitaet und Unsicherheit.
- Evaluation Agent misst Kalibrierung, RMSE, MAE, AUC und Robustheit.

Gate:
- Wenn Company-Level Modelle nur schwache oder instabile Effekte zeigen, muessen Features, Aggregation oder Hypothesen angepasst werden.

### Phase 6: Policy Layer

Ziel:
- aus Effektschaetzungen eine sichere Entscheidungslogik ableiten

Arbeitsschritte:
- Policy Agent definiert Reward-Funktion und No-Action-Baseline.
- Governance Agent prueft Fairness, Transparenz und Kontaktgrenzen.
- Statistical Agent prueft Off-Policy-Evaluation.

Gate:
- Nur Policies mit positiver erwarteter Wirkung und bestandenen Guardrails duerfen weitergehen.

### Phase 7: Offline Evaluation

Ziel:
- die Policy ohne Live-Risiko testen

Arbeitsschritte:
- Evaluation Agent berechnet DR-OPE, Lift, Segmentvergleiche und Sensitivitaeten.
- Statistical Agent prueft Signifikanz, Unsicherheiten und Robustheit.
- Orchestrator entscheidet, ob ein weiterer Iterationszyklus noetig ist.

Gate:
- Keine Live-Ausspielung ohne positiven Offline-Score und nachvollziehbaren Benchmark-Vergleich.

### Phase 8: Online Test und Lernschleife

Ziel:
- reale Wirkung testen und laufend verbessern

Arbeitsschritte:
- Policy wird als A/B/n-Test oder kontrollierter Rollout ausgesteuert.
- Evaluation Agent vergleicht Zielmetriken und Nebenwirkungen.
- ML Agent aktualisiert Modelle.
- Orchestrator startet naechste Iteration.

Gate:
- Bei negativen Nebenwirkungen sofort Rollback oder Policy-Sperre.

## Iterativer Agentenzyklus

Jede Runde laeuft in derselben Logik:

1. Orchestrator definiert das aktuelle Ziel.
2. Research Agent liefert wissenschaftliche Leitplanken.
3. Data Agent prueft Daten und Feature-Reife.
4. Statistical Agent spezifiziert Identifikation und Tests.
5. ML Agent trainiert oder aktualisiert Modelle.
6. Evaluation Agent misst Performance und Nebenwirkungen.
7. Policy Agent uebersetzt Scores in Handlungslogik.
8. Governance Agent gibt frei oder stoppt.
9. Orchestrator entscheidet: iterieren, skalieren oder abbrechen.

## Validierungslogik

### Wissenschaftliche Validierung

- Ist die Intervention theoretisch begruendbar?
- Ist die Identifikationsannahme plausibel?
- Gibt es Randomisierung oder eine belastbare Quasi-Experiment-Strategie?
- Sind die Ergebnisse mit vorhandener Forschung konsistent?

### Statistische Validierung

- Sind Effektgroessen stabil?
- Sind Konfidenzintervalle und Calibration akzeptabel?
- Bleiben die Resultate in Subgruppen robust?
- Sind Propensity Scores und Positivitaet ausreichend?

### Operative Validierung

- Sind Daten vollstaendig und zeitlich korrekt?
- Ist die Entscheidung reproduzierbar?
- Sind Kontaktbudget und Frequenzregeln eingehalten?
- Sind Monitoring und Rollback vorhanden?

### Ethik- und Governance-Validierung

- Gibt es Wahlfreiheit und Transparenz?
- Werden vulnerable Gruppen geschuetzt?
- Gibt es keine manipulativen Dark Patterns?
- Sind Zweck, Datenverwendung und Grenzen dokumentiert?

## Entscheidungsregeln fuer den Orchestrator

- Wenn Datenqualitaet schlecht ist, stoppe vor Modelltraining.
- Wenn das User-Level-Modell nicht kalibriert ist, verbessere Features oder Outcome-Definition.
- Wenn Aggregation unplausibel ist, korrigiere die Company-Logik.
- Wenn Company-Outcomes instabil sind, erweitere das Datenfenster oder die Modellklasse.
- Wenn die Policy gegen Guardrails verstoest, verlaengere die Iteration statt zu deployen.
- Wenn Offline-Evaluation negativ ist, keine Live-Ausspielung.

## Minimaler MVP-Stack

Fuer einen ersten wissenschaftlich vertretbaren MVP sollten folgende Bausteine reichen:

- sauberes Event-Logging
- User-Level Outcome-Modell
- einfache CATE- oder Uplift-Schaetzung
- Company-Aggregation
- Renewal- oder NPS-Modell
- regelbasierte Policy mit No-Action
- Offline-Evaluation mit DR-OPE oder A/B-Test
- Governance-Checks

## Praktische Arbeitsaufteilung fuer mehrere Agents

Empfohlene Parallelisierung:

- Research Agent arbeitet an Theorie und Evidenz.
- Data Agent arbeitet an Schema, Logging und Quality Checks.
- Statistical Agent arbeitet an Modellspezifikation und Testdesign.
- ML Agent arbeitet an Training und Scoring.
- Policy Agent arbeitet an Entscheidungslogik und Guardrails.
- Evaluation Agent arbeitet an Metriken und Backtesting.
- Governance Agent arbeitet an Risiko- und Ethikfreigabe.
- Orchestrator integriert alles und priorisiert die naechste Iteration.

## Empfohlene Artefakte pro Iteration

Jeder Iterationszyklus sollte mindestens diese Dateien oder Outputs erzeugen:

- `problem_definition.md`
- `data_contract.yaml`
- `feature_spec.md`
- `model_spec.md`
- `evaluation_report.md`
- `policy_rules.md`
- `governance_checklist.md`

## Ergebnis

Der Workflow macht aus der Nudge Engine kein monolithisches Modell, sondern ein kontrolliertes Lernsystem.

Das System wird erst dann erweitert, wenn jede Stufe einzeln pruefbar ist und die wissenschaftliche sowie operative Validierung bestanden hat.
