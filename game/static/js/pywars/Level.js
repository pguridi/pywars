
Level = function(game) {
	this.game = game;
	this.fpsText = null;
};

Level.prototype = {

	preload: function() {
	    this.game.load.image('background', 'static/assets/background2.png');
	    this.game.load.audio('background_music', 'static/assets/background_music.mp3');
	    game.time.advancedTiming = true;
	},

	create: function() {
        this.game.physics.startSystem(Phaser.Physics.ARCADE);
		// add background for this level
		this.game.add.tileSprite(0,0, 800, 600, 'background');
		this.background_music = game.add.audio('background_music', 1, false);
		this.background_music.volume -= 0.2;
		this.background_music.play();
        this.fpsText = game.add.text(
            20, 50, '', { font: '16px Arial', fill: '#000' }
        );
	},

	update: function() {
		if (game.time.fps !== 0) {
            this.fpsText.setText(game.time.fps + ' FPS');
        }
	}

};
