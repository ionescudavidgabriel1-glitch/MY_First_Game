extends Sprite2D

## Temporary two-tone checker that makes movement visible. Delete this and its
## node in main.tscn when the real map arrives.

@export var color_a := Color("#5f9646")
@export var color_b := Color("#598e41")
@export var square_size := 64
## Width and height of the ground, in squares.
@export var squares := 400


func _ready() -> void:
	var image := Image.create(2, 2, false, Image.FORMAT_RGBA8)
	image.set_pixel(0, 0, color_a)
	image.set_pixel(1, 1, color_a)
	image.set_pixel(1, 0, color_b)
	image.set_pixel(0, 1, color_b)
	texture = ImageTexture.create_from_image(image)
	texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	region_enabled = true
	region_rect = Rect2(0, 0, squares, squares)
	scale = Vector2.ONE * square_size
