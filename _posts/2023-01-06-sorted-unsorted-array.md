---
layout: post
title: What to choose between sorted and unsorted array
date: 2023-01-06
last-update: 
locale: en-GB
lang: en
categories: programmation
tags: data-structure array sort
image:
description: This article compares a sorted array and its unsorted version to stores data represented by numbers.
isMath: true
---

This article focuses on two structures to stores data represented by numbers: **a sorted array VS an unsorted array**.

For that, the advantages, disadvantages and the different uses cases will be studied.

## Unsorted array

With an unsorted array, the different elements are in disorder. Thus, we have the following properties

- Accessing element 

  a. Using known index: O(1)

  b. Using the value of the element: O(N)

In the second case (b), we need to perform a search inside the array, which increases the complexity

- Insert an element : O(1)

We can simply add the element at the end of the array

- Remove an element: 

  a. Using known index: O(1) or O(N)

  b. Using the value of the element: O(N)

We need to search the element (O(N)), then shift to the left all the other elements situated after this element (O(N)).  Thus we have:
$$
O(N) + O(N) = 2 * O(N) = O(N)
$$


If we can replace the removed element by another value, e.g. -1, we still have O(N) but it is more optimized. However, for the case (a), we have O(1) because we do no need to perform a research in the array.

- Search an element: O(n) 

We have to go through the entire array until we find the element we are looking for.

```c
function findElement(element){
	for(uint256 i = 0; i < myArray.length; ++i){
		if(myArray[i] == element){
			return i;
		}
	}
}
```



## Sorted array

With a sorted array, the different elements are in order, Thus, we have the following properties

### Summary

- Accessing element:
  -  Using known index: O(1)

  - Using the value of the element: O(log2(N))

- Insert an element: O(1)

- Remove an element :
  - Remove an element: 

    a. Using known index: O(1) or O(log2(N))

    b. Using the value of the element: O(N)

We need to search the element (O(log2(N)), then shift to the left all the other elements situated after this element (O(N)).  Thus we have:
$$
O(log2(N)) + O(N) = O(N)
$$
If we can replace the removed element by another value, e.g. -1, we have a complexity of O(log2(N)). However, for the case (a), we have O(1) because we do no need to perform a research in the array.



- Search an  element:  O(log2(n))

### Insert an element

1) Perform a binary search (upperbound) to find the position where the element has to be inserted
2) This search can get the following results:

- The element is already in the array => generate an error
- There are no element bigger than the searched element => you can insert the new element at the end of the array
- You have an upperbound match,

```c
// add the last element to the end of the array
myArray.push(myArray[myArray.length - 1]);
// Move all elements >= myArray[index] one position to the right
for(uint256 i = myArray.length - 2; i > index; --i) {
    myArray[i] = myArray[i - 1];
}
// Insert our new element
myArray[index] = time;
```

Another possibility is to insert the new element at the end of the array (O(1))  and use an algorithm to sort the array to place the new element in the right place.

Reference:

- [log2base2.com - Insert an element at a particular index in an array](https://www.log2base2.com/data-structures/array/insert-element-particular-index-array.html)
- [workat.tech - Insert Position in Sorted Array](https://workat.tech/problem-solving/approach/ipisa/insert-position-in-sorted-array)
- [leetcode.com - Search Insert Position](https://leetcode.com/problems/search-insert-position/)

## Remove an element

1. Perform a binary search (upperbound) to find the position where the element has to be inserted
2. This search can get the following results:

- The element is not in the array => generate an error or do nothing
- The element is in the array, you you need to move all elements after our target element one position to the left, starting by overwriting the target element. You can then remove the last element of the array with, e.g., with a pop operation.

```c
for(uint256 i = index; i + 1 < myArray.length; ++i){
	myArray[i] = myArray[i + 1];
}
myArray.pop();
```

Reference: [www.log2base2.com - Remove a specific element from array](https://www.log2base2.com/data-structures/array/remove-a-specific-element-from-array.html)

### Search an element

With a sorted array, we can use a binary search to find our target element.

1) We divide the array in two parts
2) We search in the first part, if the element is not in this one, we search in the second part, and so on.
3) We stop as soon as we found the value or reached the end of the array.

## Conclusion

**Unsorted array**

With an unsorted array, you can easily add a new element because you do not need to care about the order of the array.

Nevertheless, if you want to search an element, you have to iterate through the whole array.

It impacts, e.g, the remove operation too because you need to find the element in order to remove it from the array.

**Sorted array**

The sorted array is the exact opposite: it is more efficient to perform a research because you can use a binary search.

It is useful to remove an element because you need to perform a research in order to find the target element

Nevertheless, you have to keep the array sorted which makes it more difficult (less efficient) to insert a new element.



