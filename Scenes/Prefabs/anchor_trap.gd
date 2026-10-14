extends Node2D

# Swinging anchor trap. The AnimationPlayer swings the Pivot left and right.
# A random start time makes every anchor swing differently.

func _ready() -> void:
	var anim : AnimationPlayer = $AnimationPlayer
	anim.play("swing")
	anim.seek(randf() * anim.current_animation_length, true)
