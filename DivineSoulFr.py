import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import requests
import openai
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import pandas as pd
from leonardo_api import Leonardo
import json
from dotenv import load_dotenv
import time
from activecampaign import Client

# Configuração do SMTP e credenciais do Gmail
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_user = 'delivery@mydivinesoul.com'
smtp_password = 'tbhi oaqc jwtb dhpe'

# Configuração da API OpenAI
api_key = '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'

# Credenciais do Google Sheets
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds1 = ServiceAccountCredentials.from_json_keyfile_name('divinesoulexport-e8513080cffb.json', scope)
creds2 = ServiceAccountCredentials.from_json_keyfile_name('divinesoulforms-965054994b76.json', scope)
client1 = gspread.authorize(creds1)
client2 = gspread.authorize(creds2)

# Acesso às planilhas usando IDs em vez de nomes
sheet1_id = '1cU68d3a42-wi4Q17wxkg_AUgI_WpwEmx33qTW10y-sw'  # Substitua pelo export
sheet2_id = '15AL078Ve-pXq7YHKpTvRcHpZ9zH5Z9c5NQM1QXx2Z38'  # Substitua pelo forms
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

# Função para enviar e-mail com imagem incorporada no corpo
def enviar_email(destinatario, assunto, corpo_texto, imagem=None):
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = destinatario
    msg['Subject'] = assunto
    
    # Corpo do e-mail em HTML
    html = f"""
    <html>
      <body>
        <p><img src="cid:{imagem}" alt="Imagem gerada"></p>
        <p><strong>*Vision Écrite Des 12 Prochains Mois !*</strong></p>
        <p>{corpo_texto}</p>
        <p>Si vous ne souhaitez plus recevoir mes e-mails, vous pouvez vous désabonner à tout moment en cliquant sur le bouton "Se désabonner" ci-dessous.</p>
        <p><a href="https://maps.app.goo.gl/HbD31TTdF6Z7vAgT6">Avenida Paulista, 1765 - Bela Vista, São Paulo, SP, 01311-930.<a/></p>
        <p><a href="https://trydivinesoul.com/unscribe/">Unsubscribe</a></p>
      </body>
    </html>"""
    
    # Verificar se há imagem e anexá-la ao e-mail
    if imagem:
        with open(imagem, 'rb') as f:
            image_data = f.read()
            image_attachment = MIMEImage(image_data, 'png')
            image_attachment.add_header('Content-ID', f"<{imagem}>")
            msg.attach(image_attachment)

    # Converter o HTML em um objeto MIMEText e anexá-lo ao e-mail 
    html_part = MIMEText(html, 'html')
    msg.attach(html_part)

    # Enviar o e-mail 
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(smtp_user, destinatario, msg.as_string())
    server.quit()
    
    print(f"E-mail enviado com sucesso para {destinatario}")

def enviar_email_SpiritualConnectionGuide(destinatario, assunto, corpo_texto, imagem=None):
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = destinatario
    msg['Subject'] = assunto
    
    # Corpo do e-mail em HTML
    html = f"""
    <html>
      <body>
        <p>{corpo_texto}</p>
        <p>Si vous ne souhaitez plus recevoir mes e-mails, vous pouvez vous désabonner à tout moment en cliquant sur le bouton "Se désabonner" ci-dessous.</p>
        <p><a href="https://maps.app.goo.gl/HbD31TTdF6Z7vAgT6">Avenida Paulista, 1765 - Bela Vista, São Paulo, SP, 01311-930.<a/></p>
        <p><a href="https://trydivinesoul.com/unscribe/">Unsubscribe</a></p>
      </body>
    </html>"""
    
    # Adiciona o corpo do e-mail em HTML ao MIMEText
    msg.attach(MIMEText(html, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        
        if imagem:
            with open(imagem, "rb") as file:
                img_data = file.read()
                image_part = MIMEImage(img_data)
                image_part.add_header('Content-ID', f'<{imagem}>')
                msg.attach(image_part)

        text = msg.as_string()
        server.sendmail(smtp_user, destinatario, text)
        server.quit()
        print(f"E-mail enviado para {destinatario}")
        return True
    except Exception as e:
        print(f"Falha ao enviar e-mail para {destinatario}: {e}")
        return False

def enviar_email_Divine_Reading(destinatario, assunto, corpo_texto, imagem=None):
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = destinatario
    msg['Subject'] = assunto
    
    # Corpo do e-mail em HTML
    html = f"""
    <html>
      <body>
        <p>{corpo_texto}</p>
        <p>Si vous ne souhaitez plus recevoir mes e-mails, vous pouvez vous désabonner à tout moment en cliquant sur le bouton "Se désabonner" ci-dessous.</p>
        <p><a href="https://maps.app.goo.gl/HbD31TTdF6Z7vAgT6">Avenida Paulista, 1765 - Bela Vista, São Paulo, SP, 01311-930.<a/></p>
        <p><a href="https://trydivinesoul.com/unscribe/">Unsubscribe</a></p>
      </body>
    </html>"""
    
    # Adiciona o corpo do e-mail em HTML ao MIMEText
    msg.attach(MIMEText(html, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        
        if imagem:
            with open(imagem, "rb") as file:
                img_data = file.read()
                image_part = MIMEImage(img_data)
                image_part.add_header('Content-ID', f'<{imagem}>')
                msg.attach(image_part)

        text = msg.as_string()
        server.sendmail(smtp_user, destinatario, text)
        server.quit()
        print(f"E-mail enviado para {destinatario}")
        return True
    except Exception as e:
        print(f"Falha ao enviar e-mail para {destinatario}: {e}")
        return False

def enviar_email_Past_Life_Reading(destinatario, assunto, corpo_texto, imagem=None):
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = destinatario
    msg['Subject'] = assunto
    
    # Corpo do e-mail em HTML
    html = f"""
    <html>
      <body>
        <p>{corpo_texto}</p>
        <p>Si vous ne souhaitez plus recevoir mes e-mails, vous pouvez vous désabonner à tout moment en cliquant sur le bouton "Se désabonner" ci-dessous.</p>
        <p><a href="https://maps.app.goo.gl/HbD31TTdF6Z7vAgT6">Avenida Paulista, 1765 - Bela Vista, São Paulo, SP, 01311-930.<a/></p>
        <p><a href="https://trydivinesoul.com/unscribe/">Unsubscribe</a></p>
      </body>
    </html>"""
    
    # Adiciona o corpo do e-mail em HTML ao MIMEText
    msg.attach(MIMEText(html, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        
        if imagem:
            with open(imagem, "rb") as file:
                img_data = file.read()
                image_part = MIMEImage(img_data)
                image_part.add_header('Content-ID', f'<{imagem}>')
                msg.attach(image_part)

        text = msg.as_string()
        server.sendmail(smtp_user, destinatario, text)
        server.quit()
        print(f"E-mail enviado para {destinatario}")
        return True
    except Exception as e:
        print(f"Falha ao enviar e-mail para {destinatario}: {e}")
        return False
    
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
        response_openai = requests.post("https://api.openai.com/v1/chat/completions", headers={"Authorization": f"Bearer {api_key}"}, json=data_openai)
        
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
        has_divine_soul   = any(record['Prd ID'] == 580689 for record in records1)
        has_spiritual_connection_guide   = any(record['Prd ID'] in [580696, 580698] for record in records1)
        has_connection_guide_Divine_Reading   = any(record['Add-on product IDs'] == '547418' for record in records1)
        has_connection_guide_Past_Life_Reading   = any(record['Add-on product IDs'] == '547421' for record in records1)
        has_connection_both_guide   = any(record['Add-on product IDs'] == '547418|547421' for record in records1)

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
                
                if preferencia_genero.lower() == "J'aime les femmes.":
                    mensagem= f'''
                    Envoyez-moi un court texte de maximum 6 paragraphes parlant d'une prédiction pour la vie amoureuse d'un homme dans les 12 prochains mois. "Ne parlez jamais de son partenaire." "Dites "vous", comme si vous vous adressiez directement à lui." "Ne parlez pas de rencontrer de nouvelles personnes." "Et n’envoyez pas un sujet, mais un texte." "Ne mentionnez pas dans le texte que l’homme a un partenaire." "Ne dites pas qu’une histoire d’amour est sur le point de se produire." "Ne mentionnez pas dans le texte que l’homme est actuellement en couple." "Répondez au message qui commence par "dans les 12 prochains mois"
                    '''
                    idade_ajustada= age - 15 
                    prompt= f"Well-done sketch in real colors of a young-looking{idade_ajustada}-year-old woman"
                    assunto_imagem= f"{first_name}, Votre Âme Divine Est Prête!!"
                
                else:
                    mensagem= f'''
                    Envoyez-moi un court texte de maximum 6 paragraphes parlant d'une prédiction pour la vie amoureuse d'une femme dans les 12 prochains mois. "Ne parlez jamais de son partenaire." "Dites "vous", comme si vous vous adressiez directement à lui." "Ne parlez pas de rencontrer de nouvelles personnes." "Et n’envoyez pas un sujet, mais un texte." "Ne mentionnez pas dans le texte que l’homme a un partenaire." "Ne dites pas qu’une histoire d’amour est sur le point de se produire." "Ne mentionnez pas dans le texte que l’homme est actuellement en couple." "Répondez au message qui commence par "dans les 12 prochains mois"
                    '''
                    
                    idade_ajustada= age - 8 
                    prompt= f"Well-done sketch in real colors of a young-looking{idade_ajustada}-year-old man"
                    assunto_imagem= f"{first_name}, Votre Âme Divine Est Prête!!"
                
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
                                            
                                            sucesso_envio= enviar_email(email, assunto_imagem, resposta_texto, "generated_image.png")
                                            
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

                # Envio para guia de conexão espiritual se aplicável 
        if has_spiritual_connection_guide:
            for record2 in records2:
                age = calculate_age(record2['And your birthday?'])
                
                if age is None:
                    print(f"Error calculating age for email: {email}")
                    continue

                preferencia_genero = record2['Nice to meet you {{field:pg6q7goeo}}, which gender attracts you?']
                
                if preferencia_genero.lower() == "J'aime les femmes.":
                    prompt = f"I want a detailed fictional description (without mentioning her name) of an {idade_ajustada}-year-old single woman, reveal her personality, she lives in {record2['Which city do you live in,{{field:pg6q7goeo}}?']}, send a detailed description of her with her loves, hates, fears and desires, also talk about what she works with (preferably professions that pay well) and the places she likes to go. Finally, write a summary about this woman. (SEND ME THE RESULT IN FRENCH)"
                    assunto_imagem = f"{first_name}, Cliquez ici pour voir votre guide de connexion spirituelle!"
                else:
                    prompt = f"I want a detailed fictional description (without mentioning his name) of an {idade_ajustada}-year-old single man, reveal his personality, he lives in {record2['Which city do you live in,{{field:pg6q7goeo}}?']}, send a detailed description of him with his loves, hates, fears and desires, also talk about what he works with (preferably professions that pay well) and the places he likes to go. Finally, write a summary about this man. (SEND ME THE RESULT IN FRENCH)"
                    assunto_imagem = f"{first_name}, Cliquez ici pour voir votre guide de connexion spirituelle!"

                resposta_openai = send_openai_request(prompt)
                if resposta_openai:
                    resposta_texto = resposta_openai['choices'][0]['message']['content']
                    filename = f'resposta_gpt_{email}.txt'
                    with open(filename, 'w') as file:
                        file.write(resposta_texto)
                    print(f"Response saved successfully to {filename}!")
                    sucesso_envio = enviar_email_SpiritualConnectionGuide(email, assunto_imagem, resposta_texto)
                   
                    if sucesso_envio:
                        print(f"Spiritual Connection Guide enviado com sucesso para: {email}")
                    else:
                        print(f"Failed to send Spiritual Connection Guide to {email}")
                else:
                    print(f"Falha ao obter resposta do OpenAI após várias tentativas")

        if has_connection_guide_Divine_Reading:
            for record2 in records2:
                age = calculate_age(record2['And your birthday?'])
                if age is None:
                    print(f"Error calculating age for email: {email}")
                    continue
                preferencia_genero = record2['Nice to meet you {{field:pg6q7goeo}}, which gender attracts you?']
                if preferencia_genero.lower() == "J'aime les femmes.":
                    idade_ajustada = age - 15
                    prompt = f"I want a detailed fictional description of the personality traits (without mentioning her name) of a {idade_ajustada}-year-old woman, tell me about her hobbies and finally reveal her initials.(SEND ME THE RESULT IN FRENCH)"
                    assunto_imagem = f"*{first_name},  Cliquez ici pour voir votre lecture divine!*"
                else:
                    idade_ajustada = age - 8
                    prompt = f"I want a detailed fictional description of the personality traits (without mentioning his name) of a {idade_ajustada}-year-old man, tell me about his hobbies and finally reveal his initials.(SEND ME THE RESULT IN FRENCH)"
                    assunto_imagem = f"*{first_name},  Cliquez ici pour voir votre lecture divine!*"
                data_openai = {
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                }
                response_openai = requests.post("https://api.openai.com/v1/chat/completions", headers={"Authorization": f"Bearer {api_key}"}, json=data_openai)
                if response_openai.status_code == 200:
                    resposta_openai = response_openai.json()
                    resposta_texto = resposta_openai['choices'][0]['message']['content']
                    filename = f'resposta_gpt_{email}.txt'
                    with open(filename, 'w') as file:
                        file.write(resposta_texto)
                    print(f"Response saved successfully to {filename}!")
                    sucesso_envio = enviar_email_Divine_Reading(email, assunto_imagem, resposta_texto)
                   
                    if sucesso_envio:
                        print(f"Email sent successfully to {email}")
                    else:
                        print(f"Failed to send email to {email}")
                else:
                    print(f"Failed to get OpenAI response, status code: {response_openai.status_code}")

        if has_connection_guide_Past_Life_Reading:
            for record2 in records2:
                prompt = f"I want a detailed fictional description of what the romantic relationship was like in past lives for a couple who lived in the old town of {record2['Which city do you live in,{{field:pg6q7goeo}}?']}, talk about the beginning of their relationship, children and the like. (DO NOT MENTION NAMES) (Tell it as if you were telling the person what that part of their past life was like)(SEND ME THE RESULT IN FRENCH)"
                assunto_imagem = f"*{first_name},  Cliquez ici pour voir votre lecture divine de vies antérieures*"
                data_openai = {
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                }
                response_openai = requests.post("https://api.openai.com/v1/chat/completions", headers={"Authorization": f"Bearer {api_key}"}, json=data_openai)
                if response_openai.status_code == 200:
                    resposta_openai = response_openai.json()
                    resposta_texto = resposta_openai['choices'][0]['message']['content']
                    filename = f'resposta_gpt_{email}.txt'
                    with open(filename, 'w') as file:
                        file.write(resposta_texto)
                    print(f"Response saved successfully to {filename}!")
                    sucesso_envio = enviar_email_Past_Life_Reading(email, assunto_imagem, resposta_texto)
                    
                    if sucesso_envio:
                        print(f"Email sent successfully to {email}")
                    else:
                        print(f"Failed to send email to {email}")
                else:
                    print(f"Failed to get OpenAI response, status code: {response_openai.status_code}")


        if has_connection_both_guide:
             for record2 in records2:
                age = calculate_age(record2['And your birthday?'])
                if age is None:
                    print(f"Error calculating age for email: {email}")
                    continue
                preferencia_genero = record2['Nice to meet you {{field:pg6q7goeo}}, which gender attracts you?']
                if preferencia_genero.lower() == "J'aime les femmes.":
                    idade_ajustada = age - 15
                    prompt = f"I want a detailed fictional description of the personality traits (without mentioning her name) of a {idade_ajustada}-year-old woman, tell me about her hobbies and finally reveal her initials.(SEND ME THE RESULT IN FRENCH)"
                    assunto_imagem = f"*{first_name},  Cliquez ici pour voir votre lecture divine!*"
                else:
                    idade_ajustada = age - 8
                    prompt = f"I want a detailed fictional description of the personality traits (without mentioning his name) of a {idade_ajustada}-year-old man, tell me about his hobbies and finally reveal his initials.(SEND ME THE RESULT IN FRENCH)"
                    assunto_imagem = f"*{first_name},  Cliquez ici pour voir votre lecture divine!*"
                data_openai = {
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                }
                response_openai = requests.post("https://api.openai.com/v1/chat/completions", headers={"Authorization": f"Bearer {api_key}"}, json=data_openai)
                if response_openai.status_code == 200:
                    resposta_openai = response_openai.json()
                    resposta_texto = resposta_openai['choices'][0]['message']['content']
                    filename = f'resposta_gpt_{email}.txt'
                    with open(filename, 'w') as file:
                        file.write(resposta_texto)
                    print(f"Response saved successfully to {filename}!")
                    sucesso_envio = enviar_email_Divine_Reading(email, assunto_imagem, resposta_texto)
                    if sucesso_envio:
                        print(f"Email sent successfully to {email}")
                    else:
                        print(f"Failed to send email to {email}")
                else:
                    print(f"Failed to get OpenAI response, status code: {response_openai.status_code}")
             for record2 in records2:
                 prompt = f"I want a detailed fictional description of what the romantic relationship was like in past lives for a couple who lived in the old town of {record2['Which city do you live in,{{field:pg6q7goeo}}?']}, talk about the beginning of their relationship, children and the like. (DO NOT MENTION NAMES) (Tell it as if you were telling the person what that part of their past life was like)(SEND ME THE RESULT IN FRENCH)"
                 assunto_imagem = f"*{first_name},  Cliquez ici pour voir votre lecture divine des vies antérieures!*"
                 data_openai = {
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                }
                 response_openai = requests.post("https://api.openai.com/v1/chat/completions", headers={"Authorization": f"Bearer {api_key}"}, json=data_openai)
                 if response_openai.status_code == 200:
                    resposta_openai = response_openai.json()
                    resposta_texto = resposta_openai['choices'][0]['message']['content']
                    filename = f'resposta_gpt_{email}.txt'
                    with open(filename, 'w') as file:
                        file.write(resposta_texto)
                    print(f"Response saved successfully to {filename}!")
                    sucesso_envio = enviar_email_Past_Life_Reading(email, assunto_imagem, resposta_texto)
                   
                    if sucesso_envio:
                        print(f"Email sent successfully to {email}")
                    else:
                        print(f"Failed to send email to {email}")
                 else:
                    print(f"Failed to get OpenAI response, status code: {response_openai.status_code}")

        # Aguardar 5 minutos antes de passar para o próximo e-mail
        print(f"Aguardando 2 minutos e 30 segundos antes de processar o próximo e-mail...")
        time.sleep(150)
        
        processed_emails_all.add(email)
        print(f"Processamento finalizado para o e-mail: {email}")
        print("-------------------------------------------")