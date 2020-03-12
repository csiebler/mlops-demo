# mlops-demo

Demo for MLOps with Azure Machine Learning

:star: A fully documenated and official repository can be [found here](https://github.com/MicrosoftDocs/pipelines-azureml).

## Setup

To be written.

## Conventions

This repo is fully based on conventions in order to make MLOps reusable and easily scaleable.
The directory structure is as follows:

```
pipelines
    \- train-and-register.yml - Base pipeline for training and registering a model
models
    \- model1
        train.py (entry file for training)
        score.py (entry file for scoring)
        \- inference-config
            conda_inference.yml - Conda environement definition for inference/scoring
            inference-config.json - Azure Machine Learning config for inferencing
            prod-deployment-config.yml - Production deployment infrastructure definition (e.g., AKS configuration)
            qa-deployment-config.yml - QA deployment infrastructure definition (e.g., ACI configuration)
        \- train-config
            conda_train.yml - Conda environement definition for training
    \- model2
        ...same file and folder structure...
```

## Testing

This snipped can be used to manually showcase/test the deployed model on ACI: 

```python
import requests
import json

url = '<scoring url>'

test_sample = json.dumps({
  'data': [{
    "Age": 20,
    "Sex": "male",
    "Job": 0,
    "Housing": "own",
    "Saving accounts": "little",
    "Checking account": "little",
    "Credit amount": 100,
    "Duration": 48,
    "Purpose": "radio/TV"
  }]
})

test_sample = bytes(test_sample,encoding = 'utf8')

headers = {'Content-Type':'application/json'}
resp = requests.post(url, test_sample, headers=headers)

print("prediction:", resp.text)
```
