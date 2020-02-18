import os
import json
import sys
import argparse
import shutil
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
        "verbosity": logging.INFO,
        "primary_metric": 'accuracy',
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

    best_run, fitted_model = run.get_output()
    run.add_properties({"best_run_id": best_run.run_id})

    output_dir = './outputs/'
    os.makedirs(output_dir, exist_ok=True)
    shutil.copy2('automl.log', output_dir)

    with open(output_dir + 'best_run.json', 'w') as f:
        json.dump(best_run, f)

def getRuntimeArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--DATASET_NAME', type=str)
    args = parser.parse_args()
    return args.DATASET_NAME

if __name__ == "__main__":
    main()
