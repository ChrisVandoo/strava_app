// create a bar chart showing distance for a given month
function createChart(chart, input_data, chart_type) {
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
            plugins: {
                legend: {
                    display: false 
                }
            },
            scales: {
                y: {
                    ticks: {
                        callback: function(value, index, values) {
                            return value + " km";
                        }
                    }
                },
                x: {
                    grid: {
                        display: true,
                    },
                    ticks: {
                        callback: function(index) {
                            date = new Date(this.getLabelForValue(index))

                            if (date.getDay() == 1) {
                                return date.toDateString()
                            } else {
                                return ""
                            }
                        }
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