import os
import argparse
import joblib
import pandas as pd
from azureml.core import Run
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

from interpret.ext.blackbox import TabularExplainer
from azureml.interpret import ExplanationClient

def get_runtime_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str)
    args = parser.parse_args()
    return args

def main():
    args = get_runtime_args()

    df = pd.read_csv(os.path.join(args.data_path, 'german_credit_data.csv'))
    clf = model_train(df)

    #copying model to "outputs" directory, this will automatically upload it to Azure ML
    output_dir = './outputs/'
    os.makedirs(output_dir, exist_ok=True)
    joblib.dump(value=clf, filename=os.path.join(output_dir, 'model.pkl'))

def model_train(df):
    run = Run.get_context()

    df.drop("Sno", axis=1, inplace=True)

    y_raw = df['Risk']
    X_raw = df.drop('Risk', axis=1)

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
    print("Testing accuracy: %.3f" % test_acc)

    # Log to Azure ML
    run.log('Train accuracy', train_acc)
    run.log('Test accuracy', test_acc)
    
    # Explain model
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
    client.upload_model_explanation(global_explanation, comment='Global Explanation: All Features')

    return lr_clf

if __name__ == "__main__":
    main()
