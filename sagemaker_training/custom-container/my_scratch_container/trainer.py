from __future__ import absolute_import

import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
from fastFM.mcmc import FMClassification
from sklearn.metrics import log_loss
from sklearn.preprocessing import OneHotEncoder

hyperparameters_file_path = "/opt/ml/input/config/hyperparameters.json"
inputdataconfig_file_path = "/opt/ml/input/config/inputdataconfig.json"
resource_file_path = "/opt/ml/input/config/resourceconfig.json"
data_files_path = "/opt/ml/input/data/"
failure_file_path = "/opt/ml/output/failure"
model_artifacts_path = "/opt/ml/model/"

training_job_name_env = "TRAINING_JOB_NAME"
training_job_arn_env = "TRAINING_JOB_ARN"


def load_json_object(json_file_path):
    with open(json_file_path) as json_file:
        return json.load(json_file)


def write_failure_file(failure_file_path, failure_reason):
    failure_file = open(failure_file_path, "w")
    failure_file.write(failure_reason)
    failure_file.close()


feature_columns = [
    "id",
    "click",
    "hour",
    "C1",
    "banner_pos",
    "site_id",
    "site_domain",
    "site_category",
    "app_id",
    "app_domain",
    "app_category",
    "device_id",
    "device_ip",
    "device_model",
    "device_type",
    "device_conn_type",
    "C14",
    "C15",
    "C16",
    "C17",
    "C18",
    "C19",
    "C20",
    "C21",
]

target = "click"


def load_dataset(path: str) -> (pd.DataFrame, np.array):
    """
    Load entire dataset.
    """
    # Take the set of files and read them all into a single pandas dataframe
    files = [os.path.join(path, file) for file in os.listdir(path) if file.endswith("csv")]

    if len(files) == 0:
        raise ValueError("Invalid # of files in dir: {}".format(path))

    raw_data = [pd.read_csv(file, sep=",") for file in files]
    data = pd.concat(raw_data)

    # # labels are in the first column
    y = data[target]
    X = data[feature_columns]
    return X, y


def print_files_in_path(path):
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            files.append(os.path.join(r, file))

    for f in files:
        print(f)
    return files


class Preprocessor:
    def __init__(self, X_train):
        self.encoder = OneHotEncoder(handle_unknown="ignore").fit(X_train)

    def transorm(self, X):
        return self.encoder.transform(X)


def train():
    try:
        print("\nRunning training...")

        if os.path.exists(hyperparameters_file_path):
            hyperparameters = load_json_object(hyperparameters_file_path)
            print(hyperparameters)
            print(f"Hyperparameters configuration:{hyperparameters}")

        if os.path.exists(inputdataconfig_file_path):
            input_data_config = load_json_object(inputdataconfig_file_path)
            print(f"Input data configuration:{input_data_config}")

            for key in input_data_config:
                print("\nList of files in {0} channel: ".format(key))
                channel_path = data_files_path + key + "/"
                print_files_in_path(channel_path)

        if os.path.exists(resource_file_path):
            resource_config = load_json_object(resource_file_path)
            print(f"Resource configuration:{resource_config}")

        if training_job_name_env in os.environ:
            print(f"Training job name: {os.environ[training_job_name_env]}")

        if training_job_arn_env in os.environ:
            print(f"Training job ARN: {os.environ[training_job_arn_env]}")

        X_train, y_train = load_dataset(os.path.join(data_files_path, "train"))
        X_test, y_test = load_dataset(os.path.join(data_files_path, "test"))

        y_train = np.asarray(y_train).ravel()
        y_test = np.asarray(y_test).ravel()

        preprocessor = Preprocessor(X_train)
        X_train_preprocess = preprocessor.transorm(X_train)
        X_test_preprocess = preprocessor.transorm(X_test)

        hyperparameters = {key: int(value) for key, value in hyperparameters.items()}
        print("Training start")

        print("Training the classifier")
        model = FMClassification(rank=hyperparameters["rank"], n_iter=hyperparameters["n_iter"])

        y_pred = model.fit_predict_proba(X_train_preprocess, y_train, X_test_preprocess)

        print("fast fm log loss: ", log_loss(y_test, y_pred))

        # Save state here.
        joblib.dump(model, os.path.join(model_artifacts_path, "model.joblib"))
        print("Training completed!")

        sys.exit(0)

    except Exception as e:
        write_failure_file(failure_file_path, str(e))
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if sys.argv[1] == "train":
        train()
    else:
        print("Missing required argument 'train'.", file=sys.stderr)
        sys.exit(1)
