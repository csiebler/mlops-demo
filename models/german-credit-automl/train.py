import os
import sys
import argparse
import logging
import azureml.core
from azureml.core import Run
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
from azureml.core.dataset import Dataset
from azureml.train.automl import AutoMLConfig

def main():

    dataset_name = getRuntimeArgs()

    run = Run.get_context()
    ws = run.experiment.workspace

    ds = Dataset.get_by_name(workspace=ws, name=dataset_name)
    
    automl_settings = {
        "task": 'classification',
        "debug_log": 'automl_errors.log',
        "verbosity": logging.INFO,
        "primary_metric": 'AUC_weighted',
        "experiment_timeout_hours": 0.05,
        "n_cross_validations": 3,
        "enable_stack_ensemble": False,
        "enable_voting_ensemble": False,
        "model_explainability": True,
        "preprocess": True,
        "max_cores_per_iteration": -1,
        "max_concurrent_iterations": 4,
        "training_data": ds,
        "drop_column_names": ['Sno'],
        "label_column_name": 'Risk'
    }

    automl_config = AutoMLConfig(**automl_settings)
    run = run.submit_child(automl_config, show_output = True)

def getRuntimeArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--DATASET_NAME', type=str)
    args = parser.parse_args()
    return args.DATASET_NAME


if __name__ == "__main__":
    main()
