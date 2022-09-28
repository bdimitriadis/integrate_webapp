$(function() {
    function url_param(name) {
        var results = new RegExp('[\?&]' + name + '=([^&#]*)')
                          .exec(window.location.search);

        return (results !== null) ? results[1] || 0 : 'en';
    }

    var btn_lng = $("button.btn-lng .flag-icon");
    var classes = btn_lng.attr("class");
    var regex = new RegExp("flag-icon-\\S+");
    var flag_class_before = regex.exec(classes);
    var flag_class_after = "flag-icon-"+url_param('lang').replace("en", "gb");

    lang_text = $("."+flag_class_after).parent().text();

    btn_lng.removeClass(flag_class_before).addClass(flag_class_after);
    btn_lng.parent().children("span.btn-lng-txt").text(lang_text);
});