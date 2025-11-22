------

# Canton Ledger Privacy Model and Transaction Projections

Canton Ledger employs a hierarchical ledger structure designed not only to record transactional changes but also to enforce a nuanced privacy model. While the ledger structure defines *what* data is recorded, the privacy model specifies *who* can see which data. 



This article details the privacy mechanisms of Canton Ledger, focusing on subtransaction-level confidentiality, informees, witnesses, transaction projections, and the concepts of divulgence and disclosure.



[TOC]

## Canton Ledger: Structure and Transaction Model

The Canton Ledger provides a formal model for recording and managing interactions between parties in a Daml-based environment. Its design balances **granularity, atomicity, and hierarchical structure** to support transaction integrity and privacy. This section details the ledger structure, the hierarchical organization of actions, and the workflow of a sample DvP (Delivery versus Payment) scenario.

------

### Ledger Components

The ledger captures changes through a series of interconnected layers:

1. **Actions** – The basic units of ledger changes, representing contract creation, choice exercises, or contract fetches.
2. **Transactions** – Lists of root actions executed atomically.
3. **Commits** – Pair a transaction with the requesters that initiated it.
4. **Ledger** – A directed acyclic graph (DAG) of commits, ordered by dependencies among contract IDs.

This layered structure ensures both clarity in recording operations and the ability to reason about causality and privacy.

### Actions and Nodes

The Ledger Model distinguishes two main types of actions: **creating contracts** and **exercising choices**. Each action consists of a **root node** and optional **subactions**, forming a hierarchical tree.

- **Create node:** Records contract creation, including a unique contract ID, template ID and arguments, signatories (parties authorizing creation and archival), and observers (parties informed of changes).
- **Exercise node:** Captures a choice exercised on a contract, specifying the exercise kind (consuming or non-consuming), input contract ID, template/interface IDs, choice arguments, actors (performers), choice observers, and the exercise result.
- **Fetch node:** Represents a read-only access to a contract, similar to a non-consuming exercise, with no consequences.

An **action** inherits its type from its root node:

- **Create action:** Root is a Create node; no consequences.
- **Exercise action:** Root is an Exercise node; consequences form subactions.
- **Fetch action:** Root is a Fetch node; no consequences.

The hierarchical structure of actions allows for **nested subactions**, ensures proper contract usage, and supports the ledger’s notions of consumption, usage, and privacy.

## Privacy Model Overview

Canton Ledger operates on a **need-to-know** basis. Each participant sees only the ledger changes that involve contracts in which they have a stake, as well as the consequences of those changes. The hierarchical ledger structure naturally supports **sub-transaction privacy**, allowing fine-grained access control for participants.

### Informees

The concept of **informees** formalizes which parties should be notified of a ledger action:

- **Stakeholders** include **signatories** and **contract observers** of a contract. Stakeholders have a direct interest in contract changes.
- **Actors** are controllers of choice exercises and may have a stake in the action without necessarily being stakeholders of the underlying contract.
- **Choice observers** monitor the outcomes of specific choice exercises.

The table below summarizes the assignment of informees for different actions:

| ACTION                 | SIGNATORIES | CONTRACT OBSERVERS | ACTORS | CHOICE OBSERVERS |
| ---------------------- | ----------- | ------------------ | ------ | ---------------- |
| Create                 | X           | X                  |        |                  |
| Consuming Exercise     | X           | X                  | X      | X                |
| Non-consuming Exercise | X           |                    | X      | X                |
| Fetch                  | X           |                    |        |                  |

**Key points:**

- A contract observer is generally not informed of non-consuming exercises or fetches unless explicitly an actor or choice observer.
- Daml templates may define pre-consuming and post-consuming choices, compiled as non-consuming exercises with embedded archival actions. Observers are only informees of the archival subaction.

#### Example

In an asset swap between Alice and Bob:

- Alice, as a signatory of the input contract, is an informee of the root node of the action.
- Bob, as the actor of the choice, is also an informee.
- Banks involved may only be informees for specific subactions where they have a role, e.g., fetching or exercising a transfer.

The **informees of an action** are the informees of its root node. Since actions form complete trees of nodes, informees of an action see all nodes in that tree, regardless of their individual node-level informee status.

### Witnesses

A **witness** is a party entitled to see a node because it appears in a subaction that the party can observe. Formally:

> For a transaction, the witnesses of a node are the union of informees of all subactions containing that node.

Every informee of a node is also a witness. Witnesses ensure that nodes shared across multiple actions are visible to all relevant parties, even if those parties are not informees for some specific nodes.

### Transaction Projection

Projections define **the view of a transaction available to a group of parties**. Each party sees only the subtransaction containing nodes whose witnesses include at least one party in the group.

**Projection rules:**

1. Keep an action if at least one informee is in the party set PPP.
2. Otherwise, replace the action with the projection of its consequences.
3. Drop actions with no consequences relevant to PPP.

**Properties:**

- Projections operate at the action level, not nodes.
- The absorption property ensures that projecting first to a larger set QQQ and then to a subset PPP is equivalent to directly projecting to PPP.
- Individual projections may reveal less than joint projections for a set of parties due to ordering ambiguities.

**Example:**

- Alice and Bob, as informees of the root action in a DvP transaction, see the entire action subtree.
- Bank 1 only sees the subactions in which it is an informee, missing the rationale behind certain transfers between Alice and Bob.

### Ledger Projection

Ledger projection extends transaction projections to the ledger level:

1. Project each transaction in the ledger for the party set PPP.
2. Remove empty transactions.
3. Construct a DAG with edges for transactions that reference overlapping contracts among PPP.

Ledger projections do not retain requester information to prevent revealing witnesses beyond informees. Each party receives a DAG reflecting only the portions of the ledger relevant to them.

### Divulgence

**Divulgence** occurs when a contract becomes visible to a non-stakeholder:

- **Immediate divulgence:** Witnesses temporarily see contract creations they are not informees of to understand action consequences.
- **Input divulgence:** Non-informee witnesses see input contracts required to validate projected transactions.

Divulgence ensures transaction consistency without granting permanent access to non-stakeholders.

### Disclosure

**Disclosure** occurs when non-stakeholders actively use contracts:

- Requires explicit communication, often off-ledger, to ensure correct contract usage.
- Distinct from immediate divulgence: simply being a witness does not authorize future contract use.
- Helps maintain privacy among multiple parties without unnecessary exposure.

Adding non-stakeholders as observers can solve disclosure but introduces **privacy and scalability challenges**, as all observers learn about each other and the size of projections grows quadratically or cubically.

------

Canton Ledger’s privacy architecture thus balances **fine-grained access control** with practical usability, leveraging informees, witnesses, projections, divulgence, and disclosure to manage visibility while preserving confidentiality in multi-party transactions.

https://docs.digitalasset.com/overview/3.3/explanations/ledger-model/ledger-privacy.html