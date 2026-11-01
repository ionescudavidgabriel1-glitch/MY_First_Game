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
- `scenes/main.tscn`: test scene with the ground, y-sorted world (player and field) and HUD. The switch button is wired to the player here, through signal connections.
- `scripts/main.gd`: day number, the temporary next-day key, harvest counts and HUD labels.
- `scripts/field.gd`: the soil plots. Handles targeting, planting, growth and harvesting.
- `scripts/crop_data.gd`: the `CropData` resource (name, stage art, growth timing).
- `data/crops/`: one `.tres` file per crop. Adding a crop means cutting its art and adding a file here, with no new logic.
- `scenes/player.tscn`: player sprite, shadow, collision, camera and all animations.
- `scripts/player.gd`: movement, facing, walk bob and the current identity.
- `scripts/test_ground.gd`: temporary checker ground. Delete it when the real map arrives.
- `tools/slice_character.py`: cuts frames out of the sprite sheet. Needs Python with Pillow, NumPy and SciPy.
- `tools/slice_crops.py`: cuts crop stages out of `assets/crops.jpg`. Only tomatoes so far.
- `assets/character.png`: source sprite sheet. Don't load it in the game; use the cut frames.
- `assets/sprites/player/{farmer,drug_lord}/`: cut frames, 44x56 with feet on the bottom edge.
- `assets/sprites/crops/{crop}/stage_{1-4}.png`: cut crop stages, 40x48 with the base on the bottom edge.

Animations are named `{farmer|drug_lord}_{idle|walk}_{front|back|side}`. Side art faces right and is flipped for left.

## Controls
WASD or arrow keys to move, Shift to sprint, Tab or the on-screen button to switch identity.
E to plant or harvest on the highlighted plot. N skips to the next day (temporary test key).

## Decisions so far
- Develop in `my-game`. `D:\2D_GAME\new-game-project` is an older prototype: reuse from it, but don't modify it.
- Underground costume: black shirt and green work clothes (not the blue overalls with mask).
- Walk animation: frames from the sheet, plus a small bob in code. Front, back and underground walks have few frames.
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

## Tooling
Godot executable: `C:\Users\VIVOBOOK\Downloads\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64.exe` (the first part is a folder). The `_console.exe` next to it prints output to the terminal.
The Godot MCP tools look in `C:\Program Files\Godot\Godot.exe` and fail unless `GODOT_PATH` is set to the path above.

## Paused: smoother walk animation (must still be done)
The user paused this to work on crops. Do not forget it. Remind the user when crops are done.
- `assets/farmer.jpg`: new farmer walk frames, approved. Usable frames: all side (7) and back (6), front 1, 2 and 4 only (front 3, 5 and 6 turn sideways). The side row is about 20% taller than the front row, so rows must be scaled to match. Its pixels are about twice as big as `character.png`.
- `assets/drog_lord.png`: rejected, wrong outfit (blue overalls instead of black and olive).
- Next: the user generates a new Drug Lord sheet in the black and olive outfit, using `drug_lord_reference.png` (made from `assets/sprites/player/drug_lord/`). Then cut both together so they match in size, asking the user how to handle scaling.
- `assets/character_V2.jpg` has hoe and crafting animations for later. The title text overlaps some frames, and the crafting table is part of the drawing.

The game still uses the original frames from `assets/character.png`.

## Roadmap
Each item is one small step.

Foundations
- [ ] Character with idle and walk animations, and identity switch (works with the original frames; smoother frames are paused, see above)

Farming
- [ ] Plant, grow and harvest tomatoes on a day counter (built, waiting for the user to confirm)
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
