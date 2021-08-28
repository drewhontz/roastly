let isTimerRunning = false;
let startTime = null;
let intervalId = null;
let firstCrack = null;
let secondCrack = null;

/*
    Interface contains all our components
    Components are:
        - timer
            - has a special to string method to return mm:ss
            - no range
        - temperature
            - has a special to string method for F | C
            - different rang
        - power
        - fan
        - first crack checkbox
            - on our off and timestamp
        - second crack checkbox
*/

class Component {
    constructor(elementId, startingValue, minValue, maxValue) {
        this.elementId = elementId;
        this.value = startingValue;
        this.minValue = minValue;
        this.maxValue = maxValue;
    }

    changeValue(delta) {
        var newValue = this.value + delta;
        if (this.minValue <= newValue <= this.maxValue) {
            this.value = newValue;
            document.getElementById(this.elementId).innerHTML = this.value;
        }
    }

    get value() {
        return this.value;
    }
}


function getState(ids) {
    /* Returns a hashmap of component and status when provided an id or list of html element ids */
    var state = {};
    ids.forEach(id => {
        state[id] = document.getElementById(id).innerHTML;
    });

    // Remove this later
    state['roast_id'] = location.pathname.split("/")[3];
    return state;
}

function parameterizeState(obj) {
    /* Turns component state object into a param string 
    * https://stackoverflow.com/questions/6566456/how-to-serialize-an-object-into-a-list-of-url-query-parameters
    */
    var str = "";
    for (var key in obj) {
        if (str != "") {
            str += "&";
        }
        str += key + "=" + encodeURIComponent(obj[key]);
    }
    return str;
}

function logChangeAPI() {
    var ids = ['timerLabel', 'temperatureLabel', 'powerLabel', 'fanLabel'];
    var state = getState(ids);
    state["firstCrack"] = firstCrack;
    state["secondCrack"] = secondCrack;
    var params = parameterizeState(state);
    const Http = new XMLHttpRequest();
    const url = `api/log_event/?${params}`;
    Http.open("GET", url);
    Http.send();
}

function changeValue(id, increment=1) {
    /* Accepts an html element id and a value to change by */
    if (!isTimerRunning)
    {
        console.log("Buttons disabled until timer started.");
        return
    }
    var currentValue = document.getElementById(id).innerHTML = parseInt(document.getElementById(id).innerHTML);
    var newValue = currentValue + increment;
    if (0 <= newValue && newValue <= 9)
    {
        console.log(`New value is ${newValue}`);
        document.getElementById(id).innerHTML = newValue;
    }
    else {
        console.log(`New value ${newValue} out of range.`);
    }
    logChangeAPI();
}

function logTemperatureChange(id, increment=1) {
    if (!isTimerRunning)
    {
        console.log("Buttons disabled until timer started.");
        return
    }
    var currentValue = document.getElementById(id).innerHTML = parseInt(document.getElementById(id).innerHTML.replace("&#176;F", ""));
    var newValue = currentValue + increment;
    if (0 <= newValue && newValue <= 550)
    {
        console.log(`New value is ${newValue}`);
        document.getElementById(id).innerHTML = newValue + "&#176;F";
    }
    else {
        console.log(`New value ${newValue} out of range.`);
    }
    logChangeAPI();
}

function startRoast() {
    /* Starts the roast timer */
    if (!isTimerRunning) {
        isTimerRunning = !isTimerRunning;
        document.getElementById('start').innerHTML = 'End';
        startTime = Date.now();
        console.log(`Starting timer at ${startTime}`);
        intervalId = window.setInterval(function(){
            var elapsed = Math.floor((Date.now() - startTime) / 1000);
            var minutes = (Math.floor(elapsed / 60)).toString().padStart(2, "0");
            var seconds = (elapsed % 60).toString().padStart(2, "0");
            document.getElementById('timerLabel').innerHTML = `${minutes}:${seconds}`;
          }, 1000);
    } else {
        console.log("Stopping timer.");
        isTimerRunning = !isTimerRunning;
        clearInterval(intervalId);
        document.getElementById('timerLabel').innerHTML = "00:00";
        document.getElementById('temperatureLabel').innerHTML = "375&#176;F";
        document.getElementById('powerLabel').innerHTML = "9";
        document.getElementById('fanLabel').innerHTML = "9";
        document.getElementById('start').innerHTML = 'Start';
        roast_id = location.pathname.split("/")[3];
        window.location.href = `/roast/finish/${roast_id}`;
    }
}

function recordCrack(crackNum) {
    var checkId = crackNum == 1 ? "firstCrack" : "secondCrack";
    // disable button when pressed
    document.getElementById(checkId).disabled = true;
    // write the elapsed time next to the button
    var elapsed_time = getState(['timerLabel'])['timerLabel'];
    console.log(`Logging ${checkId} at ${elapsed_time}`);
    document.getElementById(checkId + "Label").innerHTML = document.getElementById(checkId + "Label").innerHTML + `: ${elapsed_time}`;
    // set global variable for recording
    if (checkId == 'firstCrack') firstCrack = elapsed_time;
    else secondCrack = elapsed_time;
};