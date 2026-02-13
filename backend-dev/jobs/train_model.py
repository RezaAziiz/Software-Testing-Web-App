
from fastapi import APIRouter, Response, Request, UploadFile, Depends, BackgroundTasks

from decouple import config
import requests

url = config('API_FR')
api_key = config('API_KEY_FR')

def run_train_model() :
    print("running train model job")

    headers = {
        'X-Api-Key' : api_key
    }
    response = requests.request("POST", url + "/train_model", headers=headers)
    response_data = eval(response.text)

    print(response_data)
    print("end running train model job")
    
    return response_data