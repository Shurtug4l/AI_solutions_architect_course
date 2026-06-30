import jwt
import datetime


def create_jwt(time_to_expire):
    payload = {
        "user_id": 123,
        "username": "andrea",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=time_to_expire)
    }

    my_token = jwt.encode(payload, 'SECRET_KEY', algorithm='HS256')
    return my_token


def decode_jwt(current_token: str):
    try:
        decoded_payload = jwt.decode(current_token, 'SECRET_KEY', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return 'Token has expired'
    except jwt.InvalidTokenError:
        return 'Token not valid'
    return decoded_payload


if __name__ == '__main__':
    # Create JWT
    token = create_jwt(time_to_expire=120)
    print(f"JWT: {token}")

    # Decode JWT
    decoded_jwt = decode_jwt(token)
    print(f"Decoded JWT: {decoded_jwt}")
