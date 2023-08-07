import lightgbm as lgb
import memray
import numpy as np
from sklearn import datasets
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


def main():
    iris = datasets.load_iris()
    X, y = iris.data, iris.target
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    with memray.Tracker("memray-train.bin"):
        model = lgb.LGBMClassifier()
        model.fit(X_train, y_train)
        y_prob = model.predict_proba(X_test)
        y_pred = np.argmax(y_prob, axis=1)

        accuracy = accuracy_score(y_test, y_pred)
        print(f"accuracy: {accuracy}")


if __name__ == "__main__":
    main()
