import argparse
import os
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sagemaker_training import environment
from sklearn.feature_extraction import FeatureHasher
from sklearn.linear_model import SGDClassifier

feature_columns = [
    "id",
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
    parser.add_argument("--alpha", type=float, default=0.00001)
    parser.add_argument("--n-jobs", type=int, default=env.num_cpus)
    parser.add_argument("--eta0", type=float, default=2.0)

    ## hyperparameters laoded from envrionment varibale
    # parser.add_argument("--alpha", type=float, default=float(os.environ['SM_HP_ALPHA']))
    # parser.add_argument("--n-jobs", type=int, default=env.num_cpus)
    # parser.add_argument("--eta0", type=float, default=float(os.environ['SM_HP_ETA0']))

    # data directories
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))
    parser.add_argument("--test", type=str, default=os.environ.get("SM_CHANNEL_TEST"))

    # model directory: we will use the default set by SageMaker, /opt/ml/model
    parser.add_argument("--model_dir", type=str, default=os.environ.get("SM_MODEL_DIR"))

    return parser.parse_known_args()


def load_dataset(path: str) -> (pd.DataFrame, np.array):
    # Take the set of files and read them all into a single pandas dataframe
    files = [
        os.path.join(path, file) for file in os.listdir(path) if file.endswith("csv")
    ]

    if len(files) == 0:
        raise ValueError("Invalid # of files in dir: {}".format(path))

    raw_data = [pd.read_csv(file, sep=",") for file in files]
    data = pd.concat(raw_data)

    y = data[target]
    X = data[feature_columns]
    return X, y


def preprocess(df: pd.DataFrame):
    df["hour"] = df["hour"].map(lambda x: datetime.strptime(str(x), "%y%m%d%H"))
    df["day_of_week"] = df["hour"].map(lambda x: x.hour)

    feature_hasher = FeatureHasher(n_features=2**24, input_type="string")
    hashed_feature = feature_hasher.fit_transform(np.asanyarray(df.astype(str)))

    return hashed_feature


def main(args) -> None:
    print("Training mode")

    X_train, y_train = load_dataset(args.train)
    X_test, y_test = load_dataset(args.test)

    y_train = np.asarray(y_train).ravel()
    X_train_hashed = preprocess(X_train)

    y_test = np.asarray(y_test).ravel()
    X_test_hashed = preprocess(X_test)

    hyperparameters = {
        "alpha": args.alpha,
        "n_jobs": args.n_jobs,
        "eta0": args.eta0,
    }
    print("Training the classifier")
    model = SGDClassifier(loss="log", penalty="l2", random_state=42, **hyperparameters)

    model.partial_fit(X_train_hashed, y_train, classes=[0, 1])

    print("Score: {}".format(model.score(X_test_hashed, y_test)))
    joblib.dump(model, os.path.join(args.model_dir, "model.joblib"))


if __name__ == "__main__":

    args, _ = parse_args()

    main(args)
