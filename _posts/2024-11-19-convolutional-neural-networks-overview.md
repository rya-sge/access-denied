---
layout: post
title: Convolutional Neural Networks (CNNs)- Overview
date:   2024-11-19
lang: en
locale: en-GB
categories: programmation
tags: cnn ML AI  neural-network convolutional
description: Transport Layer Security (TLS) 1.3 is the latest version of the TLS protocol, designed to enhance internet security, speed, and privacy.
image:
isMath: true
---

**Convolutional Neural Networks (CNNs)** are a specialized class of neural networks designed primarily for analyzing visual data. Inspired by the human visual cortex, CNNs are particularly used in fields like image recognition, computer vision, and video analysis. 

They  are relevant to identify features such as edges, textures, and patterns within images, typically useful in applications ranging from autonomous driving and medical imaging to augmented reality and natural language processing.

CNNs are structured to recognize spatial hierarchies in data, enabling the network to detect patterns of increasing complexity through successive layers. 

This article provides an overview of the core components of CNNs, essential terminology, and how these components contribute to the capabilities of CNNs.

[TOC]

## Layers

CNN has three main types of layers, which are:

- Convolutional layer
- Pooling layer (or downsampling)
- Fully-connected (FC) layerFully-connected (FC) layer

With each layer, the CNN increases in its complexity, identifying greater portions of the image. 

Earlier layers focus on simple features, such as colors and edges. 

As the image data progresses through the layers of the CNN, it starts to recognize more complex elements until it finally identifies the intended object.

### 1. Convolution Layer

- **Description**: The convolution layer is the fundamental building block of a CNN. It uses small filters (or kernels) that slide over the input image to capture relevant features, resulting in a set of output feature maps.
- **Function**: By applying filters across the image, the convolution layer enables the model to learn features such as edges, textures, and shapes. As the data progresses through more convolution layers, the network identifies more abstract patterns.
- Example: 
  - We take a color image as input. 
    - This image is made up of a matrix of pixels in 3D. This means that the input will have three dimensions: a height, width, and depth —which correspond to RGB in an image. 
    - We also have a feature detector, also known as a **kernel** or a **filter**, which will move across the receptive fields of the image, checking if the feature is present. This process is known as a convolution.

### 2. Pooling Layer (downsampling)

- **Description**: Pooling layers reduce the spatial dimensions of feature maps, which helps to minimize computational requirements and reduce the risk of overfitting.
- **Types**: Common pooling types include
  -  *max pooling*, which takes the maximum value within a defined region to send to the output array, 
  - *average pooling*, which calculates the average value to send to the output array.
- **Function**: Pooling layers effectively down-sample the data, preserving only the most prominent features. This not only reduces data size but also improves generalization, allowing the network to focus on the most significant aspects of an image and limit risk of overfitting. Nevertheless, there are a lot of information lost during the process.

### 3. Fully Connected Layer (FC Layer)

- **Description**: Fully connected layers are typically positioned near the end of the CNN architecture and are responsible for the final decision-making process.
- **Structure**: In these layers, each neuron connects to every neuron in the previous layer, allowing the model to consolidate information from all parts of the feature map.
- **Function**: By combining features learned from previous layers, fully connected layers enable the model to make final classifications or predictions based on the synthesized features.

## Key Processes

### Activation Function

- **Description**: Activation functions introduce non-linearity into the model, which allows the network to learn complex patterns and relationships within the data.
- **Most Common Activation Function**:
  -  ReLU (Rectified Linear Unit) is widely used in CNNs. It replaces all negative values with zero, which helps the network learn faster and more effectively.
  -  softmax activation function to classify inputs appropriately, producing a probability from 0 to 1.
  -  While convolutional and pooling layers tend to use ReLu functions, FC layers usually leverage a softmax
- **Function**: Without activation functions, CNNs would be limited to linear transformations, greatly reducing their ability to capture complex, non-linear relationships in data.

### Backpropagation and Loss Function

- **Backpropagation**: This is a learning process used to update the weights in the network. It works by calculating the gradient of the loss function with respect to each weight and adjusting weights to minimize errors.
- **Loss Function**: The loss function measures the difference between the predicted and actual values, guiding the network’s learning process.
- **Function**: Together, backpropagation and the loss function enable CNNs to optimize weight adjustments, improving their accuracy over time.

## Hyperparameters

Hyperparameters in a **Convolutional Neural Network (CNN)** are the parameters that are set before training and are not updated during the training process. They are crucial because they directly influence the performance of the model, its learning speed, and its ability to generalize to unseen data.

- Learning rate
- Number of iterations
- Regularization
- Network architecture
- Number of hidden layers
- Number of hidden units
- Choice of activation function 
- Optimization algorithm hyperparameters (e.g. momentum)
-  Minibatch size

Reference: [unibas - Deep Neural Networks - Hyperparameters](https://dmi.unibas.ch/fileadmin/user_upload/dmi/Studium/Computer_Science/Vorlesung_HS19/Pattern_Recongnition/09_Deep_Neural_Networks_hyperparameters_2019.pdf) + ChatGPT

### Stride

- **Description**: Stride is a parameter that controls the distance (or number of pixels) the filter moves across the input image or data.
- **Function**: The stride affects the resolution of the feature map; a stride of one maintains detailed features, while a higher stride skips over pixels, reducing the output size and capturing more generalized features. Larger strides can lead to faster computation but may miss fine-grained details in the image.

### Padding

- **Description**: Padding involves adding extra layers of zeros around the edges of the input image to control the output feature map's size after convolution.
- **Types of Padding**: Zero-padding is the most common method, which ensures that all features are preserved, particularly at the image edges.
- **Function**: Padding helps retain spatial dimensions, especially in layers where maintaining the size of the input and output data is important for effective feature extraction.
-  There are three types of padding:
  - **Valid padding:** This is also known as no padding. In this case, the last convolution is dropped if dimensions do not align.
  - **Same padding:** This padding ensures that the output layer has the same size as the input layer.
  - **Full padding:** This type of padding increases the size of the output by adding zeros to the border of the input.

## CNN Architectures and Variants

CNNs have evolved with several specialized architectures that cater to different applications and optimize performance in unique ways. 

Some of the most notable CNN architectures include:

- **LeNet**: One of the earliest CNN architectures, LeNet was designed for digit recognition and introduced many foundational ideas for modern CNNs. LeNet-5 is the classic CNN architecture.
- **AlexNet**: This architecture has been submitted to the ImageNet competition in 2012 and popularized the use of CNNs for large-scale image recognition tasks, featuring deep layers and ReLU activation.

[Paper](https://proceedings.neurips.cc/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf) by Alex Krizhevsky, Ilya Sutskever, and Geoffrey E. Hinton

[Medium - AlexNet Architecture Explained](https://medium.com/@siddheshb008/alexnet-architecture-explained-b6240c528bd5)

- **VGG**: VGG networks emphasized simplicity and depth, using smaller (3x3) filters stacked in multiple layers to improve accuracy with a deeper architecture.

- **ResNet**: The ResNet architecture introduced skip (or residual) connections to prevent issues like vanishing gradients in deep networks, allowing networks to be hundreds of layers deep.

- **Inception**: This architecture introduced inception modules, which combine multiple convolution operations in parallel, enabling the model to capture a wider variety of features. The first version was [GoogLeNet](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/43022.pdf).

see [Understanding Architecture Of Inception Network & Applying It To A Real-World Dataset](https://gghantiwala.medium.com/understanding-the-architecture-of-the-inception-network-and-applying-it-to-a-real-world-dataset-169874795540)

## Applications of CNNs

CNNs have been transformative across numerous domains. Here are a few significant applications:

- **Image Classification**: CNNs excel at categorizing images into predefined classes. Image classification has widespread uses, from object identification to medical diagnosis.
- **Object Detection**: CNNs detect and localize objects within images, making them essential for applications like self-driving cars, robotics, and surveillance.
- **Face Recognition**: By analyzing facial features, CNNs can identify and verify individuals, a key technology for security and user authentication.
- **Medical Imaging**: In healthcare, CNNs assist in diagnosing diseases by analyzing medical scans like MRIs, X-rays, and CT scans.
- **Natural Language Processing (NLP)**: Although traditionally focused on visual tasks, CNNs are also used in NLP for tasks like text classification, sentiment analysis, and machine translation.

## Conclusion

Convolutional Neural Networks (CNNs) allows machine learning to understand and analyze visual data.

By leveraging key components like convolution layers, pooling layers, and fully connected layers, CNNs can be used to learn complex patterns and making accurate predictions in a range of applications. 

## References

- [IBM - What are convolutional neural networks?](https://www.ibm.com/topics/convolutional-neural-networks)
- [Understanding Architecture Of Inception Network & Applying It To A Real-World Dataset](https://gghantiwala.medium.com/understanding-the-architecture-of-the-inception-network-and-applying-it-to-a-real-world-dataset-169874795540)
- [Medium - AlexNet Architecture Explained](https://medium.com/@siddheshb008/alexnet-architecture-explained-b6240c528bd5)
- [unibas - Deep Neural Networks - Hyperparameters](https://dmi.unibas.ch/fileadmin/user_upload/dmi/Studium/Computer_Science/Vorlesung_HS19/Pattern_Recongnition/09_Deep_Neural_Networks_hyperparameters_2019.pdf) 