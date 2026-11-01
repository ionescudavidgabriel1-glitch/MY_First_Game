# The Dual-Life Farmer (working title)

2D top-down farming game inspired by Stardew Valley, with an original story and features.
Built with Godot 4.7 and GDScript, using the GL Compatibility renderer.

## Working rules
- **Ask the user before making any implementation decision.** This applies to the whole project.
- Work in small steps. Each step adds one thing the user can see or test in the game.
- After each step the user runs the game and confirms it before the next one starts.
- Don't add features ahead of the current step.
- Keep this file up to date when game logic, story, or code structure changes.

## Game concept
- **Surface:** the player is an ordinary farmer. The farm is his cover.
- **Secret life:** he is also a drug lord who grows weed and makes money.
- **Brother:** his brother is in jail, and this is tied to the money and the story.

## Story
Still being written; the user will add more later. Do not invent story details. Ask, then record them here.

Open questions:
- Why is the brother in jail?
- How is the brother connected to the money?

## Codebase
- `scenes/main.tscn`: main scene with the `Ground` tile layer, `MapEdges` walls, y-sorted world (player and field) and HUD. The switch button is wired to the player here, through signal connections.
- `scripts/main.gd`: day number, the temporary next-day key, harvest counts, HUD labels, and fitting the camera limits to the painted ground. If the map size changes, move the `MapEdges` walls by hand.
- `data/tilesets/ground.tres`: ground tile set (plain grass, flower grass).
- `tools/slice_ground.py`: cuts ground tiles out of `assets/word/ground_tiles.jpg` into `assets/sprites/ground/ground_tiles.png`, trimming the edges so tiles repeat cleanly. Add a sheet index to `TILES` and a line in `ground.tres` to bring in another tile.
- `scripts/field.gd`: the soil plots. Handles targeting, planting, growth and harvesting.
- `scripts/crop_data.gd`: the `CropData` resource (name, stage art, growth timing).
- `data/crops/`: one `.tres` file per crop. Adding a crop means cutting its art and adding a file here, with no new logic.
- `scenes/player.tscn`: player sprite, shadow, collision, camera and all animations.
- `scripts/player.gd`: movement, facing, walk bob and the current identity.
- `tools/slice_character.py`: cuts the walk frames out of the sprite sheets and scales them to the same height. Needs Python with Pillow, NumPy and SciPy.
- `tools/slice_crops.py`: cuts crop stages out of `assets/crops.jpg`. Only tomatoes so far.
- `assets/farmer.jpg`, `assets/drog_dealer.jpg`, `assets/drog_lord2.jpg`: source sheets for the walk frames. `drog_lord2.jpg` is the Drug Lord's side walk; the side row in `drog_dealer.jpg` is not used. Don't load sheets in the game; use the cut frames.
- `assets/character.png`: the original sheet, no longer used for frames.
- `assets/sprites/player/{farmer,drug_lord}/`: cut frames named `{front|back|side}_{n}.png`, 44x56 with feet on the bottom edge. The figure is about 48 pixels tall.
- `assets/sprites/crops/{crop}/stage_{1-4}.png`: cut crop stages, 40x48 with the base on the bottom edge.

Animations are named `{farmer|drug_lord}_{idle|walk}_{front|back|side}`. Side art faces right and is flipped for left.

## Controls
WASD or arrow keys to move, Shift to sprint, Tab or the on-screen button to switch identity.
E to plant or harvest on the highlighted plot. N skips to the next day (temporary test key).

## Decisions so far
- Develop in `my-game`. `D:\2D_GAME\new-game-project` is an older prototype: reuse from it, but don't modify it.
- Underground costume: black shirt and green work clothes (not the blue overalls with mask).
- Walk animation: frames from the sheets at 8 frames per second, plus a small bob in code. Farmer: 3 front (`farmer.jpg` figures 1, 2 and 4; the others turn sideways), 6 back, 7 side. Drug Lord: 4 front, 4 back, 6 side.
- Both identities are the same height in every direction: each sheet row is scaled to about 48 pixels. This makes the farmer's art pixels a bit uneven, which the user accepted.
- Standing still uses the first frame of each direction.
- Physics interpolation is on and 2D pixel snapping is off. On a 120 Hz screen the old settings made the player jump back and forth, which looked like blur. Any instant move, such as a teleport, must call `reset_physics_interpolation()` or the player appears to slide there.
- `assets/drog_lord.png` is rejected (wrong outfit).
- First feature covers idle and walk only. Each action animation is added with the feature that uses it.
- Switching is instant and only changes the look for now, with no gameplay effect.
- Switch button is top-right and shows the current identity. Tab does the same thing.
- Shadow is a separate sprite that stays on the ground. The sheet's baked-in shadow is removed.
- Sprint is a faster walk (no sprint art).

Crops (`assets/crops.jpg` is the "cover crops" sheet: tomatoes, hops, tall corn, lavender, blueberries):
- Tomatoes first. The other four crops come later.
- Crops grow by game day. There is no clock or bed yet, so N is a temporary test key.
- The loop is plant, then harvest, on already prepared soil. Hoeing and watering are later steps.
- Fixed 4x3 field of 32-pixel plots. Plants don't block the player. Empty soil is a temporary drawn square, because the sheet has no soil art.
- E acts on the tile in front of the player, which is outlined.
- Ripe tomato art is one plant cut from the sheet's group of three.
- Tomatoes ripen in 3 days (1 per stage). Harvest returns the plant to the flowering stage, ripe again 2 days later.
- Harvest adds 1 to an on-screen counter. There is no inventory or selling yet.

Map (farm, 50x36 tiles of 32 pixels, painted with tile maps the user can edit in Godot):
- Built one step at a time, tested after each: ground and map edges, harvest area, buildings, pond, forage area, mine.
- Layout: forage area in the west, 14x10 fenced harvest area in the centre, house and barn north of it, shed and pond in the east, tree line around the edges, rock hillside along the north with the mine in the north-east corner.
- Mine: the hidden entrance to the underground weed operation. It looks old and boarded up. Opening it comes later.
- House, barn and shed are all on the map but locked. Missions unlock their keys later. Missions are not designed yet.
- Flower grass tiles are scattered singly with gaps, never touching. Packed together they show an obvious grid.
- Pond is a rounded rectangle, because `assets/word/pond_tiles.jpg` has no inner corners.
- Use `assets/word/props.jpg`, not the Gemini image of the same props, which has ghosted buildings in it.

## Tooling
Godot executable: `C:\Users\VIVOBOOK\Downloads\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64.exe` (the first part is a folder). The `_console.exe` next to it prints output to the terminal.
The Godot MCP tools look in `C:\Program Files\Godot\Godot.exe` and fail unless `GODOT_PATH` is set to the path above.

## Art for later
`assets/character_V2.jpg` has hoe and crafting animations. The title text overlaps some frames, and the crafting table is part of the drawing.

## Roadmap
Each item is one small step.

Foundations
- [x] Character with idle and walk animations, and identity switch

Farm map
- [x] Ground and map edges
- [ ] Harvest area: 14x10 plots with fence and gate
- [ ] Locked house, barn and shed
- [ ] Pond
- [ ] Forage area
- [ ] Boarded-up mine entrance in the rock hillside (needs new art)

Farming
- [x] Plant, grow and harvest tomatoes on a day counter
- [ ] Add the other cover crops, with a way to choose a seed
- [ ] Hoe a tile of soil
- [ ] Water crops
- [ ] Simple inventory
- [ ] Sell crops for money

Dual life
- [ ] Hidden entrance and an underground area
- [ ] Grow plants underground
- [ ] Sell underground product for money

Story and later features: to be planned once the story is written.
