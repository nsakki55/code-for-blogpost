from typing import Tuple

import lightgbm as lgb
import numpy as np
from sklearn import datasets
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


def load_dataset() -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    iris = datasets.load_iris()
    X, y = iris.data, iris.target
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    return X_train, X_test, y_train, y_test


def train(X_train: np.ndarray, y_train: np.ndarray) -> lgb.LGBMClassifier:
    model = lgb.LGBMClassifier()
    model.fit(X_train, y_train)

    return model


def validate(model: lgb.LGBMClassifier, X_test: np.ndarray, y_test: np.ndarray) -> None:
    y_prob = model.predict_proba(X_test)
    y_pred = np.argmax(y_prob, axis=1)

    accuracy = accuracy_score(y_test, y_pred)
    print(f"accuracy: {accuracy}")


def main() -> None:
    X_train, X_test, y_train, y_test = load_dataset()
    model = train(X_train, y_train)
    validate(model, X_test, y_test)


if __name__ == "__main__":
    main()
