from decouple import config
import requests

url = config('API_FR')
api_key = config('API_KEY_FR')

def compare_image(idcard, faceimage):
    # read image file
    files = {"image": open(idcard, 'rb'), "train_image": open(faceimage, 'rb')}        
    # send image 
    headers = {
        'X-Api-Key' : api_key
    }
    response = requests.request("POST", url + "/face-recognition", headers=headers, files=files)        
    return response.json()

def check_face(faceimage):
    # read image file
    files = {"image": open(faceimage, 'rb')}        

    # send image 
    headers = {
        'X-Api-Key' : api_key
    }
    response = requests.request("POST", url + "/check-face", headers=headers, files=files)
    return response

def recognize_face(faceimage):
    # read image file
    files = {"image": open(faceimage, 'rb')}        

    # send image 
    headers = {
        'X-Api-Key' : api_key
    }
    response = requests.request("POST", url + "/face-recognize", headers=headers, files=files)
    return response

def add_data_training(label, faceimage):
    # set params
    params = {"label": label}
            
    # read image file
    files = {"train_image": open(faceimage, 'rb')}        
    # send image 
    headers = {
        'X-Api-Key' : api_key
    }
    response = requests.request("POST", url + "/add-data-training", params=params, headers=headers, files=files)        
    return response