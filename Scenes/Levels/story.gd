extends Node2D

# Story screen shown before Level 1 of "Nanta and the Wind Feather"

func _ready() -> void:
	$Hero/AnimationPlayer.play("Idle")


func _on_btn_go_pressed() -> void:
	GameManager.restart()
	get_tree().change_scene_to_file("res://Scenes/Levels/level_01.tscn")
