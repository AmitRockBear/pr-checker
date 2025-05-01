# Coding Standards

## Rational

Writing clean and consistent code is not just a matter of style - it aids in enhancing readability, maintainability, and testability.
<br/>
By following this set of conventions, our code will be more maintainable, will induce less cognitive load and will enable faster onboarding for new team members. 
<br/>
These standards aim to promote modular design and encourage functional programming principles.
<br/>
Ultimately, well-structured code is easier to refactor, scale, and extend — making it a long-term investment in the quality and resilience of the system.

## Overview
- [Names and Values](#names-and-values)
    - [Naming Conventions](#naming-conventions)
    - [No Magic Values](#no-magic-values)
    - [Formatting Large Numbers](#formatting-large-numbers)
    - [Enumerated Values](#enumerated-values)
    - [No Implicit Conversions](#no-implicit-conversions)
- [Control Flow](#control-flow)
    - [Early Return over Nested Ifs](#early-return-over-nested-ifs)
    - [Expressions over Statements](#expressions-over-statements)
    - [Use Semicolons](#use-semicolons)
- [Modern JavaScript](#modern-javascript)
    - [Arrow Functions](#arrow-functions)
    - [Loops](#loops)
    - [Variables](#variables)
    - [Nullish Values](#nullish-values)
    - [String Values](#string-values)
- [Code Design](#code-design)
    - [Extract to functions](#extract-to-functions)
- [Documentation](#documentation)
    - [JSDoc](#jsdoc)
    - [Comments](#comments)

## Names and Values

### Naming Conventions

- Use meaningful names:
  
  ```js
  // BAD
  const result = allOrders.length - completeOrders.length;
  
  // GOOD
  const amountOfIncompleteOrders = allOrders.length - completeOrders.length;
  ```

- Use `camelCase` when naming functions and variables.

- Use `camelCase` for object keys.

- Use `snake_case` for object keys of database records.

- Use `PascalCase` when naming constructors functions, classes and types.

- Use `SCREAMING_SNAKE_CASE` when naming constant, static values.
  
  ```js
  // BAD
  const windowSize = 50;
  
  // GOOD
  const WINDOW_SIZE = 50;
  ```

- Function names should be verbs.
  
  ```js
  // BAD
  const candidatesOf = familyId => {...}
  
  // GOOD
  const generateCandidates = familyId => {...}
  ```

- Predicate names should be questions.
  
  ```js
  const doesServiceNeedRecalculation = service => {...}
  const isTrainerStuck = trainer => {...}
  const shouldRetry = candidateStatus => {...}
  const isCandidateOfFamily = (candidate, family) => {...}
  ```

- Avoid abbreviating variable names:
  
  ```js
  // BAD
  const fid = ...;
  
  // GOOD
  const familyId = ...;
  ```

- Names of private methods inside classes should start with a underscore (`_`):
  
  ```js
  _isCandidatesGenerationProcessRunning(serviceFamilyId) {
      // ...
  }
  ```

### No Magic Values

Avoid using magic values:

```js
// BAD
if (timeElapsed > 500) { /* ... */ }

// GOOD
if (timeElapsed > MAX_TIME_ELAPSED) { /* ... */ }
```

### Formatting Large Numbers

Write numbers with numeric separators:

```js
// BAD
const WINDOW_SIZE = 1000000;

// GOOD
const WINDOW_SIZE = 1_000_000;
```

### Enumerated Values

When you have a field with a limited set of values, create an enum object to represent the set of values:

```js
// BAD
const status = '2';

// GOOD
const statuses = {
    PENDING: '0',
    IN_PROGRESS: '1',
    DONE: '2'
};

### No Implicit Conversions

Avoid using operators for implicit type conversions:

```js
// BAD
if (!!candidates.length) {/* ... */ }
const intAverage = ~~(sum / amount);
const age = +request.body.age;
const status = value + '';

// GOOD
if (candidates.length > 0) {/* ... */ }
const intAverage = Math.floor(sum / amount);
const age = Number(request.body.age);
const status = value.toString();
```

## Control Flow

### Early Return over Nested Ifs

```javascript
// BAD
const generateCandidates = familyId => {
    let result;
    if (doesFamilyExist(familyId)) {
        if (isCandidatesGenerationInProgress(familyId)) {
            result = { status: 'error', message: 'Candidates generation already in progress' };
        }
        else {
            result = { status: 'success', message: 'Candidates generation started' };
            startCandidatesGeneration(familyId);
        }
    }
    else {
        result = { status: 'error', message: 'Family does not exist' };
    }
    return result;
};

// GOOD
const generateCandidates = familyId => {
    if (!doesFamilyExist(familyId)) {
        return { status: 'error', message: 'Family does not exist' };
    }

    if (isCandidatesGenerationInProgress(familyId)) {
        return { status: 'error', message: 'Candidates generation already in progress' };
    }

    startCandidatesGeneration(familyId);
    return { status: 'success', message: 'Candidates generation started' };
};
```

### Expressions over Statements

Avoid using statements to conditionally or iteratively set a variable's value:

```js
// BAD
let service;
if (!servicesNames.includes(name)) {
    service = new Service(name);
} else {
    service = null;
}

// GOOD
const service = !serviceNames.includes(name) ?
    new Service(name) :
    null;
```

```js
// BAD
let validServices = [];
for (let service of services) {
    if (service.isValid()) {
        validServices.push(service);
    }
}

// GOOD
const validServices = services.filter(service => service.isValid());
```

### Use Semicolons

```js
// BAD
if (shouldUpdateCandidates) {
    const candidates = getFamilyCandidates(familyId)
}

// GOOD
if (shouldUpdateCandidates) {
    const candidates = getFamilyCandidates(familyId);
}
```

## Modern JavaScript

### Arrow Functions

- Use arrow functions instead of functions.
  
  ```js
  // BAD
  function isCandidateOfFamily(candidate, familyId) {
      // ...
  }
  
  // GOOD
  const isCandidateOfFamily = (candidate, familyId) => {
      // ...
  };
  ```

- In arrow functions, if there is only one parameter, don't use parenthesis.
  
  ```js
  // BAD
  function getFamilyCandidates(familyId) {
      // ...
  }
  
  // GOOD
  const getFamilyCandidates = familyId => {
      // ...
  };
  ```

### Loops

- Don't use `for` loops, instead use `Array`'s built in methods (`map`, `filter`, `reduce`, `some`, `every` and so on).
  
  ```js
  // BAD
  const activeUsers = [];
  for (let i = 0; i < users.length; i++) {
      if (users[i].isActive) {
          activeUsers.push(users[i]);
      }
  }
  
  // GOOD
  const activeUsers = users.filter(({ isActive }) => isActive);
  ```

### Variables

- Use only `const` (not `let` nor `var`).

- Use [destructuring](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring).
  
  - Destructure at most three fields in a function's parameter.
    
    ```js
    // BAD
    const displayUserInfo = ({ name, age, country, email }) => {
        // ...
    };
    
    // GOOD
    const displayUserInfo = user => {
        const { name, age, country, email } = user;
        // ...
    };
    
    // GOOD
    const displayCandidate = ({ candidateId, familyId }) => {
        gs.info(`Candidate ID: ${candidateId}`);
        gs.info(`Candidate Family ID: ${familyId}`);
    };
    ```
  
  - Avoid using nested destructuring in a function parameter.
    
    ```js
    // BAD
    const displayUser = ({ address: { street, city }, email }) => {
        // ...
    };
    
    // GOOD
    const displayUser = ({ address, email }) => {
        const { street, city } = address;
        // ...
    };
    ```

### Nullish Values

- Use [optional chaining](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining).
  
  ```js
  // BAD
  if (user && user.name && user.name.first) {
      console.log(user.name.first);
  }
  
  // GOOD
  if (user?.name?.first) {
      console.log(user.name.first);
  }
  ```

- Use the [nullish coalescing operator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing).
  
  ```js
  // BAD
  const address = user.address ? user.address : 'No address provided';
  
  // GOOD
  const address = user.address ?? 'No address provided';
  ```
  
  ```js
  // BAD - if candidate.retryAmount is 0 then retryAmount would be 3
  const retryAmount = candidate.retryAmount || 3;
  
  // GOOD - if candidate.retryAmount is 0 then retryAmount would be 0
  const retryAmount = candidate.retryAmount ?? 3;
  ```

### String Values

Use [template literals](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals).

```js
const name = 'John';
const age = 30;

// BAD
const message = 'Hello, my name is ' + name + ' and I am ' + age + ' years old.';
console.log(message);

// GOOD
const message = `Hello, my name is ${name} and I am ${age} years old.`;
console.log(message);
```

## Code Design

### Extract to functions

- We should follow the single responsibility principle.

- Extract code to functions when:
  
  - **A block of code can be named meaningfully**
    
    If you can describe what the code does in a short phrase, it probably deserves its own function.
  
  - **The block has a single, focused responsibility**
    
    Keep each function small and focused on one task.
  
  - **The block is reused (or could be reused) elsewhere**
    
    Avoid duplicating logic by extracting reusable helpers.
    
    ```javascript
    // BAD
    const processUserData = users => {
      const activeUsers = [];
      for (let i = 0; i < users.length; i++) {
          if (users[i].isActive) {
              activeUsers.push(users[i]);
          }
      }
    
      activeUsers.sort((a, b) => new Date(b.lastLogin) - new Date(a.lastLogin));
    
      console.log('Active Users:');
      for (let i = 0; i < activeUsers.length; i++) {
          const user = activeUsers[i];
          console.log(`${user.name} (${user.email}) - Last login: ${user.lastLogin}`);
      }
    }
    
    // GOOD
    const getActiveUsers = users => users.filter(({ isActive }) => isActive);
    
    const sortByLastLogin = users => users.sort((a, b) => new Date(b.lastLogin) - new Date(a.lastLogin));
    
    const displayUsers = users => {
        console.log('Active Users:');
        users.forEach(user => {
            console.log(`${user.name} (${user.email}) - Last login: ${user.lastLogin}`);
        });
    };
    
    const processUserData = users => {
        const activeUsers = getActiveUsers(users);
        const sortedUsers = sortByLastLogin(activeUsers);
        displayUsers(sortedUsers);
    };
    ```

## Documentation

### JSDoc

- Declare new types using [@typedef](https://jsdoc.app/tags-typedef):
  
  ```js
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
  ```

- Declare variables types using [@type](https://jsdoc.app/tags-type), only when the type can not be inferred:
  
  ```js
  /**
  * @type {Tag[]}
  */
  const tags = [
      { key: 'tag1', value: 'value1' },
      { key: 'tag2', value: 'value2' }
  ];
  
  /**
  * @type {CandidateDetails}
  */
  const candidateDetails = {
      name: 'John Doe',
      tags: tags
  };
  ```

- Document functions:
  
  - Declare parameters types using [@param](https://jsdoc.app/tags-param)
  
  - Declare return type using [@returns](https://jsdoc.app/tags-returns)
    
    ```js
    /**
    * @param {CandidateDetails} candidate 
    * @param {string} tagKey 
    * @returns {boolean}
    */
    const doesCandidateHaveTagKey = (candidate, tagKey) => {
        return candidate.tags.some(({ key }) => key == tagKey);
    };
    ```
  
  - Typing a curried function:
    
    ```js
    /**
    * @param {CandidatesDAO} candidatesDAO 
    * @returns {(familyId: string) => number}
    */
    const countCandidateOfFamily = candidatesDAO =>
        familyId => {
            // ...
        };
    ```
  
  - Declare private methods as [@private](https://jsdoc.app/tags-private):
    
    ```js
    /**
    * @private
    * @param {string} serviceFamilyId
    * @returns {boolean}
    */
    _isCandidatesGenerationProcessRunning(serviceFamilyId) {
        // ...
    }
    ```
  
  - Use regions to gather type definitions:
    
    ```js
    //#region definitions
    
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
    
    //#endregion definitions
    ```

### Comments

- Comments should be avoided.

- Instead of writing comments, name functions and variables (consts) with meaningful names.
  
  ```javascript
    // BAD
    //check if the current tag value is one of the values that was defined in the category.
    const tagValuesDef = category2DefinitionValues[category];
    if (tagValuesDef && tagValuesDef.tags[value] !== undefined) {
        // ...
    }
  
    // GOOD
    const isTagInCategory = (tagValue, category) => {
        const tagValuesDef = category2DefinitionValues[category];
        return tagValuesDef && !isNil(tagValuesDef.tags[tagValue]);
    };
  
    if (isTagInCategory(tagValue, category)) {
        // ...
    }
  ```

- Name variables based on their specific role in the current context, instead of describing it in a comment.
  
  ```javascript
    // BAD
    const processTransition = transition => {
        const { letters, stackLetters, manipulation } = transition;
  
        if (isPopTransition(transition)) {
            // Here, manipulation represents a pop indicator
            return handlePopTransition(letters, stackLetters, manipulation);
        }
  
        // Here, manipulation represents the letters to be pushed onto the stack
        return handlePushTransition(letters, stackLetters, manipulation);
    };
  
    // GOOD
    const processTransition = transition => {
  
        const { letters, stackLetters, manipulation } = transition;
  
        if (isPopTransition(transition)) {
            const popIndicator = manipulation;
            return handlePopTransition(letters, stackLetters, popIndicator);
        }
  
        const pushLetters = manipulation;
        return handlePushTransition(letters, stackLetters, pushLetters);
  
    };
  ```