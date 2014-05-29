// dialog

$(window).ready(function() {
    	$('#dialog-open').click(function() {
		_open_dialog();
	});
    	$('#dialog-close').click(function() {
		_close_dialog();
    	});
	$('#shadow').click(function() {
		_close_dialog();
	});
  $('#shadow #dialog').click(function(e) {
    e.stopPropagation();
  });
});
function _open_dialog() {
  //$('#shadow').css('display', 'block');
	$('#shadow').toggle();
	$('body').width($('body').width());
  	$('body').css('overflow', 'hidden');
}
function _close_dialog() {
	$('#shadow').toggle();
	$('body').removeAttr('style');
}
