from typing import Dict
from typing_extensions import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
import uvicorn

import numpy as np
import pickle

from sklearn.datasets import load_iris


iris_data = load_iris()
target_names = iris_data.target_names

path_model = 'iris_model_rf.pkl'

with open(path_model, 'rb') as file:
    model = pickle.load(file)


class PredictParams(BaseModel):
    model_config = {"extra": "forbid"}

    petal_len: float = Field(..., gt=0)
    petal_width: float = Field(..., gt=0)
    sepal_len: float = Field(..., gt=0)
    sepal_width: float = Field(..., gt=0)


class PredictionOutput(BaseModel):
    predicted_probability: Dict[str, float] = Field(..., description='Predicted prob')
    predicted_cls: str = Field(...)


app = FastAPI()


@app.get("/predict_single_record")
def predict_single_record(param_query: Annotated[PredictParams, Query()]) -> PredictionOutput:
    current_record = np.array([param_query.sepal_len,
                               param_query.sepal_width,
                               param_query.petal_len,
                               param_query.petal_width])
    record_reshape = current_record.reshape(1, -1)

    predicted_proba = model.predict_proba(record_reshape)[0]
    predicted_cls = model.predict(record_reshape)[0]

    predicted_proba_dict = {target_names[i]: predicted_proba[i] for i in range(len(predicted_proba))}
    predcited_cls_name = target_names[predicted_cls]
    return PredictionOutput(predicted_probability=predicted_proba_dict,
                            predicted_cls=predcited_cls_name)


if __name__ == '__main__':
    uvicorn.run("lesson_8_4:app")
