var boot = function(game){
	console.log("%cStarting my awesome game", "color:white; background:red");
};
  
boot.prototype = {
    init: function(gameData){
        this.gameData = gameData;
    },

	preload: function(){
          this.game.load.image("loading","static/assets/loading.png"); 
	},
  	create: function(){
		this.game.state.start("Preload", true, false, this.gameData);
	}
}
