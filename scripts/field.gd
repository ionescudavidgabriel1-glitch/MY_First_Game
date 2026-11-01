extends Node2D

## A fixed patch of soil plots. Press interact on a plot to plant or harvest.

signal harvested(crop: CropData)

const TILE_SIZE := 32
const SOIL_COLOR := Color("#4a3322")
const SOIL_EDGE_COLOR := Color("#3b2819")
const HIGHLIGHT_COLOR := Color(1, 1, 1, 0.8)
# Crop art's base sits this far above the bottom of its plot.
const CROP_BASE_MARGIN := 5
const CROP_SPRITE_HEIGHT := 48

@export var size_in_tiles := Vector2i(4, 3)
## Only one crop for now. A seed choice can replace this later.
@export var crop: CropData
@export var player: Node2D

var _plots := {}  # Vector2i tile -> { crop, stage, days_left, sprite }
var _target := Vector2i.ZERO
var _has_target := false


func _process(_delta: float) -> void:
	var feet_tile := Vector2i((to_local(player.global_position) / TILE_SIZE).floor())
	var target: Vector2i = feet_tile + player.facing_vector()
	var has_target := Rect2i(Vector2i.ZERO, size_in_tiles).has_point(target)
	if target != _target or has_target != _has_target:
		_target = target
		_has_target = has_target
		queue_redraw()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact") and _has_target:
		_interact(_target)


func _draw() -> void:
	for y in size_in_tiles.y:
		for x in size_in_tiles.x:
			var rect := Rect2(Vector2(x, y) * TILE_SIZE, Vector2.ONE * TILE_SIZE)
			draw_rect(rect, SOIL_EDGE_COLOR)
			draw_rect(rect.grow(-1), SOIL_COLOR)
	if _has_target:
		var highlight := Rect2(Vector2(_target) * TILE_SIZE, Vector2.ONE * TILE_SIZE)
		draw_rect(highlight.grow(-1), HIGHLIGHT_COLOR, false, 1.0)


func advance_day() -> void:
	for plot in _plots.values():
		if _is_ripe(plot):
			continue
		plot.days_left -= 1
		if plot.days_left <= 0:
			_set_stage(plot, plot.stage + 1, plot.crop.days_per_stage)


func _interact(tile: Vector2i) -> void:
	if not _plots.has(tile):
		_plant(tile)
	elif _is_ripe(_plots[tile]):
		var plot: Dictionary = _plots[tile]
		_set_stage(plot, plot.crop.regrow_stage, plot.crop.regrow_days)
		harvested.emit(plot.crop)


func _plant(tile: Vector2i) -> void:
	var sprite := Sprite2D.new()
	sprite.offset.y = -CROP_SPRITE_HEIGHT / 2.0
	sprite.position = (Vector2(tile) + Vector2(0.5, 1.0)) * TILE_SIZE - Vector2(0, CROP_BASE_MARGIN)
	add_child(sprite)
	var plot := { "crop": crop, "stage": 0, "days_left": 0, "sprite": sprite }
	_plots[tile] = plot
	_set_stage(plot, 0, crop.days_per_stage)


func _set_stage(plot: Dictionary, stage: int, days_left: int) -> void:
	plot.stage = stage
	plot.days_left = days_left
	plot.sprite.texture = plot.crop.stage_textures[stage]


func _is_ripe(plot: Dictionary) -> bool:
	return plot.stage == plot.crop.stage_textures.size() - 1
