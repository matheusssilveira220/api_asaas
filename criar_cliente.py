#%%
from dotenv import load_dotenv, find_dotenv
import os
import requests

url = "https://api-sandbox.asaas.com/v3/customers"

load_dotenv(find_dotenv())

api_token = os.getenv("ASAAS_API_TOKEN")

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "access_token":api_token
    }

payload = {
    "name": "Sofia Jorge",
    "cpfCnpj": "",
    "email": "sofiajorge@gmail.com",
    "phone": "4738010919",
    "mobilePhone": "4799376637",
    "address": "Av. Paulista",
    "addressNumber": "150",
    "complement": "Sala 201",
    "province": "Centro",
    "postalCode": "01310-000",
    "externalReference": "12987382",
    "notificationDisabled": False,
    "additionalEmails": "john.doe@asaas.com,john.doe.silva@asaas.com.br",
    "municipalInscription": "46683695908",
    "stateInscription": "646681195275",
    "observations": "ótimo pagador, nenhum problema até o momento",
    "groupName": None,
    "company": None,
    "foreignCustomer": False
}


response = requests.post(url, json=payload, headers=headers)

print(response.text)
