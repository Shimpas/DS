import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import requests
import openai
import os
import pandas as pd
from leonardo_api import Leonardo
import json
from dotenv import load_dotenv
import time
from activecampaign import Client

# Configuração do ActiveCampaign
api_key = "adf7704a8a662135ce45eeb8cc2f7937da995e43788abf13a462ed69df209729d732a3d0"  # Substitua pela sua chave API
ac_url = "https://mydivinesoul.api-us1.com"  # Substitua pelo seu domínio
client = Client(ac_url, api_key)
     
# Função para enviar e-mail via ActiveCampaign
def send_email_activecampaign(recipient_email, subject, body):
    html_body = f"""<html><body><p>{body}</p></body></html>"""
    data = {
        "type": "single",
        "recipient_email": recipient_email,
        "sender_email": "support@mydivinesoul.com",  # Substitua pelo seu e-mail remetente
        "subject": subject,
        "html": html_body,
        "p[1]": body,
    }
    response = client.campaigns.send_email(data)
    if response.status_code == 201:
        print(f"E-mail enviado com sucesso para {recipient_email}")
    else:
        print(f"Falha ao enviar e-mail para {recipient_email}: {response.json()}")

# Configuração da API OpenAI
api_key_openai = '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'

# Credenciais do Google Sheets
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', 
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds1 = ServiceAccountCredentials.from_json_keyfile_name('divinesoulexport-e8513080cffb.json', scope)
creds2 = ServiceAccountCredentials.from_json_keyfile_name('divinesoulforms-965054994b76.json', scope)
client1 = gspread.authorize(creds1)
client2 = gspread.authorize(creds2)

# Acesso às planilhas usando IDs em vez de nomes
sheet1_id = '1mn4925-qzcY5qOzNCAbfgyug2Xc3te7QuS5MNpHRKlw'  # Substitua pelo export
sheet2_id = '1KbreYIPTHlagDOCklTLB7kTqMuSU6qV64xo3SogAZZU'  # Substitua pelo forms
sheet1 = client1.open_by_key(sheet1_id).sheet1  # Acessa a planilha pela chave (ID)
sheet2 = client2.open_by_key(sheet2_id).sheet1  # Acessa a planilha pela chave (ID)

# Obtenção dos registros das planilhas
data1 = sheet1.get_all_records()
data2 = sheet2.get_all_records()
df1 = pd.DataFrame(data1)
df2 = pd.DataFrame(data2)

# Função para calcular idade (mantida)
def calculate_age(dob):
    date_formats = ['%m-%d-%Y', '%m/%d/%Y', '%Y-%m-%d', '%Y/%m/%d']
    for fmt in date_formats:
        try:
            birth_date = datetime.strptime(dob, fmt)
            break
        except ValueError:
            continue
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

# Configuração da API Leonardo
class Leonardo:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.base_url = "https://cloud.leonardo.ai/api/rest/v1"

    def post_generations(self, prompt, num_images, model_id, height, width):
        url = f"{self.base_url}/generations"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.auth_token}",
            "content-type": "application/json",
        }
        data = {
            "height": height,
            "modelId": model_id,
            "prompt": prompt,
            "width": width,
            "num_images": num_images,
        }
        response = requests.post(url, headers=headers, json=data)
        return response

    def get_generation(self, generation_id):
        url = f"{self.base_url}/generations/{generation_id}"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.auth_token}",
        }
        response = requests.get(url, headers=headers)
        return response

# Inicializar a classe Leonardo com o token de autenticação
leonardo = Leonardo(auth_token='7fe4f00c-9280-40a9-9c79-acee2b8cc6e2')

# Processamento dos dados filtrados
emails1 = {record['Email']: record for record in data1}
emails2 = {record['Email to receive your drawing?']: record for record in data2}
repeated_emails = set(emails1.keys()) & set(emails2.keys())

def send_openai_request(mensagem):
    data_openai = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": mensagem}],
        "temperature": 0.5,
        "top_p": 0.9,
    }
    retry_attempts = 5
    for attempt in range(retry_attempts):
        response_openai = requests.post("https://api.openai.com/v1/chat/completions", 
                                         headers={"Authorization": f"Bearer {api_key_openai}"}, 
                                         json=data_openai)
        if response_openai.status_code == 200:
            return response_openai.json()
        elif response_openai.status_code == 429:  # Wait before retrying
            wait_time = 2 ** attempt
            print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            print(f"Falha ao tentar acessar o código do GPT: {response_openai.status_code}")
    return None

# Conjunto para rastrear e-mails já processados
processed_emails_all = set()

# Iterar sobre cada e-mail único na interseção
for email in repeated_emails:
    if email not in processed_emails_all:
        records1 = [record for record in data1 if record['Email'] == email]
        records2 = [record for record in data2 if record['Email to receive your drawing?'] == email]

        # Verificar produtos possuídos pelo dono do e-mail
        has_divine_soul = any(record['Prd ID'] == 546183 for record in records1)
        
        # Obter o primeiro nome da pessoa correta
        first_name= records1[0]['First name'] if records1 else "Cliente"

        # Prioridade para e-mails com múltiplos produtos 
        if has_divine_soul:
            for record2 in records2:
                age= calculate_age(record2['And your birthday?'])
                if age is None:
                    print(f"Error calculating age for email: {email}")
                    continue
                
                preferencia_genero= record2['Nice to meet you {{field:pg6q7goeo}}, which gender attracts you?']
                if preferencia_genero.lower() == 'i like women':
                    mensagem= f''' Send me a short text with a maximum of 6 paragraphs talking about a prediction for a man's love life in the next 12 months “Do not talk about your partner at any time” “Say “you”, as if you were talking to him” “Don’t talk about meeting new people” “And don’t send a topic, but a text” “Do not mention in the text that the man has a partner” “Don’t say that a love story is about to happen.” “Do not mention in the text that the man is in a current relationship.” “Reply to message that starts with ‘’in the next 12 months” '''
                    idade_ajustada= age - 15 
                    prompt= f"Well-done sketch in real colors of a young-looking {idade_ajustada}-year-old woman"
                    assunto_imagem= f"{first_name}, Your Divine Soul Is Ready!"
                else:
                    mensagem= f''' Send me a short text with a maximum of 6 paragraphs talking about a prediction for a woman's love life in the next 12 months “Do not talk about your partner at any time” “Say “you”, as if you were talking to her” “Don’t talk about meeting new people” “And don’t send a topic, but a text” “Do not mention in the text that the woman has a partner” “Don’t say that a love story is about to happen.” “Do not mention in the text that the woman is in a current relationship.” “Reply to message that starts with ‘’in the next 12 months” '''
                    idade_ajustada= age - 8 
                    prompt= f"Well-done sketch in real colors of a young-looking {idade_ajustada}-year-old man"
                    assunto_imagem= f"{first_name}, Your Divine Soul Is Ready!"

                resposta_openai= send_openai_request(mensagem)

                if resposta_openai:
                    resposta_texto= resposta_openai['choices'][0]['message']['content']
                    filename= f'resposta_gpt_{email}.txt'
                    with open(filename, 'w') as file:
                        file.write(resposta_texto)
                    print(f"Resposta salva com sucesso em {filename}!")

                    response_leonardo= leonardo.post_generations(prompt=prompt, num_images=1, model_id='e316348f-7773-490e-adcd-46757c738eb7', height=832, width=624)

                    if response_leonardo.status_code == 200:
                        response_leonardo_json= response_leonardo.json()
                        if 'sdGenerationJob' in response_leonardo_json and 'generationId' in response_leonardo_json['sdGenerationJob']:
                            generation_id= response_leonardo_json['sdGenerationJob']['generationId']
                            time.sleep(20)  # Esperar a imagem ser gerada

                            response_imagem= leonardo.get_generation(generation_id)

                            if response_imagem.status_code == 200:
                                response_imagem_json= response_imagem.json()
                                if 'generations_by_pk' in response_imagem_json and 'generated_images' in response_imagem_json['generations_by_pk']:
                                    generated_images= response_imagem_json['generations_by_pk']['generated_images']
                                    if generated_images:
                                        image_url= generated_images[0]['url']
                                        response_imagem_download= requests.get(image_url)

                                        if response_imagem_download.status_code == 200:
                                            with open("generated_image.png", "wb") as file:
                                                file.write(response_imagem_download.content)
                                            print("Imagem salva com sucesso como generated_image.png")

                                            sucesso_envio= send_email_activecampaign(email, assunto_imagem, resposta_texto)

                                            if sucesso_envio:
                                                print(f"Divine soul enviado com sucesso para: {email}")
                                            else:
                                                print(f"Falha ao enviar e-mail para: {email}")
                                        else:
                                            print(f"Falha ao baixar a imagem, código de status: {response_imagem_download.status_code}")
                                    else:
                                        print("Lista de 'generated_images' está vazia.")
                                else:
                                    print("Chaves 'generations_by_pk' ou 'generated_images' não encontradas na resposta JSON da imagem.")
                            else:
                                print(f"Falha ao obter a URL da imagem, código de status: {response_imagem.status_code}")
                                print("Erro na resposta:", response_imagem.text)
                        else:
                            print("Chave 'generationId' não encontrada na resposta JSON da Leonardo AI.")
                    else:
                        print(f"Falha na requisição ao Leonardo AI, código de status: {response_leonardo.status_code}")
                        print("Erro na resposta:", response_leonardo.text)
                else:
                    print(f"Falha ao obter resposta do OpenAI após várias tentativas")

        # Aguardar 5 minutos antes de passar para o próximo e-mail
        print(f"Aguardando 2 minutos antes de processar o próximo e-mail...")
        time.sleep(120)
        
        processed_emails_all.add(email)
        print(f"Processamento finalizado para o e-mail: {email}")
        print("-------------------------------------------")