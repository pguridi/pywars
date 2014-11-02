
$(document).on("click", ".select_bot", function () {
     var botId = $(this).data('id');
     var botContent = $(this).attr('content');
     $(".modal-content pre").html(botContent);
     $(".modal-title").html($(this).html());

     // As pointed out in comments,
     // it is superfluous to have to manually call the modal.
     // $('#addBookDialog').modal('show');
});

