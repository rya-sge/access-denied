# Understanding Gradient Descent: The Engine Behind Machine Learning

Gradient descent is one of the most important algorithms in machine learning and optimization. It's the backbone of many popular models, helping them learn from data by minimizing errors and improving performance.

## What is Gradient Descent?

At its core, gradient descent is an **optimization algorithm**. It’s used to find the **minimum of a function**—typically a *cost function* or *loss function* in machine learning. The goal is to adjust the model's parameters (like `weights`in a neural network) so that the predictions get closer to the actual values.

Think of it like hiking down a hill in the fog. You can’t see the bottom, but you can feel the slope beneath your feet and step in the direction that goes downward. That’s exactly what gradient descent does: it follows the slope of the cost function to reach the lowest point.

### Cost & loss function

### Loss Function (error quantification)

The **loss function** measures how far off a single prediction is from the actual result. It quantifies the "error" for one example.

**Example:** In regression tasks, a common loss function is **Mean Squared Error (MSE)** for one data point:
$$
\text{Loss} = (y_{\text{true}} - y_{\text{pred}})^2
$$


### Cost Function (holistic view of the model’s performance)

The **cost function** is the **average of the loss function** over the entire dataset. It gives a holistic view of the model’s performance.

If you have `m` examples:
$$
J(\theta) = \frac{1}{m} \sum_{i=1}^{m} (y^{(i)}_{\text{true}} - y^{(i)}_{\text{pred}})^2
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
\theta_i = \theta_i - \alpha \cdot \nabla J(\theta)
$$


Where:

- θ is the parameter vector.
- α  is the **learning rate** — a small constant that controls the step size.
- ∇J(θ)is the gradient of the cost function with respect to θ.

## Types of Gradient Descent

There are several variations:

- **Batch Gradient Descent**: Uses the entire dataset to compute the gradient. It’s accurate but can be slow for large datasets.
- **Stochastic Gradient Descent (SGD)**: Updates parameters using one training example at a time. It’s faster but more erratic.
- **Mini-Batch Gradient Descent**: A compromise that uses a small, random subset of the data. It’s widely used in practice.

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

## Challenges and Solutions

Gradient descent is powerful but not without its issues:

- **Learning rate tuning**: Too small and it’s slow; too large and it might overshoot the minimum.
- **Local minima**: In complex models, the function might have many minima. The algorithm might get stuck.
- **Plateaus and saddle points**: Areas where the gradient is close to zero but not at a minimum.

To deal with these, several enhancements exist, such as:

- **Momentum**: Adds a fraction of the previous update to the current one.
- **RMSProp** and **Adam**: Adaptive learning rates that adjust over time for each parameter.

## FAQ

> List some advantages of gradient descent algorithm

- It can handle very large sets of data (especially the stochastic or mini-batch form
  of gradient descent)
- It allows for incremental learning, i.e. on-the-fly adaptation of the model on new
  incoming data
- The learning principle is generalisable to many other form of “hypothesis families”
  hθ (x)﻿, including neural networks, deep neural networks, etc.

> What are the “Full” batch gradient descent principles?

1. Start with some initial θ﻿’s (for example random or null)
2. Visit the full training set to compute new values of the θ ﻿reducing J (θ)﻿
3. Loop in 2 until convergence
    The new values of θ﻿’s are chosen according to the “gradient” of J (θ)﻿, i.e. in the
    opposite direction of the slope

> What is the gradient descent update rule?

the parameter theta is replaced by its last value plus a step alpha in the opposite
direction (minus sign) of the gradient of the cost function.

>  What is the stochastic gradient descent principle?

1. Start with some initial θ﻿’s (for example random or null)

2. Select 1 training sample randomly in the set and perform the update of the θ﻿’s with
    this example. 
$$
  θi ← θi − α(h_θ (x_nn ) − y_n )x_n,i
$$



3. Loop in 2 until convergence.

> What about the convergence with stochastic gradient descent?
>
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

What is mini-batch gradient descent and what are its advantages?
We select randomly b samples on which we perform batch gradient descent
Advantages:
The adaptation noise of stochastic gradient descent is reduced.
It allows for vectorised implementations (more efficient, use of gpu)
It allows to distribute mini-batches on several machines or cores (map/reduce
pattern):
map = distribute the mini-batches, for example 50
reduce = update parameters with the results of the 50 mini-batches
A disadvantage is that the batch size b needs to be optimised

## Conclusion

Gradient descent is the workhorse of modern machine learning. Whether you're training a linear regression model or a deep neural network, gradient descent helps your model learn from data and improve over time. Understanding how it works—and how to tweak it—gives you a strong foundation for building intelligent systems.

## Reference

Write me an article about  gradient descent, "a) Explain cost function and loss function b) Write all math formula in mathjax latex for markdown (bracket) C) Is Gradiant descent use in transformer architecture ?"