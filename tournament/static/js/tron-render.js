//set cancas size:
function buildGrids(gridPixelSize, color, gap){
    context.lineWidth = gap;
    context.strokeStyle = color;
    // horizontal grid lines
    for(var i = 0; i <= canvas.height; i = i + gridPixelSize){
        context.beginPath();
        context.moveTo(0, i);
        context.lineTo(canvas.width, i);
        context.lineWidth = gap;
        context.closePath();
        context.stroke();
    }
    // vertical grid lines
    for(var j = 0; j <= canvas.width; j = j + gridPixelSize){
        context.beginPath();
        context.moveTo(j, 0);
        context.lineTo(j, canvas.height);
        context.lineWidth = gap;
        context.closePath();
        context.stroke();
    }
}


//INITIAL DATA
canvas = document.getElementById("the-game");
context = $('#the-game')[0].getContext("2d");
//colors
color_player1 = "orange";
color_player2 = "cyan";
grid_line_color = "lightgrey";
//draw grid

game_start = function on(data ,canvas_id) {
    
    canvas_id = '#' + canvas_id;
    $(canvas_id).attr('width', (data.width - 1) * 10);
    $(canvas_id).attr('height', (data.height - 1) * 10);
    buildGrids(10,  grid_line_color , 0.2 );
    game = true;
    
    player1 = {
        name: data.players[0],
        color: color_player1,
        color_cycle: "white",
        position: [ p1_x, p1_y],
        prev_pos: [ undefined, undefined],
    };
    player2 = {
        name: data.players[1],
        color: color_player2,
        color_cycle: "white",
        position: [ p2_x, p2_y],
        prev_pos: [ undefined, undefined],
    };
    
    var p1_x = data.moves[0].x *10;
    var p1_y = data.moves[0].y *10;
    var p2_x = data.moves[1].x *10;
    var p2_y = data.moves[1].y *10;

    //test icon cycle
    /*var logoImage = new Image(); 
    logoImage.src = './static/media/light2.gif';
    context.drawImage(logoImage, p1_x, p1_y);*/
    
    function draw(player, x , y){
        //console.log("darw: " + x + "-" + y);
        x = x *10;
        y = y *10;
        context.beginPath();
        context.moveTo(player.position[0], player.position[1] );
        context.lineTo(x , y);
        context.lineWidth = 3;
        context.closePath();
        context.strokeStyle = player.color_cycle;
        context.stroke();

        context.beginPath()
        context.moveTo(player.prev_pos[0], player.prev_pos[1])
        context.lineTo(player.position[0], player.position[1])
        context.lineWidth = 3;
        context.closePath();
        context.strokeStyle = player.color;
        context.stroke();

        player.prev_pos = [player.position[0], player.position[1]]
        player.position = [x, y];

        //context.fillStyle = 'green' ;
        //context.fill();
    }

    var i = 2;
    loop = function() {
        //console.log(delay)
        if (i >= data.moves.length - 1){
        gameover();
        return;
        }
        x = parseInt(data.moves[i].x);
        y = parseInt(data.moves[i].y);
        x2 = parseInt(data.moves[i+1].x);
        y2 = parseInt(data.moves[i+1].y);
        draw(player1, x,y);
        draw(player2, x2,y2);
        i += 2;
    };

    //speed of the game
    Object.prototype.getKey = function(value){
      for(var key in this){
        if(this[key] instanceof Array && this[key].indexOf(value) >= 0){
          return key;
        }
      }
      return null;
    };

    keys = {
      up: [38, 87, 107],
      down: [40, 83, 109],
      left: [37, 65],
      right: [39, 68],
      replay: [13, 32]
    };

    var delay = 100;
    var maxD = 10000;
    var minD = 0;

    addEventListener("keydown", function (e) {
        lastKey = keys.getKey(e.keyCode);
        //console.log(e.keyCode);
        if (['up'].indexOf(lastKey) >= 0  && delay > minD ) {
           delay -= 100;
           console.log(delay);
        } 
        else if (['down'].indexOf(lastKey) >= 0  && delay < maxD ) {
           delay += 100;
        } 
        else if (['replay'].indexOf(lastKey) >= 0  && game == false ) {
           replayMatch();
           //console.log(delay);
        } 
    }, false);

    $('#button_replay').click(function() {
        replayMatch();
    });

    //game speed 
    setInterval(loop, delay); 
    
    
    //replay the match
    replayMatch = function() {
        game = true;
        $('#button_replay').hide();
        context.clearRect(0, 0, canvas.width, canvas.height);
        i = 0; j = 1; // reset the array conts
        //set initial position
        player1.position = [ p1_x, p1_y];
        player2.position = [ p2_x, p2_y];
        buildGrids(10, grid_line_color , 0.2 );
    }

    //end game
    gameover = function() {
    game = false;
    $('#button_replay').show();
    context.fillStyle = '#FFF';
    context.font = (canvas.height / 15) + 'px FixedsysExcelsior301Regular';
    context.textAlign = 'center';
    
    
    context.fillText('GAME OVER ', canvas.width/2, canvas.height/2);
    
    if (data.result.winner == undefined ){
        msg = 'TIE!!';
    } else{
        msg = data.result.winner + ' WINS!';
    }
        context.fillText( msg , canvas.width/2, canvas.height/2 + 50); 
    };
}
