import json
import os
import numpy as np
import pandas as pd
import joblib
from inference_schema.schema_decorators import input_schema, output_schema
from inference_schema.parameter_types.standard_py_parameter_type import StandardPythonParameterType

def init():
    global model
    model_dir = os.getenv('AZUREML_MODEL_DIR')
    model_path = os.path.join(model_dir, 'credit-prediction.pkl')
    model = joblib.load(model_path)

# Automatically generate the swagger interface by providing an data example
input_sample = [{
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
output_sample = [[0.7, 0.3]]

@input_schema('data', StandardPythonParameterType(input_sample))
@output_schema(StandardPythonParameterType(output_sample))
def run(raw_data):
    try:
        df = pd.DataFrame(raw_data)
        proba = model.predict_proba(df)
        
        result = {"predict_proba": proba.tolist()}
        return result
    except Exception as e:
        error = str(e)
        return error
