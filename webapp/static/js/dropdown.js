// dropdown

$(function() {
	$('.dropdown').click(function(e) {
    //		e.preventDefault();
		e.stopPropagation();
	});
	$('.dropdown-parent').click(function(e) {
    	e.preventDefault();
		e.stopPropagation();
	});
	$('#dropdown-parent-1').click(function() {
		_toggle_dropdown_1();
		if ($('#dropdown-2').is(':visible')) {
			_toggle_dropdown_2();
		}
	});
	$('#dropdown-parent-2').click(function() {
    		_toggle_dropdown_2();
		if ($('#dropdown-1').is(':visible')) {
			_toggle_dropdown_1();
		}
	});
	$(document).click(function() {
   		$('.dropdown').hide(); 
	});
});
function _toggle_dropdown_1() {
	$('#dropdown-1').toggle();
	$('#dropdown-parent-1').toggleClass('active');
}
function _toggle_dropdown_2() {
	$('#dropdown-2').toggle();
	$('#dropdown-parent-2').toggleClass('active');
}
