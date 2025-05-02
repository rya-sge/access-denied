# kosaraju algorithm

See also : https://cp-algorithms.com/graph/strongly-connected-components.html

https://takeuforward.org/graph/strongly-connected-components-kosarajus-algorithm-g-54/

## Concepts

### Strongly Connected Components (SCCs)

**Strongly Connected Components (SCCs)** are groups of nodes where:

- **Every node** can reach **every other node** in the group through directed edges.

Kosaraju's algorithm efficiently finds all SCCs in a directed graph **in two passes of DFS**.

The **key insight** is:

> If you process nodes **in the right order** (reverse of finishing times) **after reversing the graph**, each DFS will perfectly capture one SCC.

###  Why It Works:

1. **First DFS (Original Graph):**
   - Explore the graph and record the "finish times" (when a node is fully explored).
   - Nodes that finish later depend on others — so their finishing order reveals deep dependencies.
2. **Reverse the Graph:**
   - Flip all the edges.
   - Now, where there was a dependency path from `A` to `B`, there’s a path back from `B` to `A`.
3. **Second DFS (Reversed Graph):**
   - Process nodes **in order of decreasing finish time** (most dependent nodes first).
   - When you start DFS from a node in the reversed graph, you can reach **all nodes in its SCC** — but no nodes outside.
   - Because we reversed the graph, a full traversal stays **inside one SCC**.

 Reversing the graph in Kosaraju's algorithm is crucial because it helps ensure that when we perform the second DFS pass, each DFS only explores nodes within a single strongly connected component (SCC). By reversing the graph, we ensure that when we process nodes in reverse finish time order (from the first DFS), we start a new DFS from each unvisited node, which allows us to correctly isolate and identify each SCC without mixing them together. This ensures that we capture the full set of SCCs independently.

## Functions

| Function         | What it does                                                 |
| ---------------- | ------------------------------------------------------------ |
| `new()`          | Create an empty graph                                        |
| `add_edge(u, v)` | Add a directed edge from `u` to `v`                          |
| `dfs()`          | First pass: explore graph and record node finishing times    |
| `reverse()`      | Create a reversed graph                                      |
| `dfs_util()`     | Second pass: collect nodes into a strongly connected component |
| `kosaraju()`     | Full Kosaraju algorithm to find all SCCs                     |
| `main()`         |                                                              |





## Steps

### Step 1: **Topological Sorting of Nodes by Finish Time**

**Purpose:**
 Identify the order in which nodes finish processing during a Depth-First Search (DFS). This order is crucial for exploring the reversed graph.

**Function Used:**
 `dfs()`

**How it works:**

1. Start a DFS from an unvisited node.
2. As you traverse the graph, mark nodes as visited.
3. Once a node finishes (all its neighbors are processed), push it onto a stack.

This stack will store nodes in the order of their finish times (topological sort).

------

### Step 2: **Reverse the Graph**

**Purpose:**
 Reverse all edges in the graph. If there is a directed edge from `u → v` in the original graph, make it `v → u` in the reversed graph. This reversal helps group strongly connected components (SCCs) in the second DFS.

**Function Used:**
 `reverse()`

**How it works:**

1. Create a new, empty graph.
2. For every edge in the original graph, add the reversed edge to the new graph.

------

### Step 3: **Find Strongly Connected Components (SCCs)**

**Purpose:**
 Use the reversed graph and the stack from Step 1 to identify SCCs. Start processing nodes from the stack (in reverse order of their finish times), and for each unvisited node, perform a DFS to find its SCC.

**Functions Used:**
 `dfs_util()` and `kosaraju()`

**How it works:**

1. Pop a node from the stack (highest finish time first).
2. If the node is unvisited, perform a DFS on the reversed graph starting from that node.
3. Collect all nodes reachable in this DFS—they form a single SCC.
4. Mark all visited nodes to avoid processing them again.

Repeat this process for all nodes in the stack.

------

### Full Algorithm Execution:

#### 1️⃣ Initialization (in `kosaraju()`):

- Prepare a stack for storing finish times.
- Use a `visited` set to track visited nodes.

#### 2️⃣ First Pass: DFS on Original Graph (via `dfs()`):

- Traverse each node in the graph.
- Fill the stack with nodes in order of their finish times.

#### 3️⃣ Reverse the Graph (via `reverse()`):

- Construct a reversed graph where all edges are flipped.

#### 4️⃣ Second Pass: DFS on Reversed Graph (via `dfs_util()`):

- Process nodes from the stack in reverse order.
- For each unvisited node, find its SCC using DFS on the reversed graph.
- Store each SCC as a list of nodes.

------

### Mapping Functions to Algorithm Steps:

| Step  | Description                                              | Function(s)                                     |
| ----- | -------------------------------------------------------- | ----------------------------------------------- |
| **1** | Topological sort using DFS to order nodes by finish time | `dfs()` in the first loop of `kosaraju()`       |
| **2** | Reverse the graph                                        | `reverse()`                                     |
| **3** | Second DFS on reversed graph to collect SCCs             | `dfs_util()` in the second loop of `kosaraju()` |

------

### Why These Steps Work:

- **Topological Order (Step 1):** Ensures that when we process nodes in reverse finish order, we explore all nodes in an SCC before moving to another SCC.
- **Reversed Graph (Step 2):** Groups all nodes of an SCC together in one DFS traversal.
- **Second DFS (Step 3):** Discovers each SCC as an isolated subgraph.



## Code

```rust
use std::collections::HashMap;
use std::collections::HashSet;

use std::collections::{HashMap, HashSet};

/// Struct representing a directed graph using an adjacency list
struct Graph {
    adj_list: HashMap<i32, Vec<i32>>,
}

impl Graph {
    /// Creates a new, empty graph
    fn new() -> Self {
        Graph {
            adj_list: HashMap::new(),
        }
    }

    /// Adds a directed edge from node `u` to node `v`
    fn add_edge(&mut self, u: i32, v: i32) {
        self.adj_list.entry(u).or_default().push(v);
    }

    /// First depth-first search (DFS) pass:
    /// - Visits nodes and records the order in which nodes finish processing.
    /// - This order is important for the second pass.
    fn dfs(&self, v: i32, visited: &mut HashSet<i32>, stack: &mut Vec<i32>) {
        visited.insert(v);
        if let Some(neighbors) = self.adj_list.get(&v) {
            for &neighbor in neighbors {
                if !visited.contains(&neighbor) {
                    self.dfs(neighbor, visited, stack);
                }
            }
        }
        stack.push(v); // Node finishes processing, push to stack
    }

    /// Reverses the direction of all edges in the graph.
    /// - Needed between the two DFS passes in Kosaraju's algorithm.
    fn reverse(&self) -> Graph {
        let mut rev_graph = Graph::new();
        for (&u, neighbors) in &self.adj_list {
            for &v in neighbors {
                rev_graph.add_edge(v, u); // Reverse the edge
            }
        }
        rev_graph
    }

    /// Second depth-first search (DFS) pass:
    /// - Finds all nodes in a strongly connected component (SCC),
    ///   starting from a given node `v`.
    fn dfs_util(&self, v: i32, visited: &mut HashSet<i32>, component: &mut Vec<i32>) {
        visited.insert(v);
        component.push(v);
        if let Some(neighbors) = self.adj_list.get(&v) {
            for &neighbor in neighbors {
                if !visited.contains(&neighbor) {
                    self.dfs_util(neighbor, visited, component);
                }
            }
        }
    }

    /// Kosaraju's algorithm to find all strongly connected components (SCCs):
    /// - 1st pass: order nodes by finishing time
    /// - 2nd pass: process nodes in reverse finishing order on the reversed graph
    fn kosaraju(&self) -> Vec<Vec<i32>> {
        let mut stack = Vec::new();
        let mut visited = HashSet::new();

        // Step 1: Fill stack with vertices ordered by finishing time
        for &vertex in self.adj_list.keys() {
            if !visited.contains(&vertex) {
                self.dfs(vertex, &mut visited, &mut stack);
            }
        }

        // Step 2: Reverse the graph
        let rev_graph = self.reverse();

        // Step 3: Perform DFS on reversed graph in order defined by the stack
        let mut visited = HashSet::new();
        let mut sccs = Vec::new();

        while let Some(v) = stack.pop() {
            if !visited.contains(&v) {
                let mut component = Vec::new();
                rev_graph.dfs_util(v, &mut visited, &mut component);
                sccs.push(component);
            }
        }

        sccs
    }
}

/// Example usage: build a graph and find its strongly connected components
fn main() {
    let mut graph = Graph::new();
    graph.add_edge(1, 0);
    graph.add_edge(0, 2);
    graph.add_edge(2, 1);
    graph.add_edge(0, 3);
    graph.add_edge(3, 4);

    let sccs = graph.kosaraju();
    println!("Strongly Connected Components:");
    for component in sccs {
        println!("{:?}", component);
    }
}
fn main() {
    let mut graph = Graph::new();
    graph.add_edge(1, 0);
    graph.add_edge(0, 2);
    graph.add_edge(2, 1);
    graph.add_edge(0, 3);
    graph.add_edge(3, 4);

    let sccs = graph.kosaraju();
    println!("Strongly Connected Components:");
    for component in sccs {
        println!("{:?}", component);
    }
}
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_kosaraju_sccs() {
        let mut graph = Graph::new();
        graph.add_edge(1, 0);
        graph.add_edge(0, 2);
        graph.add_edge(2, 1);
        graph.add_edge(0, 3);
        graph.add_edge(3, 4);

        let mut sccs = graph.kosaraju();

        // Optional: sort inside each component and sort the list of components for stable comparison
        for scc in &mut sccs {
            scc.sort();
        }
        sccs.sort();

        let expected_sccs = vec![
            vec![0, 1, 2],
            vec![3],
            vec![4],
        ];

        assert_eq!(sccs, expected_sccs);
    }
}
```

