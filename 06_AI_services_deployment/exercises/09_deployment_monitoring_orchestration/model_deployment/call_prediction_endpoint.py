from typing import Dict, List
import io
from typing_extensions import Annotated

from fastapi import FastAPI, Query, UploadFile
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


@app.get("/predict_file")
def predict_file(input_file: UploadFile) -> List[PredictionOutput]:
    records = input_file.file.read()
    file_stream = io.BytesIO(records)
    pred_data = np.genfromtxt(file_stream, delimiter=",", skip_header=1)

    predicted_proba = model.predict_proba(pred_data)
    predicted_cls = model.predict(pred_data)

    output = []
    for index, pred_proba_row in enumerate(predicted_proba):
        predict_cls_row = predicted_cls[index]

        predicted_proba_dict = {target_names[i]: pred_proba_row[i] for i in range(len(pred_proba_row))}
        predcited_cls_name = target_names[predict_cls_row]

        current_output = PredictionOutput(predicted_probability=predicted_proba_dict,
                                          predicted_cls=predcited_cls_name)

        output.append(current_output)
    return output


if __name__ == '__main__':
    uvicorn.run("lesson_8_5:app")