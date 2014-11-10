
Level = function(game) {
	this.game = game;
	this.fpsText = null;
};

Level.prototype = {

	preload: function() {
	    this.game.load.image('background', 'static/assets/background2.png');
	    game.time.advancedTiming = true;
	},

	create: function() {
        this.game.physics.startSystem(Phaser.Physics.ARCADE);
		// add background for this level
		this.game.add.tileSprite(0,0, 800, 600, 'background');
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
