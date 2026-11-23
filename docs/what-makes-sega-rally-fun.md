# What makes Sega Rally fun, and where Handbrake Hero falls short (23 Nov 2026)

Sourced findings are marked (S). Inferences about our game from the project docs, not from reading the code, are marked (I).

## 1. What makes Sega Rally fun

1. **Handling is the product (S).** Reviewers and developers consistently credit the handling over graphics or content. Intent: not full realism, but real technique (brake before corners, downshift, steer to start a slide). Drifting was central; lower, more abrupt downshifts gave tighter drifts. Manual cars gave more control with a steeper learning curve.
2. **Readable, forgiving slides (S).** You can feel the car start to lose grip and respond before it goes wrong. Imperfect inputs don't always spin you, so players learn gradually, and faster times reward learning each surface.
3. **Surfaces change the car (S).** First racer where grip varied by surface (asphalt, gravel, mud, puddles, dips). Codemasters credited the loose-gravel sliding as the base for Colin McRae Rally.
4. **The car feels physical (S).** Two wheels on a bump mid-turn can unsettle the car; three jumps in a row leave it progressively unbalanced; gravity and inertia read convincingly; hard acceleration can spin it. There is no single perfect line because of small surface undulations.
5. **Stages teach, then bite (S).** First turns are wide and shallow to learn 3D steering; the zebra corner looks easier than it is; a long wide bend is flat-out but just tight enough for time attackers. Dense pace: first corner, jumps, wooded puddle chicane with close walls, open area with animals, helicopter dust near the finish, all in about 55 s.
6. **Stage length and structure (S).** About one minute per stage, three stages per session, rising difficulty. Narrow roads chosen to emphasise control.
7. **Co-driver and signs replace a map (S).** No minimap. A navigator voice calls curves and jumps, backed by colour-coded arrows and "!" marks.
8. **Sound and feel (S).** Real rally cars recorded on dirt (engine, exhaust, braking, drifting, gravel). The cabinet seat shook with the car and collisions. Engine pitch let drivers judge speed and brake by downshifting.
9. **Failure is soft and motivating (S).** Championship removed crashes and off-course penalties. Rivals are mostly obstacles; time is the real threat. Sasaki designed near-misses (timing out just before the finish, failing to pass a rival) to prompt another coin. Starting 15th makes any gain feel like progress.
10. **Art direction (S).** Impact and immersion over gloss, gravel as well as tarmac, muted earthy palette.
11. **No handbrake in the core technique (S).** The 7sun fan guide never mentions one; it frames sliding as something to control and minimise, with speed carried through apex clipping, lift-off and downshift braking.

## 2. Likely reasons Handbrake Hero feels boring (I)

1. **The game drives itself too much.** Road-follow when the stick is neutral, an auto corner-speed limit, anti-spin, a held ~30 degree handbrake drift, and (on touch) auto-throttle. In Sega Rally, speed management and slide control are the skill.
2. **Slides are a button, not a feel.** Sega Rally's drift is emergent from throttle, braking, downshift and steering on a surface.
3. **Surfaces probably not different enough.** No mid-stage mud, puddles or bumps that unsettle the car in the docs.
4. **Stage rhythm.** Loops, solo practice and a single-file ghost-train of traffic lose the sprint-with-set-pieces feel.
5. **Feedback probably thin.** No documented engine/gravel/skid audio, camera shake, dust or haptics.
6. **No navigator voice.**
7. **Reward loop.** Medals and retry exist, but not the near-miss structure: tight timer, checkpoint extensions, a visible rival to catch.

## 3. Suggested changes, in order

1. Hand the throttle back: remove auto-throttle and the auto corner-speed limit as defaults (optional assist).
2. Rebuild the slide model for feel: surface grip, load transfer, throttle; recoverable slides that cost speed; demote the handbrake to a hairpin tool.
3. Surface-first stage design: per-surface grip and sound, mid-corner surface changes, bumps, crests, three-jump sequence.
4. Re-cut stages as 55-80 s sprints with set pieces and a scenic beat every 8-10 s.
5. Add a navigator voice.
6. Feedback pass: RPM-tied engine pitch, gravel/skid layers, camera lag and swing, dust, sparks, phone vibration.
7. Near-miss failure: tight checkpoint timer, rival to catch, instant restart, "missed by 0.4 s" message.

## 4. Open questions

- Main target touch or keyboard? Sega Rally controls map awkwardly to touch.
- Keep the handbrake as the game's identity, or make it a secondary tool?

## 5. Sources

- https://www.sega-16.com/?p=53832
- https://www.gamesradar.com/the-classic-game-appreciation-section-sega-rally
- https://www.generationamiga.com/2026/09/02/sega-rally-championship-how-tetsuya-mizuguchi-crashed-a-rally-car-during-development/
- https://www.7sun.com/arcade/segarally/mb/segarally.html
- https://retroxp.beehiiv.com/p/30-years-of-the-sega-saturn-sega-rally-championship-846ace5395d89720
- https://segaretro.org/Sega_Rally_Championship
- https://www.empireonline.com/gaming/reviews/sega-rally-review/
