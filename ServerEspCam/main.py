import tkinter
from tkinter import ttk
from tkinter import messagebox
import smtplib
import os
import paho.mqtt.client as mqtt


CORDEFUNDO = "#375362"
NOME = ""
EMAIL = ""
CARGO = ""


class Cadastro:
    def __init__(self):
        self.tela = tkinter.Tk()
        self.num_cel_formatado = ""
        self.tela.title("Sistema de Cadastro Inicial")
        self.tela.config(padx=5, pady=20, bg=CORDEFUNDO)
        self.tela.geometry("650x400")
        label = tkinter.Label(text='Cadastro de usuários', font=("Arial", 20, "bold"), fg='white', bg=CORDEFUNDO)
        label.grid(row=0, column=1, columnspan=2, pady=10)

        label_nome = tkinter.Label(text="Primeiro Nome", font=("Arial", 15, "bold"), fg='white', bg=CORDEFUNDO)
        label_nome.grid(row=1, column=0, pady=15)

        self.nome = tkinter.Entry(width=30)
        self.nome.grid(row=2, column=0, pady=5)

        label_ocupacao = tkinter.Label(text="Ocupação", font=("Arial", 15, "bold"), fg='white', bg=CORDEFUNDO)
        label_ocupacao.grid(row=1, column=2, padx=5)

        self.ocupacao = ttk.Combobox(values=['Administrador', 'Dependente', 'Funcionário', 'Outro'])
        self.ocupacao.grid(row=2, column=2)

        label_celular = tkinter.Label(text="Celular (com DDD)", font=("Arial", 15, "bold"), fg='white', bg=CORDEFUNDO)
        label_celular.grid(row=3, column=0, pady=15)
        self.numero_celular = tkinter.Entry(width=30)
        self.numero_celular.grid(row=4, column=0)

        label_email = tkinter.Label(text="Email", font=("Arial", 15, "bold"), fg='white', bg=CORDEFUNDO)
        label_email.grid(row=3, column=2, padx=5, pady=15)

        self.email = tkinter.Entry(width=40)
        self.email.grid(row=4, column=2, padx=5)

        self.btenviar = tkinter.Button(text="Enviar", font=('Arial', 20, 'bold'), fg='#0000FF', bg='#CCFFFF', width=10,
                                       command=self.verifica)
        self.btenviar.grid(row=5, column=1, columnspan=3, pady=100)

        self.tela.mainloop()

    def manipula_string(self):
        lista_aux = list(self.numero_celular.get())
        self.num_cel_formatado = "+55"
        for j in lista_aux:
            if j != " " and j != "(" and j != ")" and j != "-":
                self.num_cel_formatado += j

    def envia_email(self, celular, email, nome, ocupacao):
        dominio = email.split("@")[1].split(".")[0]
        conexao = smtplib.SMTP(f"smtp.{dominio}.com", port=587)
        conexao.starttls()
        mensagem = (f"Subject:Cadastro Efetuado com Sucesso!\n\n"
                    f"Hey, {nome}! Obrigado por cadastrar-se no sistema.\n"
                    f"O cargo de {ocupacao} foi instaurado com sucesso no seu sistema.\n\n"
                    f"Obervação: Caso haja alguma tentativa de entrada não permitida via detecção facial, iremos enviar uma mensagem com mais detalhes para "
                    f"{email}. Além de enviar para os emails dos administradores\n\nObrigado pela confiança!")
        mensagem_final = mensagem.encode()
        senha = os.environ.get("SENHA")
        conexao.login(user="iot974539@gmail.com", password=f"eslwlwwtpzmkfqqm")
        try:
            conexao.sendmail(from_addr="iot2023puc@gmail.com", to_addrs=email, msg=mensagem_final)
        except Exception:
            print("algo deu errado")
        finally:
            messagebox.showinfo(title="Sucesso", message="Cadastro efetuado com sucesso!")

    def verifica(self):
        self.manipula_string()
        if len(self.email.get()) == 0 or len(self.ocupacao.get()) == 0 or len(
                self.nome.get()) == 0:
            messagebox.showerror(title="Erro",
                                 message="Favor, verificar se todos os campos foram preenchidos!")
        elif len(self.num_cel_formatado) < 14:
            messagebox.showerror(title="Erro",
                                 message="Número de celular inválido!!")
        else:
            resp = messagebox.askquestion(title="Confirmação", message=f"Deseja Confirmar os seguintes Campos:\n"
                                                                       f"Nome: {self.nome.get()}\nEmail: {self.email.get()}\n"
                                                                       f"Celular: {self.numero_celular.get()}\nOcupação: {self.ocupacao.get()}")
            if resp:
                self.envia_email(self.numero_celular.get(), self.email.get(), self.nome.get(), self.ocupacao.get())
                global NOME
                global EMAIL
                global CARGO
                NOME = self.nome.get()
                EMAIL = self.email.get()
                CARGO = self.ocupacao.get()
                self.tela.destroy()


if __name__ == '__main__':
    x = Cadastro()
    # MQTT broker configuration
    broker_address = "test.mosquitto.org"
    broker_port = 1883
    topic = "Esp32_FaceWebServer_SQL"

    # Create a MQTT client
    client = mqtt.Client()
    # Connect to the MQTT broker
    client.connect(broker_address, broker_port)

    # Publish a message
    if CARGO == "Administrador":
        message = f"{NOME};{EMAIL};1"
    else:
        message = f"{NOME};{EMAIL};0"
    client.publish(topic, message)

    print("SENT: "+message)
    # Disconnect from the MQTT broker
    client.disconnect()

