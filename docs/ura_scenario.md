# URA Scenario Implementation Notes

This document captures the gameplay rules and data needed to implement the URA Finals career scenario accurately. It intentionally includes both sourced mechanics and known gaps that need verification against game data.

## Sources

Use these as the current references for implemented mechanics:

| ID | Source |
| --- | --- |
| `GT-URA` | GameTora URA Finale Scenario: `https://gametora.com/umamusume/ura-finals` |
| `GT-BEGINNER` | GameTora Beginner Guide: `https://gametora.com/umamusume/beginners-guide` |
| `GT-SUPPORT` | GameTora Support Card pages, example Kitasan Black SSR: `https://gametora.com/umamusume/supports/30028-kitasan-black` |
| `GT-EVENTS` | GameTora Training Event Helper: `https://gametora.com/umamusume/training-event-helper` |
| `GLOBAL-REF` | Umamusume Global Reference Document by Erzzy/Kireina, supplied by user: `https://docs.google.com/document/d/11X2P7pLuh-k9E7PhRiD20nDX22rNWtCpC1S4IMx_8pQ/edit` |
| `UMA-GUIDE-SIM` | uma.guide Training Simulator: `https://uma.guide/support-cards/training-simulator` |
| `UMA-GUIDE-BUNDLE` | uma.guide Training Simulator client bundle inspected on 2026-06-14: `https://uma.guide/assets/app.CW9x6dYQ.js` |
| `UMAWIKI-URA` | Umamusume Wiki URA Finale page fetched on 2026-06-14: `https://umamusu.wiki/Game:URA_Finale` |

Source notes:

- GameTora explicitly documents URA base training values, facility level-up frequency, URA fixed training events, unique skill fan thresholds, Happy Meek duels, scenario spark, and stat caps.
- GameTora Beginner Guide documents rest recovery outcomes as `30`, `50`, or `70`, with `50` being the most common outcome.
- The Global Reference Document provides more specific rest probabilities, outing probabilities, racing energy choices, G1 race reward examples, and race-bonus examples.
- uma.guide exposes a training simulator and its client bundle includes the URA facility level table and training formula used by this implementation.
- GameTora support-card pages expose support effects such as friendship bonus, training effectiveness, race bonus, fan bonus, mood effect, hint levels, hint frequency, stat bonuses, initial friendship gauge, and specialty priority.
- GameTora states event-helper data is manually gathered and may contain errors, so event data should be treated as sourced but not infallible.
- Umamusume Wiki documents the URA Finale season structure as 6 extra turns, one training turn before each of three races, and the URA race win rewards currently implemented.

## Verification Status

This table is the source of truth for whether the current implementation is intended to match the game or is only a project-level approximation.

| Mechanic | Current Status | Source / Reason |
| --- | --- | --- |
| URA three-year career structure | Sourced for broad structure; turn labels are project data | `GT-URA` describes three-year Career and URA qualifiers/finals. `UMAWIKI-URA` states the Finale season adds 6 extra turns. Current labels are implementation names. |
| Half-month turns | Sourced concept | `GT-BEGINNER` says Career is turn-based and roughly 70 turns. Exact turn labels are project data. |
| URA Finals forced races | Sourced concept | `GT-URA` says clearing all objectives allows qualifiers, then semifinals, then finals. `UMAWIKI-URA` states each race must be won to advance. Current forced-action implementation is the engine interpretation. |
| Summer camp flag | Sourced | `GLOBAL-REF` says summer training camp starts in Early July in second and third year. Code flags Classic/Senior July-August as summer camp. No stat multiplier is applied. |
| URA facility level 1-5 table | Sourced | `UMA-GUIDE-BUNDLE` simulator table `Im.ura`; level-1 values cross-check with `GT-URA`. |
| Facility level-up every four trainings | Sourced | `GT-URA` Training Facility Levels section. |
| Training energy cost/recovery by facility level | Sourced | `UMA-GUIDE-BUNDLE` simulator table `Im.ura`; level-1 values cross-check with `GT-URA`. |
| Rest recovery outcomes | Sourced | `GT-BEGINNER`: rest recovers 30, 50, or 70, with 50 most common. |
| Rest recovery probabilities | Partially sourced | `GLOBAL-REF` gives `70=25%`, `50=62.5%`, `30=10%`, and `30 + Night Owl=2.5%`. Code collapses both 30 outcomes into `30=12.5%` until conditions are modeled. |
| Race energy cost | `PROJECT ASSUMPTION` for URA | Code uses fixed `-15` energy for URA races. The `-20` top option and `-10/-25` gamble choice from `GLOBAL-REF` are MANT/Twinkle Star behavior and are intentionally not applied to URA. |
| Recreation/outing outcomes | Sourced except crane/condition details | `GLOBAL-REF` gives Karaoke/Stroll/Shrine probabilities and energy/mood outcomes. Code implements those outcomes. Bonus crane game and shrine condition healing are not modeled. |
| Training failure rates | `PROJECT ASSUMPTION` for base curve, sourced modifiers | Current bucketed base fail-rate model is not sourced. Failure Protection, Practice Perfect, and Practice Poor modifiers are sourced; only Failure Protection is currently implemented. |
| Training failure penalties | Partially sourced, simplified | `GLOBAL-REF` gives failed-training aftermath tables. Code still uses simplified failure penalties and does not model Poor Practice conditions. |
| Motivation training values | Sourced for simulator formula | `UMA-GUIDE-BUNDLE` uses Great/Good/Normal/Bad/Terrible as `+0.2/+0.1/0/-0.1/-0.2`; name mapping to code is straightforward. |
| Support-card training formula | Sourced from simulator | `UMA-GUIDE-BUNDLE` function `nN`; implemented for manual cards. |
| Support-card effect fields | Sourced as data fields | `GT-SUPPORT` pages expose friendship, mood, training effectiveness, energy reduction, stat bonuses, etc. |
| Support-card placement | `PROJECT ASSUMPTION` | Not implemented; manual cards are treated as present on every training. |
| Support bond gain | `PROJECT ASSUMPTION` | Code uses +7 on matching training; needs source. |
| Friendship threshold numeric value | `PROJECT ASSUMPTION` | Code uses bond `>= 80`; source confirms orange/friendship gauge concept but not numeric threshold in fetched docs. |
| Race schedule entries | `PROJECT ASSUMPTION` | Current race list is a scaffold and not yet sourced from a complete race database. |
| Race fan requirements/rewards | `PROJECT ASSUMPTION` | Current fan requirements and gains are rough data and need a race database source. Fan bonus scaling is implemented as a support-card effect but race fan values still need sourced data. |
| Race rewards by grade | Partially sourced | `GLOBAL-REF` says G1 gives `+10 to a stat, +45 SP`; G2/G3 gives `+8 to a stat, +35 SP`; OP/Pre-OP gives `+5 to a stat, +35 SP`. Code implements amounts and randomly chooses the stat. Exact placement rewards below 1st remain unsourced. |
| Race bonus reward scaling | Sourced | `GLOBAL-REF` example: 35% race bonus turns G1 `10 stats + 45 SP` into about `13 stats + 60 SP`; code floors each multiplied stat/SP value. `GT-SUPPORT` defines Race Bonus as increasing stat gain from races. |
| URA Finals race rewards | Sourced for win rewards | `UMAWIKI-URA` lists Qualifier/Semifinal/Final win rewards as all stats +10 and `+40/+60/+80 SP`. Loss rewards remain a `PROJECT ASSUMPTION`. |
| Optional race fatigue penalties | Partially sourced | `GLOBAL-REF` gives mood/stat-loss/skin-outbreak probabilities for repeated optional races and zero-energy racing. Code implements mood/stat-loss probabilities and logs omitted condition effects. |
| Race win probability | `PROJECT ASSUMPTION` | Deliberate heuristic placeholder; not intended to match game racing. |
| Objective handling engine | Sourced concept, project implementation | `GT-URA` and `GT-BEGINNER` describe mandatory objectives; current objective data is still manual/scaffold. |
| Scenario events in code | Partially sourced | Code implements sourced fixed URA fan/mood events that fit current state. Skill hints, unique-skill level checks, and choice events are not modeled. Senior Early April Fan Meeting requires director/president bond 60 and fan threshold. |
| Stat cap 1200 | Sourced for Global/pre-rebalance | `GT-URA` Stat Caps section. JP cap 1400 is also documented but not current code target. |

## Scope

Current implementation target:

- Python career engine for the URA Finals scenario.
- Deterministic simulation state suitable for heuristic search.
- Manual support-card inputs for now.
- Approximate racing probability for now.

Out of scope for the first complete URA pass, but should be designed for:

- Other scenarios such as Aoharu, Grand Live, MANT/Make a New Track, L'Arc, UAF, etc.
- Live screenshot/CV state extraction.
- Exact race simulator.
- Automatic support-card data ingestion from GameTora or another source.

## URA Calendar

URA career uses half-month turns.

Implemented calendar:

The broad three-year career and URA finals structure is sourced from `GT-URA`. The extra URA Finale season structure is sourced from `UMAWIKI-URA`.

- Junior year starts at June early.
- Junior year runs June early through December late.
- Classic year runs January early through December late.
- Senior year runs January early through December late.
- URA Finals add 6 turns after Senior December late: one training turn before each of three forced races.

Turn counts:

- Junior: 7 months x 2 halves = 14 turns.
- Classic: 12 months x 2 halves = 24 turns.
- Senior: 12 months x 2 halves = 24 turns.
- Normal career turns before URA Finals: 62 turns.
- URA Finals: 6 turns.
- Total simulated turns: 68 turns.

URA Finals turns:

- URA Finals Preliminary Training.
- URA Finals Preliminary Race.
- URA Finals Semifinal Training.
- URA Finals Semifinal Race.
- URA Finals Final Training.
- URA Finals Final Race.

Implementation rule:

- On URA Finals race turns, the selected action should be forced to race, even if the planner proposes another action.
- On URA Finals training turns, normal training/rest/recreation/race action generation remains available until additional source-backed restrictions are implemented.

## Summer Camp

Summer camp occurs during:

- Classic July early.
- Classic July late.
- Classic August early.
- Classic August late.
- Senior July early.
- Senior July late.
- Senior August early.
- Senior August late.

Current engine behavior:

- Summer camp turns are flagged in the calendar only.
- No summer-camp stat multiplier is currently applied.
- Resting during summer camp raises mood by one stage.

Accuracy TODO:

- Verify exact URA summer camp training stat behavior before implementing any stat modifier.
- Determine whether summer camp overrides facility levels, changes support placement, or changes event rates.
- Determine if failures, energy costs, support hints, or event rates differ during camp.

## Core Career State

The engine should track at minimum:

- Current turn index.
- Year, month, and half-month.
- Five stats: speed, stamina, power, guts, wisdom.
- Skill points.
- Energy.
- Motivation.
- Support-card bond per card.
- Support-card placement per turn, once placement RNG is implemented.
- Scenario-specific flags and event history.
- Race result history.
- Objective progress.
- Turn log entries.

Current implementation tracks:

- Stats.
- Skill points.
- Energy.
- Motivation.
- Support-card bond.
- Director/president bond.
- Trainee ID for character-specific thresholds.
- Fan count.
- Training facility levels.
- Training counts per facility.
- Scenario event history.
- Objective completion/failure state.
- Race results.
- Turn logs.

Missing but needed:

- Full character-specific objective data.
- Skills and skill hints.
- Conditions/status effects.
- Support-card placement RNG.
- Random event queue/history.
- Uma-specific events.

## Energy

Current energy model:

- Maximum energy: `100`.
- Minimum energy: `0`.
- Training energy cost/recovery comes from the sourced URA facility-level table below.
- Rest recovers one of `30`, `50`, or `70` energy.
- Rest recovery probabilities come from the Global Reference Document: `70` energy `25%`, `50` energy `62.5%`, `30` energy `10%`, and `30` energy plus Night Owl `2.5%`.
- Current implementation does not model Night Owl yet, so the `30 + Night Owl` case is represented as a `30` energy rest. This condition effect is a known TODO.
- Recreation/outing uses the sourced Global Reference Document probability table for standard recreation outcomes.
- URA race energy cost is currently a fixed `-15` energy `PROJECT ASSUMPTION`.
- The `-20` top option and `-10/-25` gamble choice from `GLOBAL-REF` are MANT/Twinkle Star behavior and are intentionally not applied to URA.
- Recreation uses the Global Reference Document outcome table: Karaoke `35%` for +2 mood, Stroll `30%` for +1 mood and +10 energy, Shrine +10 energy `20%`, Shrine +20 energy `10%`, and Shrine +30 energy `5%`.
- Recreation bonus crane game is not modeled yet.
- Rest during summer camp raises mood by one stage, matching the Global Reference Document note that summer rests raise mood.

Current training failure model:

The base failure curve is a `PROJECT ASSUMPTION` until sourced. The supplied Global reference document gives failure consequences and modifiers, but not the base fail-rate-by-energy formula in the fetched text.

- Wisdom training failure rate: `0%`.
- Energy `>= 70`: `0%` failure.
- Energy `50-69`: `5%` failure.
- Energy `30-49`: `15%` failure.
- Energy `< 30`: `30%` failure.
- Failure Protection reduces the resulting fail rate multiplicatively. Source example: 35% Failure Protection turns 9% fail chance into 6%.
- Practice Perfect reduces fail chance by 2%, Practice Perfect double-circle reduces by 4%, and Poor Practice increases by 2%; these are sourced but not implemented yet because conditions are not modeled.

Accuracy TODO:

- Verify actual rest recovery probabilities.
- Add Night Owl and other condition effects to rest outcomes.
- Verify exact URA race energy behavior for wins, losses, mandatory races, and optional races.
 - Add recreation bonus crane game and shrine condition healing.
- Replace rough failure-rate buckets with exact in-game formula or lookup table.
- Model failure penalties accurately, including stats lost, motivation loss, bad conditions, and medical room effects.

## Motivation

Current motivation levels:

- Awful.
- Bad.
- Normal.
- Good.
- Great.

Current training multipliers:

- Awful: `0.8x`.
- Bad: `0.9x`.
- Normal: `1.0x`.
- Good: `1.1x`.
- Great: `1.2x`.

Training formula mood handling:

- The uma.guide simulator represents mood as `-0.2`, `-0.1`, `0`, `0.1`, `0.2`.
- If support cards on the training have mood effect, mood multiplier is `1 + mood_value * (1 + total_mood_effect_percent / 100)`.

Accuracy TODO:

- Implement motivation changes from random events, races, recreation, failures, and objectives.

## Training Types

Training types:

- Speed.
- Stamina.
- Power.
- Guts.
- Wisdom.

Current URA facility table:

- Source: uma.guide Training Simulator client bundle, `Im.ura` table in `https://uma.guide/assets/app.CW9x6dYQ.js`, inspected 2026-06-14.
- Source cross-check: GameTora URA page documents level-1 pre-rebalance/global values and facility level-up frequency.

Speed:

| Facility Level | Speed | Power | SP | Energy |
| --- | ---: | ---: | ---: | ---: |
| 1 | 10 | 5 | 2 | -21 |
| 2 | 11 | 5 | 2 | -22 |
| 3 | 12 | 5 | 2 | -23 |
| 4 | 13 | 6 | 2 | -25 |
| 5 | 14 | 7 | 2 | -27 |

Stamina:

| Facility Level | Stamina | Guts | SP | Energy |
| --- | ---: | ---: | ---: | ---: |
| 1 | 9 | 4 | 2 | -19 |
| 2 | 10 | 4 | 2 | -20 |
| 3 | 11 | 4 | 2 | -21 |
| 4 | 12 | 5 | 2 | -23 |
| 5 | 13 | 6 | 2 | -25 |

Power:

| Facility Level | Stamina | Power | SP | Energy |
| --- | ---: | ---: | ---: | ---: |
| 1 | 5 | 8 | 2 | -20 |
| 2 | 5 | 9 | 2 | -21 |
| 3 | 5 | 10 | 2 | -22 |
| 4 | 6 | 11 | 2 | -24 |
| 5 | 7 | 12 | 2 | -26 |

Guts:

| Facility Level | Speed | Power | Guts | SP | Energy |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 4 | 4 | 8 | 2 | -22 |
| 2 | 4 | 4 | 9 | 2 | -23 |
| 3 | 4 | 4 | 10 | 2 | -24 |
| 4 | 5 | 4 | 11 | 2 | -26 |
| 5 | 5 | 5 | 12 | 2 | -28 |

Wisdom/Wit:

| Facility Level | Speed | Wisdom | SP | Energy |
| --- | ---: | ---: | ---: | ---: |
| 1 | 2 | 9 | 4 | +5 |
| 2 | 2 | 10 | 4 | +5 |
| 3 | 2 | 11 | 4 | +5 |
| 4 | 3 | 12 | 4 | +5 |
| 5 | 4 | 13 | 4 | +5 |

Facility level rules:

- Source: GameTora URA Finale Scenario, Training Facility Levels section.
- All facilities start at level 1.
- A facility levels up every four trainings at that facility.
- Maximum facility level is 5.

Training calculation currently implemented:

- Source: uma.guide Training Simulator client bundle function `nN`, inspected 2026-06-14.
- For each stat, if the base stat for that training is zero, output remains zero even if a support has that stat bonus.
- `support_stat_bonus` is the sum of stat bonuses from support cards present on that training.
- `friendship_multiplier` is the product of `1 + friendship_bonus_percent / 100` for matching-type support cards at friendship bond threshold.
- `mood_multiplier = 1 + mood_value * (1 + total_mood_effect_percent / 100)`.
- `training_effectiveness_multiplier = 1 + total_training_effectiveness_percent / 100`.
- `character_count_multiplier = 1 + 0.05 * present_character_count`.
- `growth_multiplier` is not implemented yet because character growth is not modeled yet.
- Current stat result is `floor((base + support_stat_bonus) * friendship_multiplier * mood_multiplier * training_effectiveness_multiplier * character_count_multiplier)`.
- Energy starts from the facility table energy value.
- Wisdom friendship recovery is added when applicable.
- Energy cost reduction applies to negative energy costs.

Current implementation limitation:

- Support-card placement RNG is not implemented. Manual support cards are treated as present on every training.
- NPC counts are not implemented.
- Character growth rates are not implemented.
- Scenario-specific training bonuses beyond base URA are not implemented.
- JP post-rebalance URA training values are documented by GameTora for level 1, but level 2-5 post-rebalance values were not sourced here, so the implementation uses the uma.guide/global table.

Current stat cap:

- Each main stat caps at `1200`.
- Skill points do not cap.

Source note:

- GameTora documents URA stat caps as `1400` on JP and `1200` on Global before rebalance. The code currently uses `1200`.

Accuracy TODO:

- Add character growth rates to the training formula.
- Add support-card placement RNG and NPC counts.
- Add hints and skill hint acquisition.
- Add director/reporter NPC bond if needed for URA.
- Add training failure outcomes.
- Add condition modifiers such as practice perfect/poor practice, night owl, lazy habit, etc.

## Support Cards

Current support-card model:

- Manual card definition.
- Card has a type: speed, stamina, power, guts, or wisdom.
- Card has a level.
- Card has exact user-provided stat bonuses per training type.
- Card has initial bond.
- `PROJECT ASSUMPTION`: manual cards are treated as present on every training because placement RNG is not implemented yet.
- `PROJECT ASSUMPTION`: card gains bond when training matches its card type.
- `PROJECT ASSUMPTION`: friendship bonus applies at bond `>= 80` when training matches card type.
- Card can define friendship bonus percent.
- Card can define mood effect percent.
- Card can define training effectiveness percent.
- Card can define energy cost reduction percent.
- Card can define wisdom friendship recovery.
- Card can define race bonus percent.
- Card can define fan bonus percent.
- `PROJECT ASSUMPTION`: current default bond gain on matching training is `7`.

Support-card effect source:

- GameTora support-card pages expose card effects by level. Example: Kitasan Black SSR page shows friendship bonus, initial friendship gauge, training effectiveness, race bonus, fan bonus, mood effect, hint levels, hint frequency, power bonus, and specialty priority.
- uma.guide simulator formula shows how friendship bonus, mood effect, training effectiveness, stat bonuses, energy cost reduction, wisdom friendship recovery, and present character count are combined for training output.

Needed support-card mechanics:

- Support-card placement on each training each turn.
- Training effect up.
- Friendship bonus.
- Motivation bonus.
- Race bonus.
- Fan bonus.
- Specialty priority/rate.
- Hint rate.
- Hint level.
- Initial bond.
- Initial stats.
- Skill point bonus.
- Stat bonuses by type.
- Event stat gains.
- Event skill hints.
- Friend/group card special behavior.
- Outings for friend cards.

Manual card data should eventually be shaped so it can be replaced by GameTora ingestion:

- Card name.
- Rarity.
- Card type.
- Level.
- Limit break amount.
- Passive effects at level.
- Event chain.
- Skills and hint data.
- Unique bonus unlocks.

Accuracy TODO:

- Define a normalized support-card schema that matches GameTora data.
- Add support-card event trigger rules.
- Add exact bond gain values.
- Add support placement probabilities from specialty priority.
- Add friend-card outing action and event progression.

## Racing

Current race model:

The win probability model is a `PROJECT ASSUMPTION`. It is deliberately a long-lived placeholder for heuristic-search development until a race simulator is implemented.

- Race win probability is estimated from total stats and skill points.
- Probability is clamped between `5%` and `95%`.
- Race rewards are now separated from win probability.
- Race rewards support base stat rewards, skill point rewards, fan rewards, race bonus, fan bonus, and scenario-specific rewards.

Current formula:

- `score = speed + stamina + power + guts + wisdom + skill_points * 0.25`.
- `win_probability = clamp(score / 3000, 0.05, 0.95)`.

Current race rewards:

Reward calculation:

- Race Bonus is summed from support cards.
- Fan Bonus is summed from support cards.
- Race stat and skill-point rewards are multiplied by `1 + race_bonus_percent / 100` and floored.
- Fan gain is multiplied by `1 + fan_bonus_percent / 100` and floored.
- G1 win base reward is `+10 to a stat, +45 SP` based on `GLOBAL-REF`.
- G2/G3 win base reward is `+8 to a stat, +35 SP` based on `GLOBAL-REF`.
- OP/Pre-OP win base reward is `+5 to a stat, +35 SP` based on `GLOBAL-REF`.
- `GLOBAL-REF` describes the reward as “to a stat”; code randomly selects one main stat for the reward.
- Rewards for 2nd-5th and 6th-or-worse placements are still `PROJECT ASSUMPTION` values because the reference says they are lessened but does not give exact values in the fetched text.
- URA Finals win rewards use `UMAWIKI-URA` values and are affected by Race Bonus. Loss rewards remain a `PROJECT ASSUMPTION`.

| Race Type | Win Reward | Loss Reward |
| --- | --- | --- |
| G1 race | +10 random main stat, +45 SP, then Race Bonus | +25 SP assumption, then Race Bonus |
| G2/G3 race | +8 random main stat, +35 SP, then Race Bonus | +25 SP assumption, then Race Bonus |
| OP/Pre-OP race | +5 random main stat, +35 SP, then Race Bonus | +25 SP assumption, then Race Bonus |
| Other optional race | +45 SP assumption, then Race Bonus | +25 SP assumption, then Race Bonus |
| URA Finals Qualifier | All stats +10, +40 SP, then Race Bonus | All stats +10, +25 SP assumption, then Race Bonus |
| URA Finals Semifinal | All stats +10, +60 SP, then Race Bonus | All stats +10, +25 SP assumption, then Race Bonus |
| URA Finals Final | All stats +10, +80 SP, then Race Bonus | All stats +10, +25 SP assumption, then Race Bonus |

Current race energy:

- URA races cost fixed `15` energy in the current implementation. This is a `PROJECT ASSUMPTION` until a URA-specific source is added.
- `RaceEnergyChoice` exists for future scenario-specific behavior, but URA ignores it.
- The MANT/Twinkle Star `-20` top option and `-10/-25` gamble choice must not be used for URA.

Current optional race fatigue penalties:

- The code tracks consecutive optional races.
- Mandatory races do not apply repeated-race penalties.
- If racing with positive energy, mood-down chances are `0%`, `0%`, `60%`, `100%` for 1st/2nd/3rd/4th+ consecutive optional races.
- If racing from zero energy, mood-down chances are `20%`, `33%`, `95%`, `100%` for 1st/2nd/3rd/4th+ consecutive optional races.
- Random stat loss of 10 from three stats is applied with `40%` chance on the 4th+ consecutive optional race.
- Skin Outbreak and other condition effects are not modeled yet; the race log marks them as omitted.

Needed race state:

- Race name.
- Date.
- Grade.
- Surface: turf or dirt.
- Distance category: sprint, mile, medium, long.
- Distance in meters.
- Direction and track layout if available.
- Required fan count.
- Fan gain.
- Skill point gain.
- Stat gain.
- Objective requirement.

Needed character race aptitude:

- Surface aptitude.
- Distance aptitude.
- Style aptitude.
- Growth bonuses.
- Starting stats.
- Required career objectives.

Accuracy TODO:

- Add real race calendar.
- Add race entry restrictions.
- Add fan count and fan requirements.
- Add objective races per character.
- Add objective pass/fail career termination.
- Replace placeholder probability model with a better race simulator.
- Model skill activation and race strategy eventually.
- Model race fatigue/negative events from repeated racing.

## Race Schedule Data Needed

Race schedule is not URA-only, but URA careers depend heavily on it.

Current implementation status:

- `PROJECT ASSUMPTION`: the current race schedule entries, fan requirements, and fan rewards are scaffold data and are not yet verified against a complete race database.
- Do not treat current race schedule data as game-accurate until it is replaced by sourced data.

Minimum race schedule schema:

| Field | Description |
| --- | --- |
| name | Race name |
| year_scope | Junior, Classic, Senior, or multiple |
| month | Race month |
| half | Early or late |
| grade | G1, G2, G3, OP, Pre-OP, etc. |
| surface | Turf or dirt |
| distance_m | Distance in meters |
| distance_type | Sprint, mile, medium, long |
| direction | Clockwise, counter-clockwise, straight, etc. |
| fan_requirement | Required fans to enter |
| fan_gain | Fans gained by placement |
| stat_rewards | Stat rewards by placement if applicable |
| skill_point_rewards | Skill point rewards by placement |

Implementation recommendation:

- Store race schedule as data, not code.
- Prefer `data/races/*.json` or `data/races/*.yaml` later.
- Keep scenario-specific race modifications in scenario code.

## Character-Specific Data

URA is shared, but each trainee has character-specific constraints.

Needed character schema:

| Field | Description |
| --- | --- |
| name | Trainee name |
| base_stats | Starting speed/stamina/power/guts/wisdom |
| growth_rates | Growth percentage per stat |
| surface_aptitudes | Turf/dirt aptitudes |
| distance_aptitudes | Sprint/mile/medium/long aptitudes |
| style_aptitudes | Front/pace/late/end aptitudes |
| objectives | Career objective list |
| unique_events | Uma-specific event definitions |
| unique_skill | Unique skill data |

Objective schema:

| Field | Description |
| --- | --- |
| date | Target turn or deadline |
| type | Race, fan count, training, etc. |
| race_name | Race name if objective is a race |
| required_place | Required placement |
| required_fans | Required fans if fan objective |
| reward | Stats, skill points, motivation, skills, conditions |
| failure_behavior | Career fail, continue, alternate event, etc. |

Accuracy TODO:

- Add at least one character data file to test objective handling.
- Implement objective deadlines and mandatory race turns.
- Add event choice data for each character.

## Scenario Events

URA-specific event categories to implement:

- Opening/start event.
- Debut preparation and debut race objective.
- Training facility level-up events.
- Director/reporter events if applicable.
- Scenario progression events.
- URA Finals qualification event.
- URA Finals preliminary/semifinal/final events.
- Ending event and evaluation rewards.

Current implementation status:

- Implemented fixed events from the Global Reference Document/GameTora where current state can represent the reward.
- Classic Early November Aoi event: requires 50,000 fans, gives +20 wisdom and +20 SP.
- Classic end fan event: requires 100,000 fans, gives +30 SP.
- Senior Early April Fan Meeting: requires 70,000 fans and director/president bond 60, gives +1 mood. Haru Urara and Smart Falcon use the lower 60,000 fan threshold.
- Senior end fan event: requires 240,000 fans, gives +30 SP.
- Not yet implemented: skill hints from the Aoi event, unique-skill level checks themselves, Valentine's/Christmas unique skill events, New Year choice events, support/character events, and scenario ending rewards.

General career event categories to support:

- Random stat event.
- Random motivation event.
- Random condition event.
- Support-card event.
- Support-card chain event.
- Character-specific event.
- Date-specific seasonal event.
- Objective success event.
- Objective failure event.
- Race after-event.
- Skill hint event.
- Crane game, shrine, New Year, Valentine's, fan appreciation, Christmas, etc.

Event schema should include:

| Field | Description |
| --- | --- |
| id | Stable event ID |
| name | Display name |
| source | Scenario, character, support card, random, race |
| timing | Fixed turn, random eligible range, after race, after training, etc. |
| choices | Player choices if any |
| effects | Stat, energy, motivation, bond, skill hint, condition changes |
| requirements | Conditions for event to trigger |
| once_per_career | Whether event can only occur once |
| chain_next | Next event in a chain, if any |

Accuracy TODO:

- Build a generic event engine before hardcoding many events.
- Add deterministic RNG hooks for repeatable tests.
- Record event history so one-time and chained events work.

## Conditions And Status Effects

Needed positive/negative condition model:

- Good conditions such as practice perfect, charming, etc.
- Bad conditions such as lazy habit, night owl, overweight, headache, etc.
- Medical room action.
- Condition recovery from events, rest, outings, or infirmary.

Accuracy TODO:

- Define condition enum.
- Add condition effects on training, event availability, failure rates, and motivation.
- Add infirmary action.

## Actions

Current actions:

- Train.
- Rest.
- Race.
- Recreation.

Needed actions:

- Train speed.
- Train stamina.
- Train power.
- Train guts.
- Train wisdom.
- Rest.
- Recreation/outing.
- Race, with selected race ID.
- Infirmary.
- Learn skills.
- Friend-card outing where applicable.

Legal action generation should consider:

- Current turn.
- Available races.
- Mandatory objectives.
- Energy and conditions.
- Support-card events/outings.
- Skill availability and skill points.
- URA forced finals race turns.

## Logging

Every simulated or observed turn should log:

- Turn date.
- Pre-action state snapshot.
- Legal actions.
- Chosen action.
- RNG rolls.
- Training support placements.
- Failure rate and failure result.
- Stat gains/losses.
- Energy change.
- Motivation change.
- Bond changes.
- Events triggered.
- Race result if applicable.
- Post-action state snapshot.

Implementation note:

- Logs should be machine-readable first.
- Human-readable formatting can be added later for debugging.

## Heuristic Search Requirements

The career engine should remain pure enough for search:

- State transitions should be reproducible with seeded RNG.
- Legal actions should be generated from state and scenario.
- Action scoring should be separate from transition logic.
- Scenario data should be data-driven where practical.
- Expensive race simulation should be replaceable by an approximate evaluator during search.

Initial heuristic inputs:

- Current stats versus target stats.
- Energy.
- Motivation.
- Failure risk.
- Upcoming objectives.
- Available races and fan needs.
- Support-card bond thresholds.
- Expected training gains.
- Summer camp timing.
- Remaining turns.

## Current Implementation vs Next Pass

Implemented now:

- URA calendar.
- Summer camp flag.
- Sourced global/pre-rebalance URA facility-level training table.
- Sourced facility level-up frequency.
- Simulator-style training calculation for manual support cards.
- Training energy costs from the URA facility table.
- Motivation and support mood-effect handling in the training formula.
- Manual support cards with stat bonuses and core training effects.
- Bond and friendship threshold.
- Legal action generation.
- Fan count and race calendar scaffold.
- Objective scaffold.
- Scenario event scaffold.
- Basic racing probability.
- Turn logs.
- Tests for current behavior.

Next pass should prioritize:

- Support-card placement RNG.
- Character growth rates in training calculation.
- Full character objective data.
- Full race schedule data.
- Real event data and event choice handling.
- Exact support-card schema for GameTora ingestion.
- Conditions and training failure penalties.
- Summer camp behavior from a verifiable source.
- JP post-rebalance URA level 2-5 table if targeting JP instead of Global/pre-rebalance.

Recommended first data files:

- `data/scenarios/ura.json` for scenario constants and fixed event IDs.
- `data/races/races.json` for race schedule.
- `data/characters/example_character.json` for one trainee's starting stats, objectives, and aptitudes.
- `data/support_cards/manual_schema.json` or similar for validating manual support-card input.

## Accuracy Warning

Some numeric values in the current engine are sourced and should not be changed without updating source notes and tests. These include the current URA facility table, facility level-up frequency, and the implemented training formula structure. Other values remain placeholders, especially race probability, rest recovery, race energy cost, fixed scenario event rewards, support-card placement, and training failure rates. When replacing placeholder values, update both this document and the corresponding tests in the same change.
