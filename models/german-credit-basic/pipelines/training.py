import os
import azureml.core
from azureml.core import Workspace, Dataset, RunConfiguration, Environment
from azureml.pipeline.core import Pipeline, PipelineDraft, PipelineParameter
from azureml.pipeline.steps import PythonScriptStep
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig

print("Azure ML SDK version:", azureml.core.VERSION)

print(f"git repo: {os.getenv('BUILD_REPOSITORY_URI')}")
print(f"git branch: {os.getenv('BUILD_SOURCEBRANCH')}")
print(f"git commit: {os.getenv('BUILD_SOURCEVERSION')}")
print(f"DevOps build number: {os.getenv('BUILD_BUILDNUMBER')}")

print('Connecting to workspace')
ws = Workspace.from_config()
print(f'WS name: {ws.name}\nRegion: {ws.location}\nSubscription id: {ws.subscription_id}\nResource group: {ws.resource_group}')

print('Loading dataset')
training_dataset = Dataset.get_by_name(ws, name='german_credit_file', version=1)

# Parametrize dataset input to the pipeline
training_dataset_parameter = PipelineParameter(name="training_dataset", default_value=training_dataset)
training_dataset_consumption = DatasetConsumptionConfig("training_dataset", training_dataset_parameter).as_download()

runconfig = RunConfiguration()
runconfig.environment = Environment.from_conda_specification('training-pipeline-env', 'config/train-conda.yml')

train_step = PythonScriptStep(name="train-step",
                        runconfig=runconfig,
                        source_directory='./',
                        script_name='train.py',
                        arguments=['--data_path', training_dataset_consumption, '--model_name', 'credit-prediction.pkl'],
                        inputs=[training_dataset_consumption],
                        compute_target='cpu-cluster',
                        allow_reuse=False)

register_step = PythonScriptStep(name="register-step",
                        runconfig=runconfig,
                        source_directory='pipelines/',
                        script_name='register.py',
                        arguments=['--model_name', 'credit-model-ci', '--model_path', 'outputs/credit-prediction.pkl',
                                   '--repo', os.getenv('BUILD_REPOSITORY_URI'), '--branch', os.getenv('BUILD_SOURCEBRANCH'),
                                   '--commit', os.getenv('BUILD_SOURCEVERSION'), '--build_id', os.getenv("BUILD_BUILDNUMBER")],
                        compute_target='cpu-cluster',
                        allow_reuse=False)

register_step.run_after(train_step)
steps = [train_step, register_step]

print('Creating, validating and publishing pipeline')
pipeline = Pipeline(workspace=ws, steps=steps)
pipeline.validate()
published_pipeline = pipeline.publish(name='credit-training-pipeline',
                                      description=f'Published pipeline from build id {os.getenv("BUILD_BUILDNUMBER")}')

# Output pipeline_id in specified format which will convert it to a variable in Azure DevOps
print(f'##vso[task.setvariable variable=pipeline_id]{published_pipeline.id}')