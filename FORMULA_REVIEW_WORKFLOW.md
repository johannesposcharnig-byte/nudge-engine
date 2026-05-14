# Formula Review Workflow fuer die Nudge Engine

## Zweck

Dieses Dokument beschreibt, wie der Orchestrator mathematische, statistische und theoretische Formeln in der Nudge Engine pruft.

Ziel ist nicht nur formale Korrektheit, sondern auch:
- Schätzbarkeit
- Datenbezug
- theoretische Plausibilitaet
- operative Umsetzbarkeit
- Risikoklarheit

## Grundregel

Der Orchestrator entscheidet final.

Fachagents liefern Teilpruefungen, aber keine alleinige Freigabe.

## Prüfsequenz

### Phase 1: Statistische Vorpruefung

Der Statistical Agent prüft:
- Notation
- Identifikation
- Annahmen
- Schätzbarkeit
- Inferenzlogik

### Phase 2: Datenpruefung

Der Data Agent prüft:
- ob alle Terme messbar sind
- ob Variablen sauber operationalisiert sind
- ob Leakage oder Zeitfehler drohen
- ob die Formel realistisch auf die vorhandenen Daten passt

### Phase 3: Gegenpruefung

Der Devil's Advocate Agent prüft:
- wo die Formel scheitern kann
- welche Alternativerklaerungen es gibt
- welche Annahmen besonders fragil sind
- welche Downside-Risiken uebersehen werden

### Phase 4: Theoretische Pruefung

Der Research Agent prüft:
- ob die Formel zur Theorie passt
- ob die Konstrukte konsistent sind
- ob die Richtung mit der Evidenzlage vereinbar ist

### Phase 5: Orchestrator-Entscheidung

Der Orchestrator sammelt alle Rueckmeldungen und entscheidet:
- `approve`
- `revise`
- `reject`
- `hold`

## Standardfragen des Orchestrators

- Ist die Formel mathematisch sauber?
- Sind alle Variablen eindeutig definiert?
- Ist die Formel mit den Daten schätzbar?
- Sind die Annahmen dokumentiert?
- Ist die Formel theoretisch plausibel?
- Gibt es Interferenz-, Confounding- oder Leakage-Risiken?
- Wo kann die Formel in der Praxis scheitern?
- Ist das Feedback ausreichend, um weiterzugehen?

## Entscheidungslogik

### approve

Der Orchestrator setzt `approve`, wenn:
- alle Pflichtannahmen nachvollziehbar sind
- keine kritischen Defekte offen sind
- die Formel schätzbar ist
- die Theorie und Datenbasis zusammenpassen

### revise

Der Orchestrator setzt `revise`, wenn:
- die Formel brauchbar ist, aber praezisiert werden muss
- eine Variable unklar ist
- eine Annahme noch nicht sauber formuliert ist
- ein Teilfeedback Korrekturen verlangt

### reject

Der Orchestrator setzt `reject`, wenn:
- die Formel in der aktuellen Form methodisch nicht tragfaehig ist
- die Identifikation nicht funktioniert
- die Formel unvereinbar mit den Daten ist
- die theoretische Logik kollabiert

### hold

Der Orchestrator setzt `hold`, wenn:
- ein externer Blocker offen ist
- Daten oder Kontext fehlen
- eine vorgelagerte Entscheidung erst geklaert werden muss

## Formelklassen in der Nudge Engine

### Kausale Formel

Beispiel:
- `tau_a(x) = E[Y^u(a) - Y^u(0) | X = x]`

Prueffokus:
- Identifikation
- SUTVA
- Positivitaet
- Confounding
- Interferenz

### Aggregationsformel

Beispiel:
- `U_ct = (1 / N_c) * sum 1(active_it = 1)`

Prueffokus:
- Zeitbezug
- numerische Stabilitaet
- Leckagefreiheit
- Konsistenz der Indizes

### Outcome-Formel

Beispiel:
- `P(Renewal_ct = 1 | W_ct) = sigma(beta_0 + beta^T W_ct + u_c)`

Prueffokus:
- Linkfunktion
- Koeffizientenlogik
- Mixed-Effects-Annahme
- Kalibrierung

### Policy-Formel

Beispiel:
- `pi*(x) = argmax_a E[r_it(a) | X_it = x]`

Prueffokus:
- Reward-Definition
- Nebenbedingungen
- Fairness
- No-Action-Baseline

### Evaluation-Formel

Beispiel:
- `V_hat_DR(pi)`

Prueffokus:
- Propensity-Schätzung
- Outcome-Modell
- Doubly-Robust-Logik
- Stabilitaet

## Formel-Review-Output

Jeder Review muss dieses Format enthalten:

- `formula`
- `review_status`
- `summary`
- `assumptions`
- `evidence`
- `risks`
- `open_questions`
- `recommended_action`
- `reviewed_by`

## Review-Status

- `approve`
- `revise`
- `reject`
- `hold`

## Orchestrator-Endentscheidung

Der Orchestrator dokumentiert nach jedem Review:
- welches Feedback eingegangen ist
- welche Konflikte offen sind
- welche Rückspiele ausgelöst wurden
- warum die finalen Entscheidung getroffen wurde

Damit bleibt die Formelprüfung auditierbar und wiederholbar.

