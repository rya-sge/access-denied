---
layout: post
title: "Gradient Descent in Machine Learning - Overview"
date: 2025-04-09
lang: en
locale: en-GB
categories: ai
tags: 
description: Gradient descent is an optimization algorithm used to find the minimum of a function—typically a cost function or loss function in machine learning. 
image: /assets/article/mlg/gradient-descent-mindmap.png
isMath: true
---

Gradient descent is one of the most important algorithms in machine learning and optimization. It It is used in supervised learning to minimize errors (`loss function`) and improving performance.

> This article comes primarily from ChatGPT with some modifications on my part. I hope to make it more personal in the future

## What is Gradient Descent?

Gradient descent is an **optimization algorithm**. It’s used to find the **minimum of a function**—typically a *cost function* or *loss function* in machine learning. The goal is to adjust the model's parameters (like `weights`in a neural network) so that the predictions get closer to the actual values. This adjustment is performed through the `update rule`.

Think of it like hiking down a hill in the fog. You can’t see the bottom, but you can feel the slope beneath your feet and step in the direction that goes downward. That’s exactly what gradient descent does: it follows the slope of the cost function to reach the lowest point.

### Cost & loss function

**The cost (or loss) function** measures the difference, or error, between actual `y` and `predicted y` at its current position. 

The model will use it to adjust the parameters to minimize the error and find the local or global minimum. It will continuously iterates, moving along the direction of steepest descent (or the negative gradient) until the cost function is close to or at zero. At this point, the model will stop learning. 

Cost function and loss function have a slight difference between them.

- loss function refers to the error of one training example
- cost function calculates the average error across an entire training set



![ibm-gradient-descent]({{site.url_complet}}/assets/article/mlg/ibm-gradient-descent.png)

Reference: [IBM - What is gradient descent?](https://www.ibm.com/think/topics/gradient-descent)

### Loss Function (error quantification)

The **loss function** measures how far off a single prediction is from the actual result. It quantifies the "error" for one example.

**Example:** In regression tasks, a common loss function is **Mean Squared Error (MSE)** for one data point:
$$
\begin{aligned}
\text{Loss} = (y_{\text{true}} - y_{\text{pred}})^2
\end{aligned}
$$


### Cost Function (holistic view of the model’s performance)

The **cost function** is the **average of the loss function** over the entire dataset. It gives a holistic view of the model’s performance.

If you have `m` examples:
$$
\begin{aligned}
J(\theta) = \frac{1}{m} \sum_{i=1}^{m} (y^{(i)}_{\text{true}} - y^{(i)}_{\text{pred}})^2
\end{aligned}
$$
**In short:**

- **Loss** = error for *one* example
- **Cost** = average loss over *all* examples

## How It Works

Here’s a simplified breakdown:

1. **Initialize parameters** (randomly or with some strategy).
2. **Compute the gradient** — the vector of partial derivatives that points in the direction of steepest increase.
3. **Update the parameters** by moving them in the opposite direction of the gradient.
4. **Repeat** this process until the function converges (i.e., further updates no longer significantly reduce the cost).

### The Update Rule

For a parameter θ, the update rule looks like this:
$$
\begin{aligned}
\theta_i = \theta_i - \alpha \cdot \nabla J(\theta)
\end{aligned}
$$


Where:

- θ is the parameter vector.
- α  is the **learning rate** — a small constant that controls the step size.
- ∇J(θ)is the gradient of the cost function with respect to θ.

## Types of Gradient Descent

There are three types of gradient descent learning algorithms: batch gradient descent, stochastic gradient descent and mini-batch gradient descent.

- **Batch Gradient Descent**: Uses the entire dataset to compute the gradient. It’s accurate but can be slow for large datasets.
- **Stochastic Gradient Descent (SGD)**: Updates parameters using one training example at a time. It’s faster but more erratic.
- **Mini-Batch Gradient Descent**: A compromise that uses a small, random subset of the data. It’s widely used in practice.

## Summary Comparison Table



| Type                              | Data per Update | Computational efficiency                                     | Speed for large dataset                        | Convergence Stability | Memory Usage | Use Case                     |
| --------------------------------- | --------------- | ------------------------------------------------------------ | ---------------------------------------------- | --------------------- | ------------ | ---------------------------- |
| Batch Gradient Descent            | All data        | Good (batch)                                                 | Slow <br />(store all of the data into memory) | High                  | High         | Small datasets               |
| Stochastic Gradient Descent (SGD) | 1 sample        | Bad<br />(Updates each training example's parameters one at a time) | Quick<br />(easier to store in memory)         | Low (noisy)           | Low          | Online learning, huge data   |
| Mini-Batch Gradient Descent       | Small subset    | Balance between batch and Stochastic                         | Balance between batch and Stochastic           | Medium-High           | Medium       | Deep learning, practical use |

## Gradient Descent Used in Transformer Architecture

Transformers — like BERT, GPT, T5, etc. — use **gradient descent (specifically variants of it like Adam)** for training.

### How?

- Each transformer model has **millions (or even billions)** of parameters.
- During training, we:
  1. Pass input sequences through the model.
  2. Calculate the **loss** between the predicted output and the target output (like next word in a sentence).
  3. Use **backpropagation** to compute gradients of the loss with respect to all parameters.
  4. Update the parameters using **gradient descent-based optimizers** (e.g., **Adam**, **AdamW**).

So while the architecture is complex, the **core optimization method is still gradient descent**, just highly optimized for performance and scale.



### Difference between Adam and standard gradient descent algorithm

In the standard gradient descent algorithm, the learning rate α is fixed, meaning we need to start at a high learning rate and manually change the alpha by steps or by some learning schedule. 

This lead to several challenge:

- A lower learning rate at the onset would lead to very slow convergence, 
- A very high rate at the start might miss the minima. 

Adam solves this problem by adapting the learning rate α for each parameter θ, enabling faster convergence compared to standard gradient descent with a constant global learning rate.

Reference: [builtin.com - Complete Guide to the Adam Optimization Algorithm](https://builtin.com/machine-learning/adam-optimization)

## Challenges and Solutions

Gradient descent  comes with its own set of challenges, depending notably if it a convex problems or not

#### Convex function/ Problems: 

- Only **one minimum**, which is also the **global minimum**.
- Gradient descent will always reach that bottom point as long as the learning rate is properly set.

            	|
               \|/
              \   /
               \_/



  ​    


#### Non-Convex Problems

Most **real-world machine learning problems** (especially deep learning) are **non-convex**, meaning:

- The cost surface can have **multiple valleys** (local minima) and **flat regions** (saddle points).
- Gradient descent might **not reach the best solution**.

     ```
         __       _     ___
        /  \__   / \   /   \
              \_/   \_/     \__
    ```
    
    

### Challenges

When the **slope (gradient) ≈ 0**, gradient descent **stops or slows down** — this is interpreted as a "minimum" (but not necessarily the best one).

Three places this can happen:

#### Global Minimum

-  The ideal point.

- Gradient is zero **and** cost is the **lowest possible**.

### Local Minimum

- Gradient is zero, **but** it’s **not the best spot**.
- The curve still looks like a "U", but it’s a **smaller dip** than the global minimum.

### Saddle Point

- The cost function looks like a **saddle**:
  - Going one direction: slope goes **up** (a local maximum).
  - Going the other direction: slope goes **down** (a local minimum).
- Gradient ≈ 0 at the saddle’s center → **confuses gradient descent into thinking it’s stuck.**

From [Wikipedia - Saddle_point](https://en.wikipedia.org/wiki/Saddle_point)

![wikipedia-saddle-point]({{site.url_complet}}/assets/article/mlg/wikipedia-saddle-point.png)

### Summary

Gradient descent is powerful but not without its issues:

- **Learning rate tuning**: Too small and it’s slow; too large and it might overshoot the minimum.
- **Local minima**: In complex models, the function might have many minima. The algorithm might get stuck.
- **Plateaus and saddle points**: Areas where the gradient is close to zero but not at a minimum.

To deal with these, several enhancements exist, such as:

- **Momentum**: Adds a fraction of the previous update to the current one.
- **RMSProp** and **Adam**: Adaptive learning rates that adjust over time for each parameter.





![gradient-descent-mindmap]({{site.url_complet}}/assets/article/mlg/gradient-descent-mindmap.png)

## FAQ

### Stochastic gradient descent

>  What is the stochastic gradient descent principle?

1. Start with some initial θ﻿’s (for example random or null)

2. Select 1 training sample randomly in the set and perform the update of the θ﻿’s with
   this example. 

$$
\begin{aligned}
θi ← θi − α(h_θ (x_nn ) − y_n )x_n,i
\end{aligned}
$$



3. Loop in 2 until convergence.

> What about the convergence with stochastic gradient descent?
>

The convergence is trickier to observe as we may select favorable and less
favorable points in the training set. In practice we may compute an “averaged”
cost function over the past U updates. Typically U<=N and U<<N if N is really
large.
We never actually converges like batch gradient descent does, but ends up
wandering around close to the global minimum. In practice, this isn't a problem -
as long as we are close to the minimum that's probably OK

>Stochastic gradient descent properties? And its advantages?

We update the parameters for each training samples, which is faster
We "generally" move in the direction of the global minimum, but not always
Advantages:

- It can handle very large sets of data
- It allows for incremental learning, i.e. on-the-fly adaptation of the model on
  new incoming data.
- The learning principle is generalisable to many other forms of “hypothesis
  families”.



> List some advantages of gradient descent algorithm

 - It can handle very large sets of data (especially the stochastic or mini-batch form of gradient descent)
- It allows for incremental learning, i.e. on-the-fly adaptation of the model on new incoming data
- The learning principle is generalisable to many other form of “hypothesis families” hθ (x)﻿, including neural networks, deep neural networks, etc.

> What are the “Full” batch gradient descent principles?

1. Start with some initial θ﻿’s (for example random or null)
2. Visit the full training set to compute new values of the θ ﻿reducing J (θ)﻿
3. Loop in 2 until convergence
    The new values of θ﻿’s are chosen according to the “gradient” of J (θ)﻿, i.e. in the
    opposite direction of the slope

> What is the gradient descent update rule?

The parameter theta is replaced by its last value plus a step alpha in the opposite
direction (minus sign) of the gradient of the cost function.

> What is mini-batch gradient descent and what are its advantages?
>

We select randomly b samples on which we perform batch gradient descent
Advantages:

- The adaptation noise of stochastic gradient descent is reduced.

- It allows for vectorised implementations (more efficient, use of gpu)

- It allows to distribute mini-batches on several machines or cores (map/reduce
  pattern):

  map = distribute the mini-batches, for example 50
  reduce = update parameters with the results of the 50 mini-batches
  A disadvantage is that the batch size b needs to be optimised



## Reference

- [IBM - What is gradient descent?](https://www.ibm.com/think/topics/gradient-descent)
- [builtin.com - Complete Guide to the Adam Optimization Algorithm](https://builtin.com/machine-learning/adam-optimization)
- [Wikipedia - Gradient descent](https://en.wikipedia.org/wiki/Gradient_descent)
- [Deep Learning — Part 2: Gradient Descent and variants](https://medium.com/@manoj-gupta/machine-learning-part-2-gradient-descent-and-variants-293f790850a6)
- ChatGPT with the input "Write me an article about  gradient descent, "a) Explain cost function and loss function b) Write all math formula in mathjax latex for markdown (bracket) C) Is Gradiant descent use in transformer architecture ?"