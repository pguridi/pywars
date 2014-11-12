
$(document).on("click", ".select_bot", function () {
     var botId = $(this).data('id');
     var botContent = $(this).attr('content');
     $("#bot-code .modal-content pre").html(botContent);
     $("#bot-code .modal-title").html($(this).html());
});

$(document).ready(function() {
    if ($('#div-playlist').length > 0 ) {
        $.ajax({
          url: "/get_playlist",
        }).done(function(data) {
            var JsonData = data.data || false;
            if (JsonData.length === 0 || !JsonData){
                $('.playlist-box').hide();
                return;
            }
            var list = $('<ul>');
            $.each(JsonData, function(i, d){
                var link = $('<li><a href="/' + d.pk + '">'+ d.fields.creation_date +  '<a/><li/>' )[0];
                list.append( link );
            });
            console.log('html: ' + list);
            $( "#div-playlist" ).append( list );
        }).fail(function(){
            $('.playlist-box').hide();
        });
    }
});

function updateBots(){
    $( ".bot-pending" ).each(function( index ) {
      var $item = $( this );
      var refreshBotList = $.get( "get_bot_status/" + $item.attr('id') , function(data) {
        if (data['success']) {
          if (data['status'] === 'READY') {
            $item.removeClass('list-group-item-warning');
            $item.addClass('list-group-item-success');
            $item.attr('title', data['status']);
          }
          if (data['status'] === 'INVALID') {
            $item.removeClass('list-group-item-warning');
            $item.addClass('list-group-item-danger');
            $item.attr('content', '<span class="color-red">' + data['reason'] +
                       '</span><br>' + '<span class="color-black">' + data['code'] + '</span>');
            $item.attr('title', data['status']);
          }
        }
      }).fail(function() {
        console.log("Failed to get bot");
      });

    });
}

$(document).ready(function() {
    if ($('.bot-pending').length > 0 ) {
        setInterval( function() { updateBots(); }, 5000);
    }
});