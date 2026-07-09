---
position: 50
slug: /docs/data-centric-ai/glossary
---

# 💡 Glossary

We define important terms and concepts for data-centric AI workflows.

## Data types

### Image data

2D-array of image pixels. Image data is typically represented as a link to an image file (on disk or object storage) or as an in-memory array.

### Audio data

High-frequency time series (1-D array) data. It is typically represented as a link to a (possibly compressed) audio file or an in-memory array. Often, an image representation ([spectrograms](https://en.wikipedia.org/wiki/Spectrogram)) are used as input features for ML models.

## Decision boundary

The [decision boundary](https://en.wikipedia.org/wiki/Decision_boundary) is a hypersurface in the embedding space that separate different classes. Inspecting data samples near the decision boundary is useful to find critical edge cases.

## Embedding

Many model architectures (in particular neural networks) inherently transform the input space into a low-dimensional representation. This embedding of each data sample into a latent space is very useful for understanding both data traits as well as model behavior. In practice, the embedding is dense vector (typical sizes range from 64 to 2048) which is optained by saving a hideen layer of the model.

## Error patterns on computer vision data (images, videos)

## Image data

### darkness

### lightness

### blurr

### Signal-to-noise ratio

### Aspect ratio

## Label

## Nearest neighbor & k-th nearest neighbor

## Prediction

## Probabilities

In a classification problem, the ML model output is usually given as a probability vector. The prediction is then obtained by looking for the maximum value in this vector. Depending on the model, a [softmax](https://en.wikipedia.org/wiki/Softmax_function) function has to be applied on output logits in order to obtain the probabilities.

## Features

## Metadata
