<CodingStandards>
  <Rule_1 title="Naming Conventions">
    <Description_1>
      Use meaningful names
    </Description_1>
    <BadCodeExample_1>
const result = allOrders.length - completeOrders.length;
    </BadCodeExample_1>
    <GoodCodeExample_1>
const amountOfIncompleteOrders = allOrders.length - completeOrders.length;
    </GoodCodeExample_1>
  </Rule_1>

  <Rule_2 title="Naming Conventions">
    <Description_2>
      Use `camelCase` when naming functions and variables.
    </Description_2>
    <BadCodeExample_2>
      let user_name = "John";
      function get_data() { /* ... */ }
    </BadCodeExample_2>
    <GoodCodeExample_2>
      const userName = "John";
      const getData = () => { /* ... */ };
    </GoodCodeExample_2>
  </Rule_2>

  <Rule_3 title="Naming Conventions">
    <Description_3>
      Use `camelCase` for object keys.
    </Description_3>
    <BadCodeExample_3>
      const user = { user_id: 1, first_name: "Jane" };
    </BadCodeExample_3>
    <GoodCodeExample_3>
      const user = { userId: 1, firstName: "Jane" };
    </GoodCodeExample_3>
  </Rule_3>

  <Rule_4 title="Naming Conventions">
    <Description_4>
      Use `snake_case` for object keys of database records.
    </Description_4>
    <BadCodeExample_4>
      // Assuming this object comes directly from a DB query result
      const dbRecord = { userId: 1, firstName: "Jane" };
    </BadCodeExample_4>
    <GoodCodeExample_4>
      // Assuming this object comes directly from a DB query result
      const dbRecord = { user_id: 1, first_name: "Jane" };
    </GoodCodeExample_4>
  </Rule_4>

  <Rule_5 title="Naming Conventions">
    <Description_5>
      Use `PascalCase` when naming constructors functions, classes and types.
    </Description_5>
    <BadCodeExample_5>
class userProfile { /* ... */ }
function dataProcessor() { /* ... */ } // Assuming this is a constructor
/** @typedef {object} tagData */
    </BadCodeExample_5>
    <GoodCodeExample_5>
class UserProfile { /* ... */ }
function DataProcessor() { /* ... */ } // Assuming this is a constructor
/** @typedef {object} TagData */
    </GoodCodeExample_5>
  </Rule_5>

  <Rule_6 title="Naming Conventions">
    <Description_6>
      Use `SCREAMING_SNAKE_CASE` when naming constant, static values.
    </Description_6>
    <BadCodeExample_6>
const windowSize = 50;
const maxRetries = 3;
    </BadCodeExample_6>
    <GoodCodeExample_6>
const WINDOW_SIZE = 50;
const MAX_RETRIES = 3;
    </GoodCodeExample_6>
  </Rule_6>

  <Rule_7 title="Naming Conventions">
    <Description_7>
      Function names should be verbs.
    </Description_7>
    <BadCodeExample_7>
const candidatesOf = familyId => {...} // Noun phrase
const user = id => {...} // Noun
    </BadCodeExample_7>
    <GoodCodeExample_7>
const generateCandidates = familyId => {...} // Verb phrase
const getUserById = id => {...} // Verb phrase
    </GoodCodeExample_7>
  </Rule_7>

  <Rule_8 title="Naming Conventions">
    <Description_8>
      Predicate names should be questions. (Typically starting with is, has, should, does, etc.)
    </Description_8>
    <BadCodeExample_8>
const serviceRecalculation = service => {...} // Noun phrase implies action, not check
const trainerStatus = trainer => {...} // Noun implies getting status, not checking if stuck
const retryCheck = candidateStatus => {...} // Noun implies an action, not a condition
    </BadCodeExample_8>
    <GoodCodeExample_8>
const doesServiceNeedRecalculation = service => {...}
const isTrainerStuck = trainer => {...}
const shouldRetry = candidateStatus => {...}
const isCandidateOfFamily = (candidate, family) => {...}
    </GoodCodeExample_8>
  </Rule_8>

  <Rule_9 title="Naming Conventions">
    <Description_9>
      Avoid abbreviating variable names:
    </Description_9>
    <BadCodeExample_9>
const fid = service.familyId;
const req = getRequest();
    </BadCodeExample_9>
    <GoodCodeExample_9>
const familyId = service.familyId;
const request = getRequest();
    </GoodCodeExample_9>
  </Rule_9>

  <Rule_10 title="Naming Conventions">
    <Description_10>
      Names of private methods inside classes should start with a underscore (`_`):
    </Description_10>
    <BadCodeExample_10>
class DataProcessor {
    process() {
        const isValid = this.checkValidity(); // Ambiguous if public or private helper
        // ...
    }

    checkValidity() { // Might be intended as private, but not marked
       // ...
    }
}
    </BadCodeExample_10>
    <GoodCodeExample_10>
class DataProcessor {
    process() {
        const isValid = this._checkValidity(); // Clearly calls a private helper
        // ...
    }

    /** @private */
    _checkValidity() { // Marked private by convention and potentially JSDoc
       // ...
    }

    _isCandidatesGenerationProcessRunning(serviceFamilyId) {
        // ...
    }
}
    </GoodCodeExample_10>
  </Rule_10>

  <Rule_11 title="No Magic Values">
    <Description_11>
      Avoid using magic values (unnamed constants). Define them with meaningful names.
    </Description_11>
    <BadCodeExample_11>
if (timeElapsed > 500) { /* ... */ }
if (user.role === 2) { /* ... */ }
    </BadCodeExample_11>
    <GoodCodeExample_11>
const MAX_TIME_ELAPSED_MS = 500;
const ADMIN_ROLE_ID = 2;

if (timeElapsed > MAX_TIME_ELAPSED_MS) { /* ... */ }
if (user.role === ADMIN_ROLE_ID) { /* ... */ }
    </GoodCodeExample_11>
  </Rule_11>

  <Rule_12 title="Formatting Large Numbers">
    <Description_12>
      Write numbers with numeric separators (`_`) for readability.
    </Description_12>
    <BadCodeExample_12>
const WINDOW_SIZE = 1000000;
const MIN_SALARY = 50000;
    </BadCodeExample_12>
    <GoodCodeExample_12>
const WINDOW_SIZE = 1_000_000;
const MIN_SALARY = 50_000;
    </GoodCodeExample_12>
  </Rule_12>

  <Rule_13 title="Enumerated Values">
    <Description_13>
      When you have a field with a limited set of known values, create an enum-like object to represent the set of values.
    </Description_13>
    <BadCodeExample_13>
const status = '2'; // What does '2' mean?
if (order.status === 'completed') { /* ... */ } // Prone to typos
    </BadCodeExample_13>
    <GoodCodeExample_13>
const Statuses = {
    PENDING: '0',
    IN_PROGRESS: '1',
    DONE: '2',
    COMPLETED: 'completed', // Can mix types if needed, but consistent type preferred
};
Object.freeze(Statuses); // Prevent modification

const status = Statuses.DONE;
if (order.status === Statuses.COMPLETED) { /* ... */ }
    </GoodCodeExample_13>
  </Rule_13>

  <Rule_14 title="No Implicit Conversions">
    <Description_14>
      Avoid using operators (`!!`, `~~`, `+`, `+ ''`) for implicit type conversions. Use explicit conversion functions/methods.
    </Description_14>
    <BadCodeExample_14>
if (!!candidates.length) {/* ... */ } // Use boolean operator for bool conversion
const intAverage = ~~(sum / amount); // Use bitwise NOT for floor
const age = +request.body.age; // Use unary plus for number conversion
const status = value + ''; // Use string concat for string conversion
    </BadCodeExample_14>
    <GoodCodeExample_14>
if (candidates.length > 0) {/* ... */ } // Explicit comparison
// OR if boolean needed:
if (Boolean(candidates.length)) { /* ... */ }

const intAverage = Math.floor(sum / amount); // Explicit floor
const age = Number(request.body.age); // Explicit number conversion
const status = String(value); // Explicit string conversion
// OR
const status = value.toString();
    </GoodCodeExample_14>
  </Rule_14>

  <Rule_15 title="Early Return over Nested Ifs">
    <Description_15>
      Use guard clauses and return early to reduce nesting and improve readability.
    </Description_15>
    <BadCodeExample_15>
const generateCandidates = familyId => {
    let result;
    if (doesFamilyExist(familyId)) { // Condition 1
        if (isCandidatesGenerationInProgress(familyId)) { // Condition 2
            result = { status: 'error', message: 'Candidates generation already in progress' };
        }
        else { // Condition 2 else
            result = { status: 'success', message: 'Candidates generation started' };
            startCandidatesGeneration(familyId);
        }
    }
    else { // Condition 1 else
        result = { status: 'error', message: 'Family does not exist' };
    }
    return result; // Single return point, but deep nesting
};
    </BadCodeExample_15>
    <GoodCodeExample_15>
const generateCandidates = familyId => {
    // Guard clause 1
    if (!doesFamilyExist(familyId)) {
        return { status: 'error', message: 'Family does not exist' }; // Early return
    }

    // Guard clause 2
    if (isCandidatesGenerationInProgress(familyId)) {
        return { status: 'error', message: 'Candidates generation already in progress' }; // Early return
    }

    // Main logic path
    startCandidatesGeneration(familyId);
    return { status: 'success', message: 'Candidates generation started' };
};
    </GoodCodeExample_15>
  </Rule_15>

  <Rule_16 title="Expressions over Statements">
    <Description_16>
      Prefer using expressions (like ternary operators, array methods) over statements (like `if`/`else`, `for` loops) for assignments or creating derived data when it improves conciseness and clarity.
    </Description_16>
    <BadCodeExample_16>
// Conditional assignment using statements
let service;
if (!servicesNames.includes(name)) {
    service = new Service(name);
} else {
    service = null;
}

// Iterative creation using statements
let validServices = [];
for (let service of services) {
    if (service.isValid()) {
        validServices.push(service);
    }
}
    </BadCodeExample_16>
    <GoodCodeExample_16>
// Conditional assignment using ternary expression
const service = !serviceNames.includes(name)
    ? new Service(name)
    : null;

// Iterative creation using filter expression
const validServices = services.filter(service => service.isValid());
    </GoodCodeExample_16>
  </Rule_16>

  <Rule_17 title="Use Semicolons">
    <Description_17>
      Always use semicolons at the end of statements.
    </Description_17>
    <BadCodeExample_17>
if (shouldUpdateCandidates) {
    const candidates = getFamilyCandidates(familyId) // Missing semicolon
    console.log('Candidates fetched') // Missing semicolon
}
    </BadCodeExample_17>
    <GoodCodeExample_17>
if (shouldUpdateCandidates) {
    const candidates = getFamilyCandidates(familyId); // Semicolon present
    console.log('Candidates fetched'); // Semicolon present
}
    </GoodCodeExample_17>
  </Rule_17>

  <Rule_18 title="Arrow Functions">
    <Description_18>
      Use arrow functions (`=>`) instead of the `function` keyword for function expressions.
    </Description_18>
    <BadCodeExample_18>
function isCandidateOfFamily(candidate, familyId) {
    // ...
}

const sum = function(a, b) {
    return a + b;
};
    </BadCodeExample_18>
    <GoodCodeExample_18>
const isCandidateOfFamily = (candidate, familyId) => {
    // ...
};

const sum = (a, b) => {
    return a + b;
};

// Implicit return for single expression
const multiply = (a, b) => a * b;
    </GoodCodeExample_18>
  </Rule_18>

  <Rule_19 title="Arrow Functions">
    <Description_19>
      In arrow functions, omit parentheses around the parameter list if there is exactly one parameter and no type annotation.
    </Description_19>
    <BadCodeExample_19>
const getFamilyCandidates = (familyId) => { // Unnecessary parentheses
    // ...
};

const square = (x) => x * x; // Unnecessary parentheses
    </BadCodeExample_19>
    <GoodCodeExample_19>
const getFamilyCandidates = familyId => { // No parentheses needed
    // ...
};

const square = x => x * x; // No parentheses needed

// Keep parentheses if there are zero, or more than one parameter, or for type hints/destructuring
const log = () => console.log('Done');
const add = (a, b) => a + b;
const getName = ({ name }) => name; // Parentheses needed for destructuring
    </GoodCodeExample_19>
  </Rule_19>

  <Rule_20 title="Loops">
    <Description_20>
      Don't use imperative `for` loops (like `for (let i=0;...)` or `for...of` when mutation isn't needed). Instead, prefer functional array methods (`map`, `filter`, `reduce`, `some`, `every`, `forEach`, etc.).
    </Description_20>
    <BadCodeExample_20>
// Filtering with for loop
const activeUsers = [];
for (let i = 0; i < users.length; i++) {
    if (users[i].isActive) {
        activeUsers.push(users[i]);
    }
}

// Mapping with for...of loop
const userNames = [];
for (const user of users) {
    userNames.push(user.name);
}
    </BadCodeExample_20>
    <GoodCodeExample_20>
// Filtering with .filter()
const activeUsers = users.filter(({ isActive }) => isActive);

// Mapping with .map()
const userNames = users.map(user => user.name);

// Use forEach for side effects if necessary
users.forEach(user => console.log(user.name));
    </GoodCodeExample_20>
  </Rule_20>

  <Rule_21 title="Variables">
    <Description_21>
      Use only `const`. Do not use `let` or `var`. Strive to write code where variables do not need reassignment.
    </Description_21>
    <BadCodeExample_21>
var count = 0; // Avoid var
let total = 100; // Avoid let if reassignment isn't strictly necessary
if (condition) {
    total = total + 50; // Reassignment
}
    </BadCodeExample_21>
    <GoodCodeExample_21>
const count = 0; // Use const
const initialTotal = 100;
const total = condition ? initialTotal + 50 : initialTotal; // Calculate final value without reassignment

// If state truly needs to change over time (rare in functional style),
// prefer managing state explicitly (e.g., in reducers, state machines)
// rather than arbitrary 'let' reassignments scattered in functions.
    </GoodCodeExample_21>
  </Rule_21>

  <Rule_22 title="Variables">
    <Description_22>
      Use object and array destructuring, but destructure at most three fields in a function's parameter list. For more fields, destructure inside the function body.
    </Description_22>
    <BadCodeExample_22>
// Too many destructured parameters
const displayUserInfo = ({ name, age, country, email, phone, address }) => {
    console.log(name, age, country, email, phone, address);
};
    </BadCodeExample_22>
    <GoodCodeExample_22>
// OK: Few parameters destructured
const displayCandidate = ({ candidateId, familyId, status }) => {
    gs.info(`Candidate ID: ${candidateId}`);
    gs.info(`Candidate Family ID: ${familyId}`);
    gs.info(`Status: ${status}`);
};

// Better for many properties: Pass the object, destructure inside
const displayUserInfo = user => {
    const { name, age, country, email, phone, address } = user;
    console.log(name, age, country, email, phone, address);
};
    </GoodCodeExample_22>
  </Rule_22>

  <Rule_23 title="Variables">
    <Description_23>
      Avoid using nested destructuring directly in a function parameter list. Destructure nested properties inside the function body.
    </Description_23>
    <BadCodeExample_23>
// Nested destructuring in parameter list (harder to read signature)
const displayUserAddress = ({ name, address: { street, city, zip } }) => {
    console.log(`${name} lives at ${street}, ${city} ${zip}`);
};
    </BadCodeExample_23>
    <GoodCodeExample_23>
// Destructure top-level, then nested properties inside
const displayUserAddress = ({ name, address }) => {
    const { street, city, zip } = address; // Nested destructuring done here
    console.log(`${name} lives at ${street}, ${city} ${zip}`);
};
    </GoodCodeExample_23>
  </Rule_23>

  <Rule_24 title="Nullish Values">
    <Description_24>
      Use optional chaining (`?.`) to safely access nested properties that might be null or undefined.
    </Description_24>
    <BadCodeExample_24>
let firstName = 'Guest';
if (user && user.profile && user.profile.name && user.profile.name.first) {
    firstName = user.profile.name.first;
}
console.log(firstName);
    </BadCodeExample_24>
    <GoodCodeExample_24>
// Access nested property safely, provides undefined if path breaks
const firstName = user?.profile?.name?.first;
console.log(firstName ?? 'Guest'); // Use nullish coalescing for default
    </GoodCodeExample_24>
  </Rule_24>

  <Rule_25 title="Nullish Values">
    <Description_25>
      Use the nullish coalescing operator (`??`) to provide default values for potentially null or undefined variables. Avoid `||` for defaults when falsy values (like `0`, `false`, or `''`) are valid inputs.
    </Description_25>
    <BadCodeExample_25>
// Using || for default: BAD if 0, '', false are valid values
const timeout = settings.timeout || 5000; // If settings.timeout is 0, result is 5000 (wrong)
const userName = user.name || 'Anonymous'; // If user.name is '', result is 'Anonymous' (maybe wrong)
const address = user.address ? user.address : 'No address provided'; // Verbose ternary
    </BadCodeExample_25>
    <GoodCodeExample_25>
// Using ?? for default: GOOD, only triggers for null or undefined
const timeout = settings.timeout ?? 5000; // If settings.timeout is 0, result is 0 (correct)
const userName = user.name ?? 'Anonymous'; // If user.name is '', result is '' (correct)
const address = user.address ?? 'No address provided'; // Concise and correct default
const retryAmount = candidate.retryAmount ?? 3; // If candidate.retryAmount is 0, result is 0
    </GoodCodeExample_25>
  </Rule_25>

  <Rule_26 title="String Values">
    <Description_26>
      Use template literals (backticks `` `${}` ``) for string interpolation instead of string concatenation (`+`).
    </Description_26>
    <BadCodeExample_26>
const name = 'John';
const age = 30;
const message = 'Hello, my name is ' + name + ' and I am ' + age + ' years old.';
console.log(message);
    </BadCodeExample_26>
    <GoodCodeExample_26>
const name = 'John';
const age = 30;
const message = `Hello, my name is ${name} and I am ${age} years old.`;
console.log(message);
    </GoodCodeExample_26>
  </Rule_26>

  <Rule_27 title="Extract to functions">
    <Description_27>
      Follow the Single Responsibility Principle (SRP): Functions should do one thing well.
    </Description_27>
    <BadCodeExample_27>
// Function does filtering, sorting, AND displaying
const processAndDisplayUsers = users => {
  const active = [];
  for (let i = 0; i < users.length; i++) { if (users[i].isActive) { active.push(users[i]); } } // Filter
  active.sort((a, b) => new Date(b.lastLogin) - new Date(a.lastLogin)); // Sort
  console.log('Active Users:'); // Display Header
  for (let i = 0; i < active.length; i++) { console.log(`${active[i].name}`); } // Display Data
}
    </BadCodeExample_27>
    <GoodCodeExample_27>
// Each function has one responsibility
const getActiveUsers = users => users.filter(({ isActive }) => isActive); // Filter
const sortByLastLogin = users => [...users].sort((a, b) => new Date(b.lastLogin) - new Date(a.lastLogin)); // Sort (immutable)
const displayUserNames = users => { // Display
    console.log('Active Users:');
    users.forEach(user => console.log(user.name));
};

const processAndDisplayUsers = users => { // Composition
    const activeUsers = getActiveUsers(users);
    const sortedUsers = sortByLastLogin(activeUsers);
    displayUserNames(sortedUsers);
};
    </GoodCodeExample_27>
  </Rule_27>

  <Rule_28 title="Extract to functions">
    <Description_28>
      Extract code to a new function when a block of code can be described with a meaningful name.
    </Description_28>
    <BadCodeExample_28>
const processOrder = order => {
    // ... some setup ...

    // Check inventory and reserve stock
    let stockAvailable = true;
    for (const item of order.items) {
        const currentStock = inventory.getStock(item.productId);
        if (currentStock < item.quantity) {
            stockAvailable = false;
            break;
        }
    }
    if (!stockAvailable) {
        return { status: 'error', message: 'Insufficient stock' };
    }
    for (const item of order.items) {
        inventory.reserveStock(item.productId, item.quantity);
    }
    // ... rest of processing ...
};
    </BadCodeExample_28>
    <GoodCodeExample_28>
const checkAndReserveStock = orderItems => { // Meaningful name for the block
    for (const item of orderItems) {
        const currentStock = inventory.getStock(item.productId);
        if (currentStock < item.quantity) {
            // Throwing error or returning status handled inside or by caller
            throw new Error(`Insufficient stock for product ${item.productId}`);
        }
    }
    // If checks pass, reserve stock
    for (const item of orderItems) {
        inventory.reserveStock(item.productId, item.quantity);
    }
    return true; // Indicate success
};

const processOrder = order => {
    // ... some setup ...
    try {
        checkAndReserveStock(order.items); // Use the extracted function
    } catch (error) {
        return { status: 'error', message: error.message };
    }
    // ... rest of processing ...
};
    </GoodCodeExample_28>
  </Rule_28>

  <Rule_29 title="Extract to functions">
    <Description_29>
      Extract code to a new function when a block has a single, focused responsibility (supports SRP).
    </Description_29>
    <BadCodeExample_29>
// Calculation and formatting mixed
const displayTotal = (price, quantity, taxRate) => {
    const subtotal = price * quantity;
    const tax = subtotal * taxRate;
    const total = subtotal + tax;
    console.log(`Total amount: $${total.toFixed(2)}`); // Calculation and formatting
};
    </BadCodeExample_29>
    <GoodCodeExample_29>
// Responsibility 1: Calculate total
const calculateTotal = (price, quantity, taxRate) => {
    const subtotal = price * quantity;
    const tax = subtotal * taxRate;
    return subtotal + tax;
};

// Responsibility 2: Format amount
const formatCurrency = amount => `$${amount.toFixed(2)}`;

// Responsibility 3: Display (using the other functions)
const displayTotal = (price, quantity, taxRate) => {
    const total = calculateTotal(price, quantity, taxRate);
    const formattedTotal = formatCurrency(total);
    console.log(`Total amount: ${formattedTotal}`);
};
    </GoodCodeExample_29>
  </Rule_29>

  <Rule_30 title="Extract to functions">
    <Description_30>
      Extract code to a new function when a block is reused or could potentially be reused elsewhere (DRY Principle).
    </Description_30>
    <BadCodeExample_30>
const processTypeA = data => {
    // Validation logic A, B, C
    if (!isValidA(data)) return false;
    if (!isValidB(data)) return false;
    if (!isValidC(data)) return false;
    // Process A
};

const processTypeB = data => {
    // Validation logic A, B, C (Duplicated)
    if (!isValidA(data)) return false;
    if (!isValidB(data)) return false;
    if (!isValidC(data)) return false;
    // Process B
};
    </BadCodeExample_30>
    <GoodCodeExample_30>
// Reusable validation function
const runStandardValidations = data => {
    if (!isValidA(data)) throw new Error('Validation A failed');
    if (!isValidB(data)) throw new Error('Validation B failed');
    if (!isValidC(data)) throw new Error('Validation C failed');
};

const processTypeA = data => {
    runStandardValidations(data); // Reuse validation logic
    // Process A
};

const processTypeB = data => {
    runStandardValidations(data); // Reuse validation logic
    // Process B
};
    </GoodCodeExample_30>
  </Rule_30>

  <Rule_31 title="JSDoc">
    <Description_31>
      Declare new custom types using JSDoc's `@typedef`. Use `@prop` for object properties.
    </Description_31>
    <BadCodeExample_31>
      // No type definition, relies on inline comments or guesswork
      const processItem = item => {
          // item should have an id (string) and tags (array of {key: string, value: string})
          console.log(item.id);
      }
    </BadCodeExample_31>
    <GoodCodeExample_31>
/**
 * Represents a tag with a key and value.
 * @typedef {object} Tag
 * @prop {string} key - The identifier for the tag.
 * @prop {string} value - The value associated with the tag.
 */

/**
 * Represents details of a candidate.
 * @typedef {object} CandidateDetails
 * @prop {string} name - The full name of the candidate.
 * @prop {Tag[]} tags - A list of tags associated with the candidate.
 * @prop {number} [age] - Optional age of the candidate.
 */

// Now functions can use these types
/**
 * @param {CandidateDetails} candidate
 */
const processCandidate = candidate => {
    console.log(candidate.name);
    candidate.tags.forEach(tag => console.log(tag.key));
};
    </GoodCodeExample_31>
  </Rule_31>

  <Rule_32 title="JSDoc">
    <Description_32>
      Declare variable types using JSDoc's `@type`, but *only* when the type cannot be easily inferred by the IDE or TypeScript (e.g., complex initializations, reassignments from different types - though reassignment is discouraged).
    </Description_32>
    <BadCodeExample_32>
/** @type {string} */ // Redundant, type is obvious
const name = 'John Doe';

/** @type {number[]} */ // Redundant, type is obvious
const ids = [1, 2, 3];
    </BadCodeExample_32>
    <GoodCodeExample_32>
// Good: Type is less obvious or needs clarification (e.g., from external source)
/** @type {import('./api-types').UserProfile} */
const userProfile = await fetchUserProfile(userId);

// Good: Initialized as empty, but will hold specific type
/** @type {Tag[]} */
const tags = [];
tags.push({ key: 'dept', value: 'eng' });

// Good: Complex object literal where type helps readability/tooling
/** @type {CandidateDetails} */
const candidateDetails = {
    name: 'Jane Doe',
    tags: [{ key: 'skill', value: 'javascript' }]
    // Age is optional per typedef, so omitting is fine
};
    </GoodCodeExample_32>
  </Rule_32>

  <Rule_33 title="JSDoc">
    <Description_33>
      Document functions using JSDoc: Include a description, use `@param` for parameters (with types and description), and `@returns` for the return value (with type and description).
    </Description_33>
    <BadCodeExample_33>
      // No documentation
      const checkTag = (candidate, tagKey) => {
          return candidate.tags.some(({ key }) => key == tagKey);
      };
    </BadCodeExample_33>
    <GoodCodeExample_33>
/**
 * Checks if a candidate possesses a tag with the specified key.
 *
 * @param {CandidateDetails} candidate - The candidate object to check.
 * @param {string} tagKey - The tag key to look for.
 * @returns {boolean} True if the candidate has a tag with the given key, false otherwise.
 */
const doesCandidateHaveTagKey = (candidate, tagKey) => {
    // Ensure candidate and tags exist to avoid errors
    if (!candidate?.tags) {
        return false;
    }
    return candidate.tags.some(({ key }) => key === tagKey); // Use ===
};
    </GoodCodeExample_33>
  </Rule_33>

  <Rule_34 title="JSDoc">
    <Description_34>
      Document curried functions by showing the type signature of the returned function in the `@returns` tag.
    </Description_34>
    <BadCodeExample_34>
/**
 * Creates a function to count candidates for a family.
 * @param {CandidatesDAO} candidatesDAO
 * @returns {function} // Not specific enough
 */
const countCandidateOfFamily = candidatesDAO =>
    familyId => {
        // ... implementation using candidatesDAO and familyId ...
        return candidatesDAO.count({ familyId });
    };
    </BadCodeExample_34>
    <GoodCodeExample_34>
/**
 * @typedef {object} CandidatesDAO
 * @prop {(filter: object) => number} count - Counts candidates based on filter.
 */

/**
 * Creates a function that counts candidates for a specific family ID using the provided DAO.
 * @param {CandidatesDAO} candidatesDAO - The data access object for candidates.
 * @returns {(familyId: string) => number} A function that takes a familyId and returns the count.
 */
const countCandidateOfFamily = candidatesDAO =>
    /**
     * Counts candidates for the given family ID.
     * @param {string} familyId - The ID of the family.
     * @returns {number} The number of candidates in that family.
     */
    familyId => {
        // ... implementation using candidatesDAO and familyId ...
        return candidatesDAO.count({ family_id: familyId }); // Assuming DAO expects snake_case
    };
    </GoodCodeExample_34>
  </Rule_34>

  <Rule_35 title="JSDoc">
    <Description_35>
      Mark internal/private class methods with the JSDoc `@private` tag (in addition to the `_` prefix convention).
    </Description_35>
    <BadCodeExample_35>
class CandidateService {
    // Might be intended as private, but lacks JSDoc tag
    _isGenerationRunning(familyId) {
        // ...
    }

    generateCandidates(familyId) {
       if (this._isGenerationRunning(familyId)) {
           // ...
       }
    }
}
    </BadCodeExample_35>
    <GoodCodeExample_35>
class CandidateService {
    /**
     * Checks if the candidate generation process is currently active for a family.
     * Should not be called from outside the class.
     * @private
     * @param {string} serviceFamilyId - The family ID.
     * @returns {boolean} True if generation is running, false otherwise.
     */
    _isCandidatesGenerationProcessRunning(serviceFamilyId) {
        // ... implementation ...
        return internalState.isRunning(serviceFamilyId);
    }

    generateCandidates(familyId) {
       if (this._isCandidatesGenerationProcessRunning(familyId)) {
           console.warn('Generation already in progress for', familyId);
           return;
       }
       // ... start generation ...
    }
}
    </GoodCodeExample_35>
  </Rule_35>

  <Rule_36 title="JSDoc">
    <Description_36>
      Use editor/IDE regions (`//#region name` ... `//#endregion name`) to group related JSDoc `@typedef` definitions for better organization, especially in files with many type definitions.
    </Description_36>
    <BadCodeExample_36>
      // Types scattered throughout the file or preamble without grouping
      /** @typedef {object} User ... */
      // ... some code ...
      /** @typedef {object} Order ... */
      // ... more code ...
      /** @typedef {object} Product ... */
    </BadCodeExample_36>
    <GoodCodeExample_36>
//#region Type Definitions

/**
 * @typedef {object} Tag
 * @prop {string} key
 * @prop {string} value
 */

/**
 * @typedef {object} CandidateDetails
 * @prop {string} name
 * @prop {Tag[]} tags
 */

/**
 * @typedef {object} ProcessingStatus
 * @prop {string} statusId
 * @prop {string} message
 */

//#endregion Type Definitions

// --- Rest of the code ---

/**
 * @param {CandidateDetails} details
 * @returns {ProcessingStatus}
 */
const processCandidate = details => {
    // ... function logic ...
    return { statusId: 'done', message: 'Processed successfully' };
};
    </GoodCodeExample_36>
  </Rule_36>

  <Rule_37 title="Comments">
    <Description_37>
      Avoid comments. Code should be self-documenting through clear naming and structure.
    </Description_37>
    <BadCodeExample_37>
      // This function checks if the user is active
      const checkUser = u => u.active; // Comment explains obvious code

      // Temporary variable for calculation
      let temp = x * y; // Comment explains obvious variable
    </BadCodeExample_37>
    <GoodCodeExample_37>
      // Function name makes the comment redundant
      const isUserActive = user => user.active;

      // Variable name makes the comment redundant
      const subtotal = price * quantity;
    </GoodCodeExample_37>
  </Rule_37>

  <Rule_38 title="Comments">
    <Description_38>
      Instead of commenting a block of code to explain its purpose, extract it into a function with a meaningful name.
    </Description_38>
    <BadCodeExample_38>
// Check if the current tag value is one of the values defined in the category.
const tagValuesDef = category2DefinitionValues[category];
let isInCategory = false;
if (tagValuesDef && tagValuesDef.tags && tagValuesDef.tags[value] !== undefined) {
    isInCategory = true;
}

if (isInCategory) {
    // ... process tag ...
}
    </BadCodeExample_38>
    <GoodCodeExample_38>
// Extracted function with a name that explains the purpose
const isTagValueInCategory = (tagValue, category) => {
    const categoryDefinition = category2DefinitionValues[category];
    // Using optional chaining and nullish check for clarity
    return categoryDefinition?.tags?.[tagValue] !== undefined;
    // Original example used isNil check, assuming similar null/undefined check logic:
    // return categoryDefinition && !isNil(categoryDefinition.tags[tagValue]);
};

// Call the self-documenting function
if (isTagValueInCategory(value, category)) {
    // ... process tag ...
}
    </GoodCodeExample_38>
  </Rule_38>

  <Rule_39 title="Comments">
    <Description_39>
      Instead of commenting on the changing role of a variable within a function, use different variables with names reflecting their specific roles in each context.
    </Description_39>
    <BadCodeExample_39>
const processTransition = transition => {
    // 'manipulation' has different meanings depending on the branch
    const { letters, stackLetters, manipulation } = transition;

    if (isPopTransition(transition)) {
        // Here, manipulation represents a pop indicator (e.g., number of items to pop)
        return handlePopTransition(letters, stackLetters, manipulation);
    } else {
        // Here, manipulation represents the letters (string/array) to be pushed onto the stack
        return handlePushTransition(letters, stackLetters, manipulation);
    }
};
    </BadCodeExample_39>
    <GoodCodeExample_39>
const processTransition = transition => {
    const { letters, stackLetters, manipulation } = transition; // Initial destructuring

    if (isPopTransition(transition)) {
        // Assign to a new const with a context-specific name
        const popIndicator = manipulation;
        return handlePopTransition(letters, stackLetters, popIndicator);
    } else {
        // Assign to a new const with a different context-specific name
        const pushLetters = manipulation;
        return handlePushTransition(letters, stackLetters, pushLetters);
    }
};
    </GoodCodeExample_39>
  </Rule_39>
</CodingStandards>
