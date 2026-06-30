from typing_extensions import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
import uvicorn

import numpy as np
import pickle

from sklearn.datasets import load_wine


wine_data = load_wine()
target_names = wine_data.target_names

path_model = 'wine_model_rf.pkl'


with open(path_model, 'rb') as file:
    model = pickle.load(file)


class PredictParams(BaseModel):
    model_config = {"extra": "forbid"}

    alcohol: float = Field(..., description='xxxx')
    malic_acid: float
    ash: float
    alcalinity_of_ash: float
    magnesium: float
    total_phenols: float
    flavanoids: float
    nonflavanoid_phenols: float
    proanthocyanins: float
    color_intensity: float
    hue: float
    od280_od315_of_diluted_wines: float
    proline: float


class PredictionOutput(BaseModel):
    predicted_probability: float = Field(..., description='Predicted prob')
    predicted_cls: str = Field(...)


app = FastAPI()


@app.get("/predict_single_row")
def predict_single_record(param_query: Annotated[PredictParams, Query()]) -> PredictionOutput:
    current_record = np.array([param_query.alcohol,
                               param_query.malic_acid,
                               param_query.ash,
                               param_query.alcalinity_of_ash,
                               param_query.magnesium,
                               param_query.total_phenols,
                               param_query.flavanoids,
                               param_query.nonflavanoid_phenols,
                               param_query.proanthocyanins,
                               param_query.color_intensity,
                               param_query.hue,
                               param_query.od280_od315_of_diluted_wines,
                               param_query.proline])
    record_reshape = current_record.reshape(1, -1)

    predicted_proba = model.predict_proba(record_reshape)[0]
    predicted_cls = model.predict(record_reshape)[0]

    predicted_proba_dict = {target_names[i]: predicted_proba[i] for i in range(len(predicted_proba))}
    predcited_cls_name = target_names[predicted_cls]
    return PredictionOutput(predicted_probability=predicted_proba_dict[predcited_cls_name],
                            predicted_cls=predcited_cls_name)


if __name__ == '__main__':
    uvicorn.run("prediction_main:app")