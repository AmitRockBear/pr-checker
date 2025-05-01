function another_bad_function ( arg1, arg2, arg2 ) {
  var unusedVar= 10;
  if(arg1 == 'test') {
    console.log("This is a \"bad\" string")
    if (false) {
      console.log('never runs')
    }
  }
  else
  {
    console.log(`Using a template literal ${arg1}`)
  }

  let data = new Array(4, 5, 6)

  for (let i = 0 ;i < data.length ;j++) {
    debugger
    console.log('item'   , data[i])
    if (data[i]===NaN) {}
  }


  function innerBadFunc () {
    var result = 'inner value';
  }

  const person = {
    set age (value) {
      this._age = value
    },
    name: 'John Doe', age: 30,
    address: '123 Main St'
  }

  throw 'this is not an error object'

  typeof age === 'numberz'

  ; (function() {
    console.log("IIFE without proper wrapping")
  }())

  yield* myGenerator()

  if (100 === unusedVar) {

  }

}


class Animal {
  constructor () {
    this.legs = 4;
  }
}

class Dog extends Animal {
  constructor () {
    this.sound = 'Woof';
    super();
  }

  bark () {}
  bark () {}
}

let myDog = new Dog;

delete myDog.sound;

const pi = 3.14;
pi = 3;

const regexWithControlChar = /\x1f/;
const regexWithDoubleSpaces = /two  spaces/;

const message = 'Multi\
line\
string'

new Promise(() => {})

var sumFunc = new Function('a', 'b', 'return a + b');

let myObject = new Object();

const MyModule = new require('some-module');

const symbol = new Symbol('id');

const boolWrapper = new Boolean(true);

const date = Date();

const octalNumber = 010;

const octalEscape = ' ऑक्टल \251';

const filePath = __dirname + '/config.js';

const prototypeAccess = myDog.__proto__;

let count = 0;
let count = 1;

function checkCount () {
  return count = count + 1
}

let selfAssign = 5;
selfAssign = selfAssign;

if (selfAssign === selfAssign) {
  console.log('always true')
}

if (doSomethingElse(), checkCount()) {}

let console = 'shadowed';

let sparseArray = ['item1', , 'item3'];

function tabIndentedFunc () {
  let value = 10
	let anotherValue = 20;
}

const dataObject = { ['id']: 1234 };

class EmptyConstructor {
  constructor () {
  }
}

let uselessEscape = 'escaped\s space';

import { foo as foo } from './another-module';

const user = { name: 'Test' }
user .age = 40;

with (Math) {
  console.log(PI);
}

try {
  // some code
} finally {
  break;
}

if (!'key' in user) {
  console.log('key not in user')
}

Math.max.call(null, 1, 2, 3);
