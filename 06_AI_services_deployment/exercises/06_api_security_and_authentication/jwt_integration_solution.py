from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from pydantic import BaseModel

import datetime
import jwt

class RegisterItemRequest(BaseModel):
    item_id: str


def decode_jwt(current_token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    try:
        decoded_payload = jwt.decode(current_token.credentials, 'SECRET_KEY', algorithms=['HS256'])
        if decoded_payload['user_id'] < 100 or decoded_payload['user_id'] > 300:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='user_id can not register')
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='token not valid')
    return decoded_payload


def generate_jwt(user_id, time_to_expire):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=time_to_expire)
    }
    my_token = jwt.encode(payload, 'SECRET_KEY', algorithm='HS256')
    return my_token


app = FastAPI()


@app.get("/generate-token/{user_id}")
def generate_token(user_id: int):
    token = generate_jwt(user_id=user_id, time_to_expire=120)
    return token


@app.post("/register_item")
def register_item(request_param: RegisterItemRequest,
                  authorization=Depends(decode_jwt)):
    return f"Item {request_param.item_id} registrato dall'utente {authorization['user_id']}"
