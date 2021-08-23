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

steps = [train_step]
print('Creating, validating and publishing pipeline')
pipeline = Pipeline(workspace=ws, steps=steps)
pipeline.validate()
# pipeline_draft = PipelineDraft.create(workspace=ws,
#                                       name='credit-training-pipeline',
#                                       experiment_name='credit-training-pipeline-ci',
#                                       pipeline=pipeline,
#                                       continue_on_step_failure=True,

#                                       properties={'repo': os.getenv('BUILD_REPOSITORY_URI'),
#                                                    'branch': os.getenv('BUILD_SOURCEBRANCH'), 
#                                                    'commit': os.getenv('BUILD_SOURCEVERSION'),
#                                                    'build_id': os.getenv('BUILD_BUILDNUMBER')}
#                                       )
# published_pipeline = pipeline_draft.publish()

published_pipeline = pipeline.publish(name='credit-training-pipeline',
                                      tags={'repo': os.getenv('BUILD_REPOSITORY_URI'),
                                            'branch': os.getenv('BUILD_SOURCEBRANCH'), 
                                            'commit': os.getenv('BUILD_SOURCEVERSION'),
                                            'build_id': os.getenv('BUILD_BUILDNUMBER')}
                                      )
)
# published_pipeline = pipeline.publish(name='credit-training-pipeline',
#                                       version=os.getenv('BUILD_BUILDNUMBER'),
#                                       description={'repo': os.getenv('BUILD_REPOSITORY_URI'),
#                                                    'branch': os.getenv('BUILD_SOURCEBRANCH'), 
#                                                    'commit': os.getenv('BUILD_SOURCEVERSION')})

# Output pipeline_id in specified format which will convert it to a variable in Azure DevOps
print(f'##vso[task.setvariable variable=pipeline_id]{published_pipeline.id}')