import os
import sys
import argparse
import dotenv
import joblib
import pandas as pd
from azureml.core import Run
from azureml.core import Dataset
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler

from azureml.contrib.interpret.explanation.explanation_client import ExplanationClient
from azureml.core.run import Run
from interpret.ext.blackbox import TabularExplainer


def main():

    model_name, dataset_name = getRuntimeArgs()
    dotenv.load_dotenv()

    run = Run.get_context()

    dataset = Dataset.get_by_name(workspace=run.experiment.workspace, name=dataset_name)
    credit_data_df = dataset.to_pandas_dataframe()

    clf = model_train(credit_data_df, run)

    #copying to "outputs" directory, automatically uploads it to Azure ML
    output_dir = './outputs/'
    os.makedirs(output_dir, exist_ok=True)
    joblib.dump(value=clf, filename=output_dir+model_name)

def model_train(ds_df, run):

    ds_df.drop("Sno", axis=1, inplace=True)

    y_raw = ds_df['Risk']
    X_raw = ds_df.drop('Risk', axis=1)

    categorical_features = X_raw.select_dtypes(include=['object']).columns
    numeric_features = X_raw.select_dtypes(include=['int64', 'float']).columns

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value="missing")),
        ('onehotencoder', OneHotEncoder(categories='auto', sparse=False))])

    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())])

    feature_engineering_pipeline = ColumnTransformer(
        transformers=[
            ('numeric', numeric_transformer, numeric_features),
            ('categorical', categorical_transformer, categorical_features)
        ], remainder="drop")

    # Encode Labels
    le = LabelEncoder()
    encoded_y = le.fit_transform(y_raw)

    # Train test split
    X_train, X_test, y_train, y_test = train_test_split(X_raw, encoded_y, test_size=0.20, stratify=encoded_y, random_state=42)

    # Create sklearn pipeline
    lr_clf = Pipeline(steps=[('preprocessor', feature_engineering_pipeline),
                             ('classifier', LogisticRegression(solver="lbfgs"))])
    # Train the model
    lr_clf.fit(X_train, y_train)

    # Capture metrics
    train_acc = lr_clf.score(X_train, y_train)
    test_acc = lr_clf.score(X_test, y_test)
    print("Training accuracy: %.3f" % train_acc)
    print("Test data accuracy: %.3f" % test_acc)

    # Log to Azure ML
    run.log('Train accuracy', train_acc)
    run.log('Test accuracy', test_acc)
    
    # Explain model
    client = ExplanationClient.from_run(run)

    explainer = TabularExplainer(lr_clf.steps[-1][1], 
                                 initialization_examples=X_train, 
                                 features=X_raw.columns, 
                                 classes=["Good", "Bad"], 
                                 transformations=feature_engineering_pipeline)

    # explain overall model predictions (global explanation)
    global_explanation = explainer.explain_global(X_test)

    # Sorted SHAP values
    print('ranked global importance values: {}'.format(global_explanation.get_ranked_global_values()))
    # Corresponding feature names
    print('ranked global importance names: {}'.format(global_explanation.get_ranked_global_names()))
    # Feature ranks (based on original order of features)
    print('global importance rank: {}'.format(global_explanation.global_importance_rank))
    
    client = ExplanationClient.from_run(run)
    client.upload_model_explanation(global_explanation, comment='global explanation: all features')

    return lr_clf

def getRuntimeArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--MODEL_NAME', type=str)
    parser.add_argument('--DATASET_NAME', type=str)
    args = parser.parse_args()
    return args.MODEL_NAME, args.DATASET_NAME

if __name__ == "__main__":
    main()
