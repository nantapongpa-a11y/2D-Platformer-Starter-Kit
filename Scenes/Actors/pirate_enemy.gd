extends Enemy

# Pirate enemies of Captain Go: pirate grunt, pirate crab, skeleton pirate and
# the boss Captain Black Shark. Plays the walk animation, and when a cannonball
# scene is set (boss) it fires cannonballs at the player.

@export var cannonball_scene : PackedScene
@export var shoot_interval : float = 2.2
@export var shoot_range : float = 700.0
@export var bonus_score : int = 0
@export var is_boss : bool = false

var shoot_timer : float = 1.5

func _ready() -> void:
	super._ready()
	if is_boss:
		add_to_group("Boss")
	$Sprite/AnimateSprite.play("walk")
	state_changed.connect(_on_state_changed)
	died.connect(_on_died)


func _on_state_changed(new_state: Enemy.State) -> void:
	var anim : AnimatedSprite2D = $Sprite/AnimateSprite
	if new_state == Enemy.State.IDLE:
		anim.speed_scale = 0.3
	elif new_state == Enemy.State.CHASE:
		anim.speed_scale = 1.6
	else:
		anim.speed_scale = 1.0


func _physics_process(delta: float) -> void:
	super._physics_process(delta)
	if cannonball_scene == null or not alive or GameManager.player == null:
		return
	var target : Node2D = GameManager.player
	if global_position.distance_to(target.global_position) > shoot_range:
		return
	shoot_timer -= delta
	if shoot_timer <= 0.0:
		shoot_timer = shoot_interval
		_fire_cannonball(target)


func _fire_cannonball(target: Node2D) -> void:
	var side = 1.0 if target.global_position.x > global_position.x else -1.0
	var ball = cannonball_scene.instantiate()
	get_parent().add_child(ball)
	ball.global_position = global_position + Vector2(60 * side, -110)
	ball.shoot(Vector2(side, -0.5).normalized(), randf_range(380, 600), 4.0)
	AudioManager.cannon_sfx.play()


func _on_died() -> void:
	if bonus_score > 0:
		GameManager.add_score(bonus_score)
