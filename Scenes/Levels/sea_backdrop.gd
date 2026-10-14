extends Node2D

# Animated sea background used by the menu, story, credit and ending screens:
# sky, far sea with islands, Captain Go's ship, rolling waves and seagulls.

@export var sky : Texture2D
@export var show_ship : bool = true
@export var tint : Color = Color.WHITE

var t := 0.0
var ship_y := 0.0

func _ready() -> void:
	if sky:
		$Sky.texture = sky
	$Ship.visible = show_ship
	ship_y = $Ship.position.y
	modulate = tint
	for gull in $Gulls.get_children():
		gull.play("fly")


func _process(delta: float) -> void:
	t += delta
	_scroll($Far, 6.0 * delta)
	_scroll($Waves, 40.0 * delta)
	$Ship.position.y = ship_y + sin(t * 1.2) * 5.0
	$Ship.rotation = sin(t * 0.9) * 0.025
	var i := 0
	for gull in $Gulls.get_children():
		gull.position.x -= (50.0 + i * 18.0) * delta
		gull.position.y += sin(t * 2.0 + i) * 0.3
		if gull.position.x < -60:
			gull.position.x = 1300 + i * 120
		i += 1


# Move two copies of a 1152 px wide picture to make an endless loop
func _scroll(group: Node2D, amount: float) -> void:
	for sprite in group.get_children():
		sprite.position.x -= amount
		if sprite.position.x <= -1152:
			sprite.position.x += 2304
