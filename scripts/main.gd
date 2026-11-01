extends Node2D

var day := 1
var _harvest_counts := {}  # Crop display name -> amount

@onready var ground: TileMapLayer = $Ground
@onready var camera: Camera2D = $World/Player/Camera2D
@onready var field: Node2D = $World/Field
@onready var day_label: Label = $HUD/DayLabel
@onready var harvest_label: Label = $HUD/HarvestLabel


func _ready() -> void:
	field.harvested.connect(_on_field_harvested)
	_fit_camera_to_map()
	_update_hud()


func _fit_camera_to_map() -> void:
	# Follows the painted ground, so repainting the map needs no code change.
	var map := Rect2i(ground.get_used_rect().position * ground.tile_set.tile_size,
			ground.get_used_rect().size * ground.tile_set.tile_size)
	camera.limit_left = map.position.x
	camera.limit_top = map.position.y
	camera.limit_right = map.end.x
	camera.limit_bottom = map.end.y


func _unhandled_input(event: InputEvent) -> void:
	# Temporary test key until the game has a real clock or a bed.
	if event.is_action_pressed("next_day"):
		day += 1
		field.advance_day()
		_update_hud()


func _on_field_harvested(crop: CropData) -> void:
	_harvest_counts[crop.display_name] = _harvest_counts.get(crop.display_name, 0) + 1
	_update_hud()


func _update_hud() -> void:
	day_label.text = "Day %d" % day
	var lines := PackedStringArray()
	for crop_name in _harvest_counts:
		lines.append("%s: %d" % [crop_name, _harvest_counts[crop_name]])
	harvest_label.text = "\n".join(lines)
