// hidden_list

$(function () {
	size_list = $('#hidden-list > div').size();
    	x = 5;
    	$('#hidden-list > div:lt('+x+')').show();
    	$('#display-more').click(function () {
        	x= (x + 5 <= size_list) ? x + 5 : size_list;
        	$('#hidden-list > div:lt('+x+')').show();
        	if(x == size_list){
            		$('#display-more').hide();
			$('#load-more').css('display', 'inline-block');
        	}
    	});
});
