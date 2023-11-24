---
layout: post
title:  Tools to create documentation for Solidity Smart Contracts
date:   2023-06-03
lang: en
locale: en-GB
last-update: 
categories: blockchain ethereum
tags: solidity blockchain ethereum smart-contract
image: /assets/article/blockchain/ethereum/ethereum-logo-portrait-purple-purple.png
description: This article presents some very interesting tools to perform an analyze of a smart contract written in Solidity and generate the documentation.
---

This article presents some very interesting tools to perform an analyze of a smart contract written in *Solidity* and generate the documentation.

Here a summary:

- [Slither](https://github.com/crytic/slither) to perform a static analysis on the smart contract and generate a vulnerability report.

- [Solidity-docgen](https://github.com/OpenZeppelin/solidity-docgen): extract the documentation
- [Surya](https://github.com/ConsenSys/surya) : generate graph, inheritance, markdown report, ...
- [Solgraph](https://github.com/raineorshine/solgraph): generates a [DOT](https://en.wikipedia.org/wiki/DOT_(graph_description_language)) graph that visualizes function control flow of a Solidity contract and highlights potential security vulnerabilities.
- [Sol2uml](https://github.com/naddison36/sol2uml):  generate an UML/Class diagram
- vscode-solidity-auditor: [https://github.com/ConsenSys/vscode-solidity-auditor](https://github.com/ConsenSys/vscode-solidity-auditor)

Why use these tools ?

- A good documentation allows other developers and users to better understand the code.
- it helps to find bugs and security issues inside the smart contract
- When a security audit is performed, it helps the auditor to understand the code.

## [Slither](https://github.com/crytic/slither)

Slither is a very good tool to perform a static analysis on the smart contract and generate a vulnerability report.

>Slither is a Solidity static analysis framework written in Python3. It runs a suite of vulnerability detectors, prints visual information about contract details, and provides an API to easily write custom analyses.

## [Solidity-docgen](https://github.com/OpenZeppelin/solidity-docgen)

> solidity-docgen is a program that extracts documentation for a Solidity project.

Installation

```
npm install solidity-docgen
```

You can use it as a standalone library or as a hardhat plugin

## [Surya](https://github.com/ConsenSys/surya)

> Surya is an utility tool for smart contract systems. It provides a  number of visual outputs and information about the contracts' structure. Also supports querying the function call graph in multiple ways to aid  in the manual inspection of contracts.

Installation:

```
npm install -g surya
```



Surya is also available with the VS Code extension: [vscode-solidity-auditor](https://github.com/ConsenSys/vscode-solidity-auditor) [https://github.com/ConsenSys/vscode-solidity-auditor]()



### Graph

"The `graph` command outputs a DOT-formatted graph of the control flow."

![](https://user-images.githubusercontent.com/4008213/39415345-fbac4e3a-4c39-11e8-8260-0d9670c352d6.png)

### ftrace 

"The `ftrace` command outputs a *treefied* function call trace stemming from the defined "CONTRACT::FUNCTION" and traversing "all|internal|external" types of calls."

![](https://user-images.githubusercontent.com/4008213/42409007-61473d12-81f1-11e8-8fee-1867cfd66822.png)

### flatten

"The `flatten` command outputs a flattened version of the  source code, with all import statements replaced by the corresponding  source code. "



### describe

"The `describe` command shows a summary of the contracts and methods in the files provided."

![](https://user-images.githubusercontent.com/4008213/48572168-97bfc780-e900-11e8-9e86-d265498de936.png)

### Inheritance

"The `inheritance` command outputs a DOT-formatted graph of the inheritance tree. "

![](https://user-images.githubusercontent.com/23033765/39249140-f50d2828-486b-11e8-81b8-8c4ffb7b1b54.png)

### Dependencies

"The `dependencies` command outputs the [c3-linearization](https://en.wikipedia.org/wiki/C3_linearization) of a given contract's inheritance graph. " 

### Parse

"The `parse` command outputs a *treefied* AST object coming from the parser."

![](https://user-images.githubusercontent.com/4008213/39415303-87df40de-4c39-11e8-8e03-ead72e88f1e3.png)

### mdreport

"The `mdreport` command creates a Markdown description report  with tables comprising information about the system's files, contracts  and their functions."



### [Solgraph](https://github.com/raineorshine/solgraph)

An alternative to Surya to create a CFG graph is Solgraph.

![](https://raw.githubusercontent.com/raineorshine/solgraph/master/example.png)



Generates a [DOT](https://en.wikipedia.org/wiki/DOT_(graph_description_language)) graph that visualizes function control flow of a Solidity contract and highlights potential security vulnerabilities.

```bash
npx solgraph contracts/YOUR_CONTRACT.sol > YOUR_CONTRACT.dot
```

Convert the dot file in PNG

```bash
dot -Tpng YOUR_CONTRACT.dot -o YOUR_CONTRACT.png
```



## [Sol2uml](https://github.com/naddison36/sol2uml)

> A visualisation tool for [Solidity](https://solidity.readthedocs.io/) contracts featuring:
>
> 1. [Unified Modeling Language (UML)](https://en.wikipedia.org/wiki/Unified_Modeling_Language) [class diagram](https://en.wikipedia.org/wiki/Class_diagram) generator for Solidity contracts.
> 2. Contract storage layout diagrams.
>

Example:

![](https://raw.githubusercontent.com/naddison36/sol2uml/master/examples/OpenZeppelinERC20.svg)

### Alternative

- Run a Plantuml server on your local machine, see [https://github.com/plantuml/plantuml-server](https://github.com/plantuml/plantuml-server)

- Use plantuml inside VScode to generate an uml

This feature is directly available if you install the vscode extension [Solidity Visual Developer](https://marketplace.visualstudio.com/items?itemName=tintinweb.solidity-visual-auditor)

![solidity-visual-auditor-uml]({{site.url_complet}}/assets/article/blockchain/ethereum/solidity/solidity-visual-auditor-uml.png)





## [vscode-solidity-auditor](https://github.com/ConsenSys/vscode-solidity-auditor)

> ​      Solidity language support and visual security auditor for Visual Studio Code

VScode solidity auditor is a swiss-knife which includes a varietiy of tools to analyze a contract and generate the documentation

It offers the following option: generate report, graph, inheritance, function signature, uml,...

It includes the tool Surya too.



# Reference

[https://www.alchemy.com/top/solidity-tools](https://www.alchemy.com/top/solidity-tools)