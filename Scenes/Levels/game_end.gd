extends Node2D

# Shared script for the Game Over and You Win screens

func _ready() -> void:
	if has_node("Score"):
		$Score.text = "คะแนนรวม: %d" % GameManager.get_stat("score")
	if has_node("Captain/AnimationPlayer"):
		$Captain/AnimationPlayer.play("Idle")
	var title = $Title
	title.pivot_offset = title.size / 2
	title.scale = Vector2.ZERO
	var tween = create_tween()
	tween.tween_property(title, "scale", Vector2.ONE, 0.8).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)


func _on_btn_play_pressed() -> void:
	GameManager.restart()
	get_tree().change_scene_to_file("res://Scenes/Levels/level_01.tscn")


func _on_btn_menu_pressed() -> void:
	get_tree().change_scene_to_file("res://Scenes/Levels/menu.tscn")
