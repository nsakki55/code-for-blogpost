import os
from io import StringIO
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction import FeatureHasher


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


def preprocess(df: pd.DataFrame):
    feature_hasher = FeatureHasher(n_features=2**24, input_type="string")
    hashed_feature = feature_hasher.fit_transform(np.asanyarray(df[[idx for idx in feature_names.keys()]].astype(str)))
    return hashed_feature


# Model serving
def model_fn(model_dir):
    """
    Deserialize fitted model
    """
    model = joblib.load(os.path.join(model_dir, "model.joblib"))
    return model


def input_fn(request_body, request_content_type):
    """
    request_body: The body of the request sent to the model.
    request_content_type: (string) specifies the format/variable type of the request
    """
    if request_content_type == "text/csv":
        # Read the raw input data as CSV.
        df_input = pd.read_csv(StringIO(request_body), header=None)
        input_data_hashed = preprocess(df_input)
        return input_data_hashed
    else:
        raise ValueError("This model only supports text/csv input")


def predict_fn(input_data, model):
    """
    input_data: returned array from input_fn above
    model (sklearn model) returned model loaded from model_fn above
    """

    return model.predict_proba(input_data)


# def output_fn(prediction, content_type):
#     """
#     prediction: the returned value from predict_fn above
#     content_type: the content type the endpoint expects to be returned. Ex: JSON, string
#     """

#     response = {"probability": prediction[0][1]} 
#     return json.dumps(response)
