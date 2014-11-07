
Level = function(game) {
	this.game = game;
};

Level.prototype = {

	preload: function() {
	    this.game.load.image('background', 'static/assets/background2.png');
	},

	create: function() {
        this.game.physics.startSystem(Phaser.Physics.ARCADE);
		// add background for this level
		this.game.add.tileSprite(0,0, 800, 600, 'background');

	},

	update: function() {
		//
	}

};
