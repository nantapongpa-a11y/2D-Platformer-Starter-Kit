extends Node2D

# Options screen: turn the music and the sound effects on or off

func _ready() -> void:
	GameManager.load_option()
	$Panel/Box/Music.button_pressed = GameManager.music_on
	$Panel/Box/Sound.button_pressed = GameManager.sfx_on


func _on_music_toggled(on: bool) -> void:
	GameManager.music_on = on
	GameManager.update_option()
	GameManager.save_option()


func _on_sound_toggled(on: bool) -> void:
	GameManager.sfx_on = on
	GameManager.update_option()
	GameManager.save_option()
	AudioManager.coin_pickup_sfx.play()


func _on_btn_back_pressed() -> void:
	get_tree().change_scene_to_file("res://Scenes/Levels/menu.tscn")
