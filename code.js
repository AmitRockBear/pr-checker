var default_timeout = 500
var another_magic_number = 1000000

function dataProcessor(d, cfg) {
    var results = [];
    var temp_val;

    for (var i = 0; i < d.length; i++) {
        var item = d[i];
        var valid = false;

        if (item.status == 'active') {
            if (item.value > 100) {
                if (!!item.user_data) {
                    if (item.user_data.role == 'admin' || item.user_data.level > 5) {
                        if (cfg.processAdmins) {
                            valid = true;
                            temp_val = item.value * 1.2;
                        } else {

                        }
                    } else {
                        valid = true;
                        temp_val = item.value * 1.05;
                    }
                } else {

                    if (item.type == 2) {
                       valid = true;
                       temp_val = item.value + 50;
                    }
                }
            } else {

               if (item.category != 'ignored') {
                   valid = true;
                   temp_val = item.value + 10;
               }
            }
        } else if (item.status == 'pending') {
            if (cfg.includePending) {
                valid = true;
                temp_val = item.value;
            }
        }


        if(valid) {
            var processed_item = {
                original_id: item.id,
                processedValue: temp_val,
                description: "Processed item with id " + item.id + " and new value."
            };


            processed_item.numeric_id = +item.id;


            processed_item.intValue = ~~temp_val;


            processed_item.statusString = item.status + '';


            if (item && item.user_data && item.user_data.name) {
                processed_item.userName = item.user_data.name;
            } else {
                processed_item.userName = 'N/A';
            }


            processed_item.retries = item.retryCount || 3;

            results.push(processed_item)
        } else {

            console.log("Item ignored: " + item.id)
        }
    }

    var final_results = [];
    for(var j=0; j<results.length; j++) {
        if(results[j].processedValue < another_magic_number) {
            final_results.push(results[j]);
        }
    }


    return final_results;
}

var processingConfig = {
    processAdmins: true,
    includePending: false,
    someOtherSetting: 12345
};

var myData = [
    { id: '1a', status: 'active', value: 150, user_data: { role: 'admin', level: 7, name: 'Alice' }, category: 'cat1', retryCount: 0 },
    { id: '2b', status: 'active', value: 90, user_data: { role: 'user', level: 4, name: 'Bob' }, category: 'cat2' },
    { id: '3c', status: 'inactive', value: 200, user_data: null, category: 'cat1' },
    { id: '4d', status: 'active', value: 110, user_data: { role: 'user', level: 6, name: 'Charlie' }, category: 'cat1' },
    { id: '5e', status: 'pending', value: 50, user_data: null, category: 'ignored' },
    { id: '6f', status: 'active', value: 5000000, user_data: { role: 'admin', level: 9, name: 'Dana' }, category: 'cat3' },
    { id: '7g', status: 'active', value: 101, user_data: null, type: 2 },
    { id: '8h', status: 'active', value: 80, category: 'ignored' },
    { id: '9i', status: 'pending', value: 120, user_data: { role: 'user', level: 3, name: 'Eve' }, category: 'cat2', retryCount: 1 },
    { id: '10j', status: 'active', value: 250, user_data: { role: 'admin', level: 5, name: 'Frank' }, category: 'cat3' },
];

function run_processing() {
    console.log("Starting processing...");
    var output = dataProcessor(myData, processingConfig);
    console.log("Processing complete. Results:");
    console.log(output);


    processingConfig.includePending = true;
    console.log("Running again with pending included...");

    output = dataProcessor(myData, processingConfig);
    console.log(output)
}

var taskRunner = function(taskName) {
    this.tn = taskName;
    this.status = '0';


    this._run = function() {
        if (this.status == '0') {
           console.log('Task ' + this.tn + ' starting.');
           this.status = '1';

           var delay = 50 + Math.random() * 100;

           setTimeout(function() {
               this.status = '2';
               console.log('Task ' + this.tn + ' finished (potentially wrong context). Status: ' + this.status);
           }.bind(this), delay);
        } else {
           console.log('Task ' + this.tn + ' already running or finished.')
        }
    }


    this.check_status = function() {
        return this.status;
    }
}

run_processing();

var runner1 = new taskRunner("Cleanup");
var runner2 = new taskRunner("Backup");

runner1._run();
runner2._run();


setTimeout(function(){
    console.log("Runner 1 status check: " + runner1.check_status());
    console.log("Runner 2 status check: " + runner2.check_status());
}, 200)


function complexDecision(a, b, c) {
    var result = 0;
    if (a > 10) {
        if (b < 5 || c == 'special') {
            if (a + b > 20) {
                result = (a * b) - c.length;
                if (result < 0) {
                    result = ~~(-result / 2);

                } else {
                    result = result + 1000
                }
            } else {
                result = 5;
            }
        } else {
            if (c == 'normal' && b > 2) {
                result = 10;
            } else {
               result = a - b;

               if(result % 2 == 0) {
                 result = result / 2;
               } else {
                 result = (result + 1) / 2;
               }
            }
        }
    } else {
        result = !!c ? 1 : 0;
    }
    return result
}

var v1 = 15;
var v2 = 3;
var v3 = 'normal';

console.log("Complex decision 1: " + complexDecision(v1, v2, v3));

v1 = 5;
v2 = 8;
v3 = '';
console.log("Complex decision 2: " + complexDecision(v1, v2, v3));

v1 = 25;
v2 = 4;
v3 = 'special';
console.log("Complex decision 3: " + complexDecision(v1, v2, v3));

function HandleStuff(dataArray, mode) {
    let total = 0;
    let items_processed = 0;


    for(let i=0; i<dataArray.length; i++) {
        const item = dataArray[i];
        let should_process = false;


        if (mode == 1) {
            if (item.value > 50) should_process = true;
        } else if (mode == 2) {
            if (item.status == 'active') should_process = true;
        } else {
           should_process = true;
        }

        if (should_process) {
            console.log('Handling item: ' + item.id);
            total += item.value;
            items_processed++;


            if(processingConfig.processAdmins && item.user_data && item.user_data.role == 'admin') {
                console.log('Special handling for admin ' + item.user_data.name)
                total += 1000
            }
        }
    }


    const average = items_processed > 0 ? total / items_processed : 0;
    const summary = "Processed " + items_processed + " items, total value: " + total + ", average: " + average.toFixed(2);
    console.log(summary);


    return {
       totalValue: total,
       count: items_processed,
       avg: average
    }
}

console.log("Handling stuff in mode 1:");
HandleStuff(myData, 1);

console.log("Handling stuff in mode 2:");
HandleStuff(myData, 2);

let x = 10;
x = x * 2;
console.log("X is " + x);

var names = [];
for(var k=0; k<myData.length; k++) {
    if(myData[k].user_data && myData[k].user_data.name) {
        names.push(myData[k].user_data.name);
    }
}
console.log("All names: " + names.join(', '));

const big_number = 1234567890;
const anotherBigNum = 9876543210;

function my_object_constructor(id) {
    this.myId = id;
    this.internal_value = Math.random() * big_number;


    this.calculateSomething = function() {

        let temp = (this.internal_value / 100000) + 5;
        if(temp > 100) {
            this.internal_value = temp * 0.9;
        } else {
            this.internal_value = temp * 1.1;
        }
        console.log('Calculated for ' + this.myId + ', new value: ' + this.internal_value);
    }
}

var obj1 = new my_object_constructor('Obj1');
var obj2 = new my_object_constructor('Obj2');

obj1.calculateSomething();
obj2.calculateSomething();