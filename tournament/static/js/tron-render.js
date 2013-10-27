//INITIAL DATA
canvas = document.getElementById("the-game");
context = $('#the-game')[0].getContext("2d");
delay = 10;
//colors
color_player1 = "orange";
color_player2 = "cyan";
grid_line_color = "lightgrey";
var refreshIntervalId = null;

function build_grid(gridPixelSize, color, width){
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.lineWidth = width;
    context.strokeStyle = color;
    // horizontal grid lines
    for(var i = 0; i <= canvas.height; i = i + gridPixelSize) {
        context.beginPath();
        context.moveTo(0, i);
        context.lineTo(canvas.width, i);
        context.stroke();
    }
    // vertical grid lines
    for(var j = 0; j <= canvas.width; j = j + gridPixelSize) {
        context.beginPath();
        context.moveTo(j, 0);
        context.lineTo(j, canvas.height);
        context.stroke();
    }
}

function request_match(match_id) {
    jQuery.ajax({
          url: '/get-match/' + match_id,
          dataType: 'json',
          success: function(data, status){
              game_start(data, '#the-game');
          },
    });
}

function game_start(data ,canvas_id) {
    clearInterval(refreshIntervalId);

    $(canvas_id).attr('width', (data.width - 1) * 10);
    $(canvas_id).attr('height', (data.height - 1) * 10);
    build_grid(10, grid_line_color, 0.2);
    
    player1 = {
        name: data.players[0],
        color: color_player1,
        color_cycle: "white",
        position: [undefined, undefined],
        prev_pos: [undefined, undefined],
    };

    player2 = {
        name: data.players[1],
        color: color_player2,
        color_cycle: "white",
        position: [undefined, undefined],
        prev_pos: [undefined, undefined],
    };

    players = {};
    players[player1.name] = player1;
    players[player2.name] = player2;

    $('#p1_img').css("background", color_player1);
    $('#p2_img').css("background", color_player2);
    $('#player1').text(player1.name);
    $('#player2').text(player2.name);

    function draw(player, x , y){
        x = x * 10;
        y = y * 10;
        context.lineWidth = 3;

        context.beginPath();
        context.moveTo(player.position[0], player.position[1]);
        context.lineTo(x, y);
        context.strokeStyle = player.color_cycle;
        context.stroke();

        context.beginPath()
        context.moveTo(player.prev_pos[0], player.prev_pos[1])
        context.lineTo(player.position[0], player.position[1])
        context.strokeStyle = player.color;
        context.stroke();

        player.prev_pos = [player.position[0], player.position[1]]
        player.position = [x, y];
    }

    move_index = 0;
    function loop() {
        if(move_index >= data.moves.length) {
            gameover();
            return;
        }
        move = data.moves[move_index];
        move_index += 1;
        x = parseInt(move.x);
        y = parseInt(move.y);
        draw(players[move.player], x, y);
    };

    //replay the match
    $('#button_replay').click(function() {
        $('#button_replay').hide();
        game_start(data, canvas_id);
    });

    //end game
    function gameover() {
        function shadowed_text(msg, offset) {
            offset = typeof offset !== 'undefined' ? offset : 0;
            context.fillStyle = 'black';
            context.fillText(msg, canvas.width/2 + 4, canvas.height/2 + offset + 4);
            context.fillStyle = 'white';
            context.fillText(msg, canvas.width/2, canvas.height/2 + offset);
        }
        clearInterval(refreshIntervalId);
        $('#button_replay').show();
        context.font = (canvas.height / 10) + 'px FixedsysExcelsior301Regular';
        context.textAlign = 'center';
        shadowed_text('GAME OVER');
        if (data.result.winner == undefined ) {
            msg = 'TIE!!';
        } else {
            msg = data.result.winner + ' WINS!';
        }
        shadowed_text(msg, offset=50);
    };

    refreshIntervalId = setInterval(loop, delay);
}
