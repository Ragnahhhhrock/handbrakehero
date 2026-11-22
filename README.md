# Rally90s

Browser rally simulator set in the 1990s World Rally Championship era. First stage: **Col de Turini** (Rallye Monte-Carlo), Moulinet to La Bollène-Vésubie, about 21.5 km.

Open `index.html` through any static web server (for example `python3 -m http.server`). It loads `track.json` and three.js from a CDN.

## How the stage is built

1. `tools/elev.py` takes the routed road (`data/route.json`), resamples it every 15 m and looks up elevation.
2. `tools/grid.py` fetches a coarse terrain grid around the road.
3. `tools/process.py` turns both into `track.json`: smoothed road, corner detection and pace notes.

Run the tools from inside `data/`, for example `cd data && python3 ../tools/elev.py eudem25m`. The scripts need network access to the public APIs below.

## Controls

Up/W throttle, Down/S brake and reverse, Left/Right or A/D steer, Space handbrake, C camera, V voice, R back on the road (+5 s). Gamepad: stick, triggers, A for handbrake.

## Data credits

- Road geometry: OpenStreetMap contributors (ODbL), routed through the public OSRM demo server.
- Elevation: EU-DEM via OpenTopoData.
- Pace notes are generated from road curvature, not copied from any pacenote set.

Reference footage used for look and feel is not stored in this repo.
