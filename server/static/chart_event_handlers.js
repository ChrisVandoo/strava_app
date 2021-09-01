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
        .then(new_data => {
            chart = createChart(chart, new_data, "bar")
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
            chart = createChart(chart, data, "bar")
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
            chart = createChart(chart, data, "bar")
        });

    $("#chartContainer h1").replaceWith("<h1>" + curr_month + " " + curr_year + "</h1>");
}

// event handler for "data-rep" (data representation) 
function data_rep_selected(option) {
    console.log(option.value)
    curr_rep = option.value 

    url = createUrl()
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (curr_rep == "pace") {
                chart = createChart(chart, data, "line")
            } else {
                chart = createChart(chart, data, "bar")
            }
        });

    $("#chartContainer h1").replaceWith("<h1>" + curr_month + " " + curr_year + "</h1>");
}