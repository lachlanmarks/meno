$(function() {
    var input = $('#title-input');

    input.focus(function() {
        $(this).val('');
    }).blur(function() {
        var el = $(this);

        /* use the elements title attribute to store the 
         *             default text - or the new HTML5 standard of using
         *                         the 'data-' prefix i.e.: data-default="some default" */
        if(el.val() == '')
        el.val(el.attr('title'));
    });
});
