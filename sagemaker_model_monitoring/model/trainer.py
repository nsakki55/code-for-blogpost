import argparse
import os

import joblib
import numpy as np
import pandas as pd
from sagemaker_training import environment
from sklearn.feature_extraction import FeatureHasher
from sklearn.linear_model import SGDClassifier

feature_names = {
    0: "id",
    1: "hour",
    2: "C1",
    3: "banner_pos",
    4: "site_id",
    5: "site_domain",
    6: "site_category",
    7: "app_id",
    8: "app_domain",
    9: "app_category",
    10: "device_id",
    11: "device_ip",
    12: "device_model",
    13: "device_type",
    14: "device_conn_type",
    15: "C14",
    16: "C15",
    17: "C16",
    18: "C17",
    19: "C18",
    20: "C19",
    21: "C20",
    22: "C21"
}


target = "click"


def parse_args():
    env = environment.Environment()

    parser = argparse.ArgumentParser()

    # hyperparameters sent by the client are passed as command-line arguments to the script
    parser.add_argument("--alpha", type=float, default=0.00001)
    parser.add_argument("--n-jobs", type=int, default=env.num_cpus)
    parser.add_argument("--eta0", type=float, default=2.0)

    # data directories
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))

    # model directory: we will use the default set by SageMaker, /opt/ml/model
    parser.add_argument("--model_dir", type=str, default=os.environ.get("SM_MODEL_DIR"))

    return parser.parse_known_args()


def load_dataset(path):
    # Take the set of files and read them all into a single pandas dataframe
    files = [os.path.join(path, file) for file in os.listdir(path) if file.endswith("csv")]

    if len(files) == 0:
        raise ValueError("Invalid # of files in dir: {}".format(path))

    raw_data = [pd.read_csv(file, sep=",") for file in files]
    data = pd.concat(raw_data)

    y = data[target]
    X = data.drop(target, axis=1)
    return X, y


def preprocess(df):
    feature_hasher = FeatureHasher(n_features=2**24, input_type="string")
    hashed_feature = feature_hasher.fit_transform(np.asanyarray(df[[col for col in feature_names.values()]].astype(str)))
    return hashed_feature


def main(args):
    print("Training mode")

    X_train, y_train = load_dataset(args.train)

    y_train = np.asarray(y_train).ravel()
    X_train_hashed = preprocess(X_train)

    hyperparameters = {
        "alpha": args.alpha,
        "n_jobs": args.n_jobs,
        "eta0": args.eta0,
    }
    print("Training the classifier")
    model = SGDClassifier(loss="log", penalty="l2", random_state=42, **hyperparameters)

    model.partial_fit(X_train_hashed, y_train, classes=[0, 1])

    joblib.dump(model, os.path.join(args.model_dir, "model.joblib"))


if __name__ == "__main__":

    args, _ = parse_args()

    main(args)
