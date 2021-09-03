// create a bar chart showing distance for a given month
function createChart(chart, input_data, chart_type, y_axis_label, activity_type) {

    // default y tick callback function
    let y_callback = function(value) {
        return value + " " + y_axis_label;
    };
    
    if (chart_type == "line") {
        if (activity_type == "Run") {
            y_callback = function(value) {
                let pace_in_min = value / 60;
                let minutes = Math.floor(pace_in_min);
                let seconds = Math.round((pace_in_min % minutes) * 60);
                
                if (seconds / 10 >= 1) {
                    return minutes + ":" + seconds + " /km";
                } else {
                    return minutes + ":0" + seconds + " /km";
                }     
            };
        } else {
            y_callback = function(value) {
                return value + " km/h"
            }
        }
        
    } 

    const data = {
        datasets: [{
            backgroundColor: 'rgb(255, 99, 132)',
            borderColor: 'rgb(255, 99, 132)',
            data: input_data,
        }]
    };

    const config = {
        type: chart_type,
        data,
        options: { 
            parsing: {},
            plugins: {
                legend: {
                    display: false 
                }
            },
            scales: {
                y: {
                    ticks: {
                        callback: y_callback
                    }
                }
            }
        }
    };
    
    if (chart) {
        chart.destroy()
    };
    
    return new Chart(
        document.getElementById('myChart'),
        config
    );
}        