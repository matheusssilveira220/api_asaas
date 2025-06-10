#%%
from dotenv import load_dotenv, find_dotenv
import os
import requests
import json

#url para buscar o cliente
url = "https://api-sandbox.asaas.com/v3/customers" 

load_dotenv(find_dotenv())

api_token = os.getenv("ASAAS_API_TOKEN")

#dados para a api
headers = {
    "accept": "application/json",
    "access_token": api_token
}

#parametros busca cliente, recomenda-se usar todos os elementos para busca, de forma que traga o cliente correto
params = {
    # nome cliente
    "name": "Sofia Jorge",   
    # email cliente
    "email": "sofiajorge@gmail.com", 
    # cnpj/cpf cliente
    "cpfCnpj": "11916228941",
    # número de elementos da lista    
    "limit": 1
}

response = requests.get(url, headers=headers, params=params)

#retorno busca do cliente
print("Status:", response.status_code)
print("Resposta JSON:")
dados = response.json()
print(json.dumps(dados, indent=2))

#confirma ou nega a busca pelo cliente (apenas para teste)
if dados.get("totalCount", 0) > 0:
    customer_id = dados["data"][0]["id"]
    print("Customer ID encontrado:", customer_id)
else:
    print("Cliente não encontrado.")


#cria a cobrança    
url_payments = "https://api-sandbox.asaas.com/v3/payments"

#parametros cobrança
payload = {
    #ID CLIENTE ASAAS
    "customer": customer_id,
    #TIPO PAGAMENTO                 
    "billingType": "BOLETO",
    #VALOR                        
    "value": 9.90,
    #DATA VENCIMENTO                                  
    "dueDate": "2025-06-15",
    #DESCRIÇÃo                       
    "description":"Teste cliente novo",
    #DIAS APÓS O VENCIMENTO QUE CANCELA O BOLETO               
    "daysAfterDueDateToRegistrationCancellation":1, 
    "discount":{ 
        #VALOR                                   
        "value": 10,    
        #DATA LIMITE                             
        "dueDateLimitDays":0, 
        #TIPO, PODENDO SER VALOR FIXO OU PORCENTAGEM (PERCENTAGE / FIXED)     FIXED POR ALGUM MOTIVO NÃO ESTÁ FUNCIONANDO               
        "type":"PERCENTAGE"                         
    },
    #JUROS APÓS O PAGAMENTO
    "interest": { "value": 1 }, 
    #ENVIO POR CORREIOS                    
    "postalService":False,                              
}

print("Status:", response.status_code)

if response.status_code = 200:
    print ("Boleto gerado!")
else:
    print("Erro")
    
dados = response.json()
print(json.dumps(dados, indent=2))
response = requests.post(url_payments, json=payload, headers=headers)


    

