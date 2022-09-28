$(function() {
  $('.ls-modal').bind("click", function () {   //bind handlers
    // Keep params (i.e. language)
    var params = window.location.search,
        dest = $(this).attr('href') + params;

    var url = $(this).data('target')+params;

    var modal_title = $(this).data('modal-title');

    $("#genericModal .modal-header>.modal-title").text(modal_title)
    $("#genericModal").modal('show').find('.iframe').attr("src", url);
    return false;
  });
});