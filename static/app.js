let dynamicData;
let map;
let selectedStation = "";
let staticData;
let markers = [];
let closest_positions= [];
let closest_markers = [];



function initCharts(){
    google.charts.load('current', {'packages':['corechart']});
    google.charts.setOnLoadCallback(initMap);
}

function initMap() {
//  Setting info window variable to null
    var liveWindow = null;

//  Fetching the data
    getDynamicBikes();
    fetch("/allBikes").then(response=> {
        return response.json();

    }).then(data => {
//  Creation of map
        map = new google.maps.Map(document.getElementById("map"), {
            center: {lat: 53.349804, lng: -6.260310},
            zoom: 13,
        });


//  Adding circle to map
        data.forEach(bikes => {
            if (bikes.available_bikes > 5) {
                let stationCircleGr = new google.maps.Circle({
                    strokeColor: "#00ff00",
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: "#00ff00",
                    fillOpacity: 0.35,
                    map,
                    center: {lat: bikes.pos_lat, lng: bikes.pos_lng},
                    radius: 55,
                });
            } else if (bikes.available_bikes > 2) {
                let stationCircleOr = new google.maps.Circle({
                    strokeColor: "#FFA500",
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: "#FFA500",
                    fillOpacity: 0.35,
                    map,
                    center: {lat: bikes.pos_lat, lng: bikes.pos_lng},
                    radius: 55,
                });
            } else {
                let stationCircleRd = new google.maps.Circle({
                    strokeColor: "#FF0000",
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: "#FF0000",
                    fillOpacity: 0.35,
                    map,
                    center: {lat: bikes.pos_lat, lng: bikes.pos_lng},
                    radius: 55,
                });
            }

            // Addition of google markers

            const marker = new google.maps.Marker({
                position: {lat: bikes.pos_lat, lng: bikes.pos_lng},
                map: map,
            });
            markers.push(marker);
            marker.addListener("click", () => {
                let clickedMarker = marker.position;


//          If it is open, close the infowindow
                if (liveWindow !== null) {
                    liveWindow.close();

                }

//          Create the infowindow
                const infowindow = new google.maps.InfoWindow({
                    content: "<h4>" + bikes.name + "</h4>" + "<hr>" +
                        "<p>Station Number: " + bikes.number + "</p>" +
                        "<p>Available Bikes: " + bikes.available_bikes + "</p>" +
                        "<p>Available Stands: " + bikes.available_bike_stands + "</p>"
                });

//          Open the infowindow, assign the infowindow to liveWindow variable
                infowindow.open(map, marker);
                liveWindow = infowindow;

                find_closest_marker(clickedMarker);
                getRecommendation(staticData, dynamicData);
                console.log(recommendations)
                // resetRecommendationDiv();
                // console.log(recommendations)
                bikeTable(dynamicData, bikes.number, bikes.name);
                drawOccupancyWeekly(bikes.number);
                drawOccupancyHourly(bikes.number);
            });

        })


        }).catch(err => {
            console.log("OOPS!", err);

    })
}


const chart_colors = ['#39FF14'];
const background = 'grey';
function drawOccupancyWeekly(bikes_number){
//This is called when a user clicks on the marker
    fetch("/occupancy/" + bikes_number).then(response => {
        return response.json();
    }).then(data => {
//        console.log(data);

        var options = {
                    title: 'Daily Average Availability for Station Number ' + bikes_number,
                    height: 400,
                    legend: {
                        position: 'top',
                        maxLines: 3
                    },
                    animation: {
                        duration: 1000,
                        easing: 'out'
                    },
                    colors: chart_colors,
                    bar: {
                        groupWidth: '75%'
                    },
                    isStacked: true,
                    backgroundColor: background
                };
        var chart = new google.visualization.ColumnChart(document.getElementById("dailyChart"));
        var chart_data = new google.visualization.DataTable();
        chart_data.addColumn('string', 'Day');
        chart_data.addColumn('number', 'Bikes');
        data.forEach(v => {
            chart_data.addRow([v.day, v.avgBikes]);
        })
        chart.draw(chart_data, options);
    });
}

function drawOccupancyHourly(bikes_number){
//This is called when a user clicks on the marker
    fetch("/occupancyHourly/" + bikes_number).then(response => {
        return response.json();
    }).then(data => {
        console.log(data);

        var options = {
                    title: 'Hourly Average Availability for Station Number ' + bikes_number,
                    height: 400,
                    legend: {
                        position: 'top',
                        maxLines: 3
                    },
                    animation: {
                        duration: 1000,
                        easing: 'out'
                    },
                    colors: chart_colors,
                    bar: {
                        groupWidth: '75%'
                    },
                    isStacked: true,
                    backgroundColor: background
                };
        var chart = new google.visualization.LineChart(document.getElementById("hourlyChart"));
        var chart_data = new google.visualization.DataTable();
        chart_data.addColumn('datetime', "Date");
        chart_data.addColumn('number', "Bikes");
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

                document.getElementById("bikeTable").innerHTML = "<h3>Station and Bike Availability</h3>" + tableOut;
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

    function getStaticBikes() {
        fetch("/staticBikes").then(response => {
            return response.json();
        }).then(data => {
         staticData = data;
        })
    }

    function stationSelect() {
        getDynamicBikes();
        getStaticBikes();
        fetch("/staticBikes").then(response => {
            return response.json();
        }).then(data => {
            let station_select = "<select id='stationSel'><option value='none'>Select Station</option>";
            data.forEach(bikes => {
                station_select += "<option value =" + bikes.number + ">" + bikes.name + "</option>";
            })
            station_select += "</select><button type=\"button\" onclick=\"getTable(dynamicData, staticData)\">Get Info</button>"
            document.getElementById("stationSelDiv").innerHTML += station_select;
            var selectedStation = document.getElementById("stationSel").value;
        })
    }

    document.getElementById("stationSelDiv").addEventListener("click", function() {
        var selectedStation = document.getElementById("stationSel").value;
            console.log(selectedStation);
    })


stationSelect();


    function displayWeather() {
        fetch("/weather").then(response => {
            return response.json();
        }).then(data => {
            const last_item = data.length - 1;
            const weather_main = data[last_item].weather_main;
            const weather_icon = data[last_item].weather_icon;
            const weather_city = data[last_item].city_name;
            var d = new Date();
            const weather_temp = data[last_item].main_temp - 273.53;
            var weather_temp_int = parseInt(weather_temp);
            var iconurl = "http://openweathermap.org/img/w/" + weather_icon + ".png";
            document.getElementById("weather_today").innerHTML = d.toDateString();
            document.getElementById('city').innerHTML = weather_city;
            document.getElementById('temp').innerHTML = weather_temp_int + '℃';
            document.getElementById('weather_description').innerHTML = weather_main;
            $('#wicon').attr('src', iconurl);
        });
    }

    displayWeather();


function getTable(dynamicDataJ, StaticDataJ) {
        //console.log(dynamicBikesJson)
        let dynamic = dynamicDataJ;
        let static = StaticDataJ;
        console.log(static)
        var selectedStation = document.getElementById("stationSel").value;
        console.log(selectedStation);
        for (let key in static) {
            console.log(static[key].name)
            var selectedStation = document.getElementById("stationSel").value;
            console.log(selectedStation);
            let stationName = static[key].number
            if (selectedStation == stationName) {

                let number = static[key].number;
                let availableBikes = dynamic[key].available_bikes;
                let availableBikeStands = dynamic[key].available_bike_stands;
                let station = static[key].name;

                let tableOut = "<table>";
                tableOut += "<thead>" + "<tr>" +
                    "<th>Number</th>" +
                    "<th>Name</th>" +
                    "<th>Available Bike Stands</th>" +
                    "<th>Available Bikes</th></tr>" +
                    "</thead>";


                tableOut += "<tr><td>" +
                    number + "</td></tr>" + "<tr><td>" +
                    station + "</td></tr>" + "<tr><td>" +
                    availableBikeStands + "</td></tr>" + "<tr><td>" +
                    availableBikes + "</td></tr>";
                tableOut += "</table>";

                document.getElementById("bikeTable").innerHTML = "<h3>Station and Bike Availability</h3>" + tableOut;

                drawOccupancyWeekly(selectedStation);
                drawOccupancyHourly(selectedStation);


            }
        }
    }

   function find_closest_marker(event) {
    // resetRecommendationDiv();
    console.log(recommendations);
     var distances = [];
     // var closest = -1;
     // var secondClosest = -1;
     for (i = 0; i < markers.length; i++) {
       var d = google.maps.geometry.spherical.computeDistanceBetween(event, markers[i].position);
       distances[i] = d;
       console.log(distances)
       if (d < 500 && d != 0) {
         closest_markers.push({marker_index: i, distance_lengths: d});
         closest_markers.sort(function (a, b) {
           return a.distance_lengths- b.distance_lengths;
           });
       }

     }

     for (i = 0; i < closest_markers.length; i++) {
         closest_positions.sort(function (a, b) {
           return a.distance_lengths- b.distance_lengths;
           });
         closest_positions.push({marker_positions: markers[closest_markers[i].marker_index].position, distance_lengths : closest_markers[i].distance_lengths/1000});

     }
   }

closest_positions.sort(function (a, b) {
            return a.distance_lengths- b.distance_lengths;
            });

function getRecommendation(staticBikes, dynamicBikes) {
    getDynamicBikes();
    getStaticBikes();
    var dict = [];
    var result = "";
    for (let key in staticBikes) {

        // console.log(staticBikes[key])
        let stationPosition = ("(" + staticBikes[key].pos_lat + ", " + staticBikes[key].pos_lng + ")");
        // console.log(staticBikes[key].name);
        for (i = 0; i < closest_positions.length; i++) {
            if (stationPosition == closest_positions[i].marker_positions && dynamicBikes[key].available_bikes > 5) {
                // console.log(staticBikes[key].name);
                dict.push({
                    Station_name: staticBikes[key].name,
                    Available_bikes: dynamicBikes[key].available_bikes,
                    Available_stands: dynamicBikes[key].available_bike_stands,
                    distances: closest_positions[i].distance_lengths.toFixed(3)
                })

            }
            console.log(dict);
            result = dict.reduce((unique, o) => {
                if (!unique.some(obj => obj.Station_name === o.Station_name && obj.value === o.value)) {
                    unique.push(o);
                }
                return unique;
            }, []);
            console.log(result);
            result.sort(function (a, b) {
                return a.distances - b.distances;
            });
            console.log(result);
        }

    }
    let tableOut = "<table>";
    tableOut += "<thead>" + "<tr>" +
            "<th>Station Name</th>" +
            "<th>Available Bikes</th>" +
            "<th>Available Bike Stands</th>" +
            "<th>Distance in km</th></tr>" +
            "</thead>";
    for (var i = 0; i < result.length; i++) {


        tableOut += "<tr><td>" +
            result[i].Station_name + "</td></tr>" + "<tr><td>" +
            result[i].Available_bikes + "</td></tr>" + "<tr><td>" +
            result[i].Available_stands + "</td></tr>" + "<tr><td>" +
            result[i].distances + "</td></tr>";




    }
    tableOut += "</table>";
     document.getElementById("recommendations").innerHTML = "<h3>Next Nearest Stations</h3>" + tableOut;
}
