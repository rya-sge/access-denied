# OSINT and Other security research tools

This article is a summary of the TryHackMe room [Search Skills](https://tryhackme.com/room/searchskills).

The goal of this room is to teach:

- Evaluate information sources
- Use search engines efficiently
- Explore specialized search engines
- Read technical documentation
- Make use of social media
- Check news outlets

[TOC]



## Search engines

Almost every Internet search engine allows you to carry out advanced searches. Consider the following examples:

- [Google](https://www.google.com/advanced_search)
- [Bing](https://support.microsoft.com/en-us/topic/advanced-search-options-b92e25f1-0085-4271-bdf9-14aaea720930)
- [DuckDuckGo](https://duckduckgo.com/duckduckgo-help-pages/results/syntax/)

Let’s consider the search operators supported by Google.

- `"exact phrase"`: Double quotes indicate that you are looking for pages with the exact word or phrase. For example, one might search for `"passive reconnaissance"` to get pages with this exact phrase.
- `site:`: This operator lets you specify the domain name to which you want to limit your search. For example, we can search for success stories on TryHackMe using `site:tryhackme.com success stories`.
- `-`: The minus sign allows you to omit search results that contain a particular word or phrase. For example, you might be interested in learning about the pyramids, but you don’t want to view tourism websites; one approach is to search for `pyramids -tourism` or `-tourism pyramids`.
- `filetype:`: This search operator is indispensable for finding files instead of web pages. Some of the file types you can search for using Google are Portable Document Format (PDF), Microsoft Word Document (DOC), Microsoft Excel Spreadsheet (XLS), and Microsoft PowerPoint Presentation (PPT). For example, to find cyber security presentations, try searching for `filetype:ppt cyber security`.



### FAQ

> How would you limit your Google search to PDF files containing the terms **cyber warfare report**?

filetype:pdf cyber warfare report

## Specialized Search Engines

### Shodan (connected devices)

[Shodan](https://www.shodan.io/) is a search engine for devices connected to the Internet. It allows you to search for specific types and versions of servers, networking equipment, industrial control systems, and IoT devices. 

Example:

You may want to see how many servers are still running Apache 2.4.1 and the distribution across countries. To find the answer, we can search for `apache 2.4.1`, which will return the list of servers with the string “apache 2.4.1” in their headers.

- Consider visiting Shodan [Search Query Examples](https://www.shodan.io/search/examples) for more examples. 

- Further ressource: [Shodan trends](https://trends.shodan.io/) for historical insights if you have a subscription.

### Censys (hosts, website, certificates)

At first glance, [Censys](https://search.censys.io/) appears similar to Shodan. 

- However, Shodan focuses on Internet-connected devices and systems, such as servers, routers, webcams, and IoT devices. 

- Censys, on the other hand, focuses on Internet-connected hosts, websites, certificates, and other Internet assets. 
- Further ressource: [Censys Search Use Cases](https://support.censys.io/hc/en-us/articles/20720064229140-Censys-Search-Use-Cases).

### VirusTotal (Files Virus scanning)

[VirusTotal](https://www.virustotal.com/) is an online website that provides a virus-scanning service for files using multiple antivirus engines.

-  It allows users to upload files or provide URLs to scan them against numerous antivirus engines and website scanners in a single operation. 
- They can even input file hashes to check the results of previously uploaded files.

The screenshot below shows the result of checking the submitted file against 67 antivirus engines. Furthermore, one can check the community's comments for more insights. Occasionally, a file might be flagged as a virus or a Trojan; however, this might not be accurate for various reasons, and that's when community members can provide a more in-depth explanation.

### Have I Been Pwned (email)

[Have I Been Pwned](https://haveibeenpwned.com/) (HIBP) does one thing; it tells you if an email address has appeared in a leaked data breach. Finding one’s email within leaked data indicates leaked private information and, more importantly, passwords. Many users use the same password across multiple platforms, if one platform is breached, their password on other platforms is also exposed. Indeed, passwords are usually stored in encrypted format; however, many passwords are not that complex and can be recovered using a variety of attacks.

### Exercise

> What is the top country with **lighttpd** servers?

United states

> What does BitDefenderFalx detect the file with the hash `2de70ca737c1f4602517c555ddd54165432cf231ffc0e21fb2e23b9dd14e7fb4` as?

Android.Riskware.Agent.LHH

## Vulnerabilities

### CVE

We can think of the Common Vulnerabilities and Exposures (CVE) program as a dictionary of vulnerabilities. It provides a standardized identifier for vulnerabilities and security issues in software and hardware products. Each vulnerability is assigned a CVE ID with a standardized format like `CVE-2024-29988`. This unique identifier (CVE ID) ensures that everyone from security researchers to vendors and IT professionals is referring to the same vulnerability, [CVE-2024-29988](https://nvd.nist.gov/vuln/detail/CVE-2024-29988) in this case.

The MITRE Corporation maintains the CVE system. For more information and to search for existing CVEs, visit the [CVE Program](https://www.cve.org/) website. Alternatively, visit the [National Vulnerability Database](https://nvd.nist.gov/) (NVD) website. The screenshot below shows CVE-2014-0160, also known as Heartbleed.

![The CVE-2014-0160 vulnerability on the CVE Program website](https://tryhackme-images.s3.amazonaws.com/user-uploads/5f04259cf9bf5b57aed2c476/room-content/5f04259cf9bf5b57aed2c476-1718112739122)

### Exploit Database

The [Exploit Database](https://www.exploit-db.com/). lists exploit codes from various authors; some of these exploit codes are tested and marked as verified.

Note that you should not try to exploit a vulnerable system unless you are given permission, usually via a legally binding agreement.

![The results of the search for heartbleed on the Exploit Database website](https://tryhackme-images.s3.amazonaws.com/user-uploads/5f04259cf9bf5b57aed2c476/room-content/5f04259cf9bf5b57aed2c476-1718112752814)

### GitHub

[GitHub](https://github.com/), a web-based platform for software development, can contain many tools related to CVEs, along with proof-of-concept (PoC) and exploit codes. To demonstrate this idea, check the screenshot below of search results on GitHub that are related to the Heartbleed vulnerability.

![The results of the search for CVE-2014-0160 on the GitHub website.](https://tryhackme-images.s3.amazonaws.com/user-uploads/5f04259cf9bf5b57aed2c476/room-content/5f04259cf9bf5b57aed2c476-1718112771383)

One vital skill to acquire is to look up official documentation. We will cover a few examples of official documentation pages.

> What utility does CVE-2024-3094 refer to?

xz

## Technical documentation

### Linux Manual Pages

 On Linux and every Unix-like system, each command is expected to have a man page. In fact, man pages also exist for system calls, library functions, and even configuration files.

Let’s say we want to check the manual page for the command `ip`. We issue the command `man ip`. The screenshot below shows the page we received.

![The Manual page of the ip command](https://tryhackme-images.s3.amazonaws.com/user-uploads/5f04259cf9bf5b57aed2c476/room-content/5f04259cf9bf5b57aed2c476-1718112797192)

If you prefer to read the man page of `ip` in your web browser, just type `man ip` in your favourite search engine. This [page](https://linux.die.net/man/8/ip) might be at the top of the results.

### Microsoft Windows

Microsoft provides an official [Technical Documentation](https://learn.microsoft.com/) page for its products. The screenshot below shows the search results for the command `ipconfig`.

![The results of the search for ipconfig on the Microsoft Technical Documentation website](https://tryhackme-images.s3.amazonaws.com/user-uploads/5f04259cf9bf5b57aed2c476/room-content/5f04259cf9bf5b57aed2c476-1718112815041)

### Product Documentation

Every popular product is expected to have well-organized documentation. This documentation provides an official and reliable source of information about the product features and functions. Examples include [Snort Official Documentation](https://www.snort.org/documents), [Apache HTTP Server Documentation](https://httpd.apache.org/docs/), [PHP Documentation](https://www.php.net/manual/en/index.php), and [Node.js Documentation](https://nodejs.org/docs/latest/api/).

It is always rewarding to check the official documentation as it is the most up-to-date and offers the most complete product information.

### FAQ

> What does the Linux command `cat` stand for?

Concatenate

> What is the `netstat` parameter in MS Windows that displays the executable associated with each active connection and listening port?

-b

## Social media

There are billions of users registered on social media platforms such as [Facebook](https://www.facebook.com/people/Tryhackme/100069557747714/), [X](https://x.com/), and [LinkedIn](https://www.linkedin.com/). 

The power of social media is that it allows you to connect with companies and people you are interested in. Furthermore, social media offers a wealth of information for cyber security professionals, whether they are searching for people or technical information. Why is searching for people important, you ask?

When protecting a company, you should ensure that the people you protect are not oversharing on social media. For instance, their social media might give away the answer to their secret questions, such as, “Which school did you go to as a child?”. Such information might allow adversaries to reset their passwords and take over their accounts effortlessly.

Furthermore, as a cyber security professional, you want to stay updated with new cyber security trends, technologies, and products. Following the proper channels and groups can provide a suitable environment for growing your technical expertise.

Besides staying updated via social media channels and groups, we should mention news outlets. Hundreds of news websites would offer valuable cyber-security-related news. Try different ones and stick with the ones you like most.

### FAQ

> You are hired to evaluate the security of a particular company. What is a popular social media website you would use to learn about the technical background of one of their employees?

LinkedIn

Continuing with the previous scenario, you are trying to find the answer to the secret question, “Which school did you go to as a child?”. What social media website would you consider checking to find the answer to such secret questions?

> Facebook

## Conclusion

This room focused on the most common sources of information for cyber security professionals. There are plenty more. As the information landscape keeps changing, it is impossible to cover all the sources. However, by subscribing to relevant cyber security groups, one can stay ahead and be aware whenever new interesting sources arise.