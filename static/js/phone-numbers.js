$(function() {
    var add_btns = $(".btn-add-phone");
    var remove_btns = $(".btn-remove-phone");

    var li_parents = $("[name^='phone_numbers-']").parent();
    li_parents.each(function(index){
        if($(this).children("input").first().val()!=""){
            $(this).show();
        }
    })

    $(li_parents[0]).show();
    // $(li_parents[0]).find(".btn-add-phone").show()



    add_btns.on('click', function () {
        $(this).parent().next("li").show();
        $(this).prop('disabled', true);
    })

    remove_btns.on('click', function () {
        var parent = $(this).parent();
        parent.children("input").first().val("")
        parent.hide();
        parent.prev("ul.errors").hide();
        parent.prev("li").find(".btn-add-phone").prop('disabled', false);
    })
});