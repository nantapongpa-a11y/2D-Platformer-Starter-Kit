extends Area2D

# Checkpoint flag: when Captain Go touches it, he respawns here after falling into the sea.

@export var flag_on : Texture2D
var active := false

func _on_body_entered(body: Node2D) -> void:
	if active or not body.is_in_group("Player"):
		return
	active = true
	body.spawn_point = global_position + Vector2(0, -4)
	$Flag.texture = flag_on
	AudioManager.checkpoint_sfx.play()
	var tween = create_tween()
	tween.tween_property($Flag, "scale", Vector2(1.3, 1.3), 0.12)
	tween.tween_property($Flag, "scale", Vector2.ONE, 0.2)
	var ui = get_tree().current_scene.get_node_or_null("UserInterface")
	if ui:
		ui.alert("เช็กพอยต์! เกิดใหม่ที่ธงนี้")
