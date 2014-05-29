// google maps javascript

$(function() {
	initialize_map();
});

function initialize_map() {
  var myOptions = {
      zoom: 14,
      center: new google.maps.LatLng(-37.8136, 144.9631),
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };

    var map = new google.maps.Map(document.getElementById('map_canvas'), myOptions);
    var geocoder = new google.maps.Geocoder();

    var address_str = document.getElementById('profile-location').innerHTML;

    var request = {
      address: address_str
    };
    geocoder.geocode(request, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        var marker = new google.maps.Marker({
          map: map,
          position: results[0].geometry.location
        });
        map.panTo(marker.getPosition());
      } else {
        window.console.log('failed to geocode address: ' + status);
      }
    });
}
