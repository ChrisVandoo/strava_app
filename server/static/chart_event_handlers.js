let chart_type = "bar"
let y_axis_label = "km"

function hasData(data) {
    if ($.isEmptyObject(data)) {
        $("#myChart").remove();
        $("#temp-message").remove();
        $("#chartContainer").append('<div id="temp-message">No data found for this month :(</div>')
    } else {
        $("#myChart").remove();
        $("#temp-message").remove();
        $("#chartContainer").append('<canvas id="myChart"></canvas>')
        chart = createChart(chart, data, chart_type, y_axis_label, curr_type)
    }
}

function createUrl() {
    // create url using curr_* values
    return "/chart_data?" + 
        "months=" + curr_month_int +
        "&year=" + curr_year +
        "&type=" + curr_type +
        "&rep_type=" + curr_rep;
}

// event handler for when a month is selected from the dropdown
function month_selected(option) {
    // console.log(option.value);
    curr_month_int = option.value 

    url = createUrl()
    fetch(url)
        .then(response => response.json())
        .then(data => {
            hasData(data);
        });
    
    curr_month = $("#months option").filter(":selected").attr("id")
    $("#chartContainer h1").replaceWith("<h1>" + curr_month + " " + curr_year + "</h1>");
}

// event handler for when a year is selected from the dropdown
function year_selected(option) {
    // console.log(option.value);
    curr_year = option.value;

    url = createUrl()
    fetch(url)
        .then(response => response.json())
        .then(data => {
            hasData(data);
        });
    
    $("#chartContainer h1").replaceWith("<h1>" + curr_month + " " + curr_year + "</h1>");
}

// event handler for when activity type is selected from the dropdown
function activity_type_selected(option) {
    console.log(option.value)
    curr_type = option.value;

    url = createUrl()
    fetch(url)
        .then(response => response.json())
        .then(data => {
            hasData(data);
        });

    $("#chartContainer h1").replaceWith("<h1>" + curr_month + " " + curr_year + "</h1>");
}

// event handler for "data-rep" (data representation) 
function data_rep_selected(option) {
    // console.log(option.value)
    curr_rep = option.value 

    url = createUrl()
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (curr_rep == "pace") {

                if (curr_type == "Ride") {
                    y_axis_label = "km/h";
                } else {
                    y_axis_label = "/km";
                }

                chart_type = "line";
                hasData(data);
            } else {
                if (curr_rep == "time") {
                    y_axis_label = "min"
                } else {
                    y_axis_label = "km"
                }

                chart_type = "bar";
                hasData(data);
            }
        });

    $("#chartContainer h1").replaceWith("<h1>" + curr_month + " " + curr_year + "</h1>");
}