# Google search tips

https://tryhackme.com/room/searchskills



- `"exact phrase"`: Double quotes indicate that you are looking for pages with the exact word or phrase. For example, one might search for `"passive reconnaissance"` to get pages with this exact phrase.
- `site:`: This operator lets you specify the domain name to which you want to limit your search. For example, we can search for success stories on TryHackMe using `site:tryhackme.com success stories`.
- `-`: The minus sign allows you to omit search results that contain a particular word or phrase. For example, you might be interested in learning about the pyramids, but you don’t want to view tourism websites; one approach is to search for `pyramids -tourism` or `-tourism pyramids`.
- `filetype:`: This search operator is indispensable for finding files instead of web pages. Some of the file types you can search for using Google are Portable Document Format (PDF), Microsoft Word Document (DOC), Microsoft Excel Spreadsheet (XLS), and Microsoft PowerPoint Presentation (PPT). For example, to find cyber security presentations, try searching for `filetype:ppt cyber security`.

How would you limit your Google search to PDF files containing the terms **cyber warfare report**?

filetype:pdf cyber warfare report

ou are familiar with Internet search engines; however, how much are you familiar with specialized search engines? By that, we refer to search engines used to find specific types of results.

## Shodan

[Shodan](https://www.shodan.io/) is a search engine for devices connected to the Internet. It allows you to search for specific types and versions of servers, networking equipment, industrial control systems, and IoT devices. 

Example:

You may want to see how many servers are still running Apache 2.4.1 and the distribution across countries. To find the answer, we can search for `apache 2.4.1`, which will return the list of servers with the string “apache 2.4.1” in their headers.

- Consider visiting Shodan [Search Query Examples](https://www.shodan.io/search/examples) for more examples. 

- Further ressource: [Shodan trends](https://trends.shodan.io/) for historical insights if you have a subscription.

## Censys

At first glance, [Censys](https://search.censys.io/) appears similar to Shodan. 

- However, Shodan focuses on Internet-connected devices and systems, such as servers, routers, webcams, and IoT devices. 

- Censys, on the other hand, focuses on Internet-connected hosts, websites, certificates, and other Internet assets. 
- Further ressource: [Censys Search Use Cases](https://support.censys.io/hc/en-us/articles/20720064229140-Censys-Search-Use-Cases).

## VirusTotal

[VirusTotal](https://www.virustotal.com/) is an online website that provides a virus-scanning service for files using multiple antivirus engines.

-  It allows users to upload files or provide URLs to scan them against numerous antivirus engines and website scanners in a single operation. 
- They can even input file hashes to check the results of previously uploaded files.

The screenshot below shows the result of checking the submitted file against 67 antivirus engines. Furthermore, one can check the community's comments for more insights. Occasionally, a file might be flagged as a virus or a Trojan; however, this might not be accurate for various reasons, and that's when community members can provide a more in-depth explanation.

## Have I Been Pwned

[Have I Been Pwned](https://haveibeenpwned.com/) (HIBP) does one thing; it tells you if an email address has appeared in a leaked data breach. Finding one’s email within leaked data indicates leaked private information and, more importantly, passwords. Many users use the same password across multiple platforms, if one platform is breached, their password on other platforms is also exposed. Indeed, passwords are usually stored in encrypted format; however, many passwords are not that complex and can be recovered using a variety of attacks.

What is the top country with **lighttpd** servers?

United states

What does BitDefenderFalx detect the file with the hash `2de70ca737c1f4602517c555ddd54165432cf231ffc0e21fb2e23b9dd14e7fb4` as?

Android.Riskware.Agent.LHH

## Vulnerabilities