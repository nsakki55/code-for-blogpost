from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.feature_extraction import FeatureHasher

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


def preprocess(df: pd.DataFrame):
    df["hour"] = df["hour"].map(lambda x: datetime.strptime(str(x), "%y%m%d%H"))
    df["day_of_week"] = df["hour"].map(lambda x: x.hour)

    feature_hasher = FeatureHasher(n_features=2**24, input_type="string")
    hashed_feature = feature_hasher.fit_transform(np.asanyarray(df.astype(str)))

    return hashed_feature
