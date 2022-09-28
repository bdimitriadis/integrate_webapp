// all <a> tags containing a certain rel=""
$(function() {
    $("a[rel~='keep-params']").click(function(e) {
        e.preventDefault();

        var params = window.location.search,
            dest = $(this).attr('href') + params;

        target = $(this).attr('target');

        // in my experience, a short timeout has helped overcome browser bugs
        window.setTimeout(function() {
            if(target) {
                window.open(dest, target)
            } else {
                window.location.href = dest;
            }
        }, 100);
    });
});
