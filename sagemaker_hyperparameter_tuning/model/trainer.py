import argparse
import os

import joblib
import numpy as np
import pandas as pd
from sagemaker_training import environment
from sklearn.feature_extraction import FeatureHasher
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, log_loss

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

    # チューニング対象のハイパーパラメータ
    parser.add_argument("--penalty", type=str, choices=["l1", "l2", "elasticnet"], default="l1")
    parser.add_argument("--alpha", type=float, default=0.00001)
    parser.add_argument("--fit_intercept", type=bool, choices=[True, False], default=True)

    # data directories
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))
    parser.add_argument("--validation", type=str, default=os.environ.get("SM_CHANNEL_VALIDATION"))

    # model directory
    parser.add_argument("--model_dir", type=str, default=os.environ.get("SM_MODEL_DIR"))

    return parser.parse_known_args()


def load_dataset(path: str) -> (pd.DataFrame, np.array):
    # Take the set of files and read them all into a single pandas dataframe
    files = [os.path.join(path, file) for file in os.listdir(path) if file.endswith("csv")]

    if len(files) == 0:
        raise ValueError("Invalid # of files in dir: {}".format(path))

    raw_data = [pd.read_csv(file, sep=",") for file in files]
    data = pd.concat(raw_data)

    y = data[target]
    X = data[feature_columns]
    return X, y


def preprocess(df: pd.DataFrame):
    feature_hasher = FeatureHasher(n_features=2**24, input_type="string")
    hashed_feature = feature_hasher.fit_transform(np.asanyarray(df.astype(str)))

    return hashed_feature


def start(args):
    print("Training Start.")

    X_train, y_train = load_dataset(args.train)
    X_validation, y_validation = load_dataset(args.validation)

    y_train = np.asarray(y_train).ravel()
    X_train_hashed = preprocess(X_train)

    y_validation = np.asarray(y_validation).ravel()
    X_validation_hashed = preprocess(X_validation)

    hyperparameters = {
        "alpha": args.alpha,
        "penalty": args.penalty,
        "fit_intercept": args.fit_intercept,
        "n_jobs": args.n_jobs,
    }

    model = SGDClassifier(loss="log", random_state=42, **hyperparameters)
    print(model.__dict__)
    model.partial_fit(X_train_hashed, y_train, classes=[0, 1])

    # 最適化メトリクスを標準出力
    print("train logloss: {}".format(log_loss(y_train, model.predict_proba(X_train_hashed))))
    print("train accuracy: {}".format(accuracy_score(y_train, model.predict(X_train_hashed))))
    print("validation logloss: {}".format(log_loss(y_validation, model.predict_proba(X_validation_hashed))))
    print("validation accuracy: {}".format(accuracy_score(y_validation, model.predict(X_validation_hashed))))

    joblib.dump(model, os.path.join(args.model_dir, "model.joblib"))

    print("Training Finished.")


if __name__ == "__main__":
    args, _ = parse_args()
    start(args)
