extends Node2D

# Shared level logic for "Captain Go: Pirate Sea Adventure".
# Each level can change the music and the background in the inspector.

@export var music : AudioStream
@export var sky_texture : Texture2D
@export var far_texture : Texture2D
@export var far_tint : Color = Color.WHITE
@export var show_far_sea : bool = true
@export var show_waves : bool = true
# How far the camera may look above the highest tile (0 for the cave level)
@export var camera_top_margin : int = 400

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	GameManager.player = %Player
	if music:
		$MusicPlayer.stream = music
	if sky_texture:
		$SkyLayer/Sky.texture = sky_texture
	if far_texture:
		$Level/FarBG/Sprite2D.texture = far_texture
	$Level/FarBG.modulate = far_tint
	$Level/FarBG.visible = show_far_sea
	$Level/Waves.visible = show_waves
	_setup_camera_limits()
	$MusicPlayer.play(0)
	var tween = create_tween()
	$UserInterface/Label.scale = Vector2.ZERO
	tween.stop(); tween.play()
	tween.tween_property($UserInterface/Label, "scale", Vector2.ONE, 0.8).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	await get_tree().create_timer(3).timeout
	$UserInterface/Label.queue_free()

# Keep the camera inside the level (left/right edge and the sea at the bottom)
func _setup_camera_limits() -> void:
	var rect := Rect2i()
	for layer_name in ["Level/Ground", "Level/Sea"]:
		var layer = get_node_or_null(layer_name)
		if layer is TileMapLayer:
			var r : Rect2i = layer.get_used_rect()
			rect = r if rect.size == Vector2i.ZERO else rect.merge(r)
	if rect.size == Vector2i.ZERO:
		return
	var cam : Camera2D = %Player.get_node("Camera2D")
	cam.limit_left = rect.position.x * 64
	cam.limit_right = rect.end.x * 64
	cam.limit_bottom = rect.end.y * 64 - 96  # show only the top of the sea
	cam.limit_top = rect.position.y * 64 - camera_top_margin

func _on_player_hit_enemy(amount : int = 5) -> void:
	GameManager.damage(amount)

func _on_player_hit_trap() -> void:
	GameManager.damage(15)

func _on_player_fell_in_sea() -> void:
	AudioManager.splash_sfx.play()
	GameManager.death()

func _on_music_player_finished() -> void:
	$MusicPlayer.play(0)
