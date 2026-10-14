extends Area2D

# Define the next scene to load in the inspector
@export var next_scene : PackedScene
# When true the door stays locked until every enemy in the "Boss" group is defeated
@export var need_boss_defeated : bool = false

# Load next level scene when player collide with level finish door.
func _on_body_entered(body):
	if body.is_in_group("Player") && next_scene != null:
		if need_boss_defeated and _boss_alive():
			var ui = get_tree().current_scene.get_node_or_null("UserInterface")
			if ui:
				ui.alert("ต้องปราบกัปตันฉลามดำก่อน!")
			return
		AudioManager.level_complete_sfx.play()
		SceneTransition.load_scene(next_scene)

func _boss_alive() -> bool:
	for boss in get_tree().get_nodes_in_group("Boss"):
		if boss.alive:
			return true
	return false
