class_name CropData
extends Resource

## One crop type. Adding a crop means adding a .tres file in data/crops/.

@export var display_name := ""
## Growth stages in order. The last one is ripe and can be harvested.
@export var stage_textures: Array[Texture2D] = []
@export var days_per_stage := 1
## Stage a plant returns to after harvest (0 is the first stage).
@export var regrow_stage := 2
## Days from harvest until the plant is ripe again.
@export var regrow_days := 2
