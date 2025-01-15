---
layout: post
title: Transformers - Attention is All You Need
date:   2025-01-13
lang: en
locale: en-GB
categories: ai
tags: neural-network-architecture transformer cnn rnn
description: Introduced in 2017 in the paper Attention is All You Need, transformers address the limitations of earlier architectures by leveraging a self-attention mechanism to process sequential and structured data more effectively. 
image: /assets/article/mlg/transformer-architecture-whitepaper.png
isMath: true
---

Transformers are a foundational neural network architecture widely used in modern machine learning, particularly for tasks in natural language processing (NLP), computer vision, and time-series analysis. 

Introduced in 2017 by Vaswani et al. in the seminal paper *"[Attention is All You Need](https://arxiv.org/abs/1706.03762) ([pdf](https://arxiv.org/pdf/1706.03762)),"* transformers address the limitations of earlier architectures by leveraging a self-attention mechanism to process sequential and structured data more effectively. 

This article provides an in-depth exploration of transformer architecture, its operational principles, and a comparison to traditional models like perceptrons, recurrent neural networks (RNNs), and convolutional neural networks (CNNs).

Transformers are at the foundation of Bert and Chat GPT models

[TOC]



------

## What Is a Transformer?

A transformer is a neural network architecture designed to handle sequential data using a mechanism called **self-attention**. Unlike traditional architectures that process data sequentially or with fixed windows, transformers capture relationships across all elements in the sequence simultaneously, enabling them to model long-range dependencies effectively.

The key components of a transformer include:

1. **Multi-Head Self-Attention**: Allows the model to focus on different parts of the input sequence simultaneously.
2. **Positional Encoding**: Introduces order information to the input, which the attention mechanism alone does not preserve.
3. **Feed-Forward Networks (FFN)**: Fully connected layers applied to each position independently.
4. **Encoder-Decoder Structure** (for sequence-to-sequence tasks): The encoder processes the input sequence, and the decoder generates the output sequence.

   According to this [article](https://heidloff.net/article/foundation-models-transformers-bert-and-gpt/), BERT only uses `encoder`while GPT uses `decoder`

Transformers process input data in parallel, rather than sequentially, making them highly efficient and scalable for large datasets.

From [Attention is All You Need](https://arxiv.org/abs/1706.03762)

![transformer-architecture-whitepaper]({{site.url_complet}}/assets/article/mlg/transformer-architecture-whitepaper.png)

## How It Works: Step-by-Step

### Input Processing

The input sequence (e.g., a sentence) is tokenized and embedded into dense vectors. Positional encodings are added to these embeddings.

Since a transformer model contains no recurrence and no convolution, in order for the model to make use of the order of the sequence, we must inject some information about the relative or absolute position of the tokens in the sequence. 

To this end, the transformer architecture adds "positional encodings" to the input embeddings at the bottoms of the encoder and decoder stacks. The positional encodings have the same dimension model as the embeddings, so that the two can be summed.

### Attention mechanism

- Self-attention calculates a relevance score for each token with respect to all other tokens.
- Key, Query, and Value matrices are derived from the embeddings:
  - **Query**: Represents the current token being processed.
  - **Key**: Represents other tokens in the sequence.
  - **Value**: Contains the information to be aggregated.

####  Scaled Dot-Product Attention

With this method, the relevance score is computed as: 


$$
\begin{aligned}
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
\end{aligned}
$$


The input consists of queries and keys of dimension `dk` and Values of dimension `dv`. 

We compute the dot products of the query with all keys, divide each by the root of `dk`, and apply a softmax function to obtain the weights on the values. 

In practice, we compute the attention function on a set of queries simultaneously, packed together into a matrix Q. 

The keys and values are also packed together into matrices K and V . 

####  Other type of attention functions

The two most commonly used attention functions are additive attention, and dot-product (multiplicative) attention. 

- Dot-product attention is almost identical to the algorithm **Scaled Dot-Product Attention**, except for the scaling factor of  1/√dk . 

- Additive attention computes the compatibility function using a feed-forward network with a single hidden layer. While the two are similar in theoretical complexity, dot-product attention is much faster and more space-effic

### Parallel Attention

- Multiple attention heads capture various relationships in the sequence.
- Outputs from all heads are concatenated and passed through a linear layer.

### Feed-Forward Processing

Each position undergoes a fully connected layer for further feature extraction.

In addition to attention sub-layers, each of the layers in the encoders and decoders contains a fully connected feed-forward network, which is applied to each position separately and identically. This consists of two linear transformations with a ReLU activation in between. 


$$
\begin{aligned}
FFN(x) = max(0, xW_1 + b_1)W_2 + b_2
\end{aligned}
$$


While the linear transformations are the same across different positions, they use different parameters from layer to layer

### Encoder-Decoder Interaction

The decoder takes the encoder's output and applies cross-attention to integrate it with its own self-attention mechanism.

According to the paper: 

- he queries come from the previous decoder layer, and the memory keys and values come from the output of the encoder. This allows every position in the decoder to attend over all positions in the input sequence. This mimics the typical encoder-decoder attention mechanisms in sequence-to-sequence models
- The encoder contains self-attention layers. In a self-attention layer all of the keys, values and queries come from the same place, in this case, the output of the previous layer in the encoder. Each position in the encoder can attend to all positions in the previous layer of the encoder. 
- Similarly, self-attention layers in the decoder allow each position in the decoder to attend to all positions in the decoder up to and including that position. 

### Output Generation

The decoder generates the target sequence step by step, using previously generated tokens as input during training.

------

## Comparing Transformers to Other Architectures

### Perceptrons

Perceptrons are the simplest type of neural network, consisting of a single layer of neurons. They are primarily used for linear classification tasks.

- **Strengths**: Simple and interpretable.
- **Limitations**: Cannot model non-linear relationships without extending to multi-layer perceptrons (MLPs).

**Comparison with Transformers**:

- Perceptrons are static, whereas transformers dynamically adjust their focus across input data using self-attention.
- Transformers excel in modeling complex, non-linear relationships, while perceptrons are limited to basic tasks.

------

### Recurrent Neural Networks (RNNs)

RNNs are designed to process sequential data, such as time series and text, by maintaining a hidden state that captures past information.

- **Strengths**: Good for sequential tasks and short dependencies.
- **Limitations**: Struggle with long-term dependencies due to vanishing/exploding gradient problems, and they process data sequentially, leading to inefficiency.

**Comparison with Transformers**:

- **Parallelization**: Transformers process all sequence elements simultaneously based on self-attention mechanism, while RNNs must process them sequentially.
- **Long-Range Dependencies**: Transformers handle long-term relationships better using self-attention, whereas RNNs struggle as sequence length increases.
- **Efficiency**: Transformers are more computationally efficient for large datasets due to parallel processing.

------

### Convolutional Neural Networks (CNNs)

CNNs are specialized for image and spatial data, using convolutional layers to extract features like edges and textures.

- **Strengths**: Excellent for grid-like data (e.g., images) and local feature extraction.
- **Limitations**: Limited ability to capture global context in sequential or structured data.

**Comparison with Transformers**:

- CNNs focus on local patterns, while transformers use self-attention to capture global context.
- Recent advances, such as vision transformers (ViTs), have shown that transformers can outperform CNNs in image processing tasks by capturing long-range dependencies more effectively.

------

## Pros & Cons

### Advantages of Transformers

1. **Scalability**: Transformers can handle very large datasets, making them ideal for big data applications.
2. **Parallelization**: They process input data in parallel, unlike RNNs, which are sequential.
3. **Flexibility**: Transformers are highly adaptable to various tasks, from NLP to vision.
4. **Effectiveness with Pretraining**: Models like BERT and GPT leverage pretraining on massive datasets, leading to better performance in diverse applications.

------

### Limitations of Transformers

- **Computational Cost**: Self-attention mechanisms require significant memory and compute power, especially for long sequences.
- **Data Requirements**: Transformers need large amounts of data to train effectively, which may not be feasible for all applications.

------

## Conclusion

Transformers represent a paradigm shift in machine learning, offering unparalleled capabilities for handling sequential and structured data. 

Transformer is the first sequence transduction model based entirely on attention, replacing the recurrent layers most commonly used in encoder-decoder architectures with multi-headed self-attention.

Compared to perceptrons, RNNs, and CNNs, transformers provide superior performance in capturing global context, modeling long-term dependencies, and enabling efficient parallel processing.

## References

- [Attention is All You Need](https://arxiv.org/abs/1706.03762) ([pdf](https://arxiv.org/pdf/1706.03762))
- [Wikipedia - Transformer](https://en.wikipedia.org/wiki/Transformer_(deep_learning_architecture))
- ChatGPT with the following inputs: "Write me an article about Transformer in machine learning. Explain the difference compared to other architecture (Perceptron, RNN, CNN)"

### Further ressources

- [Nvidia - What Is a Transformer Model?](https://blogs.nvidia.com/blog/what-is-a-transformer-model/)
- [IBM Transformer model](https://www.ibm.com/think/topics/transformer-model)
- [Analytics Vidhya - Transformers](https://www.linkedin.com/posts/analytics-vidhya_day-2-mastering-llms-the-attention-mechanism-ugcPost-7282356882546040833-dP6D/)
- Video
  - [YouTube - Attention in transformers, visually explained](https://www.youtube.com/watch?v=eMlx5fFNoYc)
  - [Transformers (how LLMs work) explained visually](https://www.youtube.com/watch?v=wjZofJX0v4M)
