# Endless Hairpins

A browser game (three.js, single file): one mountain pass that is nothing but hairpins, climbing forever. Every hairpin is timed. The fast way round is a handbrake 180.

Play: open `index.html` (serve the folder, e.g. `python3 -m http.server`).

## How to drive a hairpin
Brake late on the straight, turn in hard, tap **Space** to throw the tail round, let go as the nose points up the next straight, then full throttle. The yellow-on-black chevron boards mark the outside of each bend; the top-right radar shows the next hairpin in yellow.

Grades per hairpin (entry line 12 m before the bend to 12 m after): PERFECT 180 (≤ 3.9 s, no wall contact, straight exit), GREAT, GOOD, SLOW, plus wall-touch penalties in the label. Run lengths: 10 or 25 hairpins, or endless. Best times are stored in the browser per car.

## Tutorial
The start card has a **Tutorial** button: five practice hairpins with an on-screen coach that tells you when to accelerate, brake, steer in, hit the handbrake, hold it, and release, plus a tip after each bend. It does not count towards best times.

## Controls
Arrows/WASD steer and throttle, **Space** handbrake, C camera, I isometric view, V voice, R back on the road (+4 s), Esc menu. Gamepad: stick, triggers, A handbrake.

## Mobile first
The game is designed for phones, portrait or landscape. Touch layout switches on automatically.
- Drag anywhere on the left side to steer (analog, relative to where your thumb lands). Big **HB** handbrake button bottom right, **BRAKE** beside it.
- **Auto throttle** is on by default on touch (you steer, brake and handbrake); turn it off in the menu for a manual GAS button.
- ☰ menu (tap twice to quit a run), ◉ camera, ⟲ back on road (+4 s).
- Wider field of view and a higher, further-back chase camera in portrait; safe-area insets for notches; pixel ratio capped at 1.5 and lowered automatically if the frame rate drops.
- Vibration on wall hits and perfect turns (Android Chrome; iOS Safari has no vibration API).
- `manifest.webmanifest` and icons: add to home screen for full-screen play.

## Cars
Five period cars (Impreza 555, Delta Integrale Evo 2, Escort Cosworth, Lancer Evo III, Celica ST205), modelled in Blender by `models/build_cars.py` (writes `models/cars.blend`, a `.glb` per car, and `cars.json` for the game).

Each body is lofted from cross-sections driven by side-profile and plan-view curves set to the real car's published length, wheelbase, overhangs, width and height (lowered slightly to rally ride height). The models have a proper greenhouse (raked windscreen, pillars, side and rear glass), open wheel arches with flares (box-section blisters on the Delta), and per-car details: bumpers and intakes, headlamp layout (four round lamps on the Delta and Celica), rear lights that glow under braking, bonnet scoops, vents and louvres, and each car's wing (the Escort's whale tail, the tall Impreza and Lancer wings, the Delta's roof spoiler). Smooth normals are exported per triangle corner. Wheels are built in the game: rounded tyres and multi-spoke rims in each car's colour (gold on the Impreza). The start menu shows the selected car on a turntable.

Liveries are original colour schemes in team colours, with no sponsor logos or wordmarks. Handling is tuned by feel. Engine sound is synthesised per car in the browser (flat-four burble for the Impreza, different pitch and tone for the others), with anti-lag crackle, pops and exhaust flames when you lift off the throttle; no recordings are used.

## The mountain
Generated, not real: the same road every run (fixed seed). Straights of 22 to 114 m alternate with 180-degree bends, climbing as you go. Forest gives way to rock, then snow, with altitude.

## Col de Turini
The earlier stage built from real road and elevation data is still here as `turini.html` (needs `track.json`; see `tools/` for the data pipeline). Road © OpenStreetMap contributors (ODbL), elevation EU-DEM via OpenTopoData.

## Rally 90s stages: loops and laps
Every Rally 90s stage is a closed loop: the finish line is the start line. The loop is solved at build time (`closeLoop` in `index.html`: seeded corner-direction search, then a small harmonic correction so the road closes exactly with matching heading, and a minimum clearance check against itself). Elevation and road width are blended so there is no seam at the line.

Championship is one lap per stage, as before. Practice mode has a lap selector (1, 2, 3 or 5): lap times and a best lap are tracked, with a results table at the end. Best stage times are kept per lap count.
