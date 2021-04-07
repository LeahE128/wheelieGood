function initMap() {
    fetch("/staticBikes").then(response=> {
        return response.json();

    }).then(data => {
//  Creation of map
        const map = new google.maps.Map(document.getElementById("map"), {
            center: {lat: 53.349804, lng: -6.260310},
            zoom: 13,
        });
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const pos = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                };
                var route_dropdown = document.getElementById('start');
                var opt = document.createElement('option');

                opt.value = [pos.lat, pos.lng];
                console.log(pos.lat + "," + pos.lng)
                opt.innerHTML = "User Location";

                route_dropdown.add(opt);
            });
        const directionsRenderer = new google.maps.DirectionsRenderer();
        const directionsService = new google.maps.DirectionsService();

        directionsRenderer.setMap(map);
        directionsRenderer.setPanel(document.getElementById("right-panel"));
        const control = document.getElementById("floating-panel");
        control.style.display = "block";
        map.controls[google.maps.ControlPosition.TOP_CENTER].push(control);

        const onChangeHandler = function () {
            calculateAndDisplayRoute(directionsService, directionsRenderer);
        };
        document
            .getElementById("start")
            .addEventListener("change", onChangeHandler);
        document
            .getElementById("end")
            .addEventListener("change", onChangeHandler);

        let route_select = "<select id='start'>";
        data.forEach(bikes => {

            route_select += "<option value =" + bikes.pos_lat + ',' + bikes.pos_lng + ">" + bikes.name + "</option>";
        })
        route_select += "</select>";
        console.log(route_select)
        document.getElementById("start").innerHTML += route_select;
        document.getElementById("end").innerHTML += route_select;

        var selectedRoute = document.getElementById("start").value;
        console.log(selectedRoute);
    })


      function calculateAndDisplayRoute(directionsService, directionsRenderer) {
        const start = document.getElementById("start").value;
        const end = document.getElementById("end").value;
        directionsService.route(
          {
            origin: start,
            destination: end,
            travelMode: google.maps.TravelMode.DRIVING,
          },
          (response, status) => {
            if (status === "OK") {
              directionsRenderer.setDirections(response);
            } else {
              window.alert("Directions request failed due to " + status);
            }
          }
        );

      }}

