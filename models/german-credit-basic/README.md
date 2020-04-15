# Running this code from your machine

## Running this code locally using Azure Machine Learning in Docker

We can fully run this example locally on our machine, while still logging the results to Azure Machine Learning.

Let's make sure we are in the model folder:

```cli
cd models/german-credit-basic
```

Now, we can attach this local folder to the resource group with our Azure Machine Learning workspace:

```cli
az ml folder attach -g csamlfsi-rg -w csamlfsi-ws
```

Next, we can run the `train.py` locally in a Docker container on our machine:

```cli
az ml run submit-script -c config/train-local -e german-credit-train-local
```

This will create a Docker container with the conda enviroment from [`config/train-conda.yml`](config/train-conda.yml), inject our local code from this directory, and then execute [`train.py`](train.py) in it. The full configuration can be found in [`config/train-local.runconfig`](config/train-local.runconfig). All training will happen locally on your machine, however, the training run, metrics, artifacts, etc. will still show up in Azure Machine Learning. The data will come from the `Data Set` in Azure Machine Learning.

## Running this code on Azure Machine Learning Compute

Finally, we can run this example directly on Azure Machine Learning compute by using a different `runconfig` file. Let's make sure we are still in the `models/german-credit-basic` folder and that we executed `az ml folder attach -g csamlfsi-rg -w csamlfsi-ws` before.

To run the `train.py` on Azure Machine Learning compute, we just use the [`config/train-amlcompute.runconfig`](config/train-amlcompute.runconfig) configuration:

```cli
az ml run submit-script -c config/train-amlcompute -e german-credit-train-amlcompute
```

This will do exactly the same as locally, but everything will happen in Azure. The full configuration can be found in [`config/train-amlcompute.runconfig`](config/train-amlcompute.runconfig).