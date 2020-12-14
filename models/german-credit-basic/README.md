# Running this code from your machine

## Running this code locally using Azure Machine Learning in Docker

We can fully run this example locally on our machine, while still logging the results to Azure Machine Learning.

Let's make sure we are in the model folder:

```console
cd models/german-credit-basic
```

Now, we can attach this local folder to the resource group with our Azure Machine Learning workspace:

```console
az ml folder attach -g csamlfsi-rg -w csamlfsi-ws
```
(`-w` refers to the workspace name and `-g` to the resource group of the workspace)

Next, we can run the `train.py` locally in a Docker container on our machine:

```console
az ml run submit-script -c config/train-local -e german-credit-train-local
```

This will create a Docker container with the conda enviroment from [`config/train-conda.yml`](config/train-conda.yml), inject our local code from this directory, and then execute [`train.py`](train.py) in it. The full configuration can be found in [`config/train-local.runconfig`](config/train-local.runconfig). All training will happen locally on your machine, however, the training run, metrics, artifacts, etc. will still show up in Azure Machine Learning. The data will come from the `Data Set` in Azure Machine Learning.

## Running this code on Azure Machine Learning Compute

Finally, we can run this example directly on Azure Machine Learning compute by using a different `runconfig` file. Let's make sure we are still in the `models/german-credit-basic` folder and that we executed `az ml folder attach -g csamlfsi-rg -w csamlfsi-ws` beforehand.

To run the `train.py` on Azure Machine Learning compute, we just use the [`config/train-amlcompute.runconfig`](config/train-amlcompute.runconfig) configuration:

```console
az ml run submit-script -c config/train-amlcompute -e german-credit-train-amlcompute -t run.json
```

This will do exactly the same as locally, but everything will happen in Azure. The `-t` option outputs a reference to the experiment run, which can be used to directly register the model from it. The full configuration can be found in [`config/train-amlcompute.runconfig`](config/train-amlcompute.runconfig).

## Model registration

Given the `run-metadata-file` from the experiment run, we can now register the model in AML. In this case, the `asset-path` points to the path structure within the experiment run:

```console
az ml model register --name german-credit-basic-model --asset-path outputs/credit-prediction.pkl --run-metadata-file run.json
```

## Running inferencing locally

We can deploy the model locally using Docker:

```console
az ml model deploy --name german-credit-qa-local --model german-credit-basic-model:1 --inference-config-file config/inference-config.yml --deploy-config-file config/deployment-config-aci-qa.yml --runtime python --compute-type local --port 32000 --overwrite
```

We can test the local endpoint using the following request:

```
POST http://localhost:32000/score HTTP/1.1
Content-Type: application/json

{ 
    "data": [
        {
        "Age": 20,
        "Sex": "male",
        "Job": 0,
        "Housing": "own",
        "Saving accounts": "little",
        "Checking account": "little",
        "Credit amount": 100,
        "Duration": 48,
        "Purpose": "radio/TV"
        }
    ]
}
```

Once we know it is working, we can remove the local service via:

```console
az ml service delete --name german-credit-qa-local
```

## Running inferencing on Azure

Finally, we can deploy to Azure. First, we can try deploying to Azure Container Instances:

```console
az ml model deploy -n german-credit-qa-aci --model german-credit-basic-model:1 --inference-config-file config/inference-config.yml --deploy-config-file config/deployment-config-aci-qa.yml --overwrite
```

We can test the ACI endpoint using the following request (make sure to replace the URL with your container's URL):

```
POST http://xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx.xxxxxx.azurecontainer.io/score HTTP/1.1
Content-Type: application/json

{ 
    "data": [
        {
        "Age": 20,
        "Sex": "male",
        "Job": 0,
        "Housing": "own",
        "Saving accounts": "little",
        "Checking account": "little",
        "Credit amount": 100,
        "Duration": 48,
        "Purpose": "radio/TV"
        }
    ]
}
```

We can remove the ACI-based service via:

```console
az ml service delete --name german-credit-qa-aci
```