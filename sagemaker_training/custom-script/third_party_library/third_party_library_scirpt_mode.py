import argparse
import os
from datetime import datetime

import joblib
import numpy as np
import optuna
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
    parser.add_argument("--max_alpha", type=float, default=0.1)
    parser.add_argument("--n-jobs", type=int, default=env.num_cpus)

    # data directories
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))
    parser.add_argument(
        "--validation", type=str, default=os.environ.get("SM_CHANNEL_VALIDATION")
    )
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
    X_validation, y_validation = load_dataset(args.validation)
    X_test, y_test = load_dataset(args.test)

    y_train = np.asarray(y_train).ravel()
    X_train_hashed = preprocess(X_train)

    y_validation = np.asarray(y_validation).ravel()
    X_validation_hashed = preprocess(X_validation)

    y_test = np.asarray(y_test).ravel()
    X_test_hashed = preprocess(X_test)

    def objective(trial):
        alpha = trial.suggest_uniform("alpha", 0, args.max_alpha)
        model = SGDClassifier(loss="log", penalty="l2", random_state=42, alpha=alpha)

        model.partial_fit(X_train_hashed, y_train, classes=[0, 1])
        score = model.score(X_validation_hashed, y_validation)

        print("x: %1.3f, score: %1.3f" % (alpha, score))
        return score

    print("Training the classifier")
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=100)

    best_params = study.best_params
    print("best param: {}".format(best_params))

    best_model = SGDClassifier(
        loss="log", penalty="l2", random_state=42, alpha=best_params["alpha"]
    )
    best_model.partial_fit(X_train_hashed, y_train, classes=[0, 1])

    print("Score: {}".format(best_model.score(X_test_hashed, y_test)))

    joblib.dump(best_model, os.path.join(args.model_dir, "model.joblib"))


if __name__ == "__main__":

    args, _ = parse_args()

    main(args)
