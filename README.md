# Handbrake Hero: Rally 90s Championship

A browser rally game (three.js, single `index.html`): three 1990s-style stages plus a bonus stage, 15 cars, a countdown clock, checkpoints and a rival field you have to catch. Play: serve the folder (`python3 -m http.server`) and open `index.html`.

## Driving model and driver aids
The stick (or thumb drag) sets **how hard you want to corner**, as a fraction of the grip the tyres have, rather than a raw steering angle. A controller turns that into a target yaw rate and sets the front wheels (feed-forward plus feedback), so full stick can never exceed grip and the car does not snap sideways. Previously full lock was about five times what the tyres could use at speed, which made only the first 20% of the stick usable and was the main reason the game felt unforgiving.

Three driver-aid levels, chosen on the title screen, the stage card and the pause menu (default **Relaxed**):

| Level | Road assist (neutral stick follows the road) | Corner speed | Spin protection | Handbrake |
|---|---|---|---|---|
| Relaxed | 78% | auto-lift and auto-brake to 90% of the grip profile | strong | controlled drift |
| Standard | 40% | safety net above 106% of grip profile | medium | controlled drift |
| Pro | none | none | light | raw |

- Road assist fades out as you push the stick, so you always have full authority.
- **Handbrake / SLIDE** holds a controlled drift (slip angle about 20 to 35 degrees) instead of a spin. A clean slide of 0.7 s or more pays a time bonus in Championship ("DRIFT +1.4 SECONDS").
- Walls scrub speed and push the car back parallel to the road rather than bouncing it around.

Automated checks (`bot` driving through the same inputs a thumb produces; 3 skill levels, 3 stages): with the old handling a "good" bot hit walls 7 to 20 times per stage and spun out 10 times on Desert, a novice bot 17 to 25 walls and up to 15 spins; with Relaxed aids novice bots average 0.5 to 4 wall touches per stage and no spins, and finish in 1.07 to 1.16 times the reference time.

## Controls
- **Keyboard:** arrows/WASD steer, gas and brake; Space handbrake; C camera; R back on road (-3 s); Esc pause.
- **Touch:** drag anywhere on the left side to steer (a slider appears under your thumb); big **BRAKE** and **SLIDE** buttons for the right thumb; gas is automatic (switch it off under Driver aids for a GAS button); top right: pause, camera and back on road. Landscape and portrait layouts, safe-area insets for notches. The game pauses if the app goes to the background.
- **Pause menu:** resume, restart stage (instant, no intro card), change driver aids or auto-throttle, camera, quit.

## Keep-playing loop
- **Medals** per stage (Bronze / Silver / Gold) against the stage's reference time. Relaxed tops out at Silver; Gold needs Standard or Pro.
- **Splits:** each checkpoint shows your time against your best run on that stage.
- **Try again credits:** in Championship, running out of the clock offers two "Try again" credits instead of ending the run ("So close, 83% of the stage").
- Results show how many seconds you are from the next medal, and Retry is one tap.

## Cars
Five period cars (Impreza 555, Delta Integrale Evo 2, Escort Cosworth, Lancer Evo III, Celica ST205), modelled in Blender by `models/build_cars.py` (writes `models/cars.blend`, a `.glb` per car, and `cars.json` for the game).

Each body is lofted from cross-sections driven by side-profile and plan-view curves set to the real car's published length, wheelbase, overhangs, width and height (lowered slightly to rally ride height). The models have a proper greenhouse (raked windscreen, pillars, side and rear glass), open wheel arches with flares (box-section blisters on the Delta), and per-car details: bumpers and intakes, headlamp layout (four round lamps on the Delta and Celica), rear lights that glow under braking, bonnet scoops, vents and louvres, and each car's wing (the Escort's whale tail, the tall Impreza and Lancer wings, the Delta's roof spoiler). Smooth normals are exported per triangle corner. Wheels are built in the game: rounded tyres and multi-spoke rims in each car's colour (gold on the Impreza). The start menu shows the selected car on a turntable.

Liveries are original colour schemes in team colours, with no sponsor logos or wordmarks. Handling is tuned by feel. Engine sound is synthesised per car in the browser (flat-four burble for the Impreza, different pitch and tone for the others), with anti-lag crackle, pops and exhaust flames when you lift off the throttle; no recordings are used.

## Col de Turini
The earlier stage built from real road and elevation data is still here as `turini.html` (needs `track.json`; see `tools/` for the data pipeline). Road © OpenStreetMap contributors (ODbL), elevation EU-DEM via OpenTopoData.

## Rally 90s stages: loops and laps
Every Rally 90s stage is a closed loop: the finish line is the start line. The loop is solved at build time (`closeLoop` in `index.html`: seeded corner-direction search, then a small harmonic correction so the road closes exactly with matching heading, and a minimum clearance check against itself). Elevation and road width are blended so there is no seam at the line.

Championship is one lap per stage, as before. Practice mode has a lap selector (1, 2, 3 or 5): lap times and a best lap are tracked, with a results table at the end. Best stage times are kept per lap count. In Practice you are the only car on the stage: no rivals, no position HUD, no collisions with other cars.

## History
The repo began as Endless Hairpins, a single mountain pass of nothing but hairpins; that build was replaced by the Rally 90s Championship (see git history).
