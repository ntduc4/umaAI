# umaAI

Golang skeleton for an Umamusume career AI.

Current scope:

- URA career engine with calendar, stats, energy, motivation, training, rest, races, support-card bond, and manual support-card stat tables.
- Deterministic tests for the parts implemented so far.
- Placeholder modules for future CV, UI detection, heuristic scoring, turn logging, plotting, and data ingestion.

Later expansion points:

- Add new scenarios by implementing `Scenario` beside `URAScenario`.
- Replace manual support-card definitions with a GameTora-backed card database.
- Replace approximate race probability with a real race simulator.
- Connect CV/UI detection to live game state and feed candidate actions into heuristic search.
