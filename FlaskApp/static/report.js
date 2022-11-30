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
const rwList = [
"Bathroom, Shower, 10/05/2022 10:21:40, 2.5, production",
"Bathroom, Shower, 10/05/2022 10:21:41, 3, production",
"Bathroom, Shower, 10/05/2022 10:21:42, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:43, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:44, 1, production",
"Bathroom, Shower, 10/05/2022 10:21:45, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:46, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:47, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:48, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:49, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:50, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:51, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:52, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:53, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:54, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:55, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:56, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:40, 2.5, production",
"Bathroom, Shower, 10/05/2022 10:21:41, 3, production",
"Bathroom, Shower, 10/05/2022 10:21:42, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:43, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:44, 1, production",
"Bathroom, Shower, 10/05/2022 10:21:45, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:46, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:47, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:48, 2.5, production",
"Bathroom, Shower, 10/05/2022 10:21:49, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:50, 1, production",
"Bathroom, Shower, 10/05/2022 10:21:51, 2, production",
"Bathroom, Shower, 10/05/2022 10:21:52, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:53, 1, production",
"Bathroom, Shower, 10/05/2022 10:21:54, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:55, 1, production",
"Bathroom, Shower, 10/05/2022 10:21:56, 0, production"
]

const pwList = [
"Bathroom, Shower, 10/05/2022 10:21:40, 2.5, production",
"Bathroom, Shower, 10/05/2022 10:21:41, 3, production",
"Bathroom, Shower, 10/05/2022 10:21:42, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:43, 18, production",
"Bathroom, Shower, 10/05/2022 10:21:44, 1, production",
"Bathroom, Shower, 10/05/2022 10:21:45, 29, production",
"Bathroom, Shower, 10/05/2022 10:21:46, 20, production",
"Bathroom, Shower, 10/05/2022 10:21:47, 30, production",
"Bathroom, Shower, 10/05/2022 10:21:48, 60, production",
"Bathroom, Shower, 10/05/2022 10:21:49, 60, production",
"Bathroom, Shower, 10/05/2022 10:21:50, 80, production",
"Bathroom, Shower, 10/05/2022 10:21:51, 70, production",
"Bathroom, Shower, 10/05/2022 10:21:52, 100, production",
"Bathroom, Shower, 10/05/2022 10:21:53, 12, production",
"Bathroom, Shower, 10/05/2022 10:21:54, 90, production",
"Bathroom, Shower, 10/05/2022 10:21:55, 70, production",
"Bathroom, Shower, 10/05/2022 10:21:56, 20, production",
"Bathroom, Shower, 10/05/2022 10:21:40, 2.5, production",
"Bathroom, Shower, 10/05/2022 10:21:41, 3, production",
"Bathroom, Shower, 10/05/2022 10:21:42, 0, production",
"Bathroom, Shower, 10/05/2022 10:21:43, 18, production",
"Bathroom, Shower, 10/05/2022 10:21:44, 1, production",
"Bathroom, Shower, 10/05/2022 10:21:45, 29, production",
"Bathroom, Shower, 10/05/2022 10:21:46, 20, production",
"Bathroom, Shower, 10/05/2022 10:21:47, 30, production",
"Bathroom, Shower, 10/05/2022 10:21:48, 60, production",
"Bathroom, Shower, 10/05/2022 10:21:49, 60, production",
"Bathroom, Shower, 10/05/2022 10:21:50, 80, production",
"Bathroom, Shower, 10/05/2022 10:21:51, 70, production",
"Bathroom, Shower, 10/05/2022 10:21:52, 100, production",
"Bathroom, Shower, 10/05/2022 10:21:53, 12, production",
"Bathroom, Shower, 10/05/2022 10:21:54, 90, production",
"Bathroom, Shower, 10/05/2022 10:21:55, 70, production",
"Bathroom, Shower, 10/05/2022 10:21:56, 20, production"
]



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

// creating list of json objs with water data
const month_water_list = imp(rwList);
const week_water_list = imp(rwList).slice(-15);
const day_water_list = imp(rwList).slice(-5);

// creating list of json objs with power data
const month_power_list = imp(pwList);
const week_power_list = imp(pwList).slice(-10);
const day_power_list = imp(pwList).slice(-5);



function add_Water(list, time_unit){

// setting chart label name
myLineChart.data.datasets[0].label =  'Water (gallons per x)';
// clearing dataset
myLineChart.data.datasets[0].data = '';

// clearing data labels
myLineChart.data.labels = [];


// looping through list updating chart with data
for (let i = 0; i < list.length; i++){

    myLineChart.data.datasets[0].data[i] = list[i][3];  // adding amount data to chart
    myLineChart.data.labels[i] = time_unit + (i+1);   // adding time data to chart
    //fixing empty node[0]
    myLineChart.data.datasets[0].data[0] = list[0][3]
    myLineChart.update();
}
}


function add_Power(list, time_unit){

// setting chart label name
myLineChart.data.datasets[0].label =  'Power (WATTS per x)';
// clearing dataset
myLineChart.data.datasets[0].data = '';
// clearing data labels
myLineChart.data.labels = [];


// looping through list updating chart with data
for (let i = 0; i < list.length; i++){

    myLineChart.data.datasets[0].data[i] = list[i][3];  // adding amount data to chart
    myLineChart.data.labels[i] = time_unit + (i+1);   // adding time data to chart
    //fixing empty node[0]
    myLineChart.data.datasets[0].data[0] = list[0][3]
    myLineChart.update();

}
}