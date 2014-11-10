Player = function(game, username, position) {

	this.game = game;
	this.username = username;
	this.player_position = position[0] * 10;
	this.sprite = null;
	this.cursors = null;
	this.bulletPool = null;
	this.move_position = null;
	this.busy = false;
	this.bullet = null;
	this.NUMBER_OF_BULLETS = 50;
	this.GRAVITY = 980;
	
};

Player.prototype = {

	preload: function () {
		this.game.load.spritesheet('tank', 'static/assets/tank2.png', 74, 62);
		this.game.load.spritesheet('explosion', 'static/assets/GrenadeExplosion.png', 50, 128);
		this.game.load.image('bullet', 'static/assets/bullet3.png');
		this.game.load.audio('tank_running', 'static/assets/tank_running.mp3');
		this.game.load.audio('tank_firing', 'static/assets/tank_firing.mp3');
		this.game.load.audio('explosion', 'static/assets/explosion.mp3');
	},

	create: function () {
		this.sprite = game.add.sprite(74, game.world.height - 150, 'tank');
		this.moving_sound = game.add.audio('tank_running', 1, false);
		this.firing_sound = game.add.audio('tank_firing', 1, false);
		this.explosion_sound = game.add.audio('explosion', 1, false);
		this.game.physics.arcade.enable(this.sprite);
		
		this.game.physics.arcade.gravity.y = this.GRAVITY;
		this.sprite.position.x = this.player_position;
		
		if (this.player_position < 400) {
		    // is the left player
		    this.health_status = game.add.text(16, 16, this.username + ': 0', { fontSize: '32px', fill: '#ffffff' });
		    this.sprite.frame = 6;
		} else {
		    // is the right player
		    this.health_status = game.add.text(600, 16, this.username + ': 0', { fontSize: '32px', fill: '#ffffff' });
		    this.sprite.frame = 8;
		}

	    this.sprite.body.gravity.y = 300;
        this.sprite.body.collideWorldBounds = true;

        //  Our two animations, walking left and right.
        this.sprite.animations.add('left', [0, 1, 2, 3], 10, true);
        this.sprite.animations.add('right', [4, 5, 6, 7], 10, true);
        
        // Create a group for explosions
        this.explosionGroup = this.game.add.group();
        
        this.bulletPool = this.game.add.group();
        for(var i = 0; i < this.NUMBER_OF_BULLETS; i++) {
            // Create each bullet and add it to the group.
            var bullet = this.game.add.sprite(0, 0, 'bullet');
            this.bulletPool.add(bullet);

            // Set its pivot point to the center of the bullet
            bullet.anchor.setTo(0.5, 0.5);

            // Enable physics on the bullet
            this.game.physics.enable(bullet, Phaser.Physics.ARCADE);

            // Set its initial state to "dead".
            bullet.kill();
        }
	},

	update_shooting: function() {
	    console.log(this.bullet.position);
	    this.bulletPool.forEachAlive(function(bullet) {
            bullet.rotation = Math.atan2(bullet.body.velocity.y, bullet.body.velocity.x);
        }, this);
        if (this.bullet.position.y > 600) {
	        // if shooting
		    // Create an explosion
            this.getExplosion(this.bullet.x, this.bullet.y - 30);

            // Kill the bullet
            this.bullet.kill();
            this.bullet = null
        }
	},
	
	update: function() {
	    if (game.input.activePointer.isDown) {
            this.shoot(80, 55);
        }
	    if (this.move_position != null) {
	        //console.log("activity_move");
	        // means we are moving
		    if (this.sprite.body.velocity.x != 0){
		        // we are moving
		        if (this.move_position == parseInt(this.sprite.position.x)) {
		            // not moving anymore
		            this.moving_sound.stop();
		            if (this.sprite.body.position.x < 400) {
		               // left player
		               this.sprite.frame = 4;
		            } else {
		               this.sprite.frame = 0;
		            }
		            this.sprite.body.velocity.x = 0;
		            this.move_position = null;
		            this.sprite.animations.stop();
		            this.busy = false;
		        }
		    }
		    return;
		} else if (this.bullet != null) {
		    // we are shooting
		    this.update_shooting();
		}
		
	},
	
	move: function(move_position) {
	    this.move_position = move_position[0] * 10;
	    this.busy = true;
	    this.moving_sound.play('',0,1,false);
	    if (this.move_position > this.sprite.position.x) {
	        // move to the right
	        console.log(this.username + " moving to the right");
	        this.sprite.body.velocity.x = 60;
	        this.sprite.animations.play("right");
	    } else {
	        console.log(this.username + " moving to the left");
	        this.sprite.body.velocity.x = -60;
	        this.sprite.animations.play("left");
	    }
        
	},
	
	shoot: function(speed, angle) {
	    this.busy = true;
	    this.bullet = this.bulletPool.getFirstDead();
	    console.log(this.username + " shooting" + angle + " " + speed);
	        
	    if (this.bullet === null || this.bullet === undefined) return;
	    speed = speed * 10;
    	angle = -1 * angle;
	    
	    // Revive the bullet
        // This makes the bullet "alive"
	    this.bullet.revive();
	    
	    this.bullet.checkWorldBounds = true;
        this.bullet.outOfBoundsKill = true;

        // Set the bullet position to the gun position.
        this.bullet.reset(this.sprite.position.x, 600);
        this.bullet.rotation = angle * Math.PI / 180;

        // Shoot it in the right direction
        this.bullet.body.velocity.x = Math.cos(this.bullet.rotation) * speed;
        this.bullet.body.velocity.y = Math.sin(this.bullet.rotation) * speed;
        this.firing_sound.play();
	},
	
	getExplosion: function(x, y) {
        // Get the first dead explosion from the explosionGroup
        var explosion = this.explosionGroup.getFirstDead();
        

        // If there aren't any available, create a new one
        if (explosion === null) {
            explosion = this.game.add.sprite(0, 0, 'explosion');
            explosion.anchor.setTo(0.5, 0.5);

            // Add an animation for the explosion that kills the sprite when the
            // animation is complete
            var animation = explosion.animations.add('boom', [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16], 20, false);
            animation.killOnComplete = true;

            // Add the explosion sprite to the group
            this.explosionGroup.add(explosion);
        }

        // Revive the explosion (set it's alive property to true)
        // You can also define a onRevived event handler in your explosion objects
        // to do stuff when they are revived.
        explosion.revive();

        // Move the explosion to the given coordinates
        explosion.x = x;
        explosion.y = y;

        // Set rotation of the explosion at random for a little variety
        //explosion.angle = this.game.rnd.integerInRange(0, 360);

        // Play the animation
        explosion.animations.play('boom');
        //this.explosion_sound.play();

        // Return the explosion itself in case we want to do anything else with it
        return explosion;
    }

};
