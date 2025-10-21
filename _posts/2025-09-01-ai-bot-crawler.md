---
layout: post
title: "AI Crawler bots (Claude, ChatGPT, Google) - Overview"
date:   2025-09-01
lang: en
locale: en-GB
categories: 
tags: ai crawler bot
description: List of AI crawler bot use for AI training and user actions such as GPTBot, ClaudeBot or Google-Extended
image: 
isMath: false
---

List of AI crawler bot use for AI training and user actions such as GPTBot, ClaudeBot or Google-Extended,

[TOC]

## Perplexity Crawlers

| User Agent      | Description                                                  | Use  to train models | Use in search result | Use in user actions |
| --------------- | ------------------------------------------------------------ | -------------------- | -------------------- | ------------------- |
| PerplexityBot   | `PerplexityBot` is designed to surface and link websites in search results on Perplexity. It is not used to crawl content for AI foundation models. To ensure your site appears in search results, we recommend allowing `PerplexityBot` in your site’s `robots.txt` file and permitting requests from our published IP ranges listed below.  Full user-agent string: `Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)`  Published IP addresses: [https://www.perplexity.com/perplexitybot.json](https://www.perplexity.com/perplexitybot.json) | No                   | Yes                  | Probably            |
| Perplexity‑User | `Perplexity-User` supports user actions within Perplexity. When users ask Perplexity a question, it might visit a web page to help provide an accurate answer and include a link to the page in its response. `Perplexity-User` controls which sites these user requests can access. It is not used for web crawling or to collect content for training AI foundation models.  Full user-agent string: `Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Perplexity-User/1.0; +https://perplexity.ai/perplexity-user)`  Published IP addresses: [https://www.perplexity.com/perplexity-user.json](https://www.perplexity.com/perplexity-user.json)  Since a user requested the fetch, this fetcher generally ignores robots.txt rules. | No                   | No                   | Yes                 |

Reference: [docs.perplexity.ai/guides/bots](https://docs.perplexity.ai/guides/bots)

## OpenAI Crawlers (ChatGPT)

| USER AGENT    | DESCRIPTION & DETAILS                                        | Use  to train models | Use in search result | Use in user actions |
| ------------- | ------------------------------------------------------------ | -------------------- | -------------------- | ------------------- |
| OAI-SearchBot | OAI-SearchBot is for search. OAI-SearchBot is used to link to and surface websites in search results in ChatGPT's search features. It is not used to crawl content to train OpenAI’s generative AI foundation models. To help ensure your site appears in search results, we recommend allowing OAI-SearchBot in your site’s robots.txt file and allowing requests from our published IP ranges below.  Full user-agent string will contain `; OAI-SearchBot/1.0; +https://openai.com/searchbot` | No                   | Yes                  | -                   |
| ChatGPT-User  | ChatGPT-User is for user actions in ChatGPT and Custom GPTs. When users ask ChatGPT or a CustomGPT a question, it may visit a web page with a ChatGPT-User agent. ChatGPT users may also interact with external applications via [GPT Actions](https://platform.openai.com/docs/actions/introduction). ChatGPT-User is not used for crawling the web in an automatic fashion, nor to crawl content for generative AI training. | No                   | -                    | Yes                 |
| GPTBot        | GPTBot is used to make our generative AI foundation models more useful and safe. It is used to crawl content that may be used in training our generative AI foundation models. Disallowing GPTBot indicates a site’s content should not be used in training generative AI foundation models.  Full user-agent string: `Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.1; +https://openai.com/gptbot` | Yes                  | -                    | -                   |

Reference: [platform.openai.com/docs/bots](https://platform.openai.com/docs/bots)

## Anthropic (Claude)

| **Bot**          | **Use**                                                      | **What happens when you disable it**                         | Use  to train models | Use in search result | Use in user actions |
| ---------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | -------------------- | -------------------- | ------------------- |
| ClaudeBot        | ClaudeBot helps enhance the utility and safety of our generative AI models by collecting web content that could potentially contribute to their training. | When a site restricts ClaudeBot access, it signals that the site's future materials should be excluded from our AI model training datasets. | Yes                  | -                    | -                   |
| Claude-User      | Claude-User supports Claude AI users. When individuals ask questions to Claude, it may access websites using a Claude-User agent. | Claude-User allows site owners to control which sites can be accessed through these user-initiated requests. Disabling Claude-User on your site prevents our system from retrieving your content in response to a user query, which may reduce your site's visibility for user-directed web search. | -                    | -                    | Yes                 |
| Claude-SearchBot | Claude-SearchBot navigates the web to improve search result quality for users. It analyzes online content specifically to enhance the relevance and accuracy of search responses. | Disabling Claude-SearchBot on your site prevents our system from indexing your content for search optimization, which may reduce your site's visibility and accuracy in user search results. | -                    | Yes                  | -                   |

Reference: [support.anthropic.com - Does Anthropic crawl data from the web, and how can site owners block the crawler?](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)



## Bard / Vertex AI (Google)

### Google-Extended

> Today we’re announcing [Google-Extended](https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers), a new control that web publishers can use to manage whether their sites help improve[ Bard](https://bard.google.com/) and[ Vertex AI](https://cloud.google.com/vertex-ai) generative APIs, including future generations of models that power those products. By using Google-Extended to control access to content on a site, a website administrator can choose whether to help these AI models become more accurate and capable over time.

Reference: [blog.google - An update on web publisher controls](https://blog.google/technology/ai/an-update-on-web-publisher-controls/)

## Meta Web Crawlers



### Meta-ExternalAgent

> The Meta-ExternalAgent crawler crawls the web for use cases such as training AI models or improving products by indexing content directly.

Reference: [developers.facebook.com - Meta Web Crawlers](https://developers.facebook.com/docs/sharing/webmasters/web-crawlers/)



## Apple (Applebot)

### Applebot-Extended

The data crawled by Applebot may also be used to help train Apple foundation models powering generative AI features across Apple products, including Apple Intelligence, Services, and Developer Tools. Web publishers can opt-out from having their content used to train generative foundation models by disallowing [Applebot-Extended](https://support.apple.com/en-us/119829#extended) in the robots.txt file.

Reference: [support.apple.com - About Applebot](https://support.apple.com/en-us/119829)

## Amazonbot

See [developer.amazon.com - About Amazonbot](https://developer.amazon.com/amazonbot)

## Robots.txt

Example of robots.txt to forbid AI training bot but allows bot use for user interactions

```
User-agent: GPTBot
Disallow: /
User-agent: Google-Extended
Disallow: /
User-agent: ClaudeBot
Disallow: /
User-agent: Applebot-Extended
Disallow: /
User-agent: Meta-ExternalAgent
Disallow: /
User-agent: Amazonbot
Disallow: /
```

