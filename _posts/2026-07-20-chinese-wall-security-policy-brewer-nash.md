---
layout: post
title: The Chinese Wall Security Policy - Brewer and Nash Model
date:   2026-07-20
lang: en
locale: en-GB
categories: security
tags: security access-control chinese-wall brewer-nash bell-lapadula clark-wilson confidentiality
description: A formal walkthrough of the Brewer and Nash Chinese Wall security policy, its conflict-of-interest access rules, its *-property against indirect flows, and why it cannot be reduced to Bell-LaPadula.
image: /assets/article/securite/security-model/chinese-wall-security-policy-brewer-nash.png
isMath: true
---

Most early computer security theory was written for the military, where the question is how to stop classified information from leaking downward through a fixed lattice of clearances. The commercial world has a different problem. A market analyst who advises one oil company must never end up advising its direct competitor, yet nothing stops that same analyst from working with a bank in an unrelated sector. The constraint is not a static classification attached to the data; it is dynamic, and it depends on the history of what each person has already touched. The Brewer and Nash **Chinese Wall** policy, published at the 1989 IEEE Symposium on Security and Privacy, is the formal model of exactly this rule.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Why a Commercial Policy Needs Its Own Model

Military security policy dominated computer security research through the 1980s. The seminal shift came from Clark and Wilson, who argued that commercial data processing has integrity and separation requirements just as demanding as the military's confidentiality requirements, but structurally different. The Chinese Wall policy sits inside that commercial family. It is, in Brewer and Nash's words, the code of practice a market analyst working for a financial institution must follow.

The scenario is concrete. An analyst providing corporate business services holds confidential, insider knowledge about the clients they advise. To advise a second corporation that competes with the first would let that insider knowledge leak sideways, from one client to its rival. That is precisely the abuse the policy must prevent. At the same time, the analyst must stay free to advise any number of corporations that do **not** compete with each other, and free to work on general, non-confidential market information.

Two features make this hard to express with the tools of the day:

- **Access is not a property of the data alone.** In Bell-LaPadula, whether a subject may read an object is fixed by the object's label and the subject's clearance. Under the Chinese Wall, whether the analyst may open a dataset depends on which datasets they have *already* opened. The same dataset is freely readable by one analyst and forbidden to another, purely because of history.
- **It combines free choice with mandatory control.** The analyst chooses freely which company to advise first. Once that choice is made, a mandatory rule closes off every competitor of that company. Neither a purely discretionary nor a purely mandatory model captures both halves at once.

In the United Kingdom this is not merely good manners. Brewer and Nash note that the UK Stock Exchange rules carried the force of law under the Financial Services Act 1986, so a correct implementation of the policy, whether by manual procedure or by computer, provided a legitimate legal defence against certain charges of insider dealing.

## The Data Model: Objects, Company Datasets, and Conflict Classes

The model organises all corporate information into a three-level hierarchy. Every rule that follows is stated in terms of these three levels, so they are worth fixing precisely.

- **Objects** are the individual items of information, each one concerning a single corporation. In Bell-LaPadula terms, an object is the file in which such an item is stored.
- **Company datasets** group together all the objects that concern the same corporation. Every object about "Oil Company A" lives in the Oil Company A dataset.
- **Conflict of interest classes** group together all the company datasets whose corporations are in competition. All the oil companies form one conflict class; all the banks form another.

Each object therefore carries a two-part security label. For an object $$o$$, write $$X(o)$$ for its conflict of interest class and $$Y(o)$$ for its company dataset. Brewer and Nash abbreviate these as $$x_j$$ and $$y_j$$ for object $$o_j$$. The hierarchy is captured by a single structural axiom.

$$
\begin{aligned}
Y(o_1) = Y(o_2) \;\Longrightarrow\; X(o_1) = X(o_2)
\end{aligned}
$$

In words: if two objects sit in the same company dataset, they necessarily sit in the same conflict of interest class. This is axiom **A1** in the paper's formal annex, and its contrapositive (Corollary 1) is just as useful: objects in different conflict classes must belong to different company datasets.

![Composition of objects into company datasets and conflict of interest classes]({{site.url_complet}}/assets/article/securite/security-model/chinese-wall-object-composition-concept.png)

A worked example fixes the vocabulary. Suppose a system holds information on Bank A, Oil Company A, and Oil Company B. There are three company datasets, one per corporation. There are two conflict of interest classes: one for banks, holding the Bank A dataset, and one for oil companies, holding both the Oil Company A and Oil Company B datasets. Bank A conflicts with no one here; the two oil companies conflict with each other.

## The Simple Security Rule

The core of the policy is a rule about what a subject may read. A *subject* is a user, or any program acting on their behalf. To decide access, the system must remember the full history of who has read what. The model records this in a boolean matrix $$N$$, indexed by (subject, object) pairs: $$N(u, o)$$ is true exactly when subject $$s_u$$ has, or has had, access to object $$o$$. A subject *possesses* an object once it has read it.

The **simple security rule** (axiom **A2**) grants a read request from subject $$s_u$$ for object $$o_r$$ if and only if, for every object $$o$$ the subject already possesses, one of two conditions holds:

- $$o_r$$ is in the **same company dataset** as $$o$$, so it lies inside a wall the subject is already within, or
- $$o_r$$ belongs to an **entirely different conflict of interest class** from $$o$$.

Written with the label functions, access to $$o_r$$ is granted iff for all objects $$o$$ the subject possesses,

$$
\begin{aligned}
X(o) \neq X(o_r) \;\;\text{or}\;\; Y(o) = Y(o_r).
\end{aligned}
$$

The first time any subject reads anything, $$N$$ is empty for that subject, so the request is trivially granted (axioms **A3** and **A4** in the annex set the initially secure state and make the first access unconstrained). Freedom of choice lives here: a fresh analyst may open any dataset at all.

![Access decision workflow for the Chinese Wall simple security rule]({{site.url_complet}}/assets/article/securite/security-model/chinese-wall-access-decision-workflow.png)

The metaphor names itself once you trace a sequence. Say the analyst reads the Oil Company A dataset first. Later they request Bank A: granted, because banks and oil companies are different conflict classes. Later still they request Oil Company B: **denied**, because Oil Company B and the already-possessed Oil Company A are in the same conflict class but different datasets. A wall has gone up between our analyst and Oil Company B. The wall's exact position was not fixed in advance; it took shape around the first oil company the analyst happened to choose. This is the subtle blend of free choice and mandatory control: the analyst chose the side of the wall, but once chosen, the wall is mandatory.

## Three Theorems, One Staffing Consequence

From the simple security rule, Brewer and Nash prove three theorems. The first two confirm that the informal metaphor really is enforced by the formal rule.

- **Theorem T1.** Once a subject has accessed an object, the only other objects accessible to that subject lie within the same company dataset, or within a different conflict of interest class. There is no third option, which is the wall.
- **Theorem T2.** A subject can have access to at most one company dataset in each conflict of interest class. Having stepped inside one oil company, every other oil company is sealed off.

The third theorem is the pragmatic payoff, and it answers a question the metaphor alone does not: how many analysts does a firm actually need?

- **Theorem T3.** If a conflict of interest class $$X$$ contains $$X_y$$ company datasets, then the minimum number of subjects that will allow every object to be accessed by at least one subject is $$X_y$$.

The reasoning is a counting argument. By T2, no single subject can cover two datasets in the same conflict class, so covering all $$X_y$$ datasets of the largest class demands at least $$X_y$$ distinct subjects. Take the largest conflict class, the one with the most member company datasets, and its size $$L$$ is the answer: the firm needs at least $$L$$ analysts if every dataset is to be reachable by someone.

That is a floor, not a ceiling. In practice the number climbs. If two analysts happen to choose the same dataset, or if an Automobile class has five motor companies and five analysts each pick a *different* car maker, then the question of who is left free to advise Oil Company A becomes a live constraint. $$L$$ is the minimum staffing the policy can ever require, useful precisely because it is a hard lower bound.

## Sanitized Information and the *-Property

The simple security rule protects against *direct* reading across a wall. It does nothing about *indirect* flows, where information crosses the wall by being written into a dataset that a competitor's analyst can legitimately read. Bell-LaPadula met the same problem and answered it with a *-property; the Chinese Wall model needs its own.

Consider two analysts. User A has access to Oil Company A and Bank A. User B has access to Oil Company B and Bank A. Both legitimately share Bank A. Now User A reads Oil Company A information and writes it into the Bank A dataset. User B, reading Bank A, can now see Oil Company A's secrets, even though the wall between Oil Company A and Oil Company B was never directly crossed. The simple security rule alone permits this leak.

![Indirect information flow through a shared dataset that the *-property blocks]({{site.url_complet}}/assets/article/securite/security-model/chinese-wall-indirect-flow-workflow.png)

Before stating the fix, the model separates sensitive from *sanitized* data. Sanitization disguises a corporation's information so its origin can no longer be inferred, for example by aggregating it into general market statistics. The model reserves one distinguished company dataset, written $$y_0$$, to hold sanitized information relating to all corporations, and gives it its own distinguished conflict of interest class $$x_0$$ (axiom **A5** ties the two together: an object bears label $$y_0$$ if and only if it bears $$x_0$$). Everything outside $$y_0$$ is treated as sensitive and belonging to some particular corporation.

The **\*-property** (axiom **A6**) then restricts writing. A write by subject $$s_u$$ to object $$o_b$$ is permitted only if:

- the simple security rule already permits access to $$o_b$$, and
- there is no object $$o_a$$ that the subject can read which sits in a *different* company dataset and contains *unsanitized* information.

Formally, write access to $$o_b$$ is denied if there exists a readable $$o_a$$ with

$$
\begin{aligned}
Y(o_a) \neq Y(o_b) \;\;\text{and}\;\; Y(o_a) \neq y_0.
\end{aligned}
$$

The effect is proved as Theorem T4: the flow of unsanitized information is confined to its own company dataset, while sanitized information may flow freely throughout the system. In the earlier scenario, once the \*-property is in force, User A can no longer write Oil Company A's unsanitized data into Bank A, because User A can read Oil Company A, which is a different dataset holding unsanitized information. The leak is closed, but sanitized market summaries still move wherever they are needed.

## Why Bell-LaPadula Cannot Capture It

Much of the paper is devoted to a careful comparison with Bell-LaPadula (BLP), and the conclusion is negative: the Chinese Wall policy cannot be faithfully represented as a BLP model. This matters because BLP was the reference model of the era, and the natural instinct was to reduce every new policy to it.

The two models are described in parallel terms, both talking about the composition of objects and the rules for simple-security and \*-property access, which invites a translation. Brewer and Nash construct one. BLP labels each object with a `(class, category)` pair and each subject with a `(clearance, need-to-know)` pair. One can map each Chinese Wall $$(x, y)$$ label to a distinct BLP category, reserve one classification for sanitized data and another for unsanitized, and hand each subject a need-to-know set covering exactly the datasets they have accessed. Under that mapping the BLP simple-security and \*-property rules do reproduce the right accesses at a given instant.

The translation breaks on the two features from the start of the article:

- **BLP has no notion of history.** Suppose management suddenly needs User A to gain access to company dataset 8. In BLP you cannot simply extend User A's need-to-know, because you have no way to know for certain that User A never accessed dataset 2, a competitor of dataset 8. The Chinese Wall model carries exactly that history in its matrix $$N$$; BLP does not, so it cannot answer the question.
- **BLP cannot hold free choice and mandatory control together.** BLP works only if subjects are *not* free to choose which datasets they access; the need-to-know is assigned in advance. You can restore free choice by giving every subject need-to-know over all datasets, but then the mandatory separation is gone. So BLP can model the mandatory part or the free-choice part of the Chinese Wall policy, but not both at the same time.

Because the Chinese Wall policy requires both simultaneously, and BLP structurally cannot provide both, the Chinese Wall model must be regarded as distinct from BLP and significant in its own right. That is the paper's central claim, and it is the reason the model has a name of its own rather than being a footnote to BLP.

## Relation to Clark and Wilson

The paper closes by reconciling the model with Clark and Wilson's commercial integrity work. Their rule E2 controls access on the basis of relations of the form (user, program, object): a user may only touch an object through a program they are permitted to execute against it. A finer degree of control than BLP's, and the Chinese Wall model should be compatible with it to be practically useful.

To accommodate this, Brewer and Nash refine what *subject* means. Through most of the paper a subject can be read as a user. But treating a subject as a (user, process) pair would be wrong, because axiom A2 would then let a single user reach two datasets in the same conflict class simply by using two different processes, which is the very leak the wall exists to stop. So the refined model reads *subject* as the human user in all the axioms and theorems, and introduces processes separately.

Two extra axioms bolt Clark and Wilson's structure on without disturbing the theorems already proved:

- **A7.** A user may execute only certain named processes: the pair (user, process) must be in a permitted relation.
- **A8.** A process may access only certain objects, constrained by an added $$z$$ attribute on labels and on processes, with a process able to reach an object only when the object's $$z$$-component is within the process's permitted set.

With these, a process may access an object exactly when the user is allowed to execute that process *and* the Chinese Wall rules allow that user to access that object *and* the process is itself allowed to access it. The Chinese Wall model thus sits comfortably alongside Clark and Wilson rather than at odds with it.

## Conclusion

The Chinese Wall policy formalises a rule that predates computers: an advisor must not carry one client's secrets to that client's competitor. Its distinctive move is to make the read constraint depend on access history rather than on a fixed label, encoded in the possession matrix $$N$$ and enforced by the simple security rule. The \*-property then closes the indirect channel, confining unsanitized information to its own company dataset while letting sanitized data circulate. Three theorems tie the rules back to the metaphor and give a firm a concrete lower bound, $$L$$, on how many analysts it must employ.

The comparison with Bell-LaPadula sets the model apart. Because the policy requires both free choice and mandatory control at once, and BLP can supply only one of the two, the Chinese Wall model cannot be reduced to BLP; it is a separate commercial security model, compatible in turn with Clark and Wilson's access rules.

![Mindmap of the Chinese Wall security policy]({{site.url_complet}}/assets/article/securite/security-model/chinese-wall-security-policy-brewer-nash.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **Chinese Wall** | A commercial security policy that forbids a subject from accessing information about a corporation once it holds information about a competitor of that corporation. |
| **Object** | The smallest unit of information in the model, each item concerning exactly one corporation and stored in a file. |
| **Company dataset** | The group of all objects that concern the same corporation, written $$y$$ for a given object. |
| **Conflict of interest class** | The group of all company datasets whose corporations compete with each other, written $$x$$ for a given object. |
| **Subject** | A user, or a program acting on a user's behalf, whose access history determines what it may access next. |
| **Possession** | The relation, recorded in the matrix $$N$$, that a subject has read an object and now holds its information. |
| **Simple security rule** | Read is granted only if the target is in a dataset the subject already occupies, or in an entirely different conflict class (axiom A2). |
| **\*-property** | Write is permitted only when it cannot expose unsanitized information from one dataset into another (axiom A6). |
| **Sanitized information** | Data disguised so its corporate origin cannot be inferred, held in the distinguished dataset $$y_0$$ and free to flow anywhere. |
| **Bell-LaPadula** | The military confidentiality model with static `(class, category)` labels, shown unable to capture the history-dependent Chinese Wall policy. |

## Frequently Asked Questions

**Q: What are the three levels of the Chinese Wall data hierarchy?**

From the bottom up: objects (individual items of information, each about one corporation), company datasets (all objects concerning the same corporation), and conflict of interest classes (all company datasets whose corporations compete). Every object carries a label $$(x, y)$$ giving its conflict class and its company dataset, and axiom A1 ties them together: two objects in the same dataset are always in the same conflict class.

**Q: Why does the access decision depend on history rather than on the data's label alone?**

Because the policy protects against carrying one client's secrets to a competitor, and whether that risk exists depends entirely on what the subject has previously read. The same dataset is freely readable by a subject who has touched nothing conflicting and forbidden to a subject who has already entered a competitor's dataset. The model records this history in the boolean possession matrix $$N(u, o)$$, and the simple security rule reads it on every request. A model with only static labels, such as Bell-LaPadula, has no place to store this history.

**Q: How does the simple security rule decide whether to grant a read?**

A read of object $$o_r$$ by subject $$s_u$$ is granted if and only if, for every object the subject already possesses, the target is either in the same company dataset (inside a wall the subject already occupies) or in an entirely different conflict of interest class. If the target shares a conflict class with something already held but sits in a different dataset, it is a competitor and access is denied. A subject's very first access is always granted, since it possesses nothing yet.

**Q: What does the \*-property add that the simple security rule misses, and why is it needed?**

The simple security rule blocks direct reads across a wall but not indirect flows. Two analysts can legitimately share a neutral dataset, say Bank A; if one writes a client's secrets into Bank A, the other reads them without ever directly crossing the wall. The \*-property (axiom A6) closes this by forbidding a write whenever the subject can also read unsanitized information from a different dataset. Theorem T4 proves the result: unsanitized information stays confined to its own company dataset, while sanitized information flows freely.

**Q: Combining the theorems, why can Bell-LaPadula not represent the Chinese Wall policy?**

Two independent reasons, each rooted in the model's core features. First, Bell-LaPadula labels are static and carry no access history, so it cannot decide requests that depend on what a subject previously read, such as whether extending a need-to-know is safe. Second, the Chinese Wall policy needs free choice (any first dataset) and mandatory control (all competitors then sealed) at the same time; Bell-LaPadula can encode one or the other but not both, since granting free choice requires need-to-know over all datasets, which erases the mandatory separation. Theorems T1 and T2 show the enforced separation is real and history-driven, which is exactly what Bell-LaPadula cannot reproduce.

**Q: What is Theorem T3's practical meaning for a financial institution?**

Theorem T3 states that if the largest conflict of interest class contains $$L$$ company datasets, then at least $$L$$ subjects are required for every object to be accessible by someone, because by Theorem T2 no single subject can cover two datasets in the same class. It gives the firm a hard lower bound on analyst headcount. The real number is usually higher, since analysts choosing the same or scattered datasets leave some datasets uncovered, but $$L$$ is the minimum the policy can ever demand.

## References

- [Brewer, D. F. C. and Nash, M. J. — The Chinese Wall Security Policy, IEEE Symposium on Security and Privacy, 1989](https://www.cs.purdue.edu/homes/ninghui/readings/AccessControl/brewer_nash_89.pdf)
- Clark, D. R. and Wilson, D. R. — A Comparison of Commercial and Military Computer Security Policies, IEEE Symposium on Security and Privacy, 1987
- Bell, D. E. and LaPadula, L. J. — Secure Computer Systems: Unified Exposition and Multics Interpretation, MTR-2997 Rev. 1, The MITRE Corporation, 1976
- McLean, J. — The Algebra of Security, IEEE Symposium on Security and Privacy, 1988
- [Main Security Models - Overview (Bell-LaPadula, Biba, Clark-Wilson)]({{site.url_complet}}/security/2025/01/15/security-models-overview.html)
