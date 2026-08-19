---
layout: home
title: About
permalink: /about/
lang: en
locale: en-GB
description: Ryan S., computer security engineer focused on blockchain and smart contract development, and the author of the AccessDenied notes and articles.
image: /assets/1.jpg
---

<header class="c-header u-hide u-no-margin-bottom">
  <div class="c-header__box">
    {% include search-box.html class="u-full-width" %}
  </div>
</header>

<section class="c-page">

<h1>About</h1>

<p>I am a computer security engineer, with a focus on blockchain and smart contract development.</p>

<p>My notes are available on this website, <strong>AccessDenied</strong>. It covers various topics such as blockchain, cryptography, programming, networking, and so on. I hope you can find your happiness among this content.</p>

<p>Before jumping on the crypto wagon, I participated in my free time in Capture The Flags (CTFs) and solved challenges on <a href="https://tryhackme.com/" rel="noopener" target="_blank">TryHackMe</a> and <a href="https://www.root-me.org/" rel="noopener" target="_blank">Root Me</a>.</p>

<p>I also run a <a href="https://x.com/{{ site.social-twitter }}" rel="me noopener" target="_blank">Twitter/X account</a> to monitor attacks on the blockchain ecosystem. If you have any questions, you can contact me on <a href="https://www.linkedin.com/in/{{ site.social-linkedin }}" rel="me noopener" target="_blank">LinkedIn</a>.</p>

<h2>Where to find me</h2>

<ul>
  <li><a href="https://github.com/{{ site.social-github }}" rel="me noopener" target="_blank">GitHub</a> — code and the source of this site</li>
  <li><a href="https://x.com/{{ site.social-twitter }}" rel="me noopener" target="_blank">Twitter/X ({{ site.social-twitter }})</a> — attacks on the blockchain ecosystem</li>
  <li><a href="https://www.linkedin.com/in/{{ site.social-linkedin }}" rel="me noopener" target="_blank">LinkedIn</a> — the best way to reach me</li>
  <li><a href="https://bsky.app/profile/{{ site.social-bluesky }}" rel="me noopener" target="_blank">Bluesky</a></li>
</ul>

<h2>Main articles on this site</h2>

<ul>
  <li><a href="{{ '/2024/05/06/solidity-interview-question-rareskills-advanced/' | relative_url }}">RareSkills Solidity Interview Answers - Advanced</a></li>
  <li><a href="{{ '/2024/04/16/build-blockchain-oracle/' | relative_url }}">How to build a blockchain oracle</a></li>
  <li><a href="{{ '/2023/07/20/metamask-secret/' | relative_url }}">Deep dive into MetaMask Secrets</a></li>
  <li><a href="{{ '/2024/03/28/ethereum-staking/' | relative_url }}">Ethereum Staking - How It Works</a></li>
  <li><a href="{{ '/2024/10/15/trezor-wallet-security/' | relative_url }}">Trezor Crypto Wallet – Cryptography and Security</a></li>
</ul>

<h2>Published as part of my work for Taurus</h2>

<p><em>Cross-chain bridge</em></p>

<ul>
  <li><a href="https://www.taurushq.com/blog/blockchain-interoperability-explained-bridges-cross-chain-protocols-and-ccip/" rel="noopener" target="_blank">Blockchain Interoperability Explained: Bridges, Cross-Chain Protocols, and CCIP</a></li>
  <li><a href="https://www.taurushq.com/blog/how-to-bridge-usdc-across-evm-chains-using-chainlinks-ccip-protocol" rel="noopener" target="_blank">How to Bridge USDC Across EVM Chains Using Chainlink's CCIP Protocol</a></li>
</ul>

<p><em>Tokenization</em></p>

<ul>
  <li><a href="https://www.taurushq.com/blog/equity-tokenization-how-to-pay-dividend-on-chain-using-cmtat/" rel="noopener" target="_blank">Equity Tokenization: How to Pay Dividend On-Chain Using CMTAT</a></li>
  <li><a href="https://www.taurushq.com/blog/token-transfer-management-how-to-apply-restrictions-with-cmtat-and-erc-1404/" rel="noopener" target="_blank">Token Transfer Management: How to Apply Restrictions with CMTAT and ERC-1404</a></li>
  <li><a href="https://www.taurushq.com/blog/cmtat-tokenization-deployment-with-proxy-and-factory/" rel="noopener" target="_blank">Making CMTAT Tokenization More Scalable and Cost-Effective with Proxy and Factory Contracts</a></li>
  <li><a href="https://www.taurushq.com/blog/tokenization-on-ethereum-and-evm-blockchains-which-smart-contract-should-you-use/" rel="noopener" target="_blank">Tokenization on Ethereum and EVM Blockchains: Which Smart Contract Should You Use?</a></li>
</ul>

<h2>Browse the site</h2>

<p>Every article is filed under one or more <a href="{{ '/category/blockchain/' | relative_url }}">categories</a> — the largest are
<a href="{{ '/category/blockchain/' | relative_url }}">Blockchain</a>,
<a href="{{ '/category/security/' | relative_url }}">Security</a>,
<a href="{{ '/category/cryptography/' | relative_url }}">Cryptography</a>,
<a href="{{ '/category/ethereum/' | relative_url }}">Ethereum</a> and
<a href="{{ '/category/zkp/' | relative_url }}">Zero-Knowledge Proofs</a> —
and tagged on the <a href="{{ '/tags/' | relative_url }}">tags page</a>.</p>

</section> <!-- /.c-page -->

{% comment %}
  Person structured data.

  jekyll-seo-tag emits the author only as a name string inside each article's
  BlogPosting node. That is not enough for an engine to treat the author as an
  entity: the `sameAs` list below is what ties this site to the GitHub, X,
  LinkedIn and Bluesky profiles, and `mainEntityOfPage` makes this page the
  canonical description of that entity rather than one mention among 254.

  The profile URLs are built from _config.yml so there is a single source of
  truth for them.
{% endcomment %}
{% assign site_root = site.url | append: site.baseurl %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ProfilePage",
  "url": {{ site_root | append: '/about/' | jsonify }},
  "mainEntity": {
    "@type": "Person",
    "@id": {{ site_root | append: '/about/#person' | jsonify }},
    "name": {{ site.author | jsonify }},
    "jobTitle": {{ site.author-job | jsonify }},
    "description": "Computer security engineer, with a focus on blockchain and smart contract development.",
    "knowsAbout": [
      "Blockchain security",
      "Smart contract development",
      "Solidity",
      "Cryptography",
      "Zero-knowledge proofs",
      "Computer networking"
    ],
    "url": {{ site_root | append: '/about/' | jsonify }},
    "mainEntityOfPage": {{ site_root | append: '/about/' | jsonify }},
    "sameAs": [
      {% for link in site.social.links %}{{ link | jsonify }}{% unless forloop.last %},{% endunless %}
      {% endfor %}
    ]
  }
}
</script>
