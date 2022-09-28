$(function() {
    var answer_elements = $("p.answerRC");
    
    answer_elements.each(function (index, p_element) {
        var classes = $(p_element).attr("class");
        var icon_class = classes.replace("answerRC", "").trim();
        if(icon_class!="mainRCanswer"){
            $("<img class='svg-icon' src='/static/images/risk_kit/"+icon_class+".svg alt='"+icon_class+" icon'>").prependTo(p_element);
        }
    });
});