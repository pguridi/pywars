var preload = function(game){
    this.players = [];
}

preload.prototype = {
    init: function(gameData){
        this.gameData = gameData;
    },

	preload: function(){ 
          var loadingBar = this.add.sprite(400,240,"loading");
          loadingBar.anchor.setTo(0.5,0.5);
          this.load.setPreloadSprite(loadingBar);

        this.game.load.image('ground', 'static/assets/platform.png');
	    this.game.load.image('background', 'static/assets/bg.png');
        this.game.load.image('cloud1', 'static/assets/cloud1.png');
        this.game.load.image('cloud2', 'static/assets/cloud2.png');
        this.game.load.image('cloud3', 'static/assets/cloud3.png');
	    this.game.load.audio('background_music', 'static/assets/background_music.mp3');

        this.game.load.spritesheet('tank', 'static/assets/tank2.png', 74, 62);
		this.game.load.spritesheet('explosion', 'static/assets/GrenadeExplosion.png', 50, 128);
		this.game.load.image('bullet', 'static/assets/bullet3.png');
		this.game.load.audio('tank_running', 'static/assets/tank_running.mp3');
		this.game.load.audio('tank_firing', 'static/assets/tank_firing.mp3');
		this.game.load.audio('explosion', 'static/assets/explosion.mp3');

		this.game.load.image("gametitle","static/assets/gametitle.png");
		this.game.load.image("play","static/assets/play.png");
		this.game.load.image("gameover","static/assets/gameover.png");

        for (var k in this.gameData['actions']) {
            playerData = this.gameData['actions'][k];
            if (playerData['action'] == 'new_player') {
                var new_player = new Player(game, playerData['name'], playerData['position']);
                new_player.preload();
                this.players.push(new_player);
            }
        }

	},
  	create: function(){
		this.game.state.start("GameTitle", true, false, this.players);
	}
}
