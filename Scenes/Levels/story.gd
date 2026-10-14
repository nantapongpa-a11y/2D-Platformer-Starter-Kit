extends Node2D

# Story screen shown before Level 1 of "Captain Go: Pirate Sea Adventure".
# The story is typed out letter by letter; press the button to skip or start.

var typing : Tween

func _ready() -> void:
	$Captain/AnimationPlayer.play("Idle")
	$Music.play()
	$Parchment/StoryText.visible_ratio = 0.0
	typing = create_tween()
	typing.tween_property($Parchment/StoryText, "visible_ratio", 1.0, 9.0)


func _on_btn_go_pressed() -> void:
	if $Parchment/StoryText.visible_ratio < 1.0:
		typing.kill()
		$Parchment/StoryText.visible_ratio = 1.0
		return
	GameManager.restart()
	get_tree().change_scene_to_file("res://Scenes/Levels/level_01.tscn")
