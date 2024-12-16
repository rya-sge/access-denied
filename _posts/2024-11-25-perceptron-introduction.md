---
layout: post
title: Perceptron - a simple, binary neural network architecture
date:   2024-11-25
lang: en
locale: en-GB
categories: programmation
tags: ML AI perceptron neural-network
description: The perceptron, developed by Frank Rosenblatt in 1958, is one of the earliest and simplest models of artificial neural networks.
image: /assets/article/mlg/perceptron.drawio.png
isMath: true
---

The perceptron, developed by Frank Rosenblatt in 1958, is one of the earliest and simplest models of **artificial neural networks**. It is an algorithm that mimics the decision-making process of neurons in the human brain. 

## What is a Perceptron?

A perceptron is a type of linear classifier that maps input features to an output decision using a weighted sum and an activation function. 

The original Perceptron belongs to subcategory of linar classifier called **binary** because it can only solve linear separable problems

The model consists of the following components:

1. **Inputs**: A set of feature values representing the data.
2. **Weights**: Parameters associated with each input that determine the importance of each feature.
3. **Bias**: A constant added to the weighted sum to help the perceptron better fit the data.
4. **Activation Function**: A function (e.g., step or sign function) that determines the output based on the weighted sum.

Mathematically, a perceptron computes the output `y` as follows:


$$
\begin{aligned}
y = f\left(\sum_{i=1}^{n} w_i x_i + b\right)
\end{aligned}
$$
where `wi` are weights, `xi` are inputs, `b` is the bias, and `f` is the activation function.

If the perceptron's output correctly classifies the input, no changes are made to the weights. Otherwise, the perceptron adjusts its weights using a learning rule to minimize errors. This iterative process, known as training, allows the perceptron to learn a decision boundary for classification.

[TOC]

### Schema

![perceptron.drawio]({{site.url_complet}}/assets/article/mlg/perceptron.drawio.png)

### Key terms

| Terms                         | Abbreviation |
| ----------------------------- | ------------ |
| Single-layer perceptron       | SLP          |
| Multi-layer perceptron        | MLP          |
| Convolutional neural networks | CNN          |



### Strengths and Limitations of the Perceptron

The perceptron is efficient for linearly separable problems, where a straight line (or hyperplane in higher dimensions) can separate classes. 

However, it struggles with non-linear problems, such as the XOR problem, because it cannot capture complex patterns. 

This limitation was addressed by the development of multi-layer perceptrons (MLPs) and advanced architectures like convolutional neural networks (CNNs).



## Single-Layer vs. Multi-Layer Perceptrons

A **single-layer perceptron (SLP)** consists of only one layer of neurons connected directly to the input. It is capable of solving simple, linearly separable problems but cannot handle more complex, non-linear datasets (e.g., XOR problem). 

On the other hand, a **multi-layer perceptron (MLP)** introduces one or more hidden layers between the input and output layers. These hidden layers use non-linear activation functions, enabling MLPs to model non-linear relationships.

 Each layer in an MLP transforms data into higher-level abstractions, making it suitable for complex tasks like image recognition, speech processing, and natural language understanding. The additional layers allow MLPs to form intricate decision boundaries, overcoming the limitations of single-layer perceptrons.



------

## Perceptrons vs. Convolutional Neural Networks (CNNs)

Both perceptrons and convolutional neural networks (CNNs) are inspired by biological neurons and are designed to process data. However, they differ significantly in architecture and purpose:

1. **Similarities**:
   - Both use weights, biases, and activation functions to compute outputs.
   - They are trained using optimization techniques, such as gradient descent.
   - Both aim to minimize a loss function during training to improve performance.
2. **Differences**:
   - **Architecture**: A perceptron is a single-layer linear model, while CNNs are deep networks that include multiple layers, such as convolutional layers, pooling layers, and fully connected layers.
   - **Data Handling**: Perceptrons are suitable for structured data with fixed input sizes, whereas CNNs are specifically designed to handle high-dimensional data like images by extracting spatial hierarchies of features.
   - **Complexity**: While a perceptron is simple and interpretable, CNNs are more complex, capable of capturing intricate patterns through their hierarchical design.
   - **Applicability**: A perceptron performs basic linear classification, whereas CNNs excel in computer vision tasks such as image recognition, object detection, and segmentation.

In summary, while perceptrons laid the groundwork for modern machine learning, CNNs build on that foundation to solve far more complex problems, particularly in the domain of image processing.

------

## Applications of the Perceptron

Despite its simplicity, the perceptron has applications in tasks requiring linear classification. It is often used as a teaching tool to introduce concepts of supervised learning, gradient descent, and optimization. Additionally, it serves as a stepping stone to understanding advanced models like MLPs and CNNs.

------

## Conclusion

The perceptron is a historic and fundamental model that has influenced the field of machine learning profoundly. 

While its simplicity limits its use in complex tasks, the principles it embodies continue to underpin modern neural network architectures, including CNNs. 

Understanding the perceptron provides a crucial first step in exploring the broader world of artificial intelligence and neural networks.

------

## Reference

- [geeksforgeeks.org - What is Perceptron](https://www.geeksforgeeks.org/what-is-perceptron-the-simplest-artificial-neural-network/)

- [w3schools.com - perceptrons](https://www.w3schools.com/ai/ai_perceptrons.asp)

- [Wikipedia - Perceptron](https://en.wikipedia.org/wiki/Perceptron)

- [IBM Developer - A neural networks deep dive](https://developer.ibm.com/articles/cc-cognitive-neural-networks-deep-dive/)

- [Deep learning basics — Part 2 — Perceptron](https://medium.com/@sasirekharameshkumar/understanding-deep-learning-basics-part-2-466a7422d24b)

- ChatGPT with the input "Write me an article about Perceptron. Include a paragraph to explain the difference/similarity with CNN"