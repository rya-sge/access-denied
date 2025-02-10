---
layout: post
title: K-Nearest Neighbor (KNN) Algorithm  - Overview
date: 2025-02-10
lang: en
locale: en-GB
categories: ai
tags: K-Nearest-Neighbor KNN machine-learning dimensionality instance-based classification
description: This article explains the difference between supervised and unsupervised learning in Machine Learning with several examples.
image: /assets/article/mlg/knn-mindmap.png
isMath: true
---

**K-Nearest Neighbor (KNN)** is a widely used, simple, and effective machine learning algorithm. It is primarily utilized for classification and regression tasks, leveraging the concept of similarity to make predictions. Despite its simplicity, KNN can be powerful when applied to well-suited problems.

> This article comes primarily from ChatGPT with some modifications on my part. I hope to make it more personal in the future

[TOC]

------

## How KNN Works

KNN is a non-parametric and lazy learning algorithm. Here's what those terms mean:

- **Non-parametric:** It does not assume any specific form for the underlying data distribution.
- **Lazy:** It defers computation until the prediction phase, meaning no explicit model is built during training.

In essence, KNN classifies data points based on the class of their nearest neighbors in the feature space.

------

## The KNN Algorithm Steps

### Choose the Number of Neighbors (K)

The parameter `K` determines the number of nearest neighbors to consider for making a prediction. A smaller `K` may lead to high sensitivity to noise, while a larger `K` smooths the decision boundaries but may overlook local patterns.

### Measure Distance

To find the `K`-nearest neighbors of a data point, a distance metric is used. Commonly used metrics include:

- [Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance):
  $$
  \begin{aligned}
  d(\mathbf{x}, \mathbf{y}) = \sqrt{\sum_{i=1}^n (x_i - y_i)^2}
  \end{aligned}
  $$

The Euclidean distance measures the shortest possible line between two points.



- Manhattan distance:
  $$
  \begin{aligned}
  d(\mathbf{x}, \mathbf{y}) = \sum_{i=1}^n |x_i - y_i|
  \end{aligned}
  $$
  Manhattan distance measures the sum of the [absolute differences](https://www.datacamp.com/tutorial/python-absolute-value-a-quick-tutorial) between the coordinates of the points.

  

Reference: [datacamp - What is Manhattan Distance?](https://www.datacamp.com/tutorial/manhattan-distance)



- Minkowski distance:

  A generalized form of distance metrics:
  $$
  \begin{aligned}
  d(\mathbf{x}, \mathbf{y}) = \left( \sum_{i=1}^n |x_i - y_i|^p \right)^{1/p}
  \end{aligned}
  $$
  Minkowski distance provides a way to measure the distance between two points in a multi-dimensional space. It adds a parameter `p` which determines the type of distance (p ≥ 1). By testing different values of `p` during cross-validation, you can determine which value provides the best model performance for your specific dataset.

Reference: [datacamp - Minkowski Distance: A Comprehensive Guide](https://www.datacamp.com/tutorial/minkowski-distance)

### Find the Nearest Neighbors

For a given data point, locate the `K` nearest neighbors from the training dataset based on the chosen distance metric.

### Predict the Outcome

- **For Classification:** The algorithm assigns the majority class among the `K` neighbors to the data point.
- **For Regression:** The algorithm predicts the average (or weighted average) of the values of the `K` neighbors.

------

### Choosing the Right K Value

Selecting the optimal `K` is crucial for the algorithm's performance:

- **Small K:** Captures fine-grained patterns but may overfit and become sensitive to noise.
- **Large K:** Generalizes better by considering broader patterns but may miss finer details.

A common practice is to use cross-validation to find the best `K` for a specific dataset.

------

### Strengths and Weaknesses of KNN

#### Strengths

1. **Simple and Intuitive:** Easy to understand and implement.
2. **Versatile:** Works for both classification and regression tasks.
3. **Non-parametric:** Makes no assumptions about the underlying data distribution.

#### Weaknesses

1. **Computationally Expensive:** Storing all training data and computing distances at prediction time can be slow for large datasets.
2. **Memory Intensive:** Requires storing the entire dataset in memory.
3. **Sensitive to Scaling:** Feature scaling (e.g., normalization or standardization) is crucial, as distance measures are affected by the scale of data.

------

## KNN vs Perceptron, CNN, and Transformer

KNN, Perceptron, Convolutional Neural Networks (CNNs), and Transformers all serve unique purposes in machine learning but differ fundamentally in their mechanisms and applications:

### KNN vs Perceptron

- **KNN** is a lazy learning algorithm that makes predictions based on distances to training samples.
- **Perceptron** is an early neural network model that learns a linear decision boundary during training by updating weights iteratively.
- **Difference:** KNN does not build a model during training, while Perceptron builds a linear model through optimization.

See also my article [Perceptron - a simple, binary neural network architecture](https://rya-sge.github.io/access-denied/2024/11/25/perceptron-introduction/)

### KNN vs CNN

- **KNN** makes predictions by finding the nearest data points in a feature space.
- **CNN** is a deep learning model designed specifically for image data, leveraging convolutions to extract spatial features and patterns.
- **Difference:** KNN is simple and general-purpose, while CNN uses multiple layers to hierarchically learn features from complex data like images.

See also my article [Convolutional Neural Networks (CNNs) - Overview](https://rya-sge.github.io/access-denied/2024/11/19/convolutional-neural-networks-overview/)

### KNN vs Transformer

- **KNN** relies on distance measures to classify data points based on their proximity to known points.
- **Transformer** is a deep learning architecture that excels in processing sequences, using self-attention mechanisms to understand dependencies across all input data points (like words in a sentence).
- **Difference:** KNN is a simpler, instance-based learning algorithm, while Transformers are highly specialized for sequential data and involve complex deep learning architectures.

See also my article: [Transformers - Attention is All You Need](https://rya-sge.github.io/access-denied/2025/01/13/transformers/)

## FAQ

The answers come mainly from ChatGPT with some modifications on my part

### Introduction to K-NN

- **What is K-NN?**
  K-Nearest Neighbors (K-NN) is a simple, non-parametric, instance-based machine learning algorithm used for classification and regression by comparing data points based on distance metrics.
- **Is K-NN a non-parametric approach?**
  Yes, K-NN is non-parametric because it makes no assumptions about the data distribution and relies on the training data itself for predictions.
- **What does K-NN require?**
  K-NN requires a labeled dataset, a distance metric (e.g., Euclidean distance), and a value for `K` (the number of nearest neighbors to consider).

### Handling Ties and Class Imbalance

- **In K-NN, what are some tie-break strategies?**
  Common strategies include:
  1. Reducing `K` to an odd number (if using binary classification).
  2. Using weighted voting (favoring closer neighbors more).
  3. Selecting the most frequent class in the dataset.
- **With K-NN, what if we have an unbalanced training set (e.g., 10x more data for class A than class B)?**
  K-NN may be biased toward the majority class. Solutions include using weighted voting, resampling (oversampling minority class or undersampling majority class), or adjusting decision thresholds.

### Instance-Based vs. Model-Based Learning

- **What is the difference between instance-based learning and model-based learning?**
  Instance-based learning (e.g., K-NN) stores all training examples and makes predictions by comparing new instances to stored examples, while model-based learning (e.g., linear regression, neural networks) builds an explicit model from training data.
- **Is K-NN an instance-based or model-based learning algorithm?**
  K-NN is an instance-based learning algorithm because it does not create a generalized model but instead memorizes the training data and makes predictions based on comparisons.

### Computational Complexity of K-NN

- Assuming K-NN examples in the training set, what are the temporal (CPU time) and spatial (memory) complexities of K-NN? Are these complexities good or bad?
  - **Time complexity:** O(N⋅d)O(N \cdot d)O(N⋅d) (where ddd is the number of features) for each prediction, making it slow for large datasets.
  - **Space complexity:** O(N)O(N)O(N), as all training examples must be stored.
  - These complexities are bad because K-NN becomes inefficient with large datasets.

### Choosing K and Its Impact

- **What are the advantages of a large K?**
  A larger K smooths decision boundaries, reduces sensitivity to noise, and improves generalization by averaging more neighbors.
- **Why may too large values of K be detrimental?**
  If K is too large, the algorithm may overgeneralize, losing fine-grained details and potentially including irrelevant or distant points, leading to poor classification.
- **What happens if K=1?**
  The model memorizes the training data and is highly sensitive to noise, leading to overfitting.
- **What happens if K=N?**
  The model assigns all test samples to the most common class in the training set, ignoring all local structure.
- **When are larger K values beneficial?**
  Larger K values are helpful when the dataset has noise or outliers, as they help smooth out/reduce their influence.
- **Why are too large K values detrimental?**
  Excessively large K values can cause loss of important local details, leading to poor decision boundaries.

### K-NN Variants and Use Cases

- **What is K-NN Regressor?**
  K-NN regression predicts a continuous value by averaging (or weighted averaging) the K nearest neighbors' values instead of class labels.
- **K-NN shows decent performance on the MNIST dataset (digit classification), above 90% accuracy. Why?**
  1. MNIST has well-separated classes, making distance-based methods effective.
  2. Digit images have low-dimensional, structured patterns.
  3. Sufficient training samples allow good nearest-neighbor matches.
- **Are K-NN algorithms good candidates to build a 1,000-class image classification system? Explain.**
  No, because K-NN scales poorly with large datasets due to its high time and space complexity. Searching for nearest neighbors among thousands of classes is computationally expensive.

### The Curse of Dimensionality

- **What is the curse of dimensionality?**
  As the number of features (d) increases, distances between points become less meaningful, making nearest-neighbor methods less effective.
- **Why does the curse of dimensionality happen?**
  High-dimensional spaces cause data points to spread out, reducing the contrast between the closest and farthest points, making distance-based methods unreliable.
- **Is K-NN impacted by the curse of dimensionality? Explain.**
  Yes, K-NN suffers because distances become less discriminative in high dimensions, leading to poor classification performance. Dimensionality reduction techniques (e.g., PCA) can help mitigate this issue.

### Classification mode

------

**When used in classification mode, what can we do when the first categories have an equal number of votes with K-NN?**

- Use weighted voting (giving more weight to closer points).
- Reduce K or choose the most frequent class in the dataset as a tie-breaker.

## Mindmap

![knn-mindmap]({{site.url_complet}}/assets/article/mlg/knn-mindmap.png)

Made with ChatGPT with the following input:  "Create a mindmap with plantuml (mindmap) to summarize all these points and KNN" and [PlantUML](https://www.plantuml.com/plantuml/)

## References

- ChatGPT with the input "Write an article about K Nearest Neighbor (KNN)" 
- [IBM - KNN](https://www.ibm.com/think/topics/knn)
- [IBM video - What is the K-Nearest Neighbor (KNN) Algorithm?](https://www.youtube.com/watch?v=b6uHw7QW_n4)
