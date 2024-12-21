---
layout: post
title:  Most useful commands with git
date:   2024-04-15
lang: en
locale: en-GB
categories: programmation
tags: git
description: List the must useful commands, for my daily work, with git.
image: /assets/article/programmation/Git-Icon-logo.png
isMath: false
---

This articles list the must useful commands, for my daily work, with **git**.

As a reminder, **Git** is a free and open source distributed version control system, see [git-scm.com](https://git-scm.com)

Some definition are simplified, see the documentation for a more precise description.

[TOC]



## Command list

> List of useful commands

* `pull`
Fetch the content of the remote directory
Reference : [git-scm.com/docs/git-pull](https://git-scm.com/docs/git-pull)
* `checkout`
  Switch branches or restore working tree files
  Reference : [git-scm.com/docs/git-checkout](https://git-scm.com/docs/git-checkout)
  You can create a new branch and switch on this one with the flag `-b`

  ```bash
  git checkout -b <BRANCH NAME>
  ```
* `branch`
  You can print all branch
  `git branch`
  You can delete a branch with the flag `-d`

  ```bash
  git branch -d <BRANCH NAME>
  ```
* `status`
Print the change status
You can print all change recursively with :
```bash
git status -uall
```

* `add`
  Add file contents to the index
  Reference : [git-scm.com/docs/git-add](https://git-scm.com/docs/git-add)
  You can add all directories and files with the following command :

  ```bash
  git add --all
  ```
* `commit`

  ```bash
  git commit -S -m "Your Message"
  ```
* `push`
  Update remote refs along with associated objects

  ```bash
  git push
  ```

-----

## Submodule

> Manage a github submodule
>
> Submodules allow you to keep a Git repository as a subdirectory of another Git repository. This lets you clone another repository into your project and keep your commits separate. 
> Reference: [git-scm.com - Git Tools - Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)

### Add submodule
```bash
git clone   --recurse-submodules 
```

**With the clone command**

```bash
git clone --recurse-submodules https://github.com/cameronmcnz/surface.git
```

Reference : [theserverside.com - Clone a git repository with submodules using init and update example](https://www.theserverside.com/blog/Coffee-Talk-Java-News-Stories-and-Opinions/How-to-clone-a-git-repository-with-submodules-init-and-update)

**Project already cloned**

> Add submodule to a projet already cloned

Basic command

```bash
git submodule init
git submodule update
```

Reference : [git-scm.com/book/en/v2/Git-Tools-Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)

- With recrusive:

```bash
git submodule update --init --recursive
```

Reference : [stackoverflow - How do I "git clone" a repo, including its submodules?](https://stackoverflow.com/questions/3796927/how-do-i-git-clone-a-repo-including-its-submodules)

#### Update
> You can update the submodules with the following commands

```bash
git submodule update --recursive --remote
git submodule foreach git pull origin master
```

Reference: [gist.github.com/rms80/4e14099ff422af3a6df3e38914908c05](https://gist.github.com/rms80/4e14099ff422af3a6df3e38914908c05)

#### Delete
```bash
git submodule deinit <submodule_directory>
git rm <submodule_directory>
rm -rf .git/modules/<submodule_directory>

git commit -m"Removed Submodule"
git push
```

Reference: [educative.io/answers/how-to-delete-a-git-submodule](https://www.educative.io/answers/how-to-delete-a-git-submodule)

------

## Undo change

### Before git add

```
git checkout HEAD -- my-file.txt
```

See [Hard reset of a single file](https://stackoverflow.com/questions/7147270/hard-reset-of-a-single-file)

### After git add

- **Unstage Changes** 

=> After git add

=> Before git commit)

```bash
git reset HEAD README.md
git checkout README.md
```

Reference :
[earthdatascience.org -  Lesson 5. Undo Local Changes With Git](https://www.earthdatascience.org/courses/intro-to-earth-data-science/git-github/version-control/git-undo-local-changes/)

### After git commit

- **Go back**

```bash
git reset --hard HEAD~1
git push --force
```

Warning : this command will delete all files created after the commit.
Reference: [stackoverflow - How to force a git revert](https://stackoverflow.com/questions/48975429/how-to-force-a-git-revert)

-------

## Cherry pick

Cherry pick is a command to apply the changes introduced by some existing commits

> Cherry-picking from another fork  

```bash
git checkout <branch>
git fetch <other-fork-alias>
git cherry-pick <commit-hash>
git push <your-fork-alias>
```

Reference: [gist.github.com/bhumphrey/3764983](https://gist.github.com/bhumphrey/3764983), [git-scm.com - git-cherry-pick](https://git-scm.com/docs/git-cherry-pick)
