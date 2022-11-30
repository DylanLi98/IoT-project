// chart outline
var canvas = document.getElementById('myChart');
var data = {
    labels: [],
    datasets: [
        {
            label: "Make a Selection",
            lineTension: 0.1,
            borderColor: "rgba(75,192,192,1)",
            backgroundColor: "rgba(145, 169, 212, 0.2)",
            data: [],
        }
    ]
};
var option = {
	showLines: true,
    layout: {
            padding: 30
        }
};
var myLineChart = Chart.Line(canvas,{
	data:data,
    options:option
});

// example water data list
async function waterData() {
    return await fetch('/reporting/rest/getWaterUsage')
        .then(response => {
            return response.json()
        })
        .then((data) => {
            return data;
        });
}

// example power data list
async function powerData() {
    return await fetch('/reporting/rest/getPowerUsage')
    .then(response => {
        return response.json()
    })
    .then((data) => {
       return data;
    });
}


const pList = [10, 5, 7, 7, 3, 5, 7, 3, 6, 3, 6, 7, 3, 2, 2, 6, 0, 0, 0, 3, 5]

// creates list of json objs from cvs list data input
function imp(list){

    // creating lists
    var x = [];
    var y = [];
    var z = [];

    for (let i = 0; i < list.length; i++) {

       // splitting line into array bassed of commas
        x = list[i].split(",");

        // JSON object from an array with index keys
        y = JSON.stringify(Object.assign({}, x));

        // creating json obj
        myObj = JSON.parse(y);
        z.push(myObj);
    }
    return z;
}


function getDatesInRange(startDate, endDate) {
  const date = new Date(startDate);
  const eDat = new Date(endDate);
  const dates = [];
  while (date <= eDat) {
    dates.push(new Date(date));
    date.setDate(date.getDate() + 1);
  }
  return dates;
}

function aggregateData(data){
    let i = 0;
    let j = 0;
    let list = [];
    let startTime = data[0][0]
    let endTime = data[data.length - 1][0]

    let dates = getDatesInRange(startTime, endTime)
    let sum = 0;
    while (j < dates.length){
        i = 0
        sum = 0
        while (i < data.length) {
            let d = new Date(data[i][0])
            if (d.getDay() === dates[j].getDay()){
                sum += parseFloat(data[i][1])
            }
            i += 1
        }
        list.push([dates[j].toLocaleDateString("en-US"), parseFloat(sum)])
        j += 1
    }

    return list
}

function getHoursInRange(startDate, endDate) {
  const date = new Date(startDate);
  const eDat = new Date(endDate);
  const dates = [];
  while (date <= eDat) {
    dates.push(new Date(date));
    date.setHours(date.getHours() + 1);
  }
  return dates;
}

function aggregateHourlyData(data){
    let i = 0;
    let j = 0;
    let list = [];
    let startTime = data[0][0]
    let endTime = data[data.length - 1][0]

    let dates = getHoursInRange(startTime, endTime)
    let sum = 0;
    while (j < dates.length){
        i = 0
        sum = 0
        while (i < data.length) {
            let d = new Date(data[i][0])
            if (d.getDay() === dates[j].getDay() && d.getHours() === dates[j].getHours()){
                sum += parseFloat(data[i][1])
            }
            i += 1
        }
        list.push([dates[j].toLocaleDateString("en-US"), parseFloat(sum)])
        j += 1
    }

    return list
}

async function add_Water(timespan, time_unit){
    let list = [];
    let data = await waterData();
    if (timespan === '2month') {
        list = aggregateData(data.slice(-(60*24*31*2)))
    }
    else if (timespan === 'month') {
        list = aggregateData(data.slice(-(60*24*31)));
    }
    else if (timespan === 'week') {
        list = aggregateData(data.slice(-(60*24*7)));
    }
    else if (timespan === 'day') {
        list = aggregateHourlyData(data.slice(-(60*24)));
    }

    // setting chart label name
    myLineChart.data.datasets[0].label =  'Water (gallons per x)';
    // clearing dataset
    myLineChart.data.datasets[0].data = '';

    // clearing data labels
    myLineChart.data.labels = [];

    // looping through list updating chart with data
    for (let i = 0; i < list.length; i++){
        myLineChart.data.datasets[0].data[i] = list[i][1];  // adding amount data to chart
        myLineChart.data.labels[i] = list[i][0];   // adding time data to chart
        //fixing empty node[0]
        myLineChart.data.datasets[0].data[0] = list[0][1]
        myLineChart.update();
    }
}


async function add_Power(timespan, time_unit){
    let list = [];
    let data = await powerData();
    if (timespan === '2month') {
        list = aggregateData(data.slice(-(60*24*31*2)))
    }
    else if (timespan === 'month') {
        list = aggregateData(data.slice(-(60*24*31)));
    }
    else if (timespan === 'week') {
        list = aggregateData(data.slice(-(60*24*7)));
    }
    else if (timespan === 'day') {
        list = aggregateHourlyData(data.slice(-(60*24)));
    }
    // setting chart label name
    myLineChart.data.datasets[0].label =  'Power (WATTS per x)';
    // clearing dataset
    // myLineChart.data.datasets[0].data = '';
    // clearing data labels
    myLineChart.data.labels = [];

    myLineChart.data.datasets[0].data[0] = parseFloat(list[0][1])

    dataset = myLineChart.data.datasets[0]
    // looping through list updating chart with data
    for (let i = 1; i < list.length; i++){
        dataset.data[i] = parseFloat(list[i][1]);  // adding amount data to chart
        // + parseFloat(dataset.data[i - 1])
        myLineChart.data.labels[i] = list[i][0];   // adding time data to chart
    }
    myLineChart.update();
}

function getProjectedData(data){
    let list = [];
    let day = 0;
    let sum = 0;
    let j = 0;
    let weekDate = new Date();

     while (j < data.length) {
        weekDate = new Date(data[j][0]);
        weekDate.setDate(weekDate.getDate() + 31)
        if( day > 6) {
            day = 0
            list.push([weekDate.toLocaleDateString("en-US"), sum])
            sum = 0
        }
        sum += data[j][1]

        day +=1
        j += 1
    }

    return list;
}


async function add_Future_Power(){
    let list_historical = [];
    let list_future = [];
    let data = await powerData();
    list_historical = aggregateData(data.slice(-(60*24*31)));
    list_future = getProjectedData(list_historical);

    // setting chart label name
    myLineChart.data.datasets[0].label = 'Power (WATTS per x)';
    // clearing dataset
    // myLineChart.data.datasets[0].data = '';
    // clearing data labels
    myLineChart.data.labels = [];

    myLineChart.data.datasets[0].data[0] = parseFloat(list_future[0][1])

    dataset = myLineChart.data.datasets[0]
    // looping through list updating chart with data
    for (let i = 1; i < list_future.length; i++){
        dataset.data[i] = parseFloat(list_future[i][1]);  // adding amount data to chart
        // + parseFloat(dataset.data[i - 1])
        myLineChart.data.labels[i] = list_future[i][0];   // adding time data to chart
    }
    myLineChart.update();
}

async function add_Future_Water(){
    let list_historical = [];
    let list_future = [];
    let data = await waterData();
    list_historical = aggregateData(data.slice(-(60*24*31)));
    list_future = getProjectedData(list_historical);

    // setting chart label name
    myLineChart.data.datasets[0].label =  'Water (gallons per x)';
    // clearing dataset
    // myLineChart.data.datasets[0].data = '';
    // clearing data labels
    myLineChart.data.labels = [];

    myLineChart.data.datasets[0].data[0] = parseFloat(list_future[0][1])

    dataset = myLineChart.data.datasets[0]
    // looping through list updating chart with data
    for (let i = 1; i < list_future.length; i++){
        dataset.data[i] = parseFloat(list_future[i][1]);  // adding amount data to chart
        // + parseFloat(dataset.data[i - 1])
        myLineChart.data.labels[i] = list_future[i][0];   // adding time data to chart
    }
    myLineChart.update();
}
