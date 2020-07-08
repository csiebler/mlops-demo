# mlops-demo

Demo for MLOps with Azure Machine Learning

:star: A fully documented starting template repo can be found here: [microsoft/aml-acceleration-template](https://github.com/microsoft/aml-acceleration-template/).

## Setup

To be written.

## Conventions

This repo is fully based on conventions in order to make MLOps reusable and easily scaleable.
The directory structure is as follows:

```
pipelines
    \- german-credit-config.yml - Configuration for german credit model
    \- german-credit-deploy.yml - Deployment pipeline for german credit model
    \- german-credit-train-and-register.yml - Pipline for training and registering the base german credit model
models
    \- model1
        train.py (entry file for training)
        score.py (entry file for scoring)
        \- config
            deployment-config-aci-qa.yml - QA deployment infrastructure definition (e.g., ACI configuration)
            deployment-config-aks-prod.yml - Production deployment infrastructure definition (e.g., AKS configuration)
            inference-conda.yml - Conda environement definition for inferencing/scoring
            inference-config.yml - Azure Machine Learning config for inferencing
            train-conda.yml - Conda environement definition for training
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

headers = {'Content-Type':'application/json'}
resp = requests.post(url, json=test_sample, headers=headers)

print("Prediction (good, bad):", resp.text)
```
