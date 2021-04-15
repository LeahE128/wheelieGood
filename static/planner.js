let hourValue;
let stationValue;
let dayValue;
let bike_stands;


function initMap() {
    fetch("/staticBikes").then(response => {
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
        // const control = document.getElementById("floating-panel");
        // control.innerHTML = "<h2>Directions</h2>";
        // control.style.display = "block";


        const onChangeHandler = function () {
            calculateAndDisplayRoute(directionsService, directionsRenderer);
            document.getElementById("right-panel").innerHTML += "<h5>Text Directions</h5>";
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

        document.getElementById("start").innerHTML += route_select;
        document.getElementById("end").innerHTML += route_select;


        var selectedRoute = document.getElementById("start").value;

        availabilityPrediction();
    })
}


function availabilityPrediction() {
    fetch("/allBikes").then(response => {
        return response.json();
    }).then(data => {
        let station_prediction = "<select id='predictedStation'><option value='none'>Select Station</option>";
        let hour_prediction = "<select id='predictedHour'><option value='none'>Select Hour</option>";
        let day_prediction = "<select id='predictedDay'><option value='none'>Select Day</option>";

        // items for dropdowns
        let daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        let currentDate = new Date();
        let weekday = currentDate.getDay() -1;
        let cDay = currentDate.getDate();
        let cMonth = currentDate.getMonth() +1;
        let cYear = currentDate.getFullYear();
        // let time = currentDate.getHours()

        for (var i = 0; i < 24; i++) {
            if (i < 10)
                i = "0"+i
            hour_prediction += "<option value =" + i + ">" + i+":00" + "</option>";
        }

        // Populate dropdown with appropriate indexes as values, for model
        for (var i = 0; i < 7; i++) {
            let currentDay = daysOfWeek[(weekday + i) % 7];
            for (var j = 0; j < 7; j++) {
                if (currentDay == daysOfWeek[j]) {
                    day_prediction += "<option value =" + j + ">" + currentDay +
                        " - " + (cDay + i) + "/" + cMonth + "/" + cYear + "</option>";
                }
            }
        }
        hour_prediction += "</select>";
        day_prediction += "</select>";
        data.forEach(prediction => {
            station_prediction += "<option value =" + prediction.number + ">" + prediction.name + "</option>";
        })

        station_prediction += "</select><button type=\"button\" onclick=\"predictionValues(stationValue, hourValue, dayValue)\">Get Info</button>"
        document.getElementById("prediction").innerHTML += hour_prediction;
        document.getElementById("prediction").innerHTML += day_prediction;
        document.getElementById("prediction").innerHTML += station_prediction;
    })
}

    document.getElementById("prediction").addEventListener("click", function() {
        hourValue = document.getElementById("predictedHour").value;
        dayValue = document.getElementById("predictedDay").value;
        stationValue = document.getElementById("predictedStation").value;
    })


function predictionValues(stationNumber, hour, day) {
    fetch("/model/" + stationNumber + "/" + hour + "/" + day).then(response => {
        return response.json();
    }).then(data => {
        console.log(data)
        let tableOut = "<table>";
                tableOut += "<thead>" + "<tr>" +
                    "<th>Station Name</th>" +
                    "<th>Station Number</th>" +
                    "<th>Predicted Available Stands</th>" +
                    "<th>Predicted Available Bikes</th></tr>" +
                    "</thead>";


                tableOut += "<tr><td>" +
                    data.station_name + "</td></tr>" + "<tr><td>" +
                    stationNumber + "</td></tr>" + "<tr><td>" +
                    data.predicted_available_stands + "</td></tr>" + "<tr><td>" +
                    data.predicted_bikes + "</td></tr>";
                tableOut += "</table>";

                document.getElementById("bikeTable").innerHTML = tableOut;
        })
}


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
}
