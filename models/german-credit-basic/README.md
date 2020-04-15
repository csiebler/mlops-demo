# Running this code from your machine

## Running this code locally using Azure Machine Learning in Docker

We can fully run this example locally on our machine, while still logging the results to Azure Machine Learning.

First, we attach this local folder to the resource group with our Azure Machine Learning workspace:

```cli
cd models/german-credit-basic
az ml folder attach -g csamlfsi-rg -w csamlfsi-ws
```

Then we can run the `train.py` locally in a Docker container on our machine:

```cli
az ml run submit-script -c config/train-local -e german-credit-train-local
```

This will create a Docker container with the conda enviroment from [`config/train-conda.yml`](config/train-conda.yml), inject our local code from this directory, and then execute [`train.py`](train.py) in it. The full configuration can be found in [`config/train-local.runconfig`](config/train-local.runconfig). All training will happen locally on your machine, however, the training run, metrics, artifacts, etc. will still show up in Azure Machine Learning. The data will come from the `Data Set` in Azure Machine Learning.

## Running this code on Azure Machine Learning Compute

Next, we can run this example directly on Azure Machine Learning compute by using a different `runconfig` file.

First, we attach this local folder to the resource group with our Azure Machine Learning workspace (no need to run it again if we ran it before):

```cli
cd models/german-credit-basic
az ml folder attach -g csamlfsi-rg -w csamlfsi-ws
```

Then we can run the `train.py` on Azure Machine Learning compute by using the [`config/train-amlcompute.runconfig`](config/train-amlcompute.runconfig) configuration:

```cli
az ml run submit-script -c config/train-amlcompute -e german-credit-train-amlcompute
```

This will do exactly the same as locally, but everything will happen in Azure. The full configuration can be found in [`config/train-amlcompute.runconfig`](config/train-amlcompute.runconfig).