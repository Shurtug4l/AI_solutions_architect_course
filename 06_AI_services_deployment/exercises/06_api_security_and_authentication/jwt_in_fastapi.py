from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import datetime
import jwt

app = FastAPI()


def create_jwt(time_to_expire):
    payload = {
        "user_id": 123,
        "username": "andrea",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=time_to_expire)
    }

    my_token = jwt.encode(payload, 'SECRET_KEY', algorithm='HS256')
    return my_token


def decode_jwt(current_token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    try:
        decoded_payload = jwt.decode(current_token.credentials, 'SECRET_KEY', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not valid')
    return decoded_payload


@app.get("/generate-token")
def generate_token():
    token = create_jwt(120)
    return {"access_token": token}


@app.get("/protected")
def protected_function(authorization=Depends(decode_jwt)):
    return {"message": "ciao, sei autorizzato per questo endpoint"}
