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

Interested in how Git manages and stores content? Check out my article: [Merkle DAGs(IPFS, GIT) - Overview](https://rya-sge.github.io/access-denied/2024/04/15/git-cheatsheet/)

[TOC]

## Summary tab

| **Command**                | **Description**                                             | **Additional Notes**                        |
| -------------------------- | ----------------------------------------------------------- | ------------------------------------------- |
| `git init`                 | Initializes a new Git repository.                           | Creates a `.git` directory.                 |
| `git clone <repo_url>`     | Copies an existing repository to your local machine.        | Used to download projects from GitHub.      |
| `git status`               | Shows the status of the working directory and staging area. | Helps track changes before committing.      |
| `git add <file>`           | Stages changes for the next commit.                         | Use `.` to stage all changes.               |
| `git commit -m "message"`  | Records changes in the repository with a message.           | Use `-S` to sign commits.                   |
| `git push origin <branch>` | Uploads local changes to a remote repository.               | Default branch is often `main` or `master`. |
| `git pull origin <branch>` | Fetches and merges changes from a remote repository.        | Keeps your local repo up to date.           |
| `git branch`               | Lists all local branches.                                   | Use `-a` to see remote branches too.        |
| `git checkout <branch>`    | Switches to another branch.                                 | Use `-b` to create and switch.              |
| `git merge <branch>`       | Merges another branch into the current one.                 | Helps integrate changes.                    |

Reference: ChatGPT with the input "Create me a tab with 10 most commands used for git. The tab has two columns: command and the description. If relevants, add more columns"

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

-----

## Sign commit

### Retroactively sign commit

**retroactively sign (`-S`) the last `N` commits** in a repository.

This command is typically used to **retroactively sign (`-S`) the last `N` commits** in a repository, ensuring that all commits in that range are GPG-signed without modifying their content.

```bash
git rebase --interactive --exec "git commit --amend --no-edit -S" HEAD~N
```



#### Explanation

1. **`git rebase --interactive (or -i)`**
   This starts an **interactive rebase**, allowing you to modify a sequence of commits.

2. **`--exec "git commit --amend --no-edit -S"`**

   - The `--exec` flag runs the specified command **after** each commit is applied during the rebase.

   - In this case, the command being executed is:

     ```bash
     git commit --amend --no-edit -S
     ```

   - `git commit --amend --no-edit`:

     - `--amend` modifies the last commit without changing its content.
     - `--no-edit` prevents opening the commit message editor, keeping the message unchanged.

   - `-S`

      (sign commit):

     - This cryptographically signs the commit using GPG (if GPG signing is enabled in your Git config).
     - Ensures commits are verified as signed by you.

3. **`HEAD~N`**

   - This specifies that the rebase should start from **N** commits before `HEAD` (i.e., the last `N` commits).
   - All `N` commits will be sequentially amended and signed.

#### Example Usage

If you want to sign the last **5** commits:

```
git rebase -i --exec "git commit --amend --no-edit -S" HEAD~5
```

After executing this command, Git will:

1. Start an interactive rebase on the last **5** commits.
2. For each commit, run `git commit --amend --no-edit -S`, signing it.
3. Continue through all 5 commits automatically.
4. Complete the rebase process.



References: ChatGPT with the input "Can you explain this command: git rebase --interactive --exec "git commit --amend --no-edit -S" HEAD~N"

## Git Push 

This part has been made with ChatGPT

> For git push, in general I don't indicate "origin". Do you know why ?



Firstly, what is `origin`?

`origin` is the default name given to the remote repository when you clone a repository and acts as a shorthand for the remote repository’s URL. See [Zero to Hero - Understanding git push origin main](https://zerotohero.dev/inbox/git-push-origin-main/)

You don’t need to explicitly specify `origin` when running `git push` due to **Git's upstream tracking configuration**.

### Why You Can Omit "origin":

1. **Upstream (Tracking) Branch is Set**

   - When you clone a repository or use `git push -u origin <branch>`, Git sets up an **upstream branch** (also called a **tracking branch**).
   - After this, simply running `git push` will default to pushing to the tracked remote (`origin` by default).

2. **Git's Default Push Behavior**

   - The behavior depends on your Git configuration:

     ```bash
     git config --get push.default
     ```

   - If set to `simple` (default in newer Git versions), `git push` will push the current branch to the remote branch with the same name, but only if it has been set as an upstream branch.

   - If set to `current`, it pushes to the remote branch with the same name.

Reference: [betterstack - Default Behavior of “Git Push” without a Branch Specified](https://betterstack.com/community/questions/default-behavior-of-push-withour-branch-specified/)

### How to Check Your Tracking Branch:

```bash
git branch -vv
```

This will show which remote branch your local branch is tracking.

### Example:

1. First-time push with upstream tracking:

   ```bash
   git push -u origin main
   ```

2. After that, just use:

   ```bash
   git push
   ```

   No need to specify `origin`every time!

### TL;DR:

- You don’t need `origin` because your branch already tracks a remote branch.
- Git automatically knows where to push based on upstream settings.
