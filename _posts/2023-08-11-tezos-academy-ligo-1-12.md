---
layout: post
title:  "Tezos Academy - Overview"
date:   2023-08-11
last-update: 
categories: blockchain
lang: en
locale: en-GB
tags: tezos ligo blockchain JavaScript
image: /assets/article/blockchain/tezos/TezosLogo_Horizontal_Blue.png
description: Learn LIGO for Tezos by following the chapters 1-12 of the Tezos Academy, a fun interactive tutorial 
---

As indicated in their website, [Tezos Academy](https://academy.ligolang.org/) is a fun interactive tutorial on how to code smart contracts for [Tezos](https://tezos.com/) made by the company [smart-chain](https://www.smart-chain.fr).

By default, Tezos smart contracts are written in [Michelson](https://tezos.gitlab.io/whitedoc/michelson.html), but to make the learning easier, the Academy offers to use [LIGO](https://ligolang.org/?lang=jsligo) instead which is then transpiled to Michelson.

To help the programmer to understand LIGO, the different challenges are in Javascript (JsLigo)

The path is available here: [https://academy.ligolang.org/](https://academy.ligolang.org/) & [https://academy.ligolang.org/js/chapter-about](https://academy.ligolang.org/js/chapter-about)

[TOC]



## Chapter 2 - Types

#### Explanation

**Built-in types**

LIGO comes with all basic types built-in like: *string*, *int* *tez* for account balance or monetary transactions.

**Type aliases**

It is also possible to rename a given type for a more precise name

```javascript
type breed = string;
let dog_breed: breed = "Saluki";
```

or for the balances of account

```javascript
type account_balances = map<address, tez>;
```



#### Mission

**Instruction**

> 1- There is an online editor in the top right corner of this page. In the editor, define *ship_code* as a string type.
>
> 2- Then define the constant *my_ship* as a *ship_code* of value *"020433"*.
>
> 3- Then go ahead and validate your mission for a comparative view with the solution.

**Result**

```javascript
type ship_code = string;
const my_ship: ship_code = "020433";
```



## Chapter 3 - Variable

#### Explanation

**Constant**

Constants are immutable. Their value can be only assigned once, at their declaration.

```javascript
const age: int = 25;
age = 3; // gives an error
```

```javascript
let x = (a: int): int => {
  const age: int = 25;
  const age: int = 3; // will give an error
};
```

**Variable**

The variables are mutable and can not be declared in a global scope. They can only used within functions or as functions parameters.

#### Mission

**Instruction**

> 1- In the top right editor, modify the code from the previous chapter to make *my_ship* a variable.
>
> 2- On the next line, modify its value to *"222031"*

**Result**

```javascript
type ship_code = string;

let my_ship: ship_code = "020433";

my_ship = "222031";
```



## Chapter 4 - Math / numerical types

#### Explanation

LIGO offers three built-in numerical types:

- *int* are integers, such as 10, -6 and 0. But there is only one canonical zero: 0 (so, for instance, -0 and 00 are invalid).
- *nat* are natural numbers (integral numbers greater than or equal to zero). They are followed by the annotation *as nat* such as 3 *as nat*, 12 *as nat* and 0 *as nat* for the natural zero. The same restriction on zero as integers applies: 0 *as nat* is the only way to specify the natural zero.
- *tez* are units of measure of Tezos tokens. They can be decimals and are followed by annotation *tez* such as 3 *as tez*. You can also type units of millionth of tez, using the annotation *as mutez* after a natural literal, such as 10000 *as mutez* or *0 as mutez*.

Tezos doesn't support floating point

#### Mission

**Instruction**

> 1- In the editor, define *required_energy* for 1.21 gigawatts. Since Tezos doesn't support floating point numbers, let's work in megawatts instead so that you can write the amount of energy as an *int*.
>
> 2- Define *energy_per_battery_pack* for 0.16 gigawatts.
>
> 3- Define and compute *required_battery_packs* as the number of battery packs required to power your ship. Remember that floating point numbers are truncated to an integer, e.g. 10 / 3 = 3 in LIGO and not 3.33333333....

**Result**

```javascript
const required_energy: int = 1210;
const energy_per_battery_pack: int = 160;
const required_battery_packs: int = required_energy / energy_per_battery_pack + 1;
```



## Chapter 5 - String

#### Explanation

Strings can be sliced using a built-in function `String.sub` which takes three parameters:

- an *offset* describing the index of first character that will be copied
- the *length* describing the number of characters that will be copied (starting from the given offset)
- the *string* being sliced

#### Mission

**Instruction**

> 1 - Reassign *my_ship* by modifying the engine attribute (third number) from 0 to 1. 
>
> Use  substrings for the attributes before and after to make sure they are  untouched.

**Result**

```javascript
type ship_code = string;
let my_ship: ship_code = "020433";
// Type your solution below
my_ship = String.sub(0 as nat, 2 as nat, my_ship) + "1" + String.sub(3 as nat, 3 as nat, my_ship);
```



## Chapter 6 - Functions

#### Explanation

**Introduction**

- Each smart contract must have at least one function named *main* 

Calling a function

- When calling a function, LIGO makes a copy of the arguments but also the environment variables. Therefore any modification to these will not be reflected outside the  scope of the function and will be lost if not explicitly returned by the function.
- Functions in JsLIGO are defined using the `let` or `const` keyword,

One single expression

```javascript
let add = ([a, b]: [int, int]): int => a + b;
```

Several expressions

```javascript
let myFun = ([x, y]: [int, int]): int => {
  let doubleX = x + x;
  let doubleY = y + y;
  return doubleX + doubleY;
};
```



**Nested functions (closure)**

It's possible to place functions inside other functions. These functions have access to variables in the same scope.

```javascript
let closure_example = (i: int): int => {
  let closure = (j: int): int => i + j;
  return closure(i);
};
```



#### Mission

**Explanation**

> 1- Write a function *modify_ship* taking as argument *my_ship* of type *ship_code* and returning a varible of type *ship_code* as well.
>
> 2- In the function, copy/cut the code from the previous chapter that modified the third attribute from 0 to 1 and assign the result to a constant *modified_ship*
>
> 3- Return *modified_ship*

**Result**

```javascript
type ship_code = string;
let my_ship: ship_code = "020433";
// Modify the code below
let modify_ship = (my_ship: ship_code): ship_code => {
  const modified_ship: ship_code = String.sub(0 as nat, 2 as nat, my_ship) + "1" + String.sub(3 as nat, 3 as nat, my_ship);
  return modified_ship;
}
```



## Chapter 7 - Conditionals

#### Explanation

**Boolean**

- Booleans are typed *bool* in LIGO :

```
let a: bool = true; // or false
```

**Comparing values**

Only values of the same type can be natively compared, i.e. int, nat,  string, tez, timestamp, address, etc... However some values of the same  type are not natively comparable, i.e. maps, sets or lists. You will  have to write your own comparison functions for those.

```javascript
// Comparing strings
let a: string = "Alice";
let b: string = "Alice";
let c: bool = (a == b); // true

// Comparing numbers
let a: int = 5;
let b: int = 4;
let c: bool = (a == b);
let d: bool = (a > b);
let e: bool = (a < b);
let f: bool = (a <= b);
let g: bool = (a >= b);
let h: bool = (a != b);

// Comparing tez
let a: tez = 5 as mutez;
let b: tez = 10 as mutez;
let c: bool = (a == b); // false
```

**Conditionals**

```
let isSmall = (n : nat) : bool => {
  if (n < (10 as nat)) { return true; } else { return false; };
};
```

Conditional logic enables forking the control flow depending on the state.

#### Mission

**Instruction**

>  We want to conditionally change the engine attribute (third number) to 1 only if it is equal to 0.
>
> 1- Define a condition *if* the engine attribute equal 0. Don't forget the attributes are defined as strings.
>
> 2- If the condition is met, apply changes and return resulting new ship code. Otherwise, return the given ship code (parameter *my_ship*).

**Result**

```javascript
type ship_code = string;
let my_ship: ship_code = "020433";
my_ship = "222031";
const my_ship_price : tez = 3 as tez * (120 as nat);

let modify_ship = (my_ship: ship_code): ship_code => {
    // Type your solution below
  if (String.sub(2 as nat, 1 as nat, my_ship) == "0") { 
      return String.sub(0 as nat, 2 as nat, my_ship) + "1" + String.sub(3 as nat, 3 as nat, my_ship);
   } else { 
     return my_ship; 
  }
}
```

Remark: I do not understand the line `my_ship_price`which was not part of the instructions or provided code.



## Chapter 8 - Tuples

#### Explanation

Tuples gather multiple values in a specific order which can be retrieved with their indexes.

**Definition**

- To define a tuple, use *[ ]* operator :

```javascript
type name = [string, string];
```

- To define a value of this type :

```javascript
let my_name: name = ["Jack", "Oneill"];
```

**Access**

You can access each component of a tuple by their position:

```javascript
const my_name_first_name: string = my_name[0];

const my_name_last_name: string = my_name[1];
```

**Update**

You can modify a component of tuple by assigning values as if it were a variable :

```javascript
my_name[0] = "Carter"
```

#### Mission

**Instruction**

> 1- Create a tuple type *coordinates* representing a 3D location.
>
> 2- Define *earth_coordinates* at coordinates 2,7,1.
>
> 3- Let's say you made a mistake in the definition. Define a new constant *modified_earth_coordinates* which reuses parameters of *earth_coordinates* except for the last parameter of *earth_coordinates* which is fixed to 5. Direct access by postion is asked (do not destructure *earth_coordinates*)

**Result**

```
// Type your solution below
type coordinates = [int, int, int];
let earth_coordinates: coordinates = [2, 7, 1];
let modified_earth_coordinates = [earth_coordinates[0], earth_coordinates[1], 5];
```



## Chapter 9 - Records

#### Explanation

Records are like tuples but with named parameters. In other words, they  hold a set of key/data pairs. 

**Declaration**

To instantiate a record, you must first  declare its type as follows : 

```
type user = {
  id       : nat,
  is_admin : bool,
  name     : string
};
```

**Definition**

And here is how to define an associated record value :

```
let alice : user = {
  id       : 1 as nat,
  is_admin : true,
  name     : "Alice"
};
```

**Access**

You can access the whole record or get one key in particular :

```
let alice_admin: bool = alice.is_admin;
```

**Update**

You can modify values in a record as follows :

```
let change_name = (u: user): user => ({...u, name: "Mark"});
```



#### Mission

**Instruction**

1- Refactor the type of *coordinates* as a record instead of a tuple. Name the parameters *x*, *y* and *z*.

2- Refactor *earth_coordinates* with the record type.

3- Refactor the *modified_earth_coordinates* update of the last parameters with the record type.



**Result**

```javascript
// Modify the code below
type coordinates = {
  x: int,
  y: int,
  z: int
};

let earth_coordinates: coordinates = {
  x: 2,
  y: 7,
  z: 1
};

let modified_earth_coordinates = {...earth_coordinates, z:5 };
```



## Chapter 10 - Maps

#### Explanation

Maps are a data structure which associate values of the same type to  values of the same type. The former are called key and the latter  values. Together they make up a binding. An additional requirement is  that the type of the keys must be comparable, in the Michelson sense.

**Declaration**

Maps are declared as: 

```
type balances = map<string, nat>;
```

**Instantiation**

To create an empty map :

```
let empty: balances = Map.empty;
```

 Warning: An empty map must be casted to the right type. More on this later.

```
let empty: balances = (Map.empty as map<string, nat>)
```

To create an non-empty map :

```
let moves: balances = Map.literal(list([
	["tim", 5 as nat],
	["mark", 0 as nat]
]));
```

ℹ️ The *Map.literal* function expects a list of *[key, value]* pairs separated by *,*.

**Access**

Use the *Map.find_opt* built-in function to read a value of the map :

```
let my_balance: option<nat> = Map.find_opt("tim", moves);
```

ℹ️ The keyword option shows that this value is optional. More on this later.

**Update**

The values of a map can be updated using *Map.update* built-in function:

```
let user_balances: balances = Map.update("tim", Some(14 as nat), moves);
```

### Insertion

To add a new value in the map, use *Map.add* function:

```
let user_balances: balances = Map.add("ed", 39 as nat, moves);
```

Removal

A key-value can be removed from the mapping as follows :

```
Map.remove("tim", moves);
```

Big Maps

Maps load their entries into the environment, which is fine for small  maps, but for maps holding millions of entries, the cost of loading such map would be too expensive. For this we use *big_maps*. Their syntax is the same as for regular maps.

#### Mission

**Instruction**

1- Notice we defined *coordinates* as a 3D tuple.

2- Define the type *name_to_coordinates* as a mapping from the celestial body name to its coordinates.

3- Create a new map called *star_map* and add values for *earth* at 2,7,1 , the *sun* at 0,0,0 and *alpha-centauri* at 2232,7423,12342 .



**Result**

```javascript
type coordinates = [int, int, int];
// Type your solution below
type name_to_coordinates = map<string, coordinates>;
let star_map: name_to_coordinates = Map.literal(list([
    ["earth", [2,7,1]],
    ["sun", [0,0,0]],
    ["alpha-centauri", [2232,7423,12342]]
]));

```



## Chapter 11a - Lists

#### Explanation

Lists are linear collections of elements of the same type. Linear means  that, in order to reach an element in a list, we must visit all the  elements before (sequential access). Elements can be repeated, as only  their order in the collection matters. The first element is called the  head, and the sub-list after the head is called the tail. For those  familiar with algorithmic data structure, you can think of a list a  stack, where the top is written on the left.

**Defining lists**

- To define an empty list :

```
let empty_list : int list = []
```

- To define list with values:

```
let my_list : int list = [1; 2; 2] // The head is 1
```

**Adding to lists**

Lists can be augmented by adding an element before the head (or, in terms of stack, by pushing an element on top). This operation is usually called consing in functional languages. You can add elements to an existing list using the consing operator *::* :

```
let larger_list : int list = 5 :: my_list // [5;1;2;2]
```

##### Functional Iteration over Lists

A functional iterator is a function that traverses a data structure and  calls in turn a given function over the elements of that structure to  compute some value. There are three kinds of functional iterations over  LIGO lists: the *iterated operation*, the *map operation* (not to be confused with the map data structure) and the *fold operation*.

##### Iterated Operation over Lists

The first, the iterated operation, is an iteration over the list with a  unit return value. It is useful to enforce certain invariants on the  element of a list, or fail. For example you might want to check that each value inside of a list is  within a certain range, and fail otherwise. The predefined functional  iterator implementing the iterated operation over lists is called *List.iter*.

```
let iter_op (l : int list) : unit =

  let predicate = fun (i : int) -> assert (i > 3)

  in List.iter predicate l
```

##### Mapped Operation over Lists

We may want to change all the elements of a given list by applying to them a function. This is called a *map operation*, not to be confused with the map data structure. The predefined  functional iterator implementing the mapped operation over lists is  called *List.map* and is used as follows.

```
let increment (i : int) : int = i + 1
// Creates a new list with all elements incremented by 1
let plus_one : int list = List.map increment larger_list
```

##### Folded Operation over Lists

A *folded operation* is the most general of iterations. The folded function takes two  arguments: an accumulator and the structure element at hand, with which  it then produces a new accumulator. This enables having a partial result that becomes complete when the traversal of the data structure is over. The predefined functional iterator implementing the folded operation  over lists is called *List.fold* and is used as follows.

```
let sum (acc, i: int * int) : int = acc + i

let sum_of_elements : int = List.fold sum my_list 0
```

## Chapter 11b - Sets

#### Explanation

Sets are unordered collections of values of the same type, like lists  are ordered collections. Elements of sets in LIGO are unique, whereas  they can be repeated in a list.

##### Defining sets

To define an empty set :

```
let my_set : int set = Set.empty
```

In CameLIGO, there is no predefined syntactic construct for sets: you  must build your set by adding to the empty set. (This is the way in  OCaml.)

```
let my_set : int set =

  Set.add 3 (Set.add 2 (Set.add 2 (Set.add 1 (Set.empty : int set))))
```

##### Testing membership

In CameLIGO, the predefined predicate *Set.mem* tests for membership in a set as follows:

```
let contains_3 : bool = Set.mem 3 my_set
```

##### Size of a set

  The predefined function *Set.size* returns the number of elements in a given set as follows.

```
let cardinal : nat = Set.size my_set
```

##### Update a set

There are two ways to update a set, that is to add or remove from it. In CameLIGO, we can use the predefined functions *Set.add* and *Set.remove*. We update a given set by creating another one, with or without some elements.

```
let larger_set  : int set = Set.add 4 my_set
let smaller_set : int set = Set.remove 3 my_set
```

##### Functional Iteration over Sets

It is possible to iterate over elements of a set and apply a function to them (like functional iteratio over List).

There are three kinds of functional iterations over LIGO sets: the *iterated operation* and the *folded operation*.

```
let iter_op (s : int set) : unit =

  let predicate = fun (i : int) -> assert (i > 3)

  in Set.iter predicate s
```



#### Mission

**Instruction**

1- Define *itinerary* as a list of string names of celestial bodies representing your course. Start with *"earth"*

2- On the next line, add *"sun"* to the *itinerary* and save it into a *longer_itinerary* constant.

2- On the next line, add *"alpha-centauri"* to the *longer_itinerary* and save it into a *far_itinerary* constant.

**Result**

```javascript
let itinerary : string list = ["earth"]
let longer_itinerary : string list = "sun" :: itinerary
let far_itinerary : string list = "alpha-centauri" :: longer_itinerary
```

