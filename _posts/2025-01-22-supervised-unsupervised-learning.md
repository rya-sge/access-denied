---
layout: post
title: Machine Learning - Supervised vs. Unsupervised Learning
date: 2025-01-22
lang: en
locale: en-GB
categories: ai
tags: supervised unsupervised learning machine-learning
description: This article explains the difference between supervised and unsupervised learning in Machine Learning with several examples.
image: /assets/article/mlg/supervised-unsupervised-learning.png
isMath: true
---

Machine learning models are transforming how we analyze data, make predictions, and uncover patterns. 

At the heart of machine learning lie two fundamental approaches: supervised and unsupervised learning. 

Understanding their differences is crucial for selecting the right model for your data. 

Let’s dive into what distinguishes these techniques and explore their applications.

> This article comes mainly from this video by IBM: [Supervised VS. Unsupervise Learning](https://www.youtube.com/watch?v=W01tIRP_Rqs). Then:
>
> - A transcript has been generated with [NoteGPT](https://notegpt.io/)
> - A more formal article has been made with ChatGPT from this transcript
> - Finally, I have perform a few addition and personal notes.

[TOC]

## What is Supervised Learning?

Supervised learning involves training a machine learning algorithm on a **labeled dataset** called the training set, where each data point has an associated output. The algorithm learns from these labeled inputs to generalize patterns and make predictions about new, unseen data.

For example, consider a dataset of emails labeled as “spam” or “not spam.” A supervised learning model, after training, can classify future emails into these categories with high accuracy.

Supervised learning can be categorized into two main tasks:

### Classification

> Predicting discrete labels, such as categorizing emails or identifying whether a tumor is malignant or benign. Common algorithms include decision trees, random forests, and support vector machines (SVMs).

It is similar to regression except output values are labels or categories

Example :

Predictor values: age, gender, income, profession

Output value: buyer, non-buyer

### Regression

> Predicting continuous values, like forecasting house prices or stock trends. Popular methods include linear and logistic regression.

Training data, each example: 

- Set of predictor values - “independent variables” 
- Numeric output value - “dependent variable” 

Model is function from predictors to output

- Use model to predict output value for new predictor values 

Example:

Predictors: mother height, father height, current age 

Output: height

----

## What is Unsupervised Learning?

Unsupervised learning operates without labeled data. Instead, it identifies patterns, structures, or relationships within the dataset. The algorithm works autonomously to group or reduce data dimensions, offering insights without explicit human guidance.

Key tasks in unsupervised learning include:

1. **Clustering**: Grouping data points based on similarities. A common example is customer segmentation, where users are grouped by behaviors or demographics.
2. **Association**: Identifying relationships between variables, such as which items are often purchased together in a store.
3. **Dimensionality Reduction**: Simplifying datasets while retaining essential information, often used in preprocessing, like cleaning image data or reducing noise.

-----

## Core Differences Between Supervised and Unsupervised Learning

| Feature                | Supervised Learning                   | Unsupervised Learning                         |
| ---------------------- | ------------------------------------- | --------------------------------------------- |
| **Data Requirements**  | Requires labeled data                 | Works with unlabeled data                     |
| **Objective**          | Predict outcomes based on input data  | Discover hidden structures or patterns        |
| **Examples**           | Spam detection, price prediction      | Customer segmentation, market basket analysis |
| **Human Intervention** | Needs labeled training data upfront   | No labeling required                          |
| **Accuracy**           | Typically more accurate and efficient | May lack transparency in results              |

### Which Should You Use?

The choice between supervised and unsupervised learning depends on the type of data you have and your objectives:

- **Use Supervised Learning**: If you need precise predictions and have access to labeled datasets. For instance, predicting commute times based on weather conditions or diagnosing diseases using medical scans.
- **Use Unsupervised Learning**: When your dataset is unlabeled or you want to discover underlying patterns. It’s ideal for tasks like clustering similar customer behaviors or detecting anomalies in network traffic.

### Mindmap

Made with ChatGPT and [PlantUML](https://www.plantuml.com/plantuml/)

![supervised-unsupervided-learning]({{site.url_complet}}/assets/article/mlg/supervised-unsupervided-learning.png)



### The Middle Ground: Semi-Supervised Learning

Sometimes, you might have datasets where only a portion is labeled. This is where **semi-supervised learning** shines. It combines aspects of both supervised and unsupervised learning, making it particularly effective for domains like medical imaging. For instance, a small subset of labeled scans can guide the model to label the remaining images more accurately.

-----

## Final Thoughts

Supervised and unsupervised learning are not mutually exclusive; they address different problems. 

- Supervised learning is ideal for making predictions and ensuring accuracy
- Unsupervised learning excels at uncovering insights from unlabeled data. 
- Semi-supervised learning bridges the gap, leveraging the strengths of both approaches.

Choosing the right method requires understanding your dataset and the insights you wish to extract. 

As technology evolves, other possibilities exist too, from reinforcement learning to hybrid models. 

----

## FAQ

### Supervised VS Unsupervied learning

> Of the following examples, which one would you address using a supervised or an
> unsupervised learning algorithm ? Give some explanations for your answers.

**a) Given email labeled as spam/not spam, learn a spam filter.**

**Algorithm:** Supervised learning.
**Explanation:** The dataset includes labeled examples (spam or not spam), which makes this a supervised learning task. The algorithm learns a classification model based on these labels to predict the category of new emails.

------

**b) Given a set of news articles found on the web, group them into sets of related articles.**

**Algorithm:** Unsupervised learning.
**Explanation:** The task involves grouping the articles into clusters based on similarity without any predefined labels or categories. This is a typical use case for clustering algorithms like k-means or hierarchical clustering.

------

**c) Given a database of customer data, automatically discover market segments and group customers into different market segments.**

**Algorithm:** Unsupervised learning.
**Explanation:** Market segmentation aims to group customers based on shared characteristics without prior knowledge of the groups. Clustering algorithms are commonly used for this purpose.

------

**d) Given a dataset of patients diagnosed as either having glaucoma or not, learn to classify new patients as having glaucoma or not.**

**Algorithm:** Supervised learning.
**Explanation:** The dataset includes labeled examples (patients diagnosed as having glaucoma or not), making this a supervised classification problem. The algorithm learns to classify new patients based on these labels.

### General question

> Can we transform a regression problem into a classification problem? What would be the benefits of doing so?

Yes, we can transform a regression problem into a classification problem. This is often done by discretizing the continuous output variable into predefined bins or categories. For example, instead of predicting the exact age of a person (regression), we could classify them into age groups like 0–10, 11–20, etc. (classification).

**Benefits:**

- **Simplified outputs:** The transformation can make the problem easier to interpret and solve, especially when precise numerical predictions are not necessary.
- **Robustness to noise:** Classification models are often less sensitive to small variations in data than regression models.
- **Direct applicability:** Some tasks, such as decision-making based on ranges or categories, naturally align better with classification than regression.

------

> Why is it important that a test set is independent of the training set in a machine learning system?

An independent test set is critical to ensure that the model's performance evaluation reflects its ability to generalize to unseen data. If the test set is not independent of the training set:

- The model may overfit to the shared patterns between the training and test sets, resulting in overly optimistic performance metrics.
- The evaluation will fail to accurately measure the model's real-world applicability, undermining trust in its deployment.

------

> What is the meaning of the hat in the equation y^=h(x)?

$$
\hat{y} = h(x)\
$$

The hat symbol (`^`) represents an estimated or predicted value. 

- `h(x)` is the hypothesis or the model function that makes a prediction based on input `x`.
- `y^` is the predicted output, as opposed to `y`, which is the actual or true value.

------

> What is the difference between machine learning and statistics?

**Machine Learning:**

- Focuses on building predictive models that can generalize to unseen data.
- Often deals with large, high-dimensional datasets.
- Emphasizes automation, scalability, and iterative learning from data.

**Statistics:**

- Focuses on understanding relationships and testing hypotheses using data.
- Typically deals with smaller datasets with strong assumptions about distributions.
- Prioritizes interpretability and inference.

While there is overlap, machine learning is more application-driven, and statistics is more theory-driven.

------

> Is a detection system a regression or classification system? Give an example.

A detection system is typically a **classification system**. Its goal is to classify whether a particular object or event is present or absent in the input data.

**Example:** A face detection system classifies regions of an image as either containing a face (positive class) or not containing a face (negative class).

## Reference

- ChatGPT with the input 
  - "Write me an article to compare supervise and unsupervided learning. Use this transcript to help you"
  - For the FAQ: "Give answer for each question"
- IBM video: [Supervised VS. Unsupervise Learning](https://www.youtube.com/watch?v=W01tIRP_Rqs)
- Specific topic
  - [Stanford - Machine Learning - Regression](https://web.stanford.edu/class/cs102/lectureslides/RegressionSlides.pdf)