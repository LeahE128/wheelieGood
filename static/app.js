let dynamicData;
let map;

function initCharts(){
    google.charts.load('current', {'packages':['corechart']});
    google.charts.setOnLoadCallback(initMap);
}

function initMap() {
    getDynamicBikes();
    fetch("/staticBikes").then(response=> {
        return response.json();
    }).then(data => {
        map = new google.maps.Map(document.getElementById("map"), {
            center: {lat: 53.349804, lng: -6.260310},
            zoom:12,
        });

//          Addition of google markers
        data.forEach(bikes => {
            const marker = new google.maps.Marker({
                position: { lat: bikes.pos_lat, lng: bikes.pos_lng},
                map: map,
            });
            marker.addListener("click", () => {
                const infowindow = new google.maps.InfoWindow({
                    content: bikes.name + "<br>" +
                        "Station Number: " + bikes.number + "<br>" +
                        "Available Bikes: " + availability(bikes.number, dynamicData) + "<br>" +
                        "Available Stands: " + availableStands(bikes.number, dynamicData)
                });
                infowindow.open(map, marker);
                bikeTable(dynamicData, bikes.number, bikes.name);
                drawOccupancyWeekly(bikes.number);
            });
        });
    }).catch(err => {
        console.log("OOPS!", err);
    })
}

function drawOccupancyWeekly(bikes_number){
//This is called when a user clicks on the marker
    fetch("/occupancy/" + bikes_number).then(response => {
        return response.json();
    }).then(data => {
//        console.log(data);

        var options = {
            title: "Bike Availability per day",
        }
        var chart = new google.visualization.ColumnChart(document.getElementById("chart"));
        var chart_data = new google.visualization.DataTable();
        chart_data.addColumn('datetime', "Date");
        chart_data.addColumn('number', "Bike Availability");
        data.forEach(v => {
            chart_data.addRow([new Date(v.last_update), v.available_bikes]);
        })
        chart.draw(chart_data, options);

    });

}

function availability(number, dynamicBikes) {
    for (let key in dynamicBikes) {
        let stationNumber = dynamicBikes[key].number;
        if (number == stationNumber) {
            return dynamicBikes[key].available_bikes;
        }
    }
}

function availableStands(number, dynamicBikes) {
    for (let key in dynamicBikes) {
        let stationNumber = dynamicBikes[key].number;
        if (number == stationNumber) {
            return dynamicBikes[key].available_bike_stands;
        }
    }
}

    function bikeTable(dynamicBikesJson, stationNumber, stationName) {
        //console.log(dynamicBikesJson)
        for (let key in dynamicBikesJson) {
            let standNumber = dynamicBikesJson[key].number;
            if (standNumber == stationNumber) {

                let tableOut = "<table>";
                tableOut += "<thead>" + "<tr>" +
                    "<th>Number</th>" +
                    "<th>Name</th>" +
                    "<th>Available Bike Stands</th>" +
                    "<th>Available Bikes</th></tr>" +
                    "</thead>";

                let number = dynamicBikesJson[key].number;
                let availableBikes = dynamicBikesJson[key].available_bikes;
                let availableBikeStands = dynamicBikesJson[key].available_bike_stands;


                tableOut += "<tr><td>" +
                    number + "</td></tr>" + "<tr><td>" +
                    stationName + "</td></tr>" + "<tr><td>" +
                    availableBikeStands + "</td></tr>" + "<tr><td>" +
                    availableBikes + "</td></tr>";
                tableOut += "</table>";

                document.getElementById("bikeTable").innerHTML = tableOut;
            }
        }
    }

    function getDynamicBikes() {
        fetch("/currentBikes").then(response => {
            return response.json();
        }).then(data => {
            dynamicData = data;
        })
    }

    function displayWeather() {
        fetch("/weather").then(response => {
            return response.json();
        }).then(data => {
            const last_item = data.length - 1;
            const weather_main = data[last_item].weather_main;
            const weather_icon = data[last_item].weather_icon;
            const weather_city = data[last_item].city_name;
            const weather_temp = data[last_item].main_temp - 273.53;
            var weather_temp_int = parseInt(weather_temp);
            var iconurl = "http://openweathermap.org/img/w/" + weather_icon + ".png";
            document.getElementById('city').innerHTML = weather_city;
            document.getElementById('temp').innerHTML = weather_temp_int + '℃';
            document.getElementById('weather_description').innerHTML = weather_main;
            $('#wicon').attr('src', iconurl);
            
        });
    }

    displayWeather();
