extends Area2D

# Wind Feather (ขนนกวายุ) - original item of "Nanta and the Wind Feather"
# Picking it up gives +5 score and lets the player run faster and jump higher.

@export var boost_duration : float = 8.0

func _ready() -> void:
	$AnimationPlayer.play("float")


func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("Player"):
		body.wind_boost(boost_duration)
		GameManager.add_score(5)
		AudioManager.powerup_sfx.play()
		var ui = get_tree().current_scene.get_node_or_null("UserInterface")
		if ui:
			ui.alert("ขนนกวายุ! วิ่งเร็ว กระโดดสูง %d วินาที" % boost_duration)
		queue_free()
