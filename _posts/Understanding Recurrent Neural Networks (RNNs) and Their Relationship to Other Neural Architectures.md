---
layout: post
title: "Recurrent Neural Networks (RNNs) - Overview"
date:   2025-11-13
lang: en
locale: en-GB
categories: ai
tags: mlg RNN ANN CNN perceptron transformer
description: USD₮0 is an Omnichain Fungible Token (OFT) built on LayerZero, enabling cross-chain transfers of USDT. Learn how USD₮0 works, its architecture, and the Legacy Mesh that connects existing USDT networks.
image: 
isMath: false
---

Artificial neural networks (ANNs) have evolved into a diverse family of architectures designed to process various types of data and tasks. Among these, **Recurrent Neural Networks (RNNs)** are known for their ability to model **sequential and temporal dependencies**, making them fundamental in natural language processing (NLP), speech recognition, and time-series prediction.

This article provides a technical overview of RNNs, explains their internal mechanisms, and compares them with other major architectures—**Perceptrons**, **Convolutional Neural Networks (CNNs)**, and **Transformers**.

[TOC]



------

## The Structure and Function of RNNs

### Concept

Unlike feedforward networks that assume inputs are independent, **RNNs** introduce **recurrence**, meaning the output of a previous time step influences the next. This feedback loop enables the network to maintain a **hidden state**—a form of memory that captures information over time.

### Mathematical Formulation

Given a sequence of inputs x1,x2,…,xT, an RNN computes:

ht=f(Wxhxt+Whhht−1+bh)

Where:

- ht is the hidden state at time t,
- Wxh,Whh,WhyW_{xh}, W_{hh}, W_{hy}Wxh,Whh,Why are weight matrices,
- `f` and `g` are activation functions (typically tanh or ReLU).

### Activation Functions and Loss in RNNs

#### ReLU (Rectified Linear Unit)

Introduces non-linearity in the network, allowing it to learn complex patterns. ReLU outputs zero for negative inputs and passes positive inputs unchanged.

- **Usage in RNNs:** Often applied in the **hidden layers** or hidden state transformations to help mitigate the vanishing gradient problem and speed up training. While traditional RNNs use tanh or sigmoid, ReLU is sometimes preferred in modern variants for efficiency.

#### Softmax

Converts the raw output of the network into a **probability distribution** over multiple classes. Each value is between 0 and 1, and the sum across all classes equals 1.

- **Usage in RNNs:** Typically applied at the **output layer** when predicting categorical sequences, such as words in language modeling or discrete classes in classification tasks.

#### Cross-Entropy Loss

Measures the difference between the predicted probability distribution (from Softmax) and the true labels. It penalizes incorrect predictions more heavily the more confident the network is in them.

- **Usage in RNNs:** Used as the **loss function** during training, guiding the network to adjust weights so that the predicted probabilities align with the actual sequence labels. This is essential for tasks like language modeling, sequence classification, and speech recognition.

------

### Training and Limitations

RNNs are trained via **Backpropagation Through Time (BPTT)**, which unfolds the network over several time steps. However, this method suffers from **vanishing and exploding gradients**, making it difficult to learn long-term dependencies.

### Variants of RNNs

To address these limitations, specialized architectures were developed:

- **Long Short-Term Memory (LSTM)**: Introduces gates (input, forget, output) to control information flow.
- **Gated Recurrent Unit (GRU)**: Simplifies LSTM structure while retaining similar performance.

------

## Comparison with Other Neural Architectures

### Summary tab

| **Aspect**               | **Perceptron**             | **CNN**                            | **RNN**                        | **Transformer**                          |
| ------------------------ | -------------------------- | ---------------------------------- | ------------------------------ | ---------------------------------------- |
| **Data Type**            | Static, non-sequential     | Spatial (images)                   | Sequential (text, time series) | Sequential (text, audio)                 |
| **Architecture**         | Single-layer linear model  | Hierarchical convolutional filters | Recurrent hidden state         | Attention-based encoder-decoder          |
| **Memory / Context**     | None                       | Local (spatial)                    | Temporal (via hidden state)    | Global (via self-attention)              |
| **Parallelization**      | High                       | High                               | Low (sequential dependency)    | Very high                                |
| **Gradient Issues**      | N/A                        | Mild                               | Vanishing/exploding gradients  | Minimal                                  |
| **Interpretability**     | High                       | Moderate                           | Moderate                       | Moderate to Low                          |
| **Typical Applications** | Classification, regression | Vision, feature extraction         | NLP, speech, time-series       | NLP, multimodal tasks, generative models |

------

### RNN vs. Perceptron

The **Perceptron**, the simplest form of a neural network, maps inputs directly to outputs using a linear decision boundary. It has **no hidden state**, so it cannot handle temporal or contextual information.
 In contrast, **RNNs** introduce **recurrence**—they can learn patterns over time, making them suitable for sequential data. 

Conceptually, RNNs can be viewed as multiple perceptrons connected in a time-dependent chain.

------

#### RNN vs. CNN

While **CNNs** are optimized for **spatial locality**, such as pixel neighborhoods in images, RNNs are designed for **temporal locality**, where the order of inputs matters.
 CNNs can process entire inputs in parallel through convolution and pooling, while RNNs must process input sequences step by step.
 Interestingly, **1D CNNs** are sometimes used as efficient alternatives to RNNs for sequence modeling, as they can capture local dependencies without recurrence.

------

### RNN vs. Transformer

The **Transformer** architecture, introduced by Vaswani et al. (2017), represents a paradigm shift. Instead of recurrence, Transformers rely on **self-attention mechanisms** to model relationships between all elements in a sequence simultaneously.

#### Key Differences:

- **Computation**: Transformers allow **parallel processing** of sequences, while RNNs process them sequentially.
- **Long-Term Dependencies**: Transformers capture these efficiently through attention weights, whereas RNNs struggle with long-range dependencies.
- **Scalability**: Transformers scale better with data and compute resources.
- **Performance**: Transformers now dominate NLP and sequence modeling tasks (e.g., GPT, BERT), effectively replacing RNNs in most applications.

------

## When to Use RNNs Today

Despite the rise of Transformers, RNNs still hold practical value when:

- Data is relatively short or streaming in nature.
- Computational resources are limited.
- Low latency and smaller model size are priorities.

They remain effective in certain real-time systems and embedded applications, such as **sensor analysis**, **gesture recognition**, and **low-power NLP inference**.

------

## Conclusion

Recurrent Neural Networks revolutionized sequential data modeling by introducing the concept of **temporal memory**. 

However, they are gradually being supplanted by **attention-based architectures** that offer better scalability and parallelization.

------

## Reference

https://stanford.edu/~shervine/teaching/cs-230/cheatsheet-recurrent-neural-networks