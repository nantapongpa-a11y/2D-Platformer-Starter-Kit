extends Area2D


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	get_tree().create_timer(randf_range(0,1)).timeout
	$AnimationPlayer.play("move")


func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("Player"):
		GameManager.add_hp(20)
		var ui = get_tree().current_scene.get_node_or_null("UserInterface")
		if ui:
			ui.alert("น้ำมะพร้าว +20 HP")
		AudioManager.coin_pickup_sfx.play()
		queue_free()
