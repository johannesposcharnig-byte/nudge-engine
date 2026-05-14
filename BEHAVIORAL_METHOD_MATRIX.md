# Behavioral Method Matrix for the Nudge Engine

## Purpose

This document maps scientifically grounded behavioral design methods to the Nudge Engine.
Each method is treated as a concrete intervention candidate `a` in the action space.

## How to read the matrix

For each method we specify:
- scientific basis
- primary mechanism
- best-fit use cases
- main risks
- formula layers it should influence
- recommended agents for review

## Step 1: Strongly grounded methods

### 1. Defaults

- Scientific basis: choice architecture, status quo bias, bounded attention
- Mechanism: make the desired option the path of least resistance
- Best fit: activation, onboarding, completion, conversion
- Risks: opacity, manipulation concerns, weak fit if default is irrelevant
- Formula layers: `tau_a(x)`, `pi*(x)`, `Delta_a`
- Review agents: Statistical, Data, Research, Governance

### 2. Friction Reduction / Cognitive Ease

- Scientific basis: effort minimization, cognitive load reduction, processing fluency
- Mechanism: reduce steps, reduce complexity, simplify wording and flow
- Best fit: form completion, activation, task completion, feature adoption
- Risks: oversimplification, hidden tradeoffs, missing critical information
- Formula layers: `tau_a(x)`, `U_ct`, `F_ct`, `H_ct`, `pi*(x)`
- Review agents: Statistical, Data, Research, Devil's Advocate

### 3. Timely Reminders

- Scientific basis: prompt timing, cueing, present bias, memory support
- Mechanism: intervene at the right moment after a trigger or before a deadline
- Best fit: renewal, follow-up, inaction recovery, deadline-based behavior
- Risks: fatigue, annoyance, over-contact, poor trigger design
- Formula layers: `tau_a(x)`, `U_ct`, `C_ct`, `E_ct`, `pi*(x)`
- Review agents: Data, Statistical, Research, Governance

### 4. Social Proof / Social Norms

- Scientific basis: descriptive and injunctive norms, social comparison
- Mechanism: show what similar users or companies do
- Best fit: adoption, activation, renewal, upsell, compliance
- Risks: wrong comparison group, norm distortion, credibility loss
- Formula layers: `tau_a(x)`, `J_ct`, `Renewal_ct`, `Upsell_ct`, `pi*(x)`
- Review agents: Research, Statistical, Data, Devil's Advocate

### 5. Personalization

- Scientific basis: heterogeneity of treatment effects, contextual relevance
- Mechanism: tailor the intervention to the user or company context
- Best fit: almost all interventions when heterogeneity matters
- Risks: overfitting, cold-start problems, privacy concerns
- Formula layers: `tau_a(x)`, `pi*(x)`, `V_hat_DR(pi)`
- Review agents: Statistical, Data, Research, Governance

### 6. Commitment Devices

- Scientific basis: precommitment, consistency, self-signaling
- Mechanism: make the user commit to a future action or goal
- Best fit: follow-through, completion, habit building, retention
- Risks: coercive feel, abandonment, weak adherence if burden is too high
- Formula layers: `tau_a(x)`, `H_ct`, `J_ct`, `pi*(x)`
- Review agents: Research, Statistical, Governance, Devil's Advocate

## Step 2: Very useful contextual methods

### 7. Gain Framing

- Scientific basis: framing effects, prospect theory, message valence
- Mechanism: emphasize what the user gains by acting
- Best fit: low-friction adoption, positive reinforcement, feature uptake
- Risks: may be weaker than loss framing in some contexts, can feel generic
- Formula layers: `tau_a(x)`, `J_ct`, `pi*(x)`, `Delta_a`
- Review agents: Research, Statistical, Governance

### 8. Loss Framing

- Scientific basis: loss aversion, prospect theory
- Mechanism: emphasize what the user loses by not acting
- Best fit: urgency, renewal, deadline behaviors, risk-sensitive tasks
- Risks: anxiety, manipulation concerns, fatigue, ethical sensitivity
- Formula layers: `tau_a(x)`, `J_ct`, `pi*(x)`, `Delta_a`
- Review agents: Research, Governance, Statistical, Devil's Advocate

### 9. Reciprocity

- Scientific basis: reciprocity norm, exchange heuristics, social obligation
- Mechanism: provide a valuable first move before asking for action
- Best fit: engagement, trust building, response rates, relationship-based nudges
- Risks: can become manipulative if the "gift" is not genuine
- Formula layers: `tau_a(x)`, `J_ct`, `Renewal_ct`, `Upsell_ct`
- Review agents: Research, Governance, Devil's Advocate

### 10. Goal Setting

- Scientific basis: goal gradient, self-regulation, implementation intentions
- Mechanism: define a concrete target and progress toward it
- Best fit: activation, ongoing use, team performance, retention
- Risks: unrealistic goals, demotivation, metric gaming
- Formula layers: `tau_a(x)`, `H_ct`, `U_ct`, `pi*(x)`
- Review agents: Research, Statistical, Data

### 11. Progress Feedback

- Scientific basis: feedback loops, reinforcement, competence signals
- Mechanism: make progress visible and legible
- Best fit: habit building, completion, retention, engagement
- Risks: vanity metrics, false progress, miscalibrated feedback
- Formula layers: `U_ct`, `H_ct`, `J_ct`, `pi*(x)`
- Review agents: Data, Research, Statistical

### 12. Just-in-Time Interventions

- Scientific basis: event-triggered decision support, context dependence
- Mechanism: intervene exactly when the user is most receptive
- Best fit: inaction recovery, deadline support, momentary decision support
- Risks: trigger drift, timing errors, notification overload
- Formula layers: `tau_a(x)`, `U_ct`, `C_ct`, `pi*(x)`
- Review agents: Data, Statistical, Research, Governance

## Step 3: Methods that work as cross-cutting principles

### 13. Transparency / Explanation

- Scientific basis: trust calibration, informed choice, autonomy support
- Mechanism: explain why the intervention is shown
- Best fit: any intervention where legitimacy matters
- Risks: too much text, reduced conversion, revealing internal logic
- Formula layers: `J_ct`, `H_ct`, `pi*(x)`, Governance checks
- Review agents: Governance, Research, Devil's Advocate

### 14. Simplification

- Scientific basis: cognitive load reduction, processing fluency
- Mechanism: remove irrelevant options and structure the path
- Best fit: onboarding, form completion, task execution
- Risks: removing useful choice, hidden tradeoffs
- Formula layers: `U_ct`, `F_ct`, `H_ct`, `pi*(x)`
- Review agents: Statistical, Data, Research

### 15. Progress-Oriented Defaults

- Scientific basis: default effects plus progress signaling
- Mechanism: preselect a sensible next step and show the path forward
- Best fit: activation, next-best-action flows
- Risks: weak perceived agency if overused
- Formula layers: `tau_a(x)`, `U_ct`, `J_ct`, `pi*(x)`
- Review agents: Statistical, Research, Governance

## Recommended scientific starting set

For the first validated Nudge Engine release, the strongest and safest starting set is:

- Defaults
- Friction Reduction / Cognitive Ease
- Timely Reminders
- Social Proof / Social Norms
- Personalization
- Commitment Devices
- Gain Framing
- Loss Framing
- Reciprocity
- Goal Setting
- Progress Feedback
- Just-in-Time Interventions

## Recommended validation order

1. Define the intervention precisely as an action `a`
2. Assign the scientific mechanism
3. Define the target behavior and success metric
4. Check data availability and timing
5. Check statistical identifiability
6. Check theoretical fit
7. Run Devil's Advocate and Governance review
8. Map the intervention into `tau_a(x)`, `pi*(x)` and evaluation formulas

## Runtime Registry Status

The code-level Behavioral Method Registry lives in `src/behavioral_methods.py`.

Runtime action methods:

- `no_action`
- `default`
- `cognitive_ease`
- `simplification`
- `social_proof`
- `gain_frame`
- `loss_frame`
- `commitment`
- `reciprocity`
- `timely_reminder`
- `goal_setting`
- `progress_feedback`
- `just_in_time_intervention`
- `transparency_explanation`
- `progress_oriented_default`

Runtime meta methods:

- `personalization`

Rules:

- Every action method has required signals, mechanism, governance metadata and manipulation-risk metadata.
- `personalization` is not a direct nudge action; it is a selection-layer mechanism.
- Unknown methods are blocked.
- Blocked methods remain visible in the policy ranking with reason codes.
- Active methods remain `hypothesis` until validated with real outcome data.

## Notes

- Social Proof, Loss Frame, Gain Frame, Commitment, Reciprocity, and Cognitive Ease are all scientifically defensible when the use case fits.
- The Nudge Engine should prefer the least intrusive intervention that can still achieve the target behavior.
- Every method should be evaluated for efficacy, ethical risk, and maintenance burden.
