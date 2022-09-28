$(function() {
  $('#country').on('change', refreshMap);
  var test_checkboxes = $("input[name^='testing_']");
  test_checkboxes.on('change', refreshMap);
});

/* refreshMap, first filters locations then refreshes map with selected country */
function refreshMap() {
  filterLocations();
  getCountryMap();
}

/* Resets country to initial selection and unchecks filters for testing type */
function resetMap() {
  $("#country").val(init_country);
  $("input[name^='testing_']").prop('checked', false);
  refreshMap();
}

/* Filters locations by checked filters for testing */
function filterLocations() {
  // console.log($(this).is(":checked"));
  locations = (!$("input[name='testing_hiv']").is(":checked") &&
  !$("input[name='testing_hepc']").is(":checked") &&
  !$("input[name='testing_sti']").is(":checked")) ? all_locations : all_locations.filter(function(loc){
    return loc.testing_hiv==$("input[name='testing_hiv']").is(":checked") &&
        loc.testing_hepc==$("input[name='testing_hepc']").is(":checked") &&
        loc.testing_sti==$("input[name='testing_sti']").is(":checked");
  });

}

/* Draw map zooming to country selected (zoom is adapted to country's size) */
function getCountryMap() {
    $.get( "https://maps.googleapis.com/maps/api/geocode/json", { address: $('#country option:selected').val(), key: "AIzaSyCTAmGyFwXGue900TzQIBxh9Q9m_XE6bDc" } )
        .done(function( data ) {
          if(data){
              var geom = data["results"][0]["geometry"];
              var northeast = geom["bounds"]["northeast"];
              var southwest = geom["bounds"]["southwest"];
              var zoom = (Math.abs((southwest["lng"]-northeast["lng"])*(southwest["lat"]-northeast["lat"]))>165?5:6)
              var coords = geom["location"];
              testFinderMap(coords["lat"], coords["lng"], zoom);
            }
          });
}

/* Draw map zooming to specific coordinates */
function testFinderMap(x,y,zoom) {
    var country = {lat: x, lng: y};
    var map = new google.maps.Map(document.getElementById('map'), {
      zoom: zoom,
      center: country,
      mapTypeControl: false,
      streetViewControl: false,
      styles: [
        {elementType: 'geometry', stylers: [{color: '#e5e5e5'}]},
        {elementType: 'labels.text.stroke', stylers: [{color: '#e5e5e5'}]},
        {elementType: 'labels.text.fill', stylers: [{color: '#746855'}]},
        {
          featureType: 'administrative.locality',
          elementType: 'labels.text.fill',
          stylers: [{color: '#d59563'}]
        },
        {
          featureType: 'poi',
          elementType: 'labels.text.fill',
          stylers: [{color: '#d59563'}]
        },
        {
          featureType: 'poi.park',
          elementType: 'geometry',
          stylers: [{color: '#263c3f'}]
        },
        {
          featureType: 'poi.park',
          elementType: 'labels.text.fill',
          stylers: [{color: '#6b9a76'}]
        },
        {
          featureType: 'road',
          elementType: 'geometry',
          stylers: [{color: '#38414e'}]
        },
        {
          featureType: 'road',
          elementType: 'geometry.stroke',
          stylers: [{color: '#212a37'}]
        },
        {
          featureType: 'road',
          elementType: 'labels.text.fill',
          stylers: [{color: '#9ca5b3'}]
        },
        {
          featureType: 'road.highway',
          elementType: 'geometry',
          stylers: [{color: '#746855'}]
        },
        {
          featureType: 'road.highway',
          elementType: 'geometry.stroke',
          stylers: [{color: '#1f2835'}]
        },
        {
          featureType: 'road.highway',
          elementType: 'labels.text.fill',
          stylers: [{color: '#f3d19c'}]
        },
        {
          featureType: 'transit',
          elementType: 'geometry',
          stylers: [{color: '#2f3948'}]
        },
        {
          featureType: 'transit.station',
          elementType: 'labels.text.fill',
          stylers: [{color: '#d59563'}]
        },
        {
          featureType: 'water',
          elementType: 'geometry',
          stylers: [{color: '#455162'}]
        },
        {
          featureType: 'water',
          elementType: 'labels.text.fill',
          stylers: [{color: '#515c6d'}]
        },
        {
          featureType: 'water',
          elementType: 'labels.text.stroke',
          stylers: [{color: '#17263c'}]
        }
      ]

    });
    var infoWin = new google.maps.InfoWindow();
    // Add some markers to the map.
    // Note: The code uses the JavaScript Array.prototype.map() method to
    // create an array of markers based on a given "locations" array.
    // The map() method here has nothing to do with the Google Maps API.
    var markers = locations.map(function(location, i) {
      var marker = new google.maps.Marker({
        position: location,
      icon: 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|c3d045'
      });
      google.maps.event.addListener(marker, 'click', function(evt) {
        infoWin.setContent(location.info);
        infoWin.open(map, marker);
      })
      return marker;
    });

    var mcOptions = {
              //imagePath: 'https://googlemaps.github.io/js-marker-clusterer/images/m',
            styles:[{

            url: "http://test.hivedu.gr/sites/default/files/inline-images/mgreen.png",
                  width: 53,
                  height:53,
                  fontFamily:"Verdana",
                  textSize:12,
                  textColor: "#1F87B5"
            }]}
    // markerCluster.setMarkers(markers);
    // Add a marker clusterer to manage the markers.
    var markerCluster = new MarkerClusterer(map, markers, mcOptions);
        google.maps.event.addDomListener(document.getElementById("reset"), 'click', resetMap);
        //// Old function for reset
      //   function() {
      //     map.setCenter(country);
      //     map.setZoom(8);
      // }
  }


// ]]>

