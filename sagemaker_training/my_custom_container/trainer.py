import argparse
import os

import joblib
import numpy as np
import pandas as pd
from fastFM.mcmc import FMClassification
from sagemaker_training import environment
from sklearn.metrics import log_loss
from sklearn.preprocessing import OneHotEncoder

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


def parse_args():
    env = environment.Environment()

    parser = argparse.ArgumentParser()

    # hyperparameters sent by the client are passed as command-line arguments to the script
    parser.add_argument("--rank", type=int, default=9)
    parser.add_argument("--n_iter", type=int, default=12)

    # data directories
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))
    parser.add_argument("--test", type=str, default=os.environ.get("SM_CHANNEL_TEST"))

    # model directory: we will use the default set by SageMaker, /opt/ml/model
    parser.add_argument("--model_dir", type=str, default=os.environ.get("SM_MODEL_DIR"))

    return parser.parse_known_args()


def load_dataset(path: str) -> (pd.DataFrame, np.array):
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


class Preprocessor:
    def __init__(self, X_train):
        self.encoder = OneHotEncoder(handle_unknown="ignore").fit(X_train)

    def transorm(self, X):
        return self.encoder.transform(X)


def start(args):
    print("Training mode")

    X_train, y_train = load_dataset(args.train)
    X_test, y_test = load_dataset(args.test)
    y_train = np.asarray(y_train).ravel()
    y_test = np.asarray(y_test).ravel()

    preprocessor = Preprocessor(X_train)
    X_train_preprocess = preprocessor.transorm(X_train)
    X_test_preprocess = preprocessor.transorm(X_test)

    print("Training the classifier")
    model = FMClassification(rank=args.rank, n_iter=args.n_iter)

    y_pred = model.fit_predict_proba(X_train_preprocess, y_train, X_test_preprocess)

    print("fast fm log loss: ", log_loss(y_test, y_pred))

    joblib.dump(model, os.path.join(args.model_dir, "model.joblib"))


if __name__ == "__main__":

    args, _ = parse_args()

    start(args)
