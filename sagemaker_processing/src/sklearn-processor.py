import argparse
import os
import pickle
import sys
import time
from datetime import datetime
from logging import INFO, StreamHandler, getLogger
from typing import Any, Dict

import numpy as np
import pandas as pd
from sklearn.feature_extraction import FeatureHasher
from sklearn.model_selection import train_test_split

logger = getLogger(__name__)
sh = StreamHandler(sys.stdout)
sh.setLevel(INFO)
logger.addHandler(sh)

FEATURE = [
    "id",
    "event_time",
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
TARGET = "click"


def preprocess(df: pd.DataFrame):
    assert "hour" in df.columns

    df["hour"] = df["hour"].map(lambda x: datetime.strptime(str(x), "%y%m%d%H"))
    df["day_of_week"] = df["hour"].map(lambda x: x.hour)

    feature_hasher = FeatureHasher(n_features=2**24, input_type="string")
    hashed_feature = feature_hasher.fit_transform(np.asanyarray(df.astype(str)))

    return hashed_feature


def create_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    assert TARGET in df.columns

    y = df[TARGET].values
    y = np.asarray(y).ravel()
    X = df[FEATURE]
    X_hashed = preprocess(X)

    return {"feature": X_hashed, "target": y}


def save_as_pickle(path: str, data: Dict[str, Any]) -> None:
    with open(path, "wb") as p:
        pickle.dump(data, p)


def list_arg(raw_value):
    """argparse type for a list of strings"""
    return str(raw_value).split(",")


def parse_agrs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="sagemaker-processor")

    parser.add_argument(
        "--train_valid_split_percentage",
        type=float,
        default=0.8,
    )
    parser.add_argument(
        "--feature_store_offline_prefix",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--feature_group_name",
        type=str,
        default=None,
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_agrs()
    logger.info(f"args: {args}")
    
    ## 入力データ読み込み
    input_train_data_path = os.path.join("/opt/ml/processing/input", "train_partial")

    df_train = pd.read_csv(input_train_data_path)
    df_train, df_valid = train_test_split(df_train, train_size=args.train_valid_split_percentage, random_state=42)

    logger.info(f"train data: {df_train.shape}")
    logger.info(f"train data: {df_valid.shape}")

    current_time_sec = int(round(time.time()))
    df_train["event_time"] = pd.Series([current_time_sec] * len(df_train), dtype="float64")
    df_valid["event_time"] = pd.Series([current_time_sec] * len(df_valid), dtype="float64")
    
    ## データ加工
    train_data = create_dataset(df_train)
    valid_data = create_dataset(df_valid)

    ## 加工データ保存
    try:
        os.makedirs("/opt/ml/processing/output/train")
        os.makedirs("/opt/ml/processing/output/validation")
    except:
        pass

    save_as_pickle(os.path.join("/opt/ml/processing/output/train", "train_data"), train_data)
    save_as_pickle(os.path.join("/opt/ml/processing/output/validation", "valid_data"), valid_data)


