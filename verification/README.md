# Article verification

Code that tests the claims made in articles: smart contracts, Foundry tests and scripts.

This directory is kept in git, so a result can be reproduced later. It is listed under `exclude:` in `_config.yml`, so Jekyll does not publish it. The repository itself is public, so the code here can still be read on GitHub.

## Layout

One directory per article, named after the post without its date:

```text
verification/
└── <article-slug>/
    ├── README.md        what is tested, which article claims it depends on, how to run it
    ├── foundry.toml
    └── test/
```

## Rules

- Keep sources only. Build output (`out/`, `cache/`, `broadcast/`) is ignored by git.
- Pin the compiler and EVM version, so a test keeps meaning the same thing.
- Run everything from inside the article's directory, for example `forge test -vv --offline`.
- Do not commit keys, RPC URLs with tokens, or details of the machine.
- Test contracts are not audited and must not be deployed. Say so in any contract copied into an article.
