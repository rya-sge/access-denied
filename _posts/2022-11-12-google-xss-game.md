---
layout: post
title: XSS Game - Google
date: 2022-11-12
last-update: 
locale: en-GB
lang: en
categories: security web
tags: xss google xss-game
image: /assets/article/web/xss/xss-game/xss-game-cover.PNG
description: XSS-game was launched by Google to train for XSS vulnerabilities with 6 challenges to solve. This document summarizes the solutions for challenges 1 to 5.
---

A few years ago, Google launched a site, [xss-game.appspot.com](https://xss-game.appspot.com) to train for **XSS** vulnerabilities by offering 6 challenges to solve. This document summarizes the possible solutions for challenges 1 to 5.

Quick summary of XSS:

An XSS (Cross-Site Scripting) attack is a security vulnerability that allows an attacker to inject malicious scripts into web pages viewed by other users. 

XSS exploits occur when user input is improperly sanitized or validated, allowing attackers to inject their malicious script

These scripts can steal sensitive data (like cookies or session tokens), deface websites, or redirect users to malicious sites. 

There are three main types of XSS: **stored**, **reflected**, and **DOM-based**, each differing in how and where the malicious code is injected and executed.

To begin, some useful resources

- [evuln xss-encoder/](http://evuln.com/tools/xss-encoder/)
- [XSS Filter Evasion Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XSS_Filter_Evasion_Cheat_Sheet.html#xss-filter-evasion-cheat-sheet)
- [xss-payload-list](https://github.com/payloadbox/xss-payload-list)
- [resources.infosecinstitute.com - Deadly Consequences of XSS](https://resources.infosecinstitute.com/topic/deadly-consequences-xss/)
- [portswigger.net - Cross-site scripting (XSS) cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)
- [hacktricks - XSS](https://book.hacktricks.xyz/pentesting-web/xss-cross-site-scripting)

## Level 1 - Reflected

In this level, we have an html form to perform a search. The searched word will then be displayed by a new page, as below for the input `test`

![xss-1-search]({{site.url_complet}}/assets/article/web/xss/xss-game/xss-1-search.PNG)

**Solution**

Characters are not escaped. We can then generate an XSS alert using the `script` tags to contain the malicious code.

```html
<script>alert("Hello")</script>
```



## Level 2 - XSS persistence

In this one we are dealing with a `stored xss`. The user can post a message and it is in this that we will be able to put our malicious script.

![2-forms-input]({{site.url_complet}}/assets/article/web/xss/xss-game/2-forms-input.PNG)

**Solution**

To make it simple, I put the XSS in the form of a clickable link, but one could imagine using images, iframes tags, as well as automatically directing the user without going through a click.

```html
<a href="javascript:alert()">Link</a>
```



## Level 3 - url

In this challenge, the website displays images that can be selected

![3-image]({{site.url_complet}}/assets/article/web/xss/xss-game/3-image.PNG)

**Solution**

Looking at the url after clicking an image, we can see that the website displays the image specified by the fragment value. With the following url: [xss-game.appspot.com/level3/frame#2](https://xss-game.appspot.com/level3/frame#2), the cloud2 image will be displayed. 

Looking at the source code, we can see the following code:

![xss-level3-2]({{site.url_complet}}/assets/article/web/xss/xss-game/xss-level3-2.PNG)



The objective will be to escape the url in order to add a script tag after the `src` attribute of the `img` tag

```html
'><script>alert("HEllo")</script>
```

![xss-chap3]({{site.url_complet}}/assets/article/web/xss/xss-game/xss-chap3.PNG)





## Level 4

At level 4 we have a timer

![4-timer-input]({{site.url_complet}}/assets/article/web/xss/xss-game/4-timer-input.PNG)

![xss-level4-timer]({{site.url_complet}}/assets/article/web/xss/xss-game/xss-level4-timer.PNG)

**Solution**

Looking at the code more closely, we can see that a startTimer function is called

![4-timer]({{site.url_complet}}/assets/article/web/xss/xss-game/4-timer.PNG)



The attack will be devoted to the part

```javascript
seconds = parseInt(seconds) || 3
```

Since seconds is the value of our input, we can manage to execute `parseInt` and then an `alert` by adding a single quote, a parenthesis and a semicolon. 

The payload is the following:

```
3');alert('test
```

## Level 5 - DOM

Observing signup.html, we see that the url value of the link depends on the next attribute

```html
<a href="{{ next }}">Next >></a>
```

We can therefore modify the value of the link.

For this challenge, we use the bookmarklet functionality of web browsers. These allow you to indicate in a hyperlink or an url the javascript code that will be executed by the browser. Its url starts with `javascript:`

Reference: [wikipedia.org - Bookmarklet](https://fr.wikipedia.org/wiki/Bookmarklet), [medium.com - Bookmarklets are Dead…](https://medium.com/making-instapaper/bookmarklets-are-dead-d470d4bbb626)

**Solution**

```html
href="/level5/frame/signup?next=javascript:alert('Hello')"
```

![xss-level5-bookmarklet]({{site.url_complet}}/assets/article/web/xss/xss-game/xss-level5-bookmarklet.PNG)

Reference used for this challenge: [sagarvd01 - Learning XSS with Google’s XSS Game](https://sagarvd01.medium.com/learning-xss-with-googles-xss-game-f44ff8ee3d8b)

## Reference

- [xss-game.appspot.com](https://xss-game.appspot.com) 
- [portswigger.net - Cross-site scripting (XSS) cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)

- ChatGPT with the input "Write me a description of xss attack in a few line"