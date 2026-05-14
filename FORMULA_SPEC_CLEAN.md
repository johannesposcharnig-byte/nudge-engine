# Saubere Formel-Spezifikation fuer die Nudge Engine

## Zweck

Dieses Dokument fasst die zentralen Formeln der Nudge Engine in konsistenter, freigabefaehiger Notation zusammen.

Es dient als bereinigte Referenz fuer:
- Statistik
- Datenmodellierung
- ML-Implementierung
- Policy-Design
- Orchestrator-Review

## Notationsgrundsaetze

- Alle Indizes sind explizit definiert.
- Alle Variablen werden nur einmal und konsistent verwendet.
- Aggregationen sind als Mittelwerte oder Summen klar markiert.
- Kausale und statistische Aussagen werden getrennt von rein deskriptiven Kennzahlen behandelt.
- Policy- und Fairness-Regeln werden als Constraints oder Entscheidungslogik formuliert.

## 1. User-Level Effekt

### CATE / inkrementeller Effekt

```text
tau_a(x) = E[ Y_it^u(a) - Y_it^u(0) | X_it = x ]
```

### Bedeutung

- `tau_a(x)` ist der bedingte durchschnittliche Interventionseffekt fuer Intervention `a`.
- `Y_it^u(a)` ist das potenzielle Outcome fuer Nutzer `i` zum Zeitpunkt `t` unter Intervention `a`.
- `Y_it^u(0)` ist das potenzielle Outcome unter Kontrollbedingung.
- `X_it` ist der User-Kontext.

## 2. User-Level Aggregation auf Unternehmensebene

### Definitionen

```text
U_ct = (1 / N_ct) * sum_{i in I_ct} 1(active_it = 1)
F_ct = (1 / N_ct) * sum_{i in I_ct} usage_frequency_it
C_ct = (1 / N_ct) * sum_{i in I_ct} 1(complaint_it = 1)
E_ct = (1 / N_ct) * sum_{i in I_ct} 1(admin_error_it = 1)
```

### Begriffe

- `I_ct` ist die Menge der Nutzer:innen im Unternehmen `c` innerhalb des Beobachtungsfensters `Omega_ct`.
- `N_ct = |I_ct|` ist die Anzahl der Nutzer:innen in dieser Menge.
- `U_ct` ist die aktive Nutzerquote.
- `F_ct` ist die mittlere Nutzungsintensitaet.
- `C_ct` ist die Beschwerdequote.
- `E_ct` ist die Admin-Fehlerquote.

### Hinweis

- Alle vier Kennzahlen werden auf demselben Beobachtungsfenster `Omega_ct` berechnet.
- Wenn `N_ct = 0`, ist die Kennzahl nicht definiert und muss als Missing oder Null-Snapshot behandelt werden.

## 3. HR-Burden-Index

```text
H_ct = w_h1 * tickets_ct + w_h2 * manual_tasks_ct + w_h3 * escalations_ct
```

### Bedeutung

- `tickets_ct` = Anzahl der Support-Tickets
- `manual_tasks_ct` = Anzahl manueller Arbeitsschritte
- `escalations_ct` = Anzahl Eskalationen
- `w_h1, w_h2, w_h3` sind nichtnegative Gewichte

### Hinweis

- Eine robuste Spezifikation ist:

```text
H_ct = w_h1 * z(tickets_ct) + w_h2 * z(manual_tasks_ct) + w_h3 * z(escalations_ct)
```

- `z(.)` bezeichnet eine Standardisierung oder andere monotone Normalisierung.
- Alternativ koennen die Rohkomponenten vorher auf ein gemeinsames Intervall skaliert werden.

## 4. Justifiability Index

```text
J_ct = w_j1 * U_ct + w_j2 * F_ct - w_j3 * C_ct - w_j4 * E_ct + w_j5 * R_ct_report
```

### Bedeutung

- `R_ct_report` ist die Sichtbarkeit oder Nutzbarkeit der Reports auf Unternehmensebene.
- `w_j1 ... w_j5` sind Gewichtungsparameter.

### Hinweis

- Ein hohes `J_ct` bedeutet hohe Nutzbarkeit und geringe Friktion.
- Die Gewichte muessen empirisch oder fachlich begruendet werden.
- Eine explizite Spezifikation des Company-Feature-Vektors ist:

```text
W_ct = (U_ct, F_ct, C_ct, E_ct, H_ct, J_ct, R_ct_report, Price_ct)
```

- `W_ct` ist damit der vollständige Feature-Vektor fuer Company-Level-Modelle.
- `Price_ct` ist der Preis- oder Kostenindex fuer das bestehende Setup.
- `R_ct_report` ist ein normierter Index fuer Report-Sichtbarkeit, Report-Nutzung oder interne Erklaerbarkeit.
- `R_ct_report` sollte operational als auditierter, vor dem Outcome gemessener Composite-Score fuer Report-Sichtbarkeit, Report-Nutzung und Erklaerbarkeit definiert werden.
- `J_ct` ist als zusammengesetzter Nutzwert-/Transparenz-/Friktionsindex zu interpretieren, nicht als automatisch kausale latente Variable.

## 5. Company-Level Renewal Model

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

### Bedeutung

- `W_ct` ist der Company-Feature-Vektor.
- `Price_ct` ist ein Preis- oder Kostenindex.
- `u_c ~ N(0, sigma_u^2)` ist ein random intercept fuer Unternehmen `c`.
- `sigma(z) = 1 / (1 + exp(-z))`

## 6. Company-Level NPS Model

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

### Bedeutung

- `v_c ~ N(0, sigma_v^2)` ist ein random intercept fuer Unternehmen `c`.
- `epsilon_ct ~ N(0, sigma_eps^2)` ist der Fehlerterm.

### Hinweis

- Dieses Modell ist eine lineare Basisspezifikation.
- Bei ordinal skaliertem NPS kann spaeter ein ordinales Modell sinnvoll sein.

## 7. Company-Level Upsell Model

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

### Bedeutung

- `PriceNew_ct` ist der Preis- oder Kostenindex fuer das neue Produkt.
- `product_fit_ct` ist der Produkt-Fit fuer das Upsell-Target.
- `r_c ~ N(0, sigma_r^2)` ist ein random intercept fuer Unternehmen `c`.

## 8. Policy Reward und Entscheidungsregel

### Reward-Funktion

```text
r_it(a)
= lambda_1 * DeltaUsage_it(a)
- lambda_2 * DeltaComplaint_it(a)
- lambda_3 * DeltaAdminBurden_ct(a)
+ lambda_4 * DeltaJustifiability_ct(a)
+ lambda_5 * DeltaRenewalProb_ct(a)
- lambda_6 * ContactCost(a)
```

### Hilfsdefinitionen

```text
DeltaUsage_it(a; h) = E[Usage_{i,t+h}(a) - Usage_{i,t+h}(0) | X_it = x]
DeltaComplaint_it(a; h) = E[Complaint_{i,t+h}(a) - Complaint_{i,t+h}(0) | X_it = x]
DeltaAdminBurden_ct(a; h) = E[H_{c,t+h}(a) - H_{c,t+h}(0) | X_it = x]
DeltaJustifiability_ct(a; h) = E[J_{c,t+h}(a) - J_{c,t+h}(0) | X_it = x]
DeltaRenewalProb_ct(a; h) = P(Renewal_{c,t+h} = 1 | W_ct, A_it = a) - P(Renewal_{c,t+h} = 1 | W_ct, A_it = 0)
```

### Optimale Policy

```text
pi*(x) = argmax_{a in A} E[ r_it(a) | X_it = x ]
```

### Hinweis

- `lambda_1 ... lambda_6` sind Gewichtungsparameter.
- `ContactCost(a)` ist die Kostenfunktion fuer Aktion `a`.
- Die Reward-Funktion muss vor dem Rollout empirisch kalibriert werden.
- Alle Delta-Komponenten muessen denselben Horizon `h` verwenden.
- Der Reward ist eine skalierte Entscheidungsmetrik und kein direktes Outcome-Modell.

## 9. Constraints

### HR-Belastung

```text
E[H_ct] <= B_H
```

### Frequency Capping

```text
E[contacts_per_user_per_week] <= B_C
```

### Fairness / Kontrollregel

```text
FairnessGap(a; g1, g2) = |P(A = a | G = g1) - P(A = a | G = g2)|
```

Diese Verteilung soll fuer relevante Gruppen `g` innerhalb definierter Toleranzgrenzen kontrolliert werden.

### Hinweis

- Eine praktische Operationalisierung ist:

```text
max_{g1,g2 in G} FairnessGap(a; g1, g2) <= B_F
```

- `G` ist die Menge der relevanten Gruppen fuer Fairness-Pruefungen.
- `B_F` ist die maximal zulaessige Fairness-Abweichung.
- Fairness kann alternativ ueber disparate exposure, disparate impact oder gruppenspezifische Kontaktquoten operationalisiert werden.
- Optional sollte eine outcome-basierte Zusatzpruefung ergaenzt werden, zum Beispiel:

```text
OutcomeGap(a; g1, g2) = |E[Y | A = a, G = g1] - E[Y | A = a, G = g2]|
```

- `OutcomeGap` dient als Ergänzung zu Exposure-Fairness, nicht als Ersatz.

## 10. A/B Test Effekt

```text
Delta_a = E[Y | A = a] - E[Y | A = 0]
```

### Hinweis

- Diese Differenz ist kausal interpretierbar, wenn die Zuweisung randomisiert oder ausreichend gut identifiziert ist.
- Bei Beobachtungsdaten ist sie als naive Differenz oder als geschuetzte Schätzung zu kennzeichnen.

## 11. CUPED

```text
Y_CUPED = Y - theta * (X_pre - E[X_pre])
theta = Cov(Y, X_pre) / Var(X_pre)
```

### Bedeutung

- `X_pre` ist ein Pre-Period-Feature oder Pre-Outcome.
- `theta` ist der CUPED-Koeffizient.

### Hinweis

- `X_pre` muss vor dem Treatment gemessen sein.
- `Y_CUPED` ist eine Varianz-reduzierte Zielgroesse fuer Experimente.

## 12. Doubly Robust Off-Policy Evaluation

```text
V_hat_DR(pi) =
(1 / n) * sum_{i=1}^n [
  q_hat(X_i, pi(X_i))
  + 1{A_i = pi(X_i)} / p_hat(A_i | X_i)
    * (Y_i - q_hat(X_i, A_i))
]
```

### Bedeutung

- `q_hat(X_i, a)` ist das geschätzte Outcome unter Aktion `a`.
- `p_hat(A_i | X_i)` ist die Propensity oder das Verhaltenstherapiemodell.

### Hinweis

- DR-OPE setzt Overlap / Positivität voraus.
- In der Implementierung sollten Propensity-Clipping, Cross-Fitting und Support-Checks vorgesehen werden.

## 13. Kompakte Gesamtdarstellung

```text
Ebene A:
tau_a(x) = E[ Y_it^u(a) - Y_it^u(0) | X_it = x ]

Ebene B:
(U_ct, F_ct, C_ct, E_ct, H_ct, J_ct)

Ebene C:
P(Renewal_ct = 1 | W_ct)
NPS_ct
P(Upsell_ct = 1 | W_ct)

Ebene D:
pi*(x) = argmax_{a in A} E[ r_it(a) | X_it = x ]
```

## 14. Orchestrator-Freigabecheck

Eine Formel ist erst dann freigabefaehig, wenn:
- alle Variablen eindeutig definiert sind
- alle Notationen konsistent sind
- die Schätzbarkeit klar ist
- die Datenmessung moeglich ist
- Wirkungsschaetzungen ein Konfidenzintervall oder einen dokumentierten `hold`-Grund haben
- die theoretische Plausibilitaet gegeben ist
- die Gegenargumente geprueft sind
- der Orchestrator final `approve` erteilt

## 15. Konfidenzintervalle und Unsicherheit

- `confidence` im Agentenoutput ist eine subjektive Agenten-Sicherheit.
- `confidence_level` ist das statistische Konfidenzniveau fuer Intervallschaetzungen.
- Standard fuer belastbare Freigaben ist `0.95`.
- `0.90` ist nur fuer explorative oder fruehe Iterationen vorgesehen.
- Signifikanz darf erst behauptet werden, wenn ein Effekt mit `effect_estimate`, `ci_lower`, `ci_upper`, `ci_method`, `sample_size` und `confidence_level` vorliegt.
- Wenn ein Effekt keine berechenbare Unsicherheit hat, muss der Orchestrator `hold` oder `revise` setzen.

## 16. Offene Begriffe und letzte Klarstellungen

### Fenster und Aggregation

- `Omega_ct` = Beobachtungsfenster fuer Unternehmen `c` zum Zeitpunkt `t`
- Alle Aggregationen in Abschnitt 2 beziehen sich auf genau dieses Fenster

### Preisbegriffe

- `Price_ct` = Preis- oder Kostenindex fuer das aktuelle Setup
- `PriceNew_ct` = Preis- oder Kostenindex fuer das neue Produkt oder Upsell-Angebot

### Reward-Komponenten

- `Usage_it(a)` = Nutzungsniveau unter Aktion `a`
- `Complaint_it(a)` = Beschwerdelevel unter Aktion `a`
- `H_ct(a)` = HR-Belastung unter Aktion `a`
- `J_ct(a)` = Justifiability unter Aktion `a`
- `Renewal_ct(a)` = Verlängerungswahrscheinlichkeit unter Aktion `a`
- Alle Reward-Komponenten werden auf derselben Kontextinformation `X_it = x` bewertet
- Die Reward-Funktion ist eine skalierte Entscheidungsmetrik, kein direktes Outcome-Modell

### Feature-Vektor

- `W_ct = (U_ct, F_ct, C_ct, E_ct, H_ct, J_ct, R_ct_report, Price_ct)`

### Fairness

- `G` = Fairnessgruppen
- `B_F` = maximal zulaessige Fairness-Gap

## 17. Symbol-Glossar

- `i` = Nutzer- oder Mitarbeitendenindex
- `c` = Unternehmensindex
- `t` = Zeitindex
- `a` = Intervention oder Aktion
- `X_it` = User-Kontext
- `W_ct` = Company-Feature-Vektor
- `G` = Gruppenvariable fuer Fairness-Pruefungen
- `I_ct` = Menge der Nutzer:innen im Unternehmen `c` zum Zeitpunkt `t`
- `N_ct` = Anzahl der Nutzer:innen in `I_ct`
- `Y_it^u` = User-Level Outcome
- `Renewal_ct` = Verlängerungs- oder Retentionsoutcome
- `NPS_ct` = Net Promoter Score auf Unternehmensebene
- `Upsell_ct` = Upsell- oder Next-Best-Offer-Outcome
- `sigma(z)` = logistische Linkfunktion
- `u_c, v_c, r_c` = random intercepts auf Unternehmensebene
- `epsilon_ct` = Fehlerterm
- `theta` = CUPED-Koeffizient
- `q_hat` = Outcome-Modell fuer Off-Policy Evaluation
- `p_hat` = Propensity-Modell fuer Off-Policy Evaluation
- `confidence` = subjektive Sicherheit eines Agents
- `confidence_level` = statistisches Konfidenzniveau
- `ci_lower`, `ci_upper` = untere und obere Grenze eines Konfidenzintervalls

## 18. Orchestrator-Checkliste fuer Formelreview

### Struktur

- Ist die Formel eindeutig lesbar?
- Sind alle Indizes klar?
- Sind alle Variablen an anderer Stelle definiert?
- Ist die Gleichung in der Dokumentation konsistent benannt?

### Statistik

- Ist die Formel schätzbar?
- Sind Annahmen wie SUTVA, Positivitaet oder Randomisierung plausibel?
- Gibt es Confounding-, Interferenz- oder Leakage-Risiken?
- Ist die Modellklasse fuer das Ziel angemessen?
- Ist bei Wirkungsschaetzungen das Konfidenzniveau `0.95` oder explorativ `0.90` dokumentiert?

### Daten

- Lassen sich alle Terme messen?
- Gibt es fehlende Felder oder unklare Cutoffs?
- Ist die Aggregation zeitlich sauber?
- Sind die Inputs ohne Future Leakage verfügbar?

### Theorie

- Passt die Formel zur Verhaltenslogik der Nudge Engine?
- Ist der Mechanismus theoretisch nachvollziehbar?
- Ist die Richtung der Effekte plausibel?
- Gibt es bessere oder robustere Alternativformeln?

### Policy und Governance

- Kann die Formel direkt in eine sichere Policy uebersetzt werden?
- Verletzt sie Fairness- oder Kontaktregeln?
- Ist die Formel transparent und erklaerbar genug?
- Gibt es Risiken fuer Dark Patterns oder Missbrauch?

### Abschluss

- Sind die Gegenargumente geprueft?
- Ist die Rueckmeldung des zuständigen Agents eingearbeitet?
- Ist die Entscheidung des Orchestrators klar: `approve`, `revise`, `reject` oder `hold`?
