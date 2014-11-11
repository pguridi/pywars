
Level = function(game) {
	this.game = game;
	this.ground = null;
	this.fpsText = null;
};

Level.prototype = {

	preload: function() {
	    this.game.load.image('ground', 'static/assets/platform.png');
	    this.game.load.image('background', 'static/assets/bg_castle.png');
	    //this.game.load.audio('background_music', 'static/assets/background_music.mp3');
	    this.game.time.advancedTiming = true;
	},

	create: function() {
	    this.game.world.setBounds(0, 0, 1900, 600);
        this.game.physics.startSystem(Phaser.Physics.ARCADE);
        this.game.physics.arcade.gravity.y = 980;
        
        this.game.add.tileSprite(0,0, 1900, 600, 'background');
        
        this.ground = this.game.add.tileSprite(0, this.game.world.height - 70, 1900, 70, 'ground');
        this.game.physics.enable(this.ground, Phaser.Physics.ARCADE);
        
        this.ground.body.immovable = true;
        this.ground.body.collideWorldBounds = true;
        this.ground.body.allowGravity = false;
        
        cursors = this.game.input.keyboard.createCursorKeys();
        
		// music
		//this.background_music = this.game.add.audio('background_music', 1, false);
		//this.background_music.volume -= 0.2;
		//this.background_music.play();
        this.fpsText = game.add.text(
            20, 50, '', { font: '16px Arial', fill: '#000' }
        );
	},

	update: function() {
		/*if (game.time.fps !== 0) {
            this.fpsText.setText(game.time.fps + ' FPS');
        }*/
	}

};
