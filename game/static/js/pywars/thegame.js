var theGame = function(game){
	this.game = game;
    this.ground = null;
    this.players = null;
}

function verifyTurnEnd(player) {
    if (player.busy == true) {
        //console.log("player busy");
        return
    } else {
        current_turn = null;
        clearInterval(this.turnEndTimer);
    }
}

theGame.prototype = {
    init: function(players){
        this.players = players;
        this.turnEndTimer = null;
    },

    turnsTimer: function() {
        if (gameData['actions'].length > 0) {
            if (current_turn != null) {
                return;
            }
            current_turn = gameData['actions'].shift();
            if (current_turn['action'] == 'make_move') {
                player = this.getPlayer(current_turn['player']);
                game.camera.follow(player.sprite);
                
                player.move(current_turn['position']);
                this.turnEndTimer = setInterval(function () {verifyTurnEnd(player)}, 500);
            } else if (current_turn['action'] == 'make_shoot') {
                player = this.getPlayer(current_turn['player']);
                game.camera.follow(player.sprite);
                
                player.busy = true;
                /*game.time.events.add(Phaser.Timer.SECOND * 2, player.shoot, this, current_turn['speed'], 
                    current_turn['angle']);*/
                
                /*setTimeout(function () {player.shoot(current_turn['speed'], 
                    current_turn['angle'])}, 2000);*/
                
                player.shoot(current_turn['speed'], current_turn['angle']);
                this.turnEndTimer = setInterval(function () {verifyTurnEnd(player)}, 500);
            } else if (current_turn['action'] == 'make_healthy') {
                console.log(current_turn);
                player = this.getPlayer(current_turn['player']);
                player.health = current_turn["health_value"];
                current_turn = null;
            } else if (current_turn['action'] == 'result') {
                if (current_turn['draw'] == true) {
                    this.game.state.start("GameOver",true,false,'Draw');
                } else if (current_turn['winner'] != null) {
                    this.game.state.start("GameOver",true,false, gameData, current_turn['winner']);
                }
            } else {
                console.log("turn action: " + current_turn['action']);
                current_turn = null;
            }
        } else {
            console.log("end");
            game.time.events.remove(gameTimer)
        }
    },

    getPlayer: function(username) {
        for (i = 0; i < this.players.length; i++) {
            if (this.players[i].username == username) {
                return this.players[i];
            }
        }
        return;
    },

  	create: function(){
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
		this.background_music = this.game.add.audio('background_music', 1, false);
		this.background_music.volume -= 0.2;
		this.background_music.play();
        this.fpsText = game.add.text(
            20, 50, '', { font: '16px Arial', fill: '#000' }
        );
        
        for (playerK in this.players) {
            this.players[playerK].create(this.ground);
        }
        gameTimer = game.time.events.loop(Phaser.Timer.SECOND, this.turnsTimer, this);
	},

    update: function() {
        for (i = 0; i < this.players.length; i++) {
               game.physics.arcade.collide(this.players[i].sprite, this.ground);
               this.players[i].update();
            }
    }

}
