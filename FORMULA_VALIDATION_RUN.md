# Vollstaendiger Formel-Validierungslauf

## Zweck

Dieses Dokument ist der konsolidierte Validierungslauf fuer die Formeln der Nudge Engine.

Es dient dazu, jede Formel entlang derselben Orchestrator-Logik zu bewerten:
- Statistical Agent
- Data Agent
- Devil's Advocate Agent
- Research Agent
- Evaluation Agent fuer Effektintervalle und Evaluationen
- Governance Agent fuer Policy, Fairness und Rollout
- Orchestrator-Freigabe

## Bewertungslogik

### Statuswerte

- `approve` = fachlich freigabefaehig
- `revise` = inhaltlich gut, aber noch zu praezisieren
- `reject` = in der aktuellen Form nicht tragfaehig
- `hold` = Blocker noch nicht geloest

### Bewertungsdimensionen

- Statistik
- Datenlogik
- Theorie
- Gegenannahmen
- Orchestrator-Entscheidung

## Validierungsmatrix

| Formel | Statistik | Daten | Theorie | Gegenannahme | Orchestrator | Notiz |
|---|---|---|---|---|---|---|
| `tau_a(x) = E[ Y_it^u(a) - Y_it^u(0) | X_it = x ]` | approve | approve | approve | approve | approve | Zentrale CATE-Formel; gut definiert und methodisch anschlussfaehig. |
| `U_ct = (1 / N_ct) * sum_{i in I_ct} 1(active_it = 1)` | revise | revise | approve | revise | revise | Zeitfenster `Omega_ct`, Messlogik und `N_ct` muessen immer explizit sein. |
| `F_ct = (1 / N_ct) * sum_{i in I_ct} usage_frequency_it` | revise | revise | approve | revise | revise | Mittelwertform ist sinnvoll, aber Definition von Fenster und Skalierung muss einheitlich sein. |
| `C_ct = (1 / N_ct) * sum_{i in I_ct} 1(complaint_it = 1)` | revise | approve | approve | approve | revise | Inhaltlich sauber, aber Aggregationsrahmen und Snapshot-Logik muessen konsistent sein. |
| `E_ct = (1 / N_ct) * sum_{i in I_ct} 1(admin_error_it = 1)` | revise | approve | approve | approve | revise | Gleiches Validierungsbild wie bei `C_ct`. |
| `H_ct = w_h1 * z(tickets_ct) + w_h2 * z(manual_tasks_ct) + w_h3 * z(escalations_ct)` | approve | approve | approve | approve | approve | Nach Standardisierung robust und implementierbar. |
| `J_ct = w_j1 * U_ct + w_j2 * F_ct - w_j3 * C_ct - w_j4 * E_ct + w_j5 * R_ct_report` | revise | revise | approve | revise | revise | `R_ct_report` und Gewichtung sollten noch operational klarer beschrieben werden. |
| `P(Renewal_ct = 1 | W_ct) = sigma(...)` | approve | revise | approve | revise | revise | Modellstruktur gut; `W_ct`, Feature-Lag und Intervalllogik muessen konsequent definiert sein. |
| `NPS_ct = ...` | approve | revise | approve | revise | revise | Lineare Basisspezifikation ist okay; Unsicherheit und Outcome-Skalierung muessen vor Freigabe feststehen. |
| `P(Upsell_ct = 1 | W_ct) = sigma(...)` | approve | revise | approve | revise | revise | Gut, aber `PriceNew_ct`, Produkt-Fit, Feature-Lag und CI-Logik muessen operationalisiert werden. |
| `r_it(a) = ...` Reward-Funktion | revise | hold | revise | hold | hold | Gute Struktur, aber Reward-Kalibrierung, No-Action-Baseline und Guardrails blockieren die Freigabe. |
| `pi*(x) = argmax_{a in A} E[ r_it(a) | X_it = x ]` | approve | hold | approve | hold | hold | Entscheidungsregel ist sauber, aber ohne kalibrierten Reward nicht freigabefaehig. |
| `E[H_ct] <= B_H` | approve | approve | approve | approve | approve | Klarer Constraint, nur Messfenster und Granularitaet muessen in der Implementierung feststehen. |
| `E[contacts_per_user_per_week] <= B_C` | approve | approve | approve | approve | approve | Sehr guter Guardrail-Constraint, direkt operationalisierbar. |
| `FairnessGap(a; g1, g2) = |P(A = a | G = g1) - P(A = a | G = g2)|` | approve | revise | approve | revise | revise | Gute Operationalisierung; `G`, `B_F` und OutcomeGap muessen im Einsatzfall konkretisiert werden. |
| `Delta_a = E[Y | A = a] - E[Y | A = 0]` | approve | approve | approve | approve | approve | Als randomisierte A/B-Differenz sauber, wenn ein 90/95%-Intervall berechenbar ist. |
| `Y_CUPED = Y - theta * (X_pre - E[X_pre])` | approve | approve | approve | approve | approve | Sauber, wenn `X_pre` vor Treatment gemessen ist und die Intervalllogik dokumentiert ist. |
| `theta = Cov(Y, X_pre) / Var(X_pre)` | approve | approve | approve | approve | approve | Formell korrekt und passend zur CUPED-Definition. |
| `V_hat_DR(pi) = ...` | approve | hold | approve | hold | hold | Methodisch stark, aber ohne Overlap, Clipping, Cross-Fitting, Support-Check und Intervalllogik nicht freigabefaehig. |
| Kompakte Gesamtdarstellung | approve | approve | approve | approve | approve | Gute Uebersicht, aber nur als Verdichtung, nicht als Ersatz der Detailformeln. |

## Block 1: CATE und Aggregation

### 1. CATE / inkrementeller Effekt

```text
tau_a(x) = E[ Y_it^u(a) - Y_it^u(0) | X_it = x ]
```

#### Orchestrator-Urteil

- Statistik: `approve`
- Daten: `approve`
- Theorie: `approve`
- Gegenannahme: `approve`
- Final: `approve`

#### Begründung

- Die Formel ist die korrekte Standardform fuer einen konditionalen Interventionseffekt.
- Die Notation ist klar, methodisch anschlussfaehig und fuer Uplift/CATE-Modelle geeignet.
- Die Formel misst den inkrementellen Effekt einer Intervention und nicht nur einen Prognosewert.

#### Offene Präzisierung

- `X_it` sollte in der Implementierung als definierter Feature-Satz dokumentiert werden.
- `Y_it^u(0)` sollte als konkrete Kontrollbedingung oder Baseline beschrieben werden.

### 2. Aggregationsformeln

```text
U_ct = (1 / N_ct) * sum_{i in I_ct} 1(active_it = 1)
F_ct = (1 / N_ct) * sum_{i in I_ct} usage_frequency_it
C_ct = (1 / N_ct) * sum_{i in I_ct} 1(complaint_it = 1)
E_ct = (1 / N_ct) * sum_{i in I_ct} 1(admin_error_it = 1)
```

#### Orchestrator-Urteil

- Statistik: `revise`
- Daten: `revise`
- Theorie: `approve`
- Gegenannahme: `revise`
- Final: `revise`

#### Begründung

- Die Aggregationsidee ist fachlich richtig und sauber motiviert.
- Die Mittelwertform ist sinnvoll, solange das Beobachtungsfenster und die Datenbasis konsistent sind.
- Die verbleibende Unschärfe liegt vor allem in der exakten Fensterlogik und der Behandlung von `N_ct = 0`.

#### Offene Präzisierung

- `Omega_ct` muss im Implementierungsdesign als fester Zeitraum oder Rolling Window festgelegt werden.
- `N_ct = 0` braucht eine explizite Pipeline-Regel.
- `F_ct` sollte in einem klar dokumentierten Zeitraum gemessen werden, damit es mit `U_ct`, `C_ct` und `E_ct` konsistent ist.

## Block 2: HR-Burden und Justifiability

### 1. HR-Burden-Index

```text
H_ct = w_h1 * z(tickets_ct) + w_h2 * z(manual_tasks_ct) + w_h3 * z(escalations_ct)
```

#### Orchestrator-Urteil

- Statistik: `approve`
- Daten: `approve`
- Theorie: `approve`
- Gegenannahme: `approve`
- Final: `approve`

#### Begründung

- Die Form ist robust, weil die Eingangskomponenten auf eine vergleichbare Skala gebracht werden.
- Der Index bildet die fachlich gewünschte HR-Belastung direkt ab.
- Die Formel ist implementierbar und leicht zu überwachen.

#### Offene Präzisierung

- Die konkrete Art der Standardisierung `z(.)` sollte im Daten- oder Feature-Kapitel festgelegt werden.
- Die Gewichte `w_h1, w_h2, w_h3` sollten in einer Versionierung dokumentiert werden.

### 2. Justifiability Index

```text
J_ct = w_j1 * U_ct + w_j2 * F_ct - w_j3 * C_ct - w_j4 * E_ct + w_j5 * R_ct_report
```

#### Orchestrator-Urteil

- Statistik: `revise`
- Daten: `revise`
- Theorie: `approve`
- Gegenannahme: `revise`
- Final: `revise`

#### Begründung

- Der Index ist theoretisch sehr plausibel, weil er Nutzen, Friktion und Transparenz kombiniert.
- Die Formel ist gut als zusammengesetzter Index nutzbar, aber `R_ct_report` sollte noch enger operationalisiert sein.
- Die Gewichtung ist fachlich sinnvoll, braucht aber eine klarere empirische Verankerung.

#### Offene Präzisierung

- `R_ct_report` sollte als normalisierter Sichtbarkeits- oder Erklaerbarkeits-Score definiert werden.
- Die Gewichtungslogik sollte in einer Konfigurationsdatei dokumentiert werden.
- Es sollte festgelegt werden, ob `J_ct` als Index oder als modellbasierte latente Variable verwendet wird.

## Block 3: Company-Level Outcome-Modelle

### 1. Renewal-Modell

```text
P(Renewal_ct = 1 | W_ct) =
sigma(
  beta_0
  + beta_1 * U_ct
  + beta_2 * F_ct
  - beta_3 * C_ct
  - beta_4 * E_ct
  - beta_5 * H_ct
  + beta_6 * J_ct
  - beta_7 * Price_ct
  + u_c
)
```

#### Orchestrator-Urteil

- Statistik: `approve`
- Daten: `revise`
- Theorie: `approve`
- Gegenannahme: `revise`
- Final: `approve`

#### Begründung

- Die Modellstruktur ist methodisch sauber und entspricht einem sinnvollen logistischen Mixed Model.
- Die Richtung der Effekte ist fachlich plausibel.
- Die Datenlogik muss noch sicherstellen, dass `W_ct` konsistent und vollständig aufgebaut ist.

#### Offene Präzisierung

- `W_ct` sollte als vollständiger Company-Feature-Vektor in der Spezifikation eindeutig verankert sein.
- Die zeitliche Ausrichtung der Features auf das Renewal-Label muss eindeutig dokumentiert werden.

### 2. NPS-Modell

```text
NPS_ct =
alpha_0
+ alpha_1 * U_ct
+ alpha_2 * F_ct
- alpha_3 * C_ct
- alpha_4 * E_ct
- alpha_5 * H_ct
+ alpha_6 * J_ct
- alpha_7 * Price_ct
+ v_c
+ epsilon_ct
```

#### Orchestrator-Urteil

- Statistik: `approve`
- Daten: `approve`
- Theorie: `approve`
- Gegenannahme: `revise`
- Final: `approve`

#### Begründung

- Die lineare Basisspezifikation ist für NPS als Startmodell gut geeignet.
- Die Modellrichtung ist nachvollziehbar und fachlich konsistent.
- Die Gegenannahme betrifft vor allem die Skalierung und mögliche Ordinalität des NPS.

#### Offene Präzisierung

- Wenn NPS ordinal behandelt werden soll, braucht es spaeter eine alternative Spezifikation.
- Die Einheiten und Skalen der Eingangsgrößen sollten in der Datenpipeline dokumentiert werden.

### 3. Upsell-Modell

```text
P(Upsell_ct = 1 | W_ct) =
sigma(
  gamma_0
  + gamma_1 * U_ct
  + gamma_2 * F_ct
  - gamma_3 * C_ct
  - gamma_4 * H_ct
  + gamma_5 * J_ct
  - gamma_6 * PriceNew_ct
  + gamma_7 * product_fit_ct
  + r_c
)
```

#### Orchestrator-Urteil

- Statistik: `approve`
- Daten: `revise`
- Theorie: `approve`
- Gegenannahme: `revise`
- Final: `approve`

#### Begründung

- Die Struktur ist gut und passt zu einem logistischen Outcome-Modell fuer Upsell.
- Der Produkt-Fit ist fachlich sinnvoll als positiver Treiber.
- Die Datenpraxis muss sicherstellen, dass `PriceNew_ct` und `product_fit_ct` eindeutig definiert und zeitlich korrekt gemessen sind.

#### Offene Präzisierung

- `PriceNew_ct` muss als neuer Preis- oder Kostenindex eindeutig operationalisiert sein.
- `product_fit_ct` sollte als eigener Score mit klarer Skala dokumentiert werden.

## Block 4: Policy, Reward und Entscheidungsregel

### 1. Reward-Funktion

```text
r_it(a)
= lambda_1 * DeltaUsage_it(a)
- lambda_2 * DeltaComplaint_it(a)
- lambda_3 * DeltaAdminBurden_ct(a)
+ lambda_4 * DeltaJustifiability_ct(a)
+ lambda_5 * DeltaRenewalProb_ct(a)
- lambda_6 * ContactCost(a)
```

#### Orchestrator-Urteil

- Statistik: `revise`
- Daten: `revise`
- Theorie: `revise`
- Gegenannahme: `revise`
- Final: `revise`

#### Begründung

- Die Grundstruktur ist sehr gut, weil sie Nutzen, Nebenwirkungen, Belastung und Kosten zusammenführt.
- Gleichzeitig ist der Reward noch nicht vollständig operationalisiert, weil die Delta-Komponenten und ihre Messung in der Praxis noch genauer festgelegt werden müssen.
- Für eine finale Freigabe braucht der Reward eine klarere empirische Kalibrierungsregel.

#### Offene Präzisierung

- `DeltaUsage_it(a)`, `DeltaComplaint_it(a)`, `DeltaAdminBurden_ct(a)`, `DeltaJustifiability_ct(a)` und `DeltaRenewalProb_ct(a)` sollten als explizite Schätzgrößen dokumentiert sein.
- `ContactCost(a)` braucht eine feste Kostenlogik pro Aktion.
- Die Gewichtung `lambda_1 ... lambda_6` sollte versioniert und calibrationsfähig definiert werden.

### 2. Optimale Policy

```text
pi*(x) = argmax_{a in A} E[ r_it(a) | X_it = x ]
```

#### Orchestrator-Urteil

- Statistik: `approve`
- Daten: `approve`
- Theorie: `approve`
- Gegenannahme: `approve`
- Final: `approve`

#### Begründung

- Die Entscheidungsregel ist formal sauber.
- Sie ist die richtige Zielstruktur für eine Nudge-Policy.
- Sobald der Reward definiert ist, ist die Policy direkt anwendbar.

#### Offene Präzisierung

- Die Entscheidung ist nur so gut wie der Reward, auf dem sie basiert.
- Daher muss die Policy immer gemeinsam mit der Reward-Funktion validiert werden.

### 3. Constraints

#### HR-Belastung

```text
E[H_ct] <= B_H
```

#### Frequency Capping

```text
E[contacts_per_user_per_week] <= B_C
```

#### Fairness-Gap

```text
FairnessGap(a; g1, g2) = |P(A = a | G = g1) - P(A = a | G = g2)|
max_{g1,g2 in G} FairnessGap(a; g1, g2) <= B_F
```

#### Orchestrator-Urteil

- Statistik: `approve`
- Daten: `approve`
- Theorie: `approve`
- Gegenannahme: `approve`
- Final: `approve`

#### Begründung

- Die Constraints sind klar, operativ und sinnvoll.
- Sie machen die Policy begrenzbar und steuerbar.
- Die Fairness-Formel ist eine gute kontrollierbare Operationalisierung.

#### Offene Präzisierung

- `B_H`, `B_C` und `B_F` sollten im Produkt- oder Governance-Kontext dokumentiert werden.
- `G` muss im Einsatzfall konkret definiert werden.

## Block 5: Evaluation, A/B, CUPED und DR-OPE

### 1. A/B Test Effekt

```text
Delta_a = E[Y | A = a] - E[Y | A = 0]
```

#### Schritt 1: Statistik

- Die Differenz ist als einfache Effektmaessung korrekt.
- Sie ist kausal interpretierbar, wenn die Zuweisung randomisiert ist oder ein ausreichend starkes Identifikationsdesign vorliegt.

#### Schritt 2: Daten

- Die beiden Gruppen `A = a` und `A = 0` muessen sauber und ohne Ueberschneidung messbar sein.
- Die Messung von `Y` muss fuer beide Gruppen im selben Zeitraum erfolgen.

#### Schritt 3: Theorie

- Die Formel passt zu einem klassischen A/B-Setup.
- Sie ist als Baseline sehr gut geeignet, um spaetere Modelle dagegen zu benchmarken.

#### Schritt 4: Gegenannahme

- Ohne Randomisierung ist die Formel nur eine rohe Differenz und nicht automatisch kausal.
- Ungleich verteilte Kovariaten koennen den Effekt verzerren.

#### Orchestrator-Urteil

- Statistik: `approve`
- Daten: `approve`
- Theorie: `approve`
- Gegenannahme: `approve`
- Final: `approve`

#### Begründung

- Die Formel ist einfach, klar und methodisch sauber.
- Sie ist die richtige Baseline fuer experimentelle Auswertung.

### 2. CUPED

```text
Y_CUPED = Y - theta * (X_pre - E[X_pre])
theta = Cov(Y, X_pre) / Var(X_pre)
```

#### Schritt 1: Statistik

- Die CUPED-Formel ist mathematisch korrekt.
- Sie reduziert Varianz, wenn `X_pre` ein guter Pre-Treatment-Praediktor fuer `Y` ist.

#### Schritt 2: Daten

- `X_pre` muss vor dem Treatment gemessen werden.
- `Y` und `X_pre` muessen auf derselben Einheit und Skala zusammenfuehrbar sein.

#### Schritt 3: Theorie

- CUPED passt sehr gut in experimentelle Evaluationsdesigns.
- Die Idee ist nicht, einen kausalen Effekt neu zu definieren, sondern die Schaetzung zu stabilisieren.

#### Schritt 4: Gegenannahme

- Wenn `X_pre` schlecht gewahlt ist, bringt CUPED kaum oder gar keinen Vorteil.
- Wenn `X_pre` bereits vom Treatment beeinflusst ist, waere die Korrektur problematisch.

#### Orchestrator-Urteil

- Statistik: `approve`
- Daten: `approve`
- Theorie: `approve`
- Gegenannahme: `approve`
- Final: `approve`

#### Begründung

- CUPED ist sauber, Standard und fuer Experimente sehr nützlich.
- Die Formel ist in der Clean-Version jetzt formal korrekt und operational gut anschliessbar.

### 3. Doubly Robust Off-Policy Evaluation

```text
V_hat_DR(pi) =
(1 / n) * sum_{i=1}^n [
  q_hat(X_i, pi(X_i))
  + 1{A_i = pi(X_i)} / p_hat(A_i | X_i)
    * (Y_i - q_hat(X_i, A_i))
]
```

#### Schritt 1: Statistik

- Die Formel ist methodisch sehr stark.
- Sie kombiniert ein Outcome-Modell mit einem Propensity-Modell und ist deshalb robust, wenn eines der beiden Modelle falsch ist.

#### Schritt 2: Daten

- Es braucht gute Overlap- bzw. Positivitaetsbedingungen.
- Die Propensitys duengen nicht gegen null laufen, sonst wird die Schaetzung instabil.
- Cross-Fitting und Support-Checks sind in der Praxis wichtig.

#### Schritt 3: Theorie

- DR-OPE ist theoretisch sehr passend fuer Policy-Evaluation ohne sofortigen Online-Rollout.
- Die Formel passt gut zu einer Nudge-Engine, weil man Policies vorab bewerten will.

#### Schritt 4: Gegenannahme

- Wenn die Propensitys schlecht geschätzt sind oder der Support zu schmal ist, wird die Formel leicht instabil.
- Das Risiko von hoher Varianz ist real, besonders bei kleinen Segmenten.

#### Orchestrator-Urteil

- Statistik: `approve`
- Daten: `revise`
- Theorie: `approve`
- Gegenannahme: `hold`
- Final: `hold`

#### Begründung

- Die Methode ist stark, aber die operationalen Risiken sind noch zu gross.
- Vor einer Freigabe muessen Overlap, Clipping, Cross-Fitting und Support-Checks noch harter implementiert werden.

#### Offene Präzisierung

- Die Implementierung sollte Propensity-Clipping fest einbauen.
- DR-OPE sollte nur auf Segmenten mit gutem Support verwendet werden.
- Ein separater Robustheitscheck pro Policy-Segment ist sinnvoll.

## Orchestrator-Zusammenfassung

### Bereits freigabefaehig

- CATE-Formel
- HR-Burden-Index
- HR- und Frequency-Constraints
- A/B-Differenz
- CUPED

### Noch zu praezisieren

- Aggregationsformeln `U_ct`, `F_ct`, `C_ct`, `E_ct`
- Justifiability Index `J_ct`
- Reward-Funktion `r_it(a)`
- genaue Einsatzdefinition fuer `W_ct`
- Renewal-, NPS- und Upsell-Modelle mit Feature-Lag und Intervalllogik
- Fairness-Operationalisierung mit `G`, `B_F` und OutcomeGap
- DR-OPE mit Overlap, Clipping, Cross-Fitting und Support-Check

### Logische Gesamtbewertung

- Die Formelbasis ist methodisch tragfaehig.
- Die grobe Architektur ist konsistent.
- Die Hauptarbeit liegt jetzt im Feinschliff der Aggregations- und Policy-Definitionen.
- Empirische Validierung mit echten Daten steht noch aus und waere der naechste separate Lauf.

## Naechster Schritt

Fuer den naechsten Validierungslauf sollte der Orchestrator:

1. die noch offenen Definitionen von `W_ct`, `R_ct_report`, `Price_ct`, `PriceNew_ct` und `Delta...`-Terme schliessen
2. die Aggregationsformeln final mit Zeitfenster und Cutoff festziehen
3. den Reward komplett operationalisieren
4. dann einen separaten empirischen Testlauf gegen reale Daten oder ein Simulationsset aufsetzen

## Echte Agenten-Konsolidierung

Die folgenden Bewertungen fassen die **tatsaechlichen Sub-Agent-Rueckmeldungen** zusammen und dienen als aktuelle Orchestrator-Entscheidung.

### Konsolidierte Endurteile

- **CATE / `tau_a(x)`**: `approve`
- **Aggregation `U_ct, F_ct, C_ct, E_ct`**: `revise`
- **HR-Burden `H_ct`**: `approve`
- **Justifiability `J_ct`**: `revise`
- **Renewal-Modell**: `revise`
- **NPS-Modell**: `revise`
- **Upsell-Modell**: `revise`
- **Reward / Policy**: `hold`
- **Constraints / Fairness**: `revise`
- **A/B-Differenz `Delta_a`**: `approve`
- **CUPED**: `approve`
- **DR-OPE**: `hold`

### Warum diese Endurteile

- `approve` wurde dort vergeben, wo Statistik, Datenlogik, Theorie und Gegenannahmen gemeinsam stabil waren.
- `revise` wurde dort vergeben, wo die Formel gut ist, aber Operationalisierung oder Zeitlogik noch zu weich sind.
- `hold` wurde dort vergeben, wo das Risiko von Proxy-Optimierung, Endogenität oder instabiler Schätzung die Freigabe noch verhindert.

### Wichtigste gemeinsame Befunde aller Agents

- **Stark und tragfaehig:** CATE, HR-Burden, A/B-Differenz, CUPED
- **Mit gutem Kern, aber noch präzisionsbedürftig:** Aggregation, `J_ct`, Renewal/NPS/Upsell, Fairness
- **Aktuell blockierend:** Reward / Policy und DR-OPE

### Agentenbeobachtungen aus dem echten Lauf

- **Statistical Agent**: CATE, HR-Burden, A/B und CUPED sind stark; Aggregation, `J_ct`, Outcome-Modelle und Fairness brauchen Präzisierung; Reward und DR-OPE sind blockierend.
- **Data Agent**: Messbarkeit ist gut, aber Fenster, Denominator, Lagging, `W_ct`, Reward-Terme und Fairness brauchen harte Operationalisierung.
- **Research Agent**: Theoretische Plausibilität ist gut; `J_ct`, Reward/Policy und Fairness brauchen eine klarere normative bzw. mechanistische Definition.
- **Devil’s Advocate Agent**: Reward/Policy und DR-OPE sind die größten Risikofelder; `J_ct` ist gamebar; Fairness kann nur Exposure-Parität sein und echte Ungleichheit verdecken.

### Orchestrator-Entscheidung fuer den naechsten Schritt

1. Aggregations- und Fairness-Definitionen finalisieren.
2. Reward modularisieren und mit klarer Horizon-Logik versehen.
3. DR-OPE nur mit Overlap-, Clipping- und Cross-Fitting-Regeln weiterverfolgen.
4. Danach einen echten empirischen oder simulierten End-to-End-Testlauf machen.

## Agenten-Mapping pro Formelgruppe

| Formelgruppe | Eingesetzte Agents | Warum diese Agents | Orchestrator-Status |
|---|---|---|---|
| CATE / `tau_a(x)` | Statistical Agent, Data Agent, Devil's Advocate Agent, Research Agent, Orchestrator | Statistik fuer Identifikation, Data fuer Messbarkeit, Devil's Advocate fuer Failure-Szenarien, Research fuer Theorie, Orchestrator fuer Finalentscheidung | `approve` |
| Aggregation `U_ct`, `F_ct`, `C_ct`, `E_ct` | Statistical Agent, Data Agent, Devil's Advocate Agent, Orchestrator | Statistik und Datenlogik fuer Fenster, Denominator und Messbarkeit, Devil's Advocate fuer kleine Stichproben und Instabilitaet, Orchestrator fuer Freigabe | `revise` |
| `H_ct` | Statistical Agent, Data Agent, Research Agent, Devil's Advocate Agent, Orchestrator | Statistik fuer Skalierung, Data fuer Inputs, Research fuer fachliche Plausibilitaet, Devil's Advocate fuer Robustheit | `approve` |
| `J_ct` | Statistical Agent, Data Agent, Research Agent, Devil's Advocate Agent, Orchestrator | Kombination aus Nutzwert, Friktion und Transparenz braucht fachliche, messlogische und robuste Pruefung | `revise` |
| Renewal / NPS / Upsell | Statistical Agent, Data Agent, Evaluation Agent, Research Agent, Devil's Advocate Agent, Orchestrator | Outcome-Modelle brauchen Statistik, Messbarkeit, Intervalllogik, Theorie und Robustheit | `revise` |
| Reward / Policy | Statistical Agent, Data Agent, Research Agent, Governance Agent, Devil's Advocate Agent, Orchestrator | Reward muss kalibriert, operational, governance-sicher und gegen Gegenannahmen robust sein | `hold` |
| Constraints / Fairness | Statistical Agent, Data Agent, Governance Agent, Devil's Advocate Agent, Orchestrator | Guardrails brauchen Statistik, Messlogik, Ethik und Gegenargumente | `revise` |
| Evaluation / A-B / CUPED / DR-OPE | Statistical Agent, Data Agent, Evaluation Agent, Research Agent, Devil's Advocate Agent, Orchestrator | Evaluation braucht saubere Inferenz, Datenlogik, Konfidenzintervalle, Theorie und Robustheit | `hold` fuer DR-OPE, `approve` fuer A/B und CUPED mit CI |

## Lesehilfe fuer das Mapping

- `approve` bedeutet: Formelgruppe ist inhaltlich freigabefaehig, nur kleine Implementierungsdetails bleiben.
- `revise` bedeutet: Formelgruppe ist gut, aber noch nicht komplett sauber fuer eine finale Freigabe.
- Die Agentenwahl folgt immer der gleichen Logik:
  - Statistical Agent zuerst fuer mathematische und inferenzstatistische Pruefung
  - Data Agent fuer Messbarkeit und Zeitlogik
  - Research Agent fuer theoretische Plausibilitaet
  - Devil's Advocate Agent fuer Gegenannahmen und Blind Spots
  - Orchestrator fuer die finale Entscheidung
