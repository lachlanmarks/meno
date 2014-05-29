// jqte_hookup

$(function () {
    $('textarea').jqte();
    $("#post-question-submit").click(function() {
       $('textarea').jqte({"status" : false});
    //   var some_text =  $('textarea').text();
	//   $('#text-area-render').text(some_text);
    //   $('textarea').jqte({"status" : true});
    });
});
