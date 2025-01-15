---
layout: post
title: Zama Concrete ML
date:   2025-01-15
lang: en
locale: en-GB
categories: programmation cryptography
tags: machine-learning zama ML
description: Concrete ML is an open source, privacy-preserving, machine learning framework based on Fully Homomorphic Encryption (FHE)
image: 
isMath: false
---

## Introduction

Concrete ML is an open source, privacy-preserving, machine learning framework based on Fully Homomorphic Encryption (FHE). It enables data scientists without any prior knowledge of cryptography to perform:

- **Automatic model conversion**: Use familiar APIs from scikit-learn and PyTorch to convert machine learning models to their FHE equivalent. This is applicable for [linear models](https://docs.zama.ai/concrete-ml/built-in-models/linear), [tree-based models](https://docs.zama.ai/concrete-ml/built-in-models/tree), and [neural networks](https://docs.zama.ai/concrete-ml/built-in-models/neural-networks)).
- **Encrypted data training**: [Train models](https://docs.zama.ai/concrete-ml/built-in-models/training) directly on encrypted data to maintain privacy.
- **Encrypted data pre-processing**: [Pre-process encrypted data](https://docs.zama.ai/concrete-ml/built-in-models/encrypted_dataframe) using a DataFrame paradigm.

## Cryptography concepts

Concrete ML and Concrete abstract the details of the underlying cryptography scheme, TFHE. However, understanding some cryptography concepts is still useful:

- **Encrypted inference:** FHE allows third parties to execute a machine learning model on encrypted data. The inference result is also encrypted and can only be decrypted by the key holder.
- **Key generation:** Cryptographic keys are generated using random number generators. Key generation can be time-consuming and produce large keys, but each model used by a client only requires key generation once.
  - **Private encryption key**: The private encryption key is used to encrypt data so that the corresponding ciphertext appears random.
  - **Public evaluation key**: A public evaluation key is used to perform homomorphic operations on encrypted data, typically by a server.
- **Guaranteed correctness of encrypted computations:** To ensure security, TFHE adds random noise to ciphertexts. Depending on the noise parameters, it can cause errors during encrypted data processing. By default, Concrete ML uses parameters that guarantee the correctness of encrypted computations, so the results on encrypted data equals to those of simulations on clear data.
- **Programmable Boostrapping (PBS)** : Programmable Bootstrapping enables the homomorphic evaluation of any function of a ciphertext, with a controlled level of noise. Learn more about PBS in [this paper](https://eprint.iacr.org/2021/091).

For a deeper understanding of the cryptography behind the Concrete stack, refer to the [whitepaper on TFHE and Programmable Boostrapping](https://whitepaper.zama.ai/) or [this series of blogs](https://www.zama.ai/post/tfhe-deep-dive-part-1).

## Key features

- **Training on encrypted data**: FHE is an encryption technique that allows computing directly on encrypted data, without needing to decrypt it. With FHE, you can build private-by-design applications without compromising on features.
- **Federated learning**: Training on encrypted data provides the highest level of privacy but is slower than training on clear data. Federated learning is an alternative approach, where data privacy can be ensured by using a **trusted gradient aggregator**, coupled with optional *differential privacy* instead of encryption. Concrete ML can import all types of models: linear, tree-based and neural networks, that are trained using federated learning using the [`from_sklearn_model` function](https://docs.zama.ai/concrete-ml/built-in-models/linear#pre-trained-models) and the [`compile_torch_model`](https://docs.zama.ai/concrete-ml/deep-learning/torch_support) function.

## Example usage

Here is a simple example of classification on encrypted data using logistic regression. You can find more examples [here](https://docs.zama.ai/concrete-ml/tutorials/ml_examples).

This example shows the typical flow of a Concrete ML model:

1. **Training the model**: Train the model on unencrypted (plaintext) data using scikit-learn. Since Fully Homomorphic Encryption (FHE) operates over integers, Concrete ML quantizes the model to use only integers during inference.
2. **Compiling the model**: Compile the quantized model to an FHE equivalent. Under the hood, the model is first converted to a Concrete Python program and then compiled.
3. **Performing inference**: Perform inference on encrypted data. The example above shows encrypted inference in the model-development phase. Alternatively, during [deployment](https://docs.zama.ai/concrete-ml/get-started/cloud) in a client/server setting, the client encrypts the data, the server processes it securely, and then the client decrypts the results.

Workflow example: 

1)  create a synthetic data-set
2) Split the data-set into a train and test set
3)  Train in the clear and quantize the weights
4)  simulate the predictions in the clear
5) compile on a representative set
6) run the inference on encrypted inputs

It is also possible to call encryption, model prediction, and decryption functions separately as follows. Executing these steps separately is equivalent to calling `predict_proba` on the model instance. Example

```python
# Predict probability for a single example
y_proba_fhe = model.predict_proba(X_test[[0]], fhe="execute")

# Quantize an original float input
q_input = model.quantize_input(X_test[[0]])

# Encrypt the input
q_input_enc = model.fhe_circuit.encrypt(q_input)

# Execute the linear product in FHE 
q_y_enc = model.fhe_circuit.run(q_input_enc)

# Decrypt the result (integer)
q_y = model.fhe_circuit.decrypt(q_y_enc)

# De-quantize and post-process the result
y0 = model.post_processing(model.dequantize_output(q_y))
```

## Current limitations

- **Precision and accuracy**: In order to run models in FHE, Concrete ML requires models to be within the precision limit, currently 16-bit integers. Thus, machine learning models must be quantized and it sometimes leads to a loss of accuracy versus the original model that operates on plaintext.
- **Models availability**: Concrete ML currently only supports *training* on encrypted data for some models, while it supports *inference* for a large variety of models.
- **Processing**: Concrete currently doesn't support pre-processing model inputs and post-processing model outputs. These processing stages may involve:
  - Text-to-numerical feature transformation
  - Dimensionality reduction
  - KNN or clustering
  - Featurization
  - Normalization
  - The mixing of ensemble models' results.

These issues are currently being addressed, and significant improvements are expected to be released in the near future.

## Key concepts

This section explains the essential cryptographic terms and the important concepts of Concrete ML model lifecycle with Fully Homomorphic Encryption (FHE).

Concrete ML is built on top of Concrete, which enables the conversion from NumPy programs into FHE circuits.

### Lifecycle of a Concrete ML model

With Concrete ML, you can train a model on clear or encrypted data, then deploy it to predict on encrypted inputs. During deployment, data can be pre-processed while being encrypted. Therefore, data stay encrypted during the entire lifecycle of the machine learning model, with some limitations.

### I. Model development

1. **Training:** A model is trained either using plaintext (non-encrypted) training data, or encrypted training data.
2. **Quantization:** Quantization converts inputs, model weights, and all intermediate values of the inference computation to integer equivalents. More information is available [here](https://docs.zama.ai/concrete-ml/explanations/quantization). Concrete ML performs this step in two ways depending on model type:
   - During training (Quantization Aware Training): by adding quantization layers in the neural network model, weights can be forced to have discrete values and activation quantization parameters are optimized through gradient descent. QAT requires re-training a neural network with these quantization layers.
   - After training (Post Training Quantization): the floating point neural network is kept as-is and a calibration step determines quantization parameters for each layer. No re-training is necessary and thus, no training data or labels are needed to convert a neural network to FHE using PTQ.
3. **Simulation:** Simulation allows you to execute a model that was quantized, to measure its accuracy in FHE, and to determine the modifications required to make it FHE compatible. Simulation is described in more detail [here](https://docs.zama.ai/concrete-ml/explanations/compilation#fhe-simulation).
4. **Compilation:** After quantizing the model and confirming that it has good FHE accuracy through simulation, the model then needs to be compiled using Concrete's FHE Compiler to produce an equivalent FHE circuit. This circuit is represented as an MLIR program consisting of low level cryptographic operations. You can read more about FHE compilation [here](https://docs.zama.ai/concrete-ml/explanations/compilation), MLIR [here](https://mlir.llvm.org/), and about the low-level Concrete library [here](https://github.com/zama-ai/concrete).
5. **Inference:** The compiled model can then be executed on encrypted data, once the proper keys have been generated. The model can also be deployed to a server and used to run private inference on encrypted inputs.

You can find examples of the model development workflow [here](https://docs.zama.ai/concrete-ml/tutorials/ml_examples).

### II. Model deployment

1. **Pre-processing:** Data owners(client) can generate keys to encrypt/decrypt data and store it in a [DataFrame](https://docs.zama.ai/concrete-ml/built-in-models/encrypted_dataframe) for further processing on a server. The server can pre-process such data with pre-compiled circuits, to prepare it for encrypted training or inference.
2. **Client/server model deployment:** In a client/server setting, Concrete ML models can be exported to:
   - Allow the client to generate keys, encrypt, and decrypt.
   - Provide a compiled model that can run on the server to perform inference on encrypted data.
3. **Key generation:** The data owner (client) needs to generate a set of keys:
   - A private encryption key to encrypt/decrypt their data and results
   - A public evaluation key for the model's FHE evaluation on the server.

You can find an example of the model deployment workflow [here](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/ClientServer.ipynb).



## Model accuracy considerations under FHE constraints

FHE requires all inputs, constants, and intermediate values to be integers of maximum 16 bits. To make machine learning models compatible with FHE, Concrete ML implements some techniques with accuracy considerations:

- **Quantization**: Concrete ML quantizes inputs, outputs, weights, and activations to meet FHE limitations. See [the quantization documentation](https://docs.zama.ai/concrete-ml/explanations/quantization) for details.
  - **Accuracy trade-off**: Quantization may reduce accuracy, but careful selection of quantization parameters or of the training approach can mitigate this. Concrete ML offers built-in quantized models; users only configure parameters like bit-width. For more details of quantization configurations, see [the advanced quantization guide](https://docs.zama.ai/concrete-ml/explanations/quantization#configuring-model-quantization-parameters).
- **Additional methods**: Dimensionality reduction and pruning are additional ways to make programs compatible for FHE. See [Poisson regression example](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/PoissonRegression.ipynb) for dimensionality reduction and [built-in neural networks](https://docs.zama.ai/concrete-ml/built-in-models/neural-networks) for pruning.

# Inference in the cloud

This document illustrate how Concrete ML model and DataFrames are deployed in client/server setting when creating privacy-preserving services in the cloud.

Once compiled to FHE, a Concrete ML model or DataFrame generates machine code that execute prediction, training or pre-processing on encrypted data. During this process, Concrete ML generates [the private encryption keys](https://docs.zama.ai/concrete-ml/get-started/concepts#cryptography-concepts) and [the pubic evaluation keys](https://docs.zama.ai/concrete-ml/get-started/concepts#cryptography-concepts).

## Communication protocols

The overall communications protocol to enable cloud deployment of machine learning services can be summarized in the following diagram:

![img](https://docs.zama.ai/~gitbook/image?url=https%3A%2F%2F982026572-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FVo0VAsu7f5LmyTWU78D1%252Fuploads%252Fgit-blob-98dd1e7c0dcb71b807582e66439445e0bbbdd2e8%252FClientServerDiag.png%3Falt%3Dmedia&width=768&dpr=4&quality=100&sign=8d9667b4&sv=2)

The steps detailed above are:

1. **Model Deployment**: The model developer deploys the compiled machine learning model to the server. This model includes the cryptographic parameters. The server is now ready to provide private inference. Cryptographic parameters and compiled programs for DataFrames are included directly in Concrete ML.
2. **Client request**: The client requests the cryptographic parameters (client specs). Once the client receives them from the server, the *secret* and *evaluation* keys are generated.
3. **Key exchanges**: The client sends the *evaluation* key to the server. The server is now ready to accept requests from this client. The client sends their encrypted data. Serialized DataFrames include client evaluation keys.
4. **Private inference**: The server uses the *evaluation* key to securely run prediction, training and pre-processing on the user's data and sends back the encrypted result.
5. **Decryption**: The client now decrypts the result and can send back new requests.

For more information on how to implement this basic secure inference protocol, refer to the [Production Deployment section](https://docs.zama.ai/concrete-ml/guides/client_server) and to the [client/server example](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/ClientServer.ipynb). For information on training on encrypted data, see [the corresponding section](https://docs.zama.ai/concrete-ml/built-in-models/training).

## Built-in model examples

These examples illustrate the basic usage of built-in Concrete ML models. For more examples showing how to train high-accuracy models on more complex data-sets, see the [Demos and Tutorials](https://docs.zama.ai/concrete-ml/tutorials/showcase) section.

### FHE constraints

In Concrete ML, built-in linear models are exact equivalents to their scikit-learn counterparts. As they do not apply any non-linearity during inference, these models are very fast (~1ms FHE inference time) and can use high-precision integers (between 20-25 bits).

Tree-based models apply non-linear functions that enable comparisons of inputs and trained thresholds. Thus, they are limited with respect to the number of bits used to represent the inputs. But as these examples show, in practice 5-6 bits are sufficient to exactly reproduce the behavior of their scikit-learn counterpart models.

In the examples below, built-in neural networks can be configured to work with user-specified accumulator sizes, which allow the user to adjust the speed/accuracy trade-off.

It is recommended to use [simulation](https://docs.zama.ai/concrete-ml/explanations/compilation#fhe-simulation) to configure the speed/accuracy trade-off for tree-based models and neural networks, using grid-search or your own heuristics.

There are several different models available as example: , Generalized linear models, Decision tree

|                                      |                                                              |                                                              |
| ------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Linear models                        | These examples show how to use the built-in linear models on synthetic data | [Linear Regression example](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/LinearRegression.ipynb) [Logistic Regression example](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/LogisticRegression.ipynb) [Linear Support Vector Regression example](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/LinearSVR.ipynb) [Linear SVM classification](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/SVMClassifier.ipynb) |
| Generalized linear models            | These two examples show generalized linear models (GLM) on the real-world [OpenML insurance](https://www.openml.org/d/41214) data-set. | [Poisson Regression example](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/PoissonRegression.ipynb) [Generalized Linear Models comparison](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/GLMComparison.ipynb) |
| Decision tree                        | Using the [OpenML spams](https://www.openml.org/d/44) data-set, this example shows how to train a classifier that detects spam, based on features extracted from email messages. A grid-search is performed over decision-tree hyper-parameters to find the best ones. | [Decision Tree Classifier](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/DecisionTreeClassifier.ipynb), [Decision Tree Regressor](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/DecisionTreeRegressor.ipynb) |
| XGBoost and Random Forest classifier | This example shows how to train tree-ensemble models (either XGBoost or Random Forest), first on a synthetic data-set, and then on the [Diabetes](https://www.openml.org/d/37) data-set. Grid-search is used to find the best number of trees in the ensemble. | [XGBoost/Random Forest example](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/XGBClassifier.ipynb) |
| XGBoost regression                   | Privacy-preserving prediction of house prices is shown in this example, using the [House Prices](https://www.openml.org/d/43926) data-set. | [XGBoost Regression example](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/XGBRegressor.ipynb) |
| Fully connected neural network       | Two different configurations of the built-in, fully-connected neural networks are shown. | [NN Iris example](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/FullyConnectedNeuralNetwork.ipynb) [NN MNIST example](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/FullyConnectedNeuralNetworkOnMNIST.ipynb) |
| Comparison of models                 | [Classifier comparison](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/ClassifierComparison.ipynb) [Regressor comparison](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/RegressorComparison.ipynb) | Based on three different synthetic data-sets, all the built-in classifiers are demonstrated in this notebook, showing accuracies, inference times, accumulator bit-widths, and decision boundaries. |
| Training on encrypted data           | [LogisticRegression training](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/LogisticRegressionTraining.ipynb) | This example shows how to configure a training algorithm that works on encrypted data and how to deploy it in a client/server application. |



## Deep learning examples

These examples illustrate the basic usage of Concrete ML to build various types of neural networks. They use simple data-sets, focusing on the syntax and usage of Concrete ML. For examples showing how to train high-accuracy models on more complex data-sets, see the [Demos and Tutorials](https://docs.zama.ai/concrete-ml/tutorials/showcase) section.

### FHE constraints considerations

The examples listed here make use of [simulation](https://docs.zama.ai/concrete-ml/explanations/compilation#fhe-simulation) to perform evaluation over large test sets. Since FHE execution can be slow, only a few FHE executions can be performed. The [correctness guarantees](https://docs.zama.ai/concrete-ml/get-started/concepts#cryptography-concepts) of Concrete ML ensure that accuracy measured with simulation is the same as that which will be obtained during FHE execution.

Some examples constrain accumulators to 7-8 bits, which can be sufficient for simple data-sets. Up to 16-bit accumulators can be used, but this introduces a slowdown of 4-5x compared to 8-bit accumulators.

### List of Examples

#### 1. Step-by-step guide to building a custom NN

- [Quantization aware training example](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/QuantizationAwareTraining.ipynb)

This shows how to use Quantization Aware Training and pruning when starting out from a classical PyTorch network. This example uses a simple data-set and a small NN, which achieves good accuracy with low accumulator size.

#### 2. Custom convolutional NN on the [Digits](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html) data-set

- [Convolutional Neural Network](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/advanced_examples/ConvolutionalNeuralNetwork.ipynb)

Following the [Step-by-step guide](https://docs.zama.ai/concrete-ml/deep-learning/fhe_friendly_models), this notebook implements a Quantization Aware Training convolutional neural network on the MNIST data-set. It uses 3-bit weights and activations, giving a 7-bit accumulator.

## Security model

The default parameters for Concrete ML are chosen considering the [IND-CPA](https://en.wikipedia.org/wiki/Ciphertext_indistinguishability) security model, and are selected with a [bootstrapping off-by-one error probability](https://docs.zama.ai/concrete-ml/explanations/advanced_features#tolerance-to-off-by-one-error-for-an-individual-tlu) of 2−402−40. In particular, it is assumed that the results of decrypted computations are not shared by the secret key owner with any third parties, as such an action can lead to leakage of the secret encryption key. If you are designing an application where decryptions must be shared, you will need to craft custom encryption parameters which are chosen in consideration of the IND-CPA^D security model [1].

### Correctness of computations

The [cryptography concepts](https://docs.zama.ai/concrete-ml/get-started/concepts#cryptography-concepts) section explains how Concrete ML can ensure **guaranteed correctness of encrypted computations**. In this approach, a quantized machine learning model will be converted to an FHE circuit that produces the same result on encrypted data as the original model on clear data.

However, the [bootstrapping off-by-one error probability](https://docs.zama.ai/concrete-ml/explanations/advanced_features#tolerance-to-off-by-one-error-for-an-individual-tlu) can be configured by the user. Raising this probability results in lower latency when executing on encrypted data, but higher values cancel the correctness guarantee of the default setting. In practice this may not be an issue, as the accuracy of the model may be maintained, even though slight differences are observed in the model outputs. Moreover, as noted in the [paragraph above](https://docs.zama.ai/concrete-ml/explanations/security_and_correctness#security-model), raising the off-by-one error probability may negatively impact the security model.

Furthermore, a second approach to reduce latency at the expense of correctness is approximate computation of univariate functions. This mode is enabled by using the [rounding setting](https://docs.zama.ai/concrete-ml/explanations/advanced_features#rounded-activations-and-quantizers). When using the [`fhe.Exactness.APPROXIMATE`](https://github.com/zama-ai/concrete-ml/blob/release/1.8.x/docs/references/api/concrete.ml.torch.compile.md#function-compile_torch_model) rounding method, off-by-one errors are always induced in the computation of activation functions, irrespective of the bootstrapping off-by-one error probability.

When trading-off better latency for correctness, it is highly recommended to use the [FHE simulation feature](https://docs.zama.ai/concrete-ml/get-started/concepts#i-model-development) to measure accuracy on a drawn-out test-set. In many cases the accuracy of the model is only slightly impacted by approximate computations.

##  