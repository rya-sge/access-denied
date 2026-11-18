---
layout: post
title: "Recurrent Neural Networks (RNNs) - Overview"
date:   2025-11-14
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: ai
tags: neural-network-architecture transformer cnn rnn
description: "Overview of Recurrent Neural Networks (RNNs): mathematical foundations, activation and loss functions, and a comparison with perceptrons, CNNs and Transformers."
image: /assets/article/mlg/RNN-variant.drawio.png
isMath: true
---

Artificial neural networks (ANNs) have evolved into a diverse family of architectures designed to process various types of data and tasks. Among these, **Recurrent Neural Networks (RNNs)** are known for their ability to model **sequential and temporal dependencies**, making them fundamental in natural language processing (NLP), speech recognition, and time-series prediction.

This article provides a technical overview of RNNs, explains their internal mechanisms, and compares them with other major architectures—**Perceptrons**, **Convolutional Neural Networks (CNNs)**, and **Transformers**.

[TOC]

## What you need to know first

The article assumes the reader knows what a neural network and its training data are, and uses a few mechanisms one level below without explaining them.

- **Feedforward layer**: a layer computes $$f(Wx + b)$$, a weight matrix $$W$$ applied to the input vector $$x$$, plus a bias $$b$$, followed by a non-linear activation $$f$$. The RNN hidden-state update is this computation with a second input, the previous hidden state; see [Perceptron - a simple, binary neural network architecture]({{site.url_complet}}/2024/11/25/perceptron-introduction/).
- **Training by gradient descent**: a network learns by computing the gradient of a loss function with respect to each weight, through backpropagation, and moving the weights a small step against it. The article's loss and gradient discussions all refer to this loop; see [Gradient Descent in Machine Learning - Overview]({{site.url_complet}}/2025/04/09/gradient-descent-overview/).
- **Backpropagation through time**: an RNN is trained by unrolling it over the $$T$$ steps of a sequence and backpropagating through the unrolled copies, which share the same weights. The gradient that reaches an early step is a product of one factor per step, so it tends to shrink towards zero or grow without bound as the sequence gets longer, which is the vanishing and exploding gradient problem the article refers to.
- **tanh and sigmoid**: two classic activation functions, which map any real number into $$(-1, 1)$$ and $$(0, 1)$$ respectively. Both flatten out for large inputs, so their derivative becomes small there, which feeds the vanishing gradient problem and is why the article mentions ReLU as an alternative.
- **One-hot encoding**: a class label among $$K$$ is represented as a vector of length $$K$$ with a 1 at the position of the correct class and 0 elsewhere. The cross-entropy formula uses this vector as the true label $$y_i$$, so only the term for the correct class remains.

## What is an RNN?

An RNN is a neural network designed to recognize patterns in sequences of data, such as text, time series, speech, or video. Unlike traditional feedforward neural networks, RNNs have loops within their architecture. These loops allow information to persist, meaning the network has a "memory" of previous inputs, making it well-suited to sequential tasks.

At each time step, the RNN takes an input and combines it with the "hidden state" (the memory from previous steps) to produce an output and an updated hidden state. This recurrent mechanism enables the network to model temporal dynamics.

### Key characteristics of RNNs and limitation:

- **Sequential Processing**: Data is processed step-by-step, respecting order.
- **Parameter Sharing**: The same weights are reused at every time step.
- **Memory**: Past information can influence future outputs.

However, standard RNNs face challenges like vanishing and exploding gradients, which make it difficult for them to capture long-term dependencies. 

Variants like Long Short-Term Memory (LSTM) and Gated Recurrent Units (GRU) were developed to address these issues.

#### Schema

![RNN-limit.drawio]({{site.url_complet}}/assets/article/mlg/RNN-limit.drawio.png)

### Mathematical Formulation

**Hidden state update**

Given a sequence of inputs x1,x2,…,xT, an RNN computes:

$$
\begin{aligned}
h_t=f(W_{xh}x_t+W_{hh}h_{t−1}+bh)
\end{aligned}
$$

Where:

- `ht` is the hidden state at time t,
- `W_xh`,`W_hh`,`W_hy` are weight matrices,
- `f` is an activation function (typically tanh or ReLU).

**Output computation:**
$$
\begin{aligned}
y_t =g(W_{hy}ht+by)
\end{aligned}
$$

Where:

- y_t: raw output (logits) at time t

$$
y_t \in \mathbb{R}^{d_y}
$$



- W_hy: hidden-to-output weights.

$$
W_{hy} \in \mathbb{R}^{d_y \times d_h}
$$



- `by`: output bias.
- `g`: If used for classification, `yt` is typically passed to a **Softmax** function.

Note: **d** represents the **dimension (size) of a vector space**. It tells you **how many components** the vector has.

### Activation Functions and Loss in RNNs

#### ReLU (Rectified Linear Unit)

Introduces non-linearity in the network, allowing it to learn complex patterns. ReLU outputs zero for negative inputs and passes positive inputs unchanged.

- **Usage in RNNs:** Often applied in the **hidden layers** or hidden state transformations to help mitigate the vanishing gradient problem and speed up training. While traditional RNNs use tanh or sigmoid, ReLU is sometimes preferred in modern variants for efficiency.

#### Softmax

Converts the raw output of the network into a **probability distribution** over multiple classes. Each value is between 0 and 1, and the sum across all classes equals 1.

This is used at the **output layer** of RNNs that perform **classification or sequence prediction** (e.g., predicting the next word).
$$
\hat{y}_{t,i} = \text{Softmax}(y_t)_i 
= \frac{e^{y_{t,i}}}{\sum_{j=1}^{K} e^{y_{t,j}}}
$$
Where:

- y_{t,i]} the logit (raw score) for class i.
- y^_t,i predicted probability for class i.
- The denominator ensures all probabilities sum to 1.


- **Usage in RNNs:** Typically applied at the **output layer** when predicting categorical sequences, such as words in language modeling or discrete classes in classification tasks.

#### Cross-Entropy Loss

Measures the difference between the predicted probability distribution (from Softmax) and the true labels. It penalizes incorrect predictions more heavily the more confident the network is in them.
$$
\begin{aligned}
\mathcal{L} = - \sum_{i=1}^{K} y_i \log(\hat{y}_i)
\end{aligned}
$$
Where:

- `yi`is the true one-hot label,
- `y^i` is the predicted probability from Softmax.

- **Usage in RNNs:** Used as the **loss function** during training, guiding the network to adjust weights so that the predicted probabilities align with the actual sequence labels. This is essential for tasks like language modeling, sequence classification, and speech recognition.



## Types of RNNs

To address these limitations, specialized architectures were developed:

- **Long Short-Term Memory (LSTM)**: Introduces gates (input, forget, output) to control information flow.
- **Gated Recurrent Unit (GRU)**: Simplifies LSTM structure while retaining similar performance.

- Bidirectional recurrent neural networks (BRNNs)
- Encoder-decoder RNN

| **Type**                          | **Description**                                              | **Strengths**                                                | **Weaknesses**                                               |
| --------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Standard RNN**                  | Basic RNN architecture with feedback loops for memory over sequences. | Simple, lightweight, easy to implement.                      | Struggles with long-term dependencies (vanishing/exploding gradients).<br /> |
| **Bidirectional RNN (BRNN)**      | RNN that processes the sequence in both forward and backward directions and combines the information. | Can access both past and future context, improving accuracy in many tasks. | Doubles the computational load; not suitable for real-time applications. |
| **Long Short-Term Memory (LSTM)** | RNN variant with special gates (input, forget, output) to manage memory and handle long-term dependencies. | Excellent at learning long-term relationships; widely used in NLP and time series. | More complex and computationally expensive than standard RNNs. |
| **Gated Recurrent Unit (GRU)**    | A simplified version of LSTM with fewer gates (update and reset gates). | Faster to train, fewer parameters; good balance between performance and complexity. | May be slightly less expressive than LSTM for very complex patterns. |
| **Encoder-Decoder RNN**           | A two-part architecture: encoder summarizes input into a fixed vector; decoder generates output from that vector (common in seq2seq tasks). | Great for variable-length input/output tasks like translation, summarization. | Performance drops for very long sequences without attention mechanisms.<br />The fixed-length context vector can be a bottleneck, especially for long input sequences. |

### Schema

![RNN-variant.drawio]({{site.url_complet}}/assets/article/mlg/RNN-variant.drawio.png)



------

## Comparison with Other Neural Architectures

### Summary tab

| **Aspect**               | **Perceptron**             | **CNN**                            | **RNN**                        | **Transformer**                          |
| ------------------------ | -------------------------- | ---------------------------------- | ------------------------------ | ---------------------------------------- |
| **Data Type**            | Static, non-sequential     | Spatial data (images/video)        | Sequential (text, time series) | Sequential (text, audio)                 |
| **Architecture**         | Single-layer linear model  | Hierarchical convolutional filters | Recurrent hidden state         | Attention-based encoder-decoder          |
| **Memory / Context**     | None                       | Local (spatial)                    | Temporal (via hidden state)    | Global (via self-attention)              |
| **Parallelization**      | High                       | High                               | Low (sequential dependency)    | Very high                                |
| **Gradient Issues**      | N/A                        | Mild                               | Vanishing/exploding gradients  | Minimal                                  |
| **Interpretability**     | High                       | Moderate                           | Moderate                       | Moderate to Low                          |
| **Typical Applications** | Classification, regression | Vision, feature extraction         | NLP, speech, time-series       | NLP, multimodal tasks, generative models |



### RNN vs. Perceptron

- **Perceptron**: The simplest form of a neural network, consisting of a single layer of weights followed by an activation function. It processes one input at a time and has no concept of sequence or memory.
- **RNN**: Extends the perceptron by introducing the notion of time and sequence. It has feedback connections (recurrent loops) that allow it to maintain a state across inputs.

**Summary**: A Perceptron handles static data points independently; an RNN handles sequences with context from past data.

------

### RNN vs. CNN

- **CNN**: Primarily designed for spatial data like images. It uses convolutional layers to detect local patterns (e.g., edges in an image) and pooling layers to downsample feature maps.
- **RNN**: Primarily designed for temporal data, where the sequence and timing of inputs are critical.

While CNNs are highly effective for visual tasks, they are less natural fits for time-series or language modeling where RNNs shine. However, CNNs have been adapted for sequential data too, for example Temporal Convolutional Networks (TCNs), offering competitive or even superior performance in some cases because of their ability to capture dependencies without the vanishing gradient problem.

**Summary**: CNNs excel in spatial pattern recognition; RNNs excel in temporal pattern recognition.

More information in my article on CNN: [Convolutional Neural Networks - Overview](https://rya-sge.github.io/access-denied/2024/11/19/convolutional-neural-networks-overview/)

------

### RNN vs. Transformer

- **Transformer**: A more recent architecture that has largely supplanted RNNs in fields like NLP. Transformers rely entirely on **attention mechanisms** instead of recurrence to model dependencies, allowing for greater parallelization and the ability to capture long-range relationships effectively.
- **RNN**: Processes **sequences** step-by-step, making it inherently sequential and harder to parallelize.

Transformers, through mechanisms like self-attention, can look at all parts of the sequence at once, leading to faster training and better modeling of long-range dependencies. This is why models like GPT, BERT, and T5 are built on Transformer architectures rather than RNNs.

Transformers can capture long-range dependencies much more effectively, are easier to parallelize and perform better on tasks such as NLP, speech recognition and time-series [forecasting](https://www.ibm.com/think/topics/forecasting).

#### Summary

Transformers outperform RNNs on long sequences, offering more efficient training and better results, especially in large-scale tasks.

- **Computation**: Transformers allow **parallel processing** of sequences, while RNNs process them sequentially.
- **Long-Term Dependencies**: Transformers capture these efficiently through attention weights, whereas RNNs struggle with long-range dependencies.
- **Scalability**: Transformers scale better with data and compute resources.
- **Performance**: Transformers now dominate NLP and sequence modeling tasks (e.g., GPT, BERT), effectively replacing RNNs in most applications.

See also my article on the [Transformer](https://rya-sge.github.io/access-denied/2025/01/13/transformers) architecture

## Conclusion

Recurrent Neural Networks revolutionized sequential data modeling by introducing the concept of **temporal memory**. 

However, they are gradually being supplanted by **attention-based architectures** that offer better scalability and parallelization.

However, RNNs still hold practical value when:

- Data is relatively short or streaming in nature.
- Computational resources are limited.
- Low latency and smaller model size are priorities.

They remain effective in certain real-time systems and embedded applications, such as **sensor analysis**, **gesture recognition**, and **low-power NLP inference**.

![rnn-mindmap]({{site.url_complet}}/assets/article/mlg/rnn-mindmap.png)



## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Recurrent Neural Network (RNN)** | A neural network with loops in its architecture that processes a sequence step by step and carries information from previous inputs to the next step. |
| **Time step** | One position $$t$$ in the input sequence, at which the RNN reads $$x_t$$ and updates its hidden state. |
| **Hidden state** | The vector $$h_t$$ that acts as the network's memory, computed from the current input and the previous hidden state. |
| **Parameter sharing** | The reuse of the same weight matrices $$W_{xh}$$, $$W_{hh}$$ and $$W_{hy}$$ at every time step. |
| **Activation function** | The non-linear function applied after the weighted sum, such as tanh, sigmoid or ReLU, which lets the network learn complex patterns. |
| **ReLU** | The Rectified Linear Unit, which outputs zero for negative inputs and passes positive inputs unchanged. |
| **Logits** | The raw output scores $$y_t$$ produced by the output layer before they are turned into probabilities. |
| **Softmax** | The function that turns a vector of logits into a probability distribution, each value between 0 and 1 and summing to 1. |
| **Cross-entropy loss** | The loss that compares the predicted probabilities with the true one-hot labels and penalises confident wrong predictions more heavily. |
| **Vanishing and exploding gradients** | The tendency of gradients to shrink or grow too much during training of a standard RNN, which makes long-term dependencies hard to learn. |
| **Long Short-Term Memory (LSTM)** | An RNN variant with input, forget and output gates that control the flow of information and handle long-term dependencies. |
| **Gated Recurrent Unit (GRU)** | A simplified version of LSTM with only update and reset gates, with fewer parameters and faster training. |
| **Bidirectional RNN (BRNN)** | An RNN that processes the sequence forwards and backwards and combines both directions, at about twice the computational cost. |
| **Encoder-decoder RNN** | A two-part architecture in which an encoder summarises the input into a fixed vector and a decoder generates the output from it, as in translation. |
| **Self-attention** | The mechanism used by Transformers instead of recurrence, which looks at all positions of a sequence at once and allows parallel training. |

## Reference

- [Stanford - Recurrent Neural Networks cheatsheet](https://stanford.edu/~shervine/teaching/cs-230/cheatsheet-recurrent-neural-networks)
- [AWS - What is RNN (Recurrent Neural Network)?](https://aws.amazon.com/what-is/recurrent-neural-network/)
- ChatGPT with the input "Write me an article about RNN, include a comparison with CNN, Perceptron and transformer.", "Add a paragraph to explain the role of  relu softmax cross-entropy in RNN"