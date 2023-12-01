import base64
import os
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from PubBD import PubBD
import paho.mqtt.client as mqtt
import smtplib

# MQTT broker information
broker_address = "test.mosquitto.org"
broker_port = 1883
topic = "Esp32_FaceWebServer_IMAGE"
topicBD = "Esp32_FaceWebServer_EMAIL"

open('emails.txt', 'w').close()#toda primeira execucao iremos reescrever os arquivos da base de dados


#SENT EMAIL
def envia_email(nome, email):
    with open("recieve_img.jpg", 'rb') as f:
        img_data = f.read()

    msg = MIMEMultipart()
    msg['Subject'] = 'Alerta De Intruso!'
    msg['From'] = 'iot974539@gmail.com'
    msg['To'] = email

    text = MIMEText(f"Olá, {nome}!\nRecebemos um alerta de uma possível"
                f" tentativa de invasão decetectada pela ESP32CAM.\n"
                f"Em anexo, segue a imagem que foi detectada.\n"
                f"Caso deseja autorizar a entrada, basta entrar no seu APP"
                f" e clicar no botão para destravar a porta.")
    msg.attach(text)
    image = MIMEImage(img_data, name=os.path.basename("recieve_img.jpg"))
    msg.attach(image)

    conexao = smtplib.SMTP("smtp.gmail.com", port=587)
    conexao.ehlo()
    conexao.starttls()
    conexao.ehlo()
    conexao.login(user="iot974539@gmail.com", password=f"eslwlwwtpzmkfqqm")
    try:
        conexao.sendmail(from_addr="iot2023puc@gmail.com", to_addrs=email, msg=msg.as_string())
    except Exception:
        print("algo deu errado")
    finally:
        conexao.quit()


# Callback function for when the connection is established
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic)


# Callback function for when a new message is received
def on_message(client, userdata, msg):
    message = str(msg.payload.decode('utf-8'))
    img = message.encode("ascii")
    final_msg = base64.b64decode(img)
    open("recieve_img.jpg", "wb").write(final_msg)
    print("RECEBIDO")
    PubBD()
    file = open("emails.txt", "r")
    lines = file.readlines()
    for dados in lines:
        linha = dados.split(";")
        email = linha[0]
        nome = linha[1].split("\n")[0]
        envia_email(nome, email)
        print("enviado para: "+nome+"; com email: "+email)


# Create an MQTT client instance
client = mqtt.Client()

# Set the callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect(broker_address, broker_port)

# Start the MQTT client loop (this is a blocking call and will run forever)
client.loop_forever()
