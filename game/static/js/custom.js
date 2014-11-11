
$(document).on("click", ".select_bot", function () {
     var botId = $(this).data('id');
     var botContent = $(this).attr('content');
     $(".modal-content pre").html(botContent);
     $(".modal-title").html($(this).html());
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