Player = function(game, username, position) {

	this.game = game;
	this.username = username;
	this.player_position = position[0] * 10;
	this.sprite = null;
	this.cursors = null;
	this.bulletPool = null;
	this.NUMBER_OF_BULLETS = 50;
	
};

Player.prototype = {

	preload: function () {
		this.game.load.spritesheet('tank', 'static/assets/tanks.png', 74, 62);
		this.game.load.image('bullet', 'static/assets/bullet.png');
	},

	create: function () {
		this.sprite = game.add.sprite(74, game.world.height - 150, 'tank');
		this.game.physics.arcade.enable(this.sprite);
		this.sprite.position.x = this.player_position;
		
		if (this.player_position < 400) {
		    // is the left player
		    this.health_status = game.add.text(16, 16, this.username + ': 0', { fontSize: '32px', fill: '#ffffff' });
		    this.sprite.frame = 6;
		} else {
		    // is the right player
		    this.health_status = game.add.text(650, 16, this.username + ': 0', { fontSize: '32px', fill: '#ffffff' });
		    this.sprite.frame = 8;
		}

	    this.sprite.body.gravity.y = 300;
        this.sprite.body.collideWorldBounds = true;

        //  Our two animations, walking left and right.
        this.sprite.animations.add('left', [0, 1, 2, 3], 10, true);
        this.sprite.animations.add('right', [4, 5, 6, 7], 10, true);
        
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

	update: function() {
		this.sprite.body.velocity.x = 0;
		if (game.input.activePointer.isDown) {
            this.shoot(100, 90);
        }
	},
	
	shoot: function(bullet_speed, angle) {
	    var bullet = this.bulletPool.getFirstDead();
	    if (bullet === null || bullet === undefined) return;
	    
	    // Revive the bullet
        // This makes the bullet "alive"
	    bullet.revive();
	    
	    bullet.checkWorldBounds = true;
        bullet.outOfBoundsKill = true;

        // Set the bullet position to the gun position.
        bullet.reset(this.sprite.position.x, 0);
        bullet.rotation = angle;

        // Shoot it in the right direction
        bullet.body.velocity.x = Math.cos(angle) * bullet_speed;
        bullet.body.velocity.y = Math.sin(angle) * bullet_speed;
	}

};
