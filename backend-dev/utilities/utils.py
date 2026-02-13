from passlib.hash import md5_crypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from decouple import config
from fastapi import Request
import os
import random


def get_hashed_password(password: str) -> str:
    return md5_crypt.hash(password)


def verify_password(plain_password: str, hash_password: str) -> bool:
    return md5_crypt.verify(plain_password, hash_password)


def encode_jwt(data_to_encode: object) -> str:
    expires_delta = timedelta(minutes=int(
        config('ACCESS_TOKEN_EXPIRE_MINUTES')))
    if expires_delta:  # check expired token
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    data_to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(data_to_encode, config(
        'SECRET_KEY'), algorithm=config('ALGORITHM'))
    return encoded_jwt

def encode_refresh_jwt(data_to_encode: object, access_token: str) -> str:
    expires_delta = timedelta(minutes=int(
        config('REFRESH_TOKEN_EXPIRE_MINUTES')))
    if expires_delta:  # check expired token
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    data_to_encode.update({"exp": expire})

    try:
        payload = decode_jwt(access_token)
        data_to_encode.update({"access_exp": payload['exp']})

        encoded_jwt = jwt.encode(data_to_encode, config(
            'SECRET_KEY'), algorithm=config('ALGORITHM'))
        return encoded_jwt
    except:
        pass

def decode_jwt(token: str, options = None) -> object:
    decoded_jwt = jwt.decode(token, config(
        'SECRET_KEY'), options=options, algorithms=[config('ALGORITHM')])
    return decoded_jwt

def refresh_jwt(access_token: str, refresh_token: str) -> (str, str):
    isTokenValid: bool = False
    isRefreshTokenValid: bool = False

    options = {
        'verify_iat': False,
        'verify_exp': False,
        'verify_nbf': False,
    }

    try:
        access_payload = decode_jwt(access_token, options) # validity check access token
        refresh_payload = decode_jwt(refresh_token) # validity + expiry check refresh token
    except:
        access_payload = None
        refresh_payload = None
    if access_payload and refresh_payload:
        isTokenValid = True

    if isTokenValid and ('access_exp' in refresh_payload):
        refresh_payload.update({'exp': refresh_payload['access_exp']})
        refresh_payload.pop('access_exp')

        isRefreshTokenValid = access_payload == refresh_payload
    
    if isRefreshTokenValid:
        new_access_token = encode_jwt(access_payload)
        new_refresh_token = encode_refresh_jwt(access_payload, new_access_token)
        return (new_access_token, new_refresh_token)

def getDataFromJwt(request: Request):
    # for attribute, value in request.__dict__.items():
    #     print(attribute, value)
    #     print('------------------------------')
    # print(dir(request))
    token = request.headers["Authorization"]
    return decode_jwt(token[7:])


def check_folder(foldername: str):
    if not os.path.exists(foldername):
        os.makedirs(foldername)


def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)


def generateToken():
    token = ''
    for index in range(5):
        token += str(random.randint(0, 9))
    return token

def dataTypeValidation(dataType:str, value:str, parameter_name:str):
    if dataType == "int":
        try:
            temp = int(value)
        except:
            return {"status": False, "message":"Parameter dengan nama \""+parameter_name+"\" Seharusnya berisi nilai int"}
    elif dataType == "float":
        try:
            temp = float(value)
        except:
            return {"status": False, "message":"Parameter dengan nama \""+parameter_name+"\" Seharusnya berisi nilai float"}
    
    elif dataType == "boolean":
        val = value.lower()
        if val not in ('1', '0', 'true', 'false'):
            return {"status": False, "message":"Parameter dengan nama \""+parameter_name+"\" Seharusnya berisi nilai boolean"}
    
    return {"status": True,
            "message":""}