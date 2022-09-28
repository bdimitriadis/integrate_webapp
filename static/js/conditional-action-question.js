$(function() {
    toggle_which_action();
    $("input[name='take_action']").change(function () {
        toggle_which_action();
    })
});

function toggle_which_action() {
    if($("input[name='take_action']:checked").val() == "1"){
            $("input[name='which_action']").prop("checked", false);
            $("span.which_action, label[for='which_action'], ul#which_action").addClass("disabled-question");
        } else {
            $("span.which_action, label[for='which_action'], ul#which_action").removeClass("disabled-question");
        }
}