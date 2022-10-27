---
layout: post
title:  Unit Test Key Principles
date:   2022-10-27
last-update: 
categories: programmation
tags: unit test OOP
description: This article presents some principles to respect when you create unit testing: DRY test, KISS, SRP and Yagni.
image: 
isMath: false
---

This article presents some principles to respect when you create unit testing. The list is recovered from this post  [Gomes 2017](https://medium.com/@pjbgf/title-testing-code-ocd-and-the-aaa-pattern-df453975ab80).

Some articles presenting a list of good practices : [Microsoft 2022](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices), [Semyon 2022](https://semaphoreci.com/blog/unit-testing), [Gomes 2017](https://medium.com/@pjbgf/title-testing-code-ocd-and-the-aaa-pattern-df453975ab80)

**DRY test**
A dry test was originally thought by firefighter (according to Wikipedia): it is better to train without a real fire  and without water. It consumes less resource, and it is less risky because there is not
check the code before you run it OR with less outside components
For example, the most basic example is by reading the code by hand. You remove execution error of the computer of the scope of the test.

But it can be too complicated, and one of the possible next step is to test a functionality offline before online.

Reference : [Tech With Tech’s Team 2022], [Wikipedia 2022]

**KISS / Keep it Simple, Stupid**
With this acronym, we can immediately understand the purpose
A test must be more simple than the code it checks
Reference : [Simpson no date]



**SRP / Single-responsibility principle**
The single-Responsibility principle, more particularly used in OOP, involves dividing responsibilities into functions, modules or classes. By extension, this principle can be adapted to tests: a test, an element (= a responsibility) to be tested
Reference : [Wynn 2021]
SRP is a part of the acronym SOLID, more information is available in the reference : [Kovan 2019], [Abba 2022]

**Yagni / You Aren't Gonna Need It**

When you create a test, it is important not to have to develop features of the project you are testing.

You shouldn't write a test that drives you to develop code that's not needed, because it has a cost

- cost of build
- cost of delay
- cost of carry
- cost of repair 

Reference : [Fowler 2015], [tvanfosson 2021], [Gomes 2017]

# Reference

ABBA, Ihechikara Vincent, 2022. SOLID Definition – the SOLID Principles of Object-Oriented Design Explained. *freeCodeCamp*. Online. 26 April 2022. [Accessed 25 October 2022]. Retrieved from: [https://www.freecodecamp.org/news/solid-principles-single-responsibility-principle-explained/](https://www.freecodecamp.org/news/solid-principles-single-responsibility-principle-explained/)

FOWLER, Martin, 2015. Yagni. *martinFowler.com*. Online. 26 May 2015. [Accessed 25 October 2022]. Retrieved from: [https://martinfowler.com/bliki/Yagni.html](https://martinfowler.com/bliki/Yagni.html)

GOMES, Paulo, 2017. Unit Testing and the Arrange, Act and Assert (AAA) Pattern. *Medium*. Online. 9 September 2017. [Accessed 25 October 2022]. Retrieved from: [https://medium.com/@pjbgf/title-testing-code-ocd-and-the-aaa-pattern-df453975ab80](https://medium.com/@pjbgf/title-testing-code-ocd-and-the-aaa-pattern-df453975ab80)

KOVAN, Gerry, 2019. SOLID design principles make test-driven development (TDD) faster and easier. Online. 17 May 2019. [Accessed 27 October 2022]. Retrieved from: [https://gkovan.medium.com/solid-design-principles-makes-test-driven-development-faster-and-easier-35c9eec22ff1](https://gkovan.medium.com/solid-design-principles-makes-test-driven-development-faster-and-easier-35c9eec22ff1)

MICROSOFT, 2022. Unit testing best practices with .NET Core and .NET Standard. *Medium*. Online. 10 April 2022. [Accessed 25 October 2022]. Retrieved from: [https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices)

SEMYON, Kirekov, 2022. A Deep Dive into Unit Testing. *semaphore*. Online. 11 August 2022. [Accessed 25 October 2022]. Retrieved from: [https://semaphoreci.com/blog/unit-testing](https://semaphoreci.com/blog/unit-testing)

SIMPSON, Mark, no date. The fundamentals of unit testing: KISS. *Mark’s Devblog*. Online. [Accessed 25 October 2022]. Retrieved from: [https://defragdev.com/blog/2012/11/04/the-fundamentals-of-automated-testing-kiss.html](https://defragdev.com/blog/2012/11/04/the-fundamentals-of-automated-testing-kiss.html)

TECH WITH TECH’S TEAM, 2022. Dry Run Testing: Meaning. *Tech With Tech*. Online. 6 August 2022. [Accessed 25 October 2022]. Retrieved from: [https://techwithtech.com/dry-run-testing-meaning/](https://techwithtech.com/dry-run-testing-meaning/)

TVANFOSSON, 2021. Does YAGNI also apply when writing tests? *Stack Overflow*. Online. 31 May 2021. [Accessed 25 October 2022]. Retrieved from: [https://stackoverflow.com/questions/945493/does-yagni-also-apply-when-writing-tests](https://stackoverflow.com/questions/945493/does-yagni-also-apply-when-writing-tests)

WIKIPEDIA, 2022. Dry run (testing). *Wikipedia*. Online. 24 October 2022. [Accessed 25 October 2022]. Retrieved from: [https://en.wikipedia.org/wiki/Dry_run_(testing)](https://en.wikipedia.org/wiki/Dry_run_(testing))

WYNN, Richard, 2021. Single Responsibility Principle (SRP) in 100 seconds. *DEV*. Online. 31 May 2021. [Accessed 25 October 2022]. Retrieved from: [https://dev.to/richardwynn/single-responsibility-principle-srp-in-100-seconds-3b1d](https://dev.to/richardwynn/single-responsibility-principle-srp-in-100-seconds-3b1d)