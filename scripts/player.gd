extends CharacterBody2D

signal identity_changed(display_name: String)

enum Identity { FARMER, DRUG_LORD }

const ANIMATION_PREFIX := {
	Identity.FARMER: "farmer",
	Identity.DRUG_LORD: "drug_lord",
}
const DISPLAY_NAME := {
	Identity.FARMER: "Farmer",
	Identity.DRUG_LORD: "Drug Lord",
}

@export var walk_speed := 90.0
@export var sprint_speed := 170.0
## How far the sprite lifts on each step, in pixels.
@export var bob_height := 2.0
@export var steps_per_second := 4.0

var identity := Identity.FARMER
var _facing := "front"
var _step_time := 0.0

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("switch_identity"):
		toggle_identity()


func _physics_process(delta: float) -> void:
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var sprinting := Input.is_action_pressed("sprint")
	var speed := sprint_speed if sprinting else walk_speed

	velocity = direction * speed
	move_and_slide()

	_update_facing(direction)
	var moving := direction != Vector2.ZERO
	sprite.speed_scale = speed / walk_speed
	sprite.play("%s_%s_%s" % [ANIMATION_PREFIX[identity], "walk" if moving else "idle", _facing])
	_update_bob(moving, speed, delta)


func toggle_identity() -> void:
	identity = Identity.DRUG_LORD if identity == Identity.FARMER else Identity.FARMER
	identity_changed.emit(DISPLAY_NAME[identity])


func facing_vector() -> Vector2i:
	match _facing:
		"back":
			return Vector2i.UP
		"side":
			return Vector2i.LEFT if sprite.flip_h else Vector2i.RIGHT
	return Vector2i.DOWN


func _update_facing(direction: Vector2) -> void:
	# Side art faces right. Standing still keeps the last facing.
	if direction.x != 0.0:
		_facing = "side"
		sprite.flip_h = direction.x < 0.0
	elif direction.y != 0.0:
		_facing = "back" if direction.y < 0.0 else "front"
		sprite.flip_h = false


func _update_bob(moving: bool, speed: float, delta: float) -> void:
	# The sheet has little leg movement, so a small hop sells the walk.
	# Only the sprite moves, which keeps the shadow on the ground.
	if not moving:
		_step_time = 0.0
		sprite.position.y = 0.0
		return
	_step_time += delta * speed / walk_speed
	sprite.position.y = -absf(sin(_step_time * steps_per_second * PI)) * bob_height
