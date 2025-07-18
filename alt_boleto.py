from dotenv import load_dotenv, find_dotenv
import os
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import re

load_dotenv(find_dotenv())
api_token = os.getenv("ASAAS_API_TOKEN")

headers = {
    "accept": "application/json",
    "access_token": api_token
}

def limpar_cpf_cnpj(documento):
    """Remove caracteres especiais do CPF/CNPJ"""
    return re.sub(r'[^\d]', '', documento)

def buscar_cliente_por_nome(nome):
    """Busca cliente por nome"""
    url_clientes = "https://api-sandbox.asaas.com/v3/customers"
    params = {
        "name": nome,
        "limit": 100
    }
    
    response = requests.get(url_clientes, headers=headers, params=params)
    return response.json()

def buscar_cliente_por_documento(documento):
    """Busca cliente por CPF/CNPJ"""
    url_clientes = "https://api-sandbox.asaas.com/v3/customers"
    params = {
        "cpfCnpj": documento,
        "limit": 100
    }
    
    response = requests.get(url_clientes, headers=headers, params=params)
    return response.json()

def buscar_cliente_combinado(nome, documento):
    """Busca cliente combinando nome e documento"""
    documento_limpo = limpar_cpf_cnpj(documento)
    
    print(f"Buscando por documento: {documento_limpo}")
    dados_doc = buscar_cliente_por_documento(documento_limpo)
    
    if dados_doc.get("totalCount", 0) > 0:
        print(f"Cliente encontrado por documento!")
        return dados_doc
    
    print(f"Documento não encontrado. Buscando por nome: {nome}")
    dados_nome = buscar_cliente_por_nome(nome)
    
    if dados_nome.get("totalCount", 0) > 0:
        print(f"Cliente encontrado por nome!")
    
        for cliente in dados_nome["data"]:
            cliente_doc = limpar_cpf_cnpj(cliente.get("cpfCnpj", ""))
            if cliente_doc == documento_limpo:
                print(f"Confirmado: Cliente com nome '{nome}' e documento '{documento_limpo}'")
                return {"data": [cliente], "totalCount": 1}
        
        print(f"Encontrados {dados_nome['totalCount']} clientes com nome similar.")
        print("Clientes encontrados:")
        for i, cliente in enumerate(dados_nome["data"]):
            doc_cliente = cliente.get("cpfCnpj", "N/A")
            print(f"{i+1}. {cliente['name']} - {doc_cliente}")
        
        return dados_nome
    
    return {"data": [], "totalCount": 0}

nome = input("Nome: ").strip()
documento = input("CNPJ/CPF: ").strip()

if not nome and not documento:
    print("Erro: Informe pelo menos o nome ou o CPF/CNPJ")
    exit()

if nome and documento:
    dados = buscar_cliente_combinado(nome, documento)
elif documento:
    documento_limpo = limpar_cpf_cnpj(documento)
    dados = buscar_cliente_por_documento(documento_limpo)
else:
    dados = buscar_cliente_por_nome(nome)

if dados.get("totalCount", 0) == 0:
    print("Cliente não encontrado.")
    print("Dicas:")
    print("- Verifique se o CPF/CNPJ está correto")
    print("- Tente buscar apenas por nome")
    print("- Verifique se o cliente existe no ambiente sandbox")
    exit()

# Se houver múltiplos resultados, permite escolher
if dados.get("totalCount", 0) > 1:
    print(f"\n{dados['totalCount']} clientes encontrados:")
    for i, cliente in enumerate(dados["data"]):
        doc_cliente = cliente.get("cpfCnpj", "N/A")
        print(f"{i+1}. {cliente['name']} - {doc_cliente}")
    
    while True:
        try:
            escolha = int(input("\nEscolha o número do cliente: ")) - 1
            if 0 <= escolha < len(dados["data"]):
                customer_id = dados["data"][escolha]["id"]
                cliente_escolhido = dados["data"][escolha]
                print(f"Cliente selecionado: {cliente_escolhido['name']} - {cliente_escolhido.get('cpfCnpj', 'N/A')}")
                break
            else:
                print("Número inválido. Tente novamente.")
        except ValueError:
            print("Digite um número válido.")
else:
    customer_id = dados["data"][0]["id"]
    cliente_escolhido = dados["data"][0]
    print(f"✓ Cliente encontrado: {cliente_escolhido['name']} - {cliente_escolhido.get('cpfCnpj', 'N/A')}")

# Busca dos boletos
print(f"\nBuscando boletos para o cliente ID: {customer_id}")
url_cobrancas = f"https://api-sandbox.asaas.com/v3/payments?customer={customer_id}"
response = requests.get(url_cobrancas, headers=headers)

if response.status_code != 200:
    print(f"❌ Erro ao buscar boletos: {response.status_code}")
    print(response.text)
    exit()

boletos = response.json()["data"]

if not boletos:
    print("❌ Nenhum boleto encontrado para este cliente.")
    exit()

df_boletos = pd.DataFrame(boletos)

colunas_exibir = ["id", "value", "dueDate", "status"]

status_permitidos = ["OVERDUE", "PENDING"]
df_boletos_filtrados = df_boletos[df_boletos['status'].isin(status_permitidos)]

if df_boletos_filtrados.empty:
    print("❌ Nenhum boleto vencido ou em aberto encontrado.")
    print("Apenas boletos com status 'OVERDUE' ou 'PENDING' podem ser alterados.")
    print(f"\nTodos os boletos encontrados ({len(df_boletos)}):")
    print(df_boletos[colunas_exibir])
    exit()

print(f"\n✓ Boletos encontrados (apenas vencidos ou em aberto - {len(df_boletos_filtrados)} de {len(df_boletos)}):")

# Exibir boletos com numeração para seleção
boletos_lista = df_boletos_filtrados.to_dict('records')
for i, boleto in enumerate(boletos_lista):
    print(f"{i+1}. ID: {boleto['id']} | Valor: R$ {boleto['value']:.2f} | Vencimento: {boleto['dueDate']} | Status: {boleto['status']}")

# Seleção do boleto
if len(boletos_lista) == 1:
    boleto_selecionado = boletos_lista[0]
    payment_id = boleto_selecionado['id']
    print(f"\n✓ Boleto selecionado automaticamente: {payment_id}")
else:
    while True:
        try:
            escolha = int(input(f"\nEscolha o número do boleto (1-{len(boletos_lista)}): ")) - 1
            if 0 <= escolha < len(boletos_lista):
                boleto_selecionado = boletos_lista[escolha]
                payment_id = boleto_selecionado['id']
                print(f"✓ Boleto selecionado: {payment_id} - R$ {boleto_selecionado['value']:.2f}")
                break
            else:
                print("❌ Número inválido. Tente novamente.")
        except ValueError:
            print("❌ Digite um número válido.")

print("✓ Boleto encontrado!")

data_vencimento_original = boleto_selecionado['dueDate']

print(f"Data de vencimento atual: {data_vencimento_original}")

def validar_data_vencimento(nova_data_str, data_original_str):
    try:
        nova_data = datetime.strptime(nova_data_str, "%Y-%m-%d")
        data_original = datetime.strptime(data_original_str, "%Y-%m-%d")

        data_maxima = data_original + timedelta(days=5)

        if nova_data > data_maxima:
            return False, f"Erro: A data não pode ser superior a {data_maxima.strftime('%Y-%m-%d')} (5 dias a partir da data original {data_original_str})"

        if nova_data < data_original:
            return False, f"Erro: A data não pode ser anterior à data original ({data_original_str})"
        
        return True, "Data válida"
        
    except ValueError:
        return False, "Erro: Formato de data inválido. Use YYYY-MM-DD"

while True:
    nova_data_input = input("Nova data de vencimento (YYYY-MM-DD) (Podendo incluir apenas +5 dias a partir da data original): ").strip()
    
    valida, mensagem = validar_data_vencimento(nova_data_input, data_vencimento_original)
    
    if valida:
        print("Data válida!")
        break
    else:
        print(f"{mensagem}")
        print("Tente novamente.")

payload = {
    "dueDate": nova_data_input
}

url_update = f"https://api-sandbox.asaas.com/v3/payments/{payment_id}"
headers_update = {
    "accept": "application/json",
    "content-type": "application/json",
    "access_token": api_token
}

print(f"\nAtualizando boleto {payment_id}...")
response = requests.put(url_update, json=payload, headers=headers_update)

if response.status_code == 200:
    response_data = response.json()
    campos_exibir = ["dueDate", "originalDueDate", "invoiceUrl"]
    resultado_filtrado = {campo: response_data.get(campo) for campo in campos_exibir}
    
    print("\n✓ Resultado da alteração:")
    print(json.dumps(resultado_filtrado, indent=2))
else:
    print(f"Erro ao atualizar boleto: {response.status_code}")
    print(response.text)