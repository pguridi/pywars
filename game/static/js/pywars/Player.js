Player = function(game, username, position) {

	this.game = game;
	this.username = name;
	this.player_position = position;
	this.sprite = null;
	this.cursors = null;
	
};

Player.prototype = {

	preload: function () {
		this.game.load.spritesheet('tank', 'static/assets/tanks.png', 74, 62);
	},

	create: function () {
		this.sprite = game.add.sprite(74, game.world.height - 150, 'tank');
		
		this.game.physics.arcade.enable(this.sprite);
		
		console.log("position: " + this.player_position);
		this.sprite.position.x = this.player_position;
		
		if (this.player_position < 400) {
		    // is the left player
		    console.log("Is left player");
		    score1Text = game.add.text(16, 16, 'player1: 0', { fontSize: '32px', fill: '#000' });
		    this.sprite.frame = 6;
		} else {
		    // is the right player
		    console.log("Is right player");
		    score1Text = game.add.text(16, 16, 'player2: 0', { fontSize: '32px', fill: '#000' });
		    this.sprite.frame = 8;
		}

	    this.sprite.body.gravity.y = 300;
        this.sprite.body.collideWorldBounds = true;

        //  Our two animations, walking left and right.
        this.sprite.animations.add('left', [0, 1, 2, 3], 10, true);
        this.sprite.animations.add('right', [4, 5, 6, 7], 10, true);
	},

	update: function() {
		this.sprite.body.velocity.x = 0;
	}

};
