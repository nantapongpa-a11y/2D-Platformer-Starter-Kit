extends Node2D

# Start screen of "Captain Go: Pirate Sea Adventure"

@onready var btn_continue: Button = $UI/Menu/btnContinue

var t := 0.0

func _ready() -> void:
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	btn_continue.disabled = !GameManager.has_gamesaved()
	GameManager.load_option()
	$Captain/AnimationPlayer.play("Idle")
	$Music.play()
	for button in $UI/Menu.get_children():
		button.mouse_entered.connect(_on_button_hover.bind(button, true))
		button.mouse_exited.connect(_on_button_hover.bind(button, false))
	_intro()


func _process(delta: float) -> void:
	t += delta
	$TitleGroup/Title.scale = Vector2.ONE * (1.0 + sin(t * 2.0) * 0.02)


# Title drops in, buttons slide in from the right
func _intro() -> void:
	var title_y = $TitleGroup.position.y
	$TitleGroup.position.y = title_y - 300
	var menu_x = $UI/Menu.position.x
	$UI/Menu.position.x = menu_x + 400
	$UI/Menu.modulate.a = 0.0
	var tween = create_tween()
	tween.tween_property($TitleGroup, "position:y", title_y, 1.0).set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)
	tween.parallel().tween_property($UI/Menu, "position:x", menu_x, 0.7).set_delay(0.4).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.parallel().tween_property($UI/Menu, "modulate:a", 1.0, 0.5).set_delay(0.4)


func _on_button_hover(button: Button, inside: bool) -> void:
	button.pivot_offset = button.size / 2
	var tween = create_tween()
	tween.tween_property(button, "scale", Vector2.ONE * (1.08 if inside else 1.0), 0.12)


func _on_btn_start_pressed() -> void:
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN)
	get_tree().change_scene_to_file("res://Scenes/Levels/story.tscn")


func _on_btn_option_pressed() -> void:
	get_tree().change_scene_to_file("res://Scenes/Levels/options.tscn")


func _on_btn_credit_pressed() -> void:
	get_tree().change_scene_to_file("res://Scenes/Levels/credit.tscn")


func _on_btn_continue_pressed() -> void:
	GameManager.load_game()


func _on_btn_exit_pressed() -> void:
	get_tree().quit()


func _on_music_finished() -> void:
	$Music.play()
