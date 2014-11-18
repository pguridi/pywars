var gameOver = function(game) {
    this.gameData = null;
    this.players = null;
    }

gameOver.prototype = {
	init: function(players, gameData,  msg){
        this.gameData = gameData;
        this.players = players;
        if (msg != 'Draw') {
            this.msg = "Winner: " + msg;
        } else {
            this.msg = msg;
        }
	},
  	create: function(){
  		//var gameOverTitle = this.game.add.sprite(160,80,"gameover");
        this.end_text = game.add.text(200, 200, '', { fontSize: '40px', fill: '#ffffff' });
        this.end_text.text = this.msg;

		//gameOverTitle.anchor.setTo(0.5,0.5);
		var playButton = this.game.add.button(160,320,"play",this.playTheGame,this);
		playButton.anchor.setTo(0.5,0.5);
	},
	playTheGame: function(){
        //this.end_text.destroy();
        this.game.state.start("TheGame", true, false, this.players);
	}
}
