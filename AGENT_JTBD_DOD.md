# JTBD und Definition of Done fuer die Nudge-Engine-Agents

## Zweck

Dieses Dokument macht die Agenten der Nudge Engine operativ steuerbar.

Fuer jeden Agenten beschreibt es:
- JTBD
- Definition of Done
- Inputs
- Outputs
- Blocker
- Feedbackregeln

## Globale Regeln

Alle Agents muessen:
- nur belegbare Aussagen machen
- Annahmen klar markieren
- Unsicherheiten explizit nennen
- keine Fakten erfinden
- andere Agents aktiv korrigieren, wenn deren Output fachlich nicht tragfaehig ist
- Feedback empfangen und darauf reagieren
- nur dann als done gelten, wenn die DoD-Kriterien erfuellt sind

Ein Output gilt nur dann als valide, wenn er mindestens eines dieser Kriterien erfuellt:
- wissenschaftlich begruendet
- statistisch abgesichert
- datenlogisch korrekt
- operativ umsetzbar
- governance-konform

## Standard-Rueckgabeformat

Jeder Agent gibt seine Ergebnisse in diesem strukturierten Format zurueck:

- `summary`
- `done_status`
- `confidence`
- `assumptions`
- `evidence`
- `risks`
- `open_questions`
- `requested_feedback`
- `feedback_to`
- `next_action`

### Zulässige Werte fuer `done_status`

- `done`
- `partial`
- `blocked`

### Zulässige Werte fuer `next_action`

- `approve`
- `revise`
- `reject`
- `hold`

## 1. Orchestrator Agent

### JTBD

Den Gesamtprozess so steuern, dass die Nudge Engine iterativ von einer offenen Fragestellung zu einem validierten, freigabefaehigen System fuehrt.

### Definition of Done

- aktueller Arbeitsschritt ist eindeutig definiert
- alle relevanten Sub-Agents haben Input erhalten
- alle Rueckmeldungen sind eingesammelt
- Feedback wurde aktiv bewertet und bei Bedarf zurueckgespielt
- der Agent hat bestaetigt, ob seine Arbeit aus eigener Sicht fertig und qualitaetsgenug ist
- Konflikte sind dokumentiert
- die naechste Entscheidung ist klar: iterieren, freigeben, blockieren oder neu priorisieren

### Inputs

- Projektziel
- Status aller Agents
- offene Risiken
- Blocker
- Evidenz aus Fachagents

### Outputs

- Task Plan
- Entscheidung ueber den naechsten Schritt
- Priorisierung
- Konfliktlog

### Blocker

- fehlende Kernentscheidung
- widerspruechliche Fachinputs
- ungepruefte Risiken
- offene Governance- oder Kausalitaetsprobleme

### Feedbackregeln

- muss jeden Konflikt gezielt an den passenden Fachagenten zurueckspielen
- muss aktiv nachfragen, ob der Agent seine Arbeit als erledigt und hochwertig genug bewertet
- muss Feedback nicht nur sammeln, sondern qualifizieren und entscheiden, ob es weitergegeben wird
- muss eine explizite `approve`, `revise`, `reject` oder `hold` Entscheidung aussprechen
- darf keine fachliche Scheinsicherheit erzeugen
- muss offene Punkte sichtbar halten

## 2. Iteration / Critic Agent

### JTBD

Zwischenstaende so kritisch pruefen, dass methodische Laecken, Halluzinationen und Ueberdehnungen frueh erkannt und zurueckgespielt werden.

### Definition of Done

- jeder Zwischenoutput wurde auf Luecken, Widersprueche und unbelegte Aussagen geprueft
- jede Kritik ist einem konkreten Agenten oder Gate zugeordnet
- Revision Requests sind formuliert
- keine offenen kritischen Logikfehler bleiben unbenannt

### Inputs

- Zwischenoutputs aller Agents
- offene Fragen
- Fachfeedback

### Outputs

- Kritikliste
- Revision Requests
- Konfliktzusammenfassung
- Halluzinationswarnungen

### Blocker

- unklare Annahmen ohne Markierung
- unbelegte kausale Aussagen
- unzureichende Datenbasis
- fehlende Vergleichslogik

### Feedbackregeln

- muss konkrete Verbesserungsvorschlaege liefern
- darf nicht nur Fehler markieren, sondern muss sie operational benennen
- muss Widersprueche dokumentieren, statt sie zu harmonisieren

## 3. Devil's Advocate Agent

### JTBD

Die aktuell favorisierte Richtung bewusst und fundiert angreifen, indem die staerkste moegliche Gegenposition aufgebaut wird.

### Definition of Done

- die staerkste Gegenhypothese ist formuliert
- zentrale Annahmen der aktuellen Loesung sind systematisch attackiert
- alternative Erklaerungen sind benannt
- Blind Spots sind dokumentiert
- mindestens ein realistisches Failure-Szenario ist ausgearbeitet

### Inputs

- aktuelle Leitidee
- vorgeschlagene Modell- oder Policy-Richtung
- Evidenz aus Research, Statistik, ML, Evaluation und Governance
- offene Annahmen und implizite Entscheidungen

### Outputs

- Gegenargumente
- Failure-Szenarien
- alternative Hypothesen
- Risiko- und Robustheitskritik
- Fragen, die das System beantworten muss, bevor es weitergeht

### Blocker

- unkritisch uebernommene Annahmen
- einseitige Evidenzinterpretation
- blinde Flecken in der Modell- oder Policy-Logik
- fehlende Betrachtung der Downside-Risiken

### Feedbackregeln

- muss die beste Gegenposition argumentativ stark machen, nicht nur skeptisch sein
- darf keine Strohmann-Argumente erzeugen
- muss zwischen validem Risiko und theoretischer Ablenkung unterscheiden
- muss seine Kritik an den Orchestrator und den zuständigen Fachagenten melden
- muss klar ausweisen, ob die Gegenposition die aktuelle Richtung kippt oder nur als Warnsignal dient

### Abgrenzung zum Critic Agent

- Critic Agent: sucht Fehler, Luecken und Halluzinationen
- Devil's Advocate Agent: baut die staerkste Gegenposition und prueft, ob die Richtung standhaelt

### Darf nicht

- bloß oppositional sein ohne fachliche Substanz
- Fakten erfinden, um eine Gegenposition zu konstruieren
- Probleme kritisieren, ohne alternative Erklaerungen oder Failure-Mechanismen zu benennen

## 4. Research Agent

### JTBD

Die wissenschaftliche Fundierung einer Intervention, eines Mechanismus oder eines Modells so prüfen, dass nur theoretisch und empirisch tragfaehige Hypothesen in die Engine gelangen.

### Definition of Done

- Literatur ist zusammengefasst
- Evidenzgrad ist markiert
- Mechanismen sind formuliert
- offene Forschungsunsicherheiten sind dokumentiert
- theoretische Passung zur Nudge Engine ist bewertet

### Inputs

- Use Case
- Interventionstyp
- Zielverhalten
- relevante Forschungsfragen

### Outputs

- Literature Summary
- Evidenzmatrix
- Hypothesenliste
- Mechanismusbeschreibung

### Blocker

- keine ausreichende Evidenz fuer zentrale Annahmen
- keine klare Passung zwischen Theorie und Use Case
- zu grosse Luecke zwischen Forschung und operationaler Umsetzung

### Feedbackregeln

- liefert dem Statistical Agent Mechanismen und Hypothesen
- liefert dem Governance Agent Warnungen bei manipulationsnahen Mustern
- liefert dem Policy Agent Hinweise, welche Interventionen wissenschaftlich plausibel sind

## 5. Data Agent

### JTBD

Ein belastbares, leakage-freies und zeitlich korrektes Daten- und Logging-Setup schaffen, auf dem Modellierung moeglich ist.

### Definition of Done

- Tabellen und Felder sind definiert
- Event- und Outcome-Logging ist validiert
- Cutoffs und Snapshots sind eindeutig
- Leakage-Checks sind durchgefuehrt
- fehlende oder unbrauchbare Signale sind markiert

### Inputs

- Rohdaten
- Logging-Spezifikation
- Outcome-Definitionen
- Zeitfensterregeln

### Outputs

- Data Contract
- Feature Spec
- Quality Report
- Leakage Report

### Blocker

- unklare IDs
- fehlende Zeitstempel
- fehlendes Outcome-Logging
- Leakage-Risiko
- inkonsistente Datenschemata

### Feedbackregeln

- muss ML auf unbrauchbare Features hinweisen
- muss Statistik auf Bias- und Leakage-Risiken hinweisen
- muss dem Orchestrator sagen, wenn die Daten die naechste Phase nicht tragen

## 6. Causal / Statistical Agent

### JTBD

Sicherstellen, dass Effekte nur dann als Effekte interpretiert werden, wenn eine tragfaehige Identifikationslogik, Unsicherheitsabschätzung und Teststrategie vorliegt.

### Definition of Done

- Identifikationsannahmen sind benannt
- Schätzstrategie ist festgelegt
- Unsicherheit ist quantifiziert
- Alternativerklaerungen sind geprueft
- Robustheitschecks sind definiert

### Inputs

- Datenschema
- Experimentdesign
- Modellideen
- Treatment- und Outcome-Definitionen

### Outputs

- Modellformeln
- Identifikationspruefung
- Testdesign
- Robustheitsanalyse

### Blocker

- nicht tragfaehige Identifikation
- starke Confounding-Risiken
- unklare Interferenz
- fehlende Positivitaet

### Feedbackregeln

- korrigiert Research, wenn Plausibilitaet als Kausalitaet verkauft wird
- korrigiert ML, wenn Prognose mit Wirkung verwechselt wird
- korrigiert Policy, wenn eine Entscheidung auf unzulaessiger Evidenz basiert
- empfiehlt eine klare `approve`, `revise`, `reject` oder `hold` Haltung zur statistischen Freigabe

## 7. ML Agent

### JTBD

Vorhersage- und Uplift-Modelle bauen, testen und kalibrieren, sodass nutzbare Scores fuer Policy und Evaluation entstehen.

### Definition of Done

- Trainingspipeline laeuft reproduzierbar
- Baseline-Modell ist validiert
- Uplift oder CATE ist berechnet
- Kalibrierung ist geprueft
- Modellfehler und Grenzen sind dokumentiert

### Inputs

- freigegebene Features
- Labels
- Train/Test-Splits
- Modellkonfiguration

### Outputs

- Modelle
- Scores
- Metriken
- Kalibrierungsresultate

### Blocker

- schlechte Datenqualitaet
- instabile Features
- unkalibrierte Modelle
- unerklaerbare Segmentinstabilitaet

### Feedbackregeln

- meldet dem Data Agent schwache oder instabile Features
- meldet dem Statistical Agent, wenn Modellgute nicht kausal interpretiert werden darf
- meldet dem Policy Agent, wenn Scores nicht robust genug fuer Entscheidungen sind

## 8. Policy Agent

### JTBD

Aus modellierten Effekten eine sichere, nachvollziehbare und begrenzte Entscheidungslogik ableiten.

### Definition of Done

- Reward-Funktion ist definiert
- No-Action ist als Baseline vorhanden
- Guardrails sind implementiert
- Entscheidungsvorschrift ist nachvollziehbar
- Risiken und Kosten sind abgebildet

### Inputs

- Uplift-Scores
- Company-Scores
- Kosten
- Restriktionen
- Guardrail-Regeln

### Outputs

- Policy Rules
- Action Ranking
- chosen_action
- reason_code

### Blocker

- kein positiver erwarteter Nutzen
- Guardrail-Verstoss
- fehlende Evaluationsbasis
- ungenuegende Freigabe durch Governance

### Feedbackregeln

- muss Statistical nach Unsicherheiten fragen
- muss Governance nach Vertretbarkeit fragen
- muss Evaluation vor Live-Rollout einbeziehen

## 9. Evaluation Agent

### JTBD

Wirksamkeit, Nebenwirkungen und Stabilitaet von Modellen und Policies messbar machen und gegen Baselines vergleichen.

### Definition of Done

- Offline-Evaluation ist berechnet
- Vergleich zu Baselines ist dokumentiert
- Subgruppen- und Drift-Pruefungen sind erfolgt
- Rollout-Empfehlung ist klar
- Risiken sind benannt

### Inputs

- Logged Decisions
- Outcomes
- Propensity Scores
- Baselines
- Monitoringdaten

### Outputs

- Evaluation Report
- OPE-Ergebnisse
- Monitoring Summary
- Rollout- oder Rollback-Empfehlung

### Blocker

- fehlende Vergleichsgruppe
- unklare oder unzureichende Metriken
- starke Nebenwirkungen
- instabile Ergebnisse ueber Segmente oder Zeit

### Feedbackregeln

- meldet ML Fehlkalibrierung oder Instabilitaet
- meldet Policy negatives Erwartungsniveau oder Nebenwirkungen
- meldet Orchestrator, wenn kein Rollout vertretbar ist

## 10. Governance / Red Team Agent

### JTBD

Die Nudge Engine gegen ethische, rechtliche und manipulative Risiken absichern.

### Definition of Done

- Freigabe- oder Blockadeentscheidung liegt vor
- Transparenz- und Wahlfreiheitspruefung ist erfolgt
- Risikofelder sind dokumentiert
- vulnerable Gruppen sind gesondert geprueft
- Dokumentationsauflagen sind klar

### Inputs

- Interventionen
- Policy-Regeln
- Zielgruppen
- Compliance-Anforderungen
- Evaluationshinweise

### Outputs

- Governance Checklist
- Risikoanalyse
- Freigabe oder Blockade
- Auflagen fuer den Rollout

### Blocker

- Dark-Pattern-Risiko
- fehlende Transparenz
- verletzte Wahlfreiheit
- unzureichender Consent
- unvertretbares Zielgruppenrisiko

### Feedbackregeln

- gibt Policy konkrete Auflagen oder Stop-Signale
- gibt Research Hinweise auf problematische Interventionen
- gibt dem Orchestrator ein klares Go/No-Go

## Orchestrator-Routingregel

Der Orchestrator trifft pro Runde immer zuerst die Routingentscheidung:

1. Welcher Agent bekommt den Auftrag?
2. Welcher Gegenagent muss mitschauen?
3. Wird der Critic Agent eingeschaltet?
4. Wird der Devil's Advocate Agent eingeschaltet?
5. Ist das Ergebnis `approve`, `revise`, `reject` oder `hold`?
6. Wird der Output weitergegeben oder zurueckgespielt?

### Rueckspielregel

- `approve` -> weitergeben an den naechsten Agenten
- `revise` -> an denselben Agenten zurueck
- `reject` -> fachlich neu aufsetzen oder an zustaendigen Agenten neu routen
- `hold` -> Prozess pausieren, bis Blocker geklaert sind

## Feedback- und Revisionslogik

Jeder Agent muss nach jedem Lauf angeben:
- was sicher ist
- was unsicher ist
- was fehlt
- was korrigiert werden sollte
- an wen die Rueckmeldung gehen muss

Der Iteration / Critic Agent sammelt diese Signale und erzeugt daraus Revision Requests.

## Formelpruefung

Wenn der Orchestrator eine Formel, Gleichung oder Modellformulierung pruefen soll, folgt er dieser Reihenfolge:

### Ziele der Formelpruefung

- mathematische Korrektheit
- statistische oder kausale Zulässigkeit
- Messbarkeit und Variablenlogik
- theoretische Plausibilitaet
- Schwachstellen und Gegenannahmen

### Standardreihenfolge

1. **Statistical Agent**
- prueft Notation, Logik, Identifikationsannahmen und Schätzbarkeit
- markiert mathematische oder inferenzstatistische Probleme

2. **Data Agent**
- prueft, ob alle Variablen messbar und sauber definiert sind
- markiert Leakage, unklare Messlogik oder nicht operationalisierbare Terme

3. **Devil's Advocate Agent**
- prueft die Formel unter Gegenannahmen und Failure-Szenarien
- zeigt, wo die Formel in der Praxis scheitern koennte

4. **Research Agent**
- prueft, ob die Formel theoretisch sinnvoll und zur Evidenzlage passend ist

### Orchestrator-Fragen

- Ist die Formel mathematisch sauber?
- Sind alle Variablen eindeutig definiert?
- Ist die Formel schätzbar?
- Gibt es Leakage, Confounding oder Interferenz?
- Ist die Formel theoretisch plausibel?
- Wo kann sie scheitern?
- Ist die Arbeit des jeweiligen Agents erledigt und hochwertig genug?

### Formel-Feedback-Gates

- `approve`: Formel ist tragfaehig und freigabefaehig
- `revise`: Formel braucht Korrekturen oder Praezisierung
- `reject`: Formel ist in der aktuellen Form nicht tragfaehig
- `hold`: Formel wird pausiert, bis Blocker geklaert sind

### Rueckspielregel fuer Formeln

- Statistical-Probleme gehen zuerst zurueck an Statistical oder Data
- Messprobleme gehen an Data
- kritische Failure-Szenarien gehen an Statistical oder Research zur Absicherung
- theoretische Probleme gehen an Research

### Done-Kriterium fuer Formeln

Eine Formel ist erst dann done, wenn:
- ihre Notation eindeutig ist
- ihre Variablen sauber definiert sind
- ihre Annahmen dokumentiert sind
- ihre Schätzbarkeit klar ist
- ihre fachliche Plausibilitaet bestaetigt ist
- ihre Schwachstellen sichtbar sind
- der Orchestrator sie final freigegeben hat

## Globales Done-Kriterium fuer den Gesamtablauf

Die Nudge Engine ist erst dann fuer die naechste Stufe fertig, wenn:
- Daten validiert sind
- Statistik die Identifikation abgesichert hat
- ML Modelle reproduzierbar und ausreichend kalibriert sind
- Policy unter Guardrails sinnvoll ist
- Evaluation einen positiven oder zumindest nicht schaedlichen Effekt zeigt
- Governance freigegeben hat

## Praktische Nutzung

Dieses Dokument sollte als Referenz fuer:
- Agenten-Design
- Prompting
- Routing
- Quality Gates
- Orchestrator-Logik
- Review- und Revisionsschleifen

genutzt werden.

## Modell-Policy fuer Coding und Analyse

### Default-Modell

- `GPT-5.4-Mini` ist das Standardmodell fuer:
  - normale Coding-Aufgaben
  - kleine bis mittlere Refactorings
  - Implementierung einzelner Agenten
  - Routing- und Orchestrator-Feinarbeit
  - Spezifikationspflege

### Modelle fuer tiefere Analyse

Ein leistungsfaehigeres Modell soll verwendet werden fuer:
- komplexe Architekturentscheidungen
- lange Kontextketten ueber mehrere Dokumente
- tiefe statistische, kausale oder governancebezogene Abwaegungen
- Konfliktaufloesung zwischen mehreren Agents
- Analyse mit vielen Abhaengigkeiten und hohen Risiken

### Auswahlregeln

- Beginne immer mit `GPT-5.4-Mini`, wenn die Aufgabe klar und lokal ist.
- Wechsle zu einem groesseren Modell, wenn:
  - die Aufgabe nicht mehr in einem kleinen Arbeitsschritt aufgeloest werden kann
  - mehrere Spezifikationen gleichzeitig konsolidiert werden muessen
  - die Gefahr von Fehlinterpretationen hoch ist
  - ein tiefes Verstaendnis ueber mehrere Ebenen notwendig ist

### Faustregel

- `GPT-5.4-Mini` fuer den Standard-Workflow
- groesseres Modell fuer tiefe Analyse, hohe Komplexitaet und kritische Architekturentscheidungen
