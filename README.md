# mlops-demo

Demo for MLOps with Azure Machine Learning

:star: A fully documented starting template repo can be found here: [microsoft/aml-acceleration-template](https://github.com/microsoft/aml-acceleration-template/).

## Setup & Demo Flow

This gives a short, high-level overview of how this repo may be used.

### Interactive demo part

1. If required, create an Azure Machine Learning workspace
1. Create a tabular dataset from [`data/german_credit_data.csv`](data/german_credit_data.csv) (download the file to your machine and select `From Local File` when creating a new Dataset)
1. Clone the whole repo into a Compute Instance
1. Walk through the following notebooks
    * [`models/german-credit-basic/notebooks/german-credit-local.ipynb`](models/german-credit-basic/notebooks/german-credit-local.ipynb) - Shows how to run local training inside the Compute Instance, registers the model with data linage, and calculates the model explainability
    * [`models/german-credit-basic/notebooks/german-credit-amlcompute.ipynb`](models/german-credit-basic/notebooks/german-credit-amlcompute.ipynb) - Shows how to train the same model on a Compute Cluster
    * [`models/german-credit-basic/notebooks/deploy_webservices.ipynb`](models/german-credit-basic/notebooks/deploy_webservices.ipynb) - Shows how to deploy the trained model to an Azure Container Instance

### MLOps demo part

1. Create a new project in Azure DevOps
1. Fork this repo or import it into Azure DevOps (so that you can make changes to the repo)
1. Create a service connection to your Azure Machine Learning workspace and use the name `aml-workspace-connection`
1. Edit [`pipelines/german-credit-config.yml`](pipelines/german-credit-config.yml) and adapt the values to point to your workspace
1. Import the following pipelines into DevOps
    * [`pipelines/german-credit-train-and-register.yml`](pipelines/german-credit-train-and-register.yml) - Trains and registers the model automatically
    * [`pipelines/german-credit-deploy.yml`](pipelines/german-credit-deploy.yml) - Deploys the trained model to ACI and AKS
1. Run the pipelines

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

test_data = {
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
}

headers = {'Content-Type': 'application/json'}
resp = requests.post(url, json=test_data, headers=headers)

print("Prediction (good, bad):", resp.text)
```
