# Aderyn

Aderyn uses a series of [detectors](https://cyfrin.gitbook.io/cyfrin-docs/aderyn-cli/detectors-quickstart) that, given a set of Solidity smart contracts within a directory, analyze the smart contracts Abstract Syntax Tree ([AST](https://cyfrin.gitbook.io/cyfrin-docs/aderyn-cli/what-is-an-ast)) to find vulnerability patterns and report them in an easy-to-consume markdown document.

In this article, you will learn how to get started using Aderyn to analyze your Solidity codebase and generate a report on its vulnerabilities.

https://cyfrin.gitbook.io/cyfrin-docs/aderyn-cli/quickstart

```
aderyn [OPTIONS] path/to/your/project
```

Replace `[OPTIONS]` with specific [command-line arguments ](https://cyfrin.gitbook.io/cyfrin-docs/cli-options)as needed.

**What happens when you call** `**aderyn?**`

- Search for all Solidity files within the directory structure
- Compile the Solidity files and load their ASTs into its [`WorkspaceContext`](https://cyfrin.gitbook.io/cyfrin-docs/aderyn-cli/detectors-quickstart/detectors-api-reference/workspacecontext)
- For each available [detector](https://cyfrin.gitbook.io/cyfrin-docs/aderyn-cli/detectors-quickstart), call [`detect`](https://cyfrin.gitbook.io/cyfrin-docs/aderyn-cli/detectors-quickstart/detectors-api-reference/detect) and pass in the [`WorkspaceContext`](https://cyfrin.gitbook.io/cyfrin-docs/aderyn-cli/detectors-quickstart/detectors-api-reference/workspacecontext)

Your codebase's full markdown security report will be generated for you now.

### Hardhat

Path to the source contracts. Used to avoid analyzing libraries, tests or scripts and focus on the contracts.

​          In Foundry projects, it's auto-captured by foundry.toml and it's usually not necessary to provide it.

```
aderyn [OPTIONS]  --src=contracts/ path/to/your/project
```

https://cyfrin.gitbook.io/cyfrin-docs/cli-options

```


         
```



Useful option

```
**-x, --path-excludes <PATH_EXCLUDE>**
```



Output the list of detectors.

```

```

