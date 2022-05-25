import argparse
import os

import joblib
import numpy as np
import pandas as pd
from my_custom_library import feature_columns, preprocess, target
from sagemaker_training import environment
from sklearn.linear_model import SGDClassifier


def parse_args():
    """
    Parse arguments.
    """
    env = environment.Environment()

    parser = argparse.ArgumentParser()

    # hyperparameters sent by the client are passed as command-line arguments to the script
    parser.add_argument("--alpha", type=float, default=0.00001)
    parser.add_argument("--n-jobs", type=int, default=env.num_cpus)
    parser.add_argument("--eta0", type=float, default=2.0)

    # data directories
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))
    parser.add_argument("--test", type=str, default=os.environ.get("SM_CHANNEL_TEST"))

    # model directory: we will use the default set by SageMaker, /opt/ml/model
    parser.add_argument("--model_dir", type=str, default=os.environ.get("SM_MODEL_DIR"))

    return parser.parse_known_args()


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


def main(args):
    """
    Train a CTR Prediction
    """
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


def model_fn(model_dir):
    """
    Deserialized and return fitted model
    Note that this should have the same name as the serialized model in the main method
    """
    clf = joblib.load(os.path.join(model_dir, "model.joblib"))
    return clf


if __name__ == "__main__":

    args, _ = parse_args()

    main(args)
