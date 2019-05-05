import tkinter
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import imaplib, email, os, re



user = 'aa'
password = 'bc'
imap_url = 'imap.gmail.com'
principal = tkinter.Tk()
# --------------------------------------SMTP--------------------


msg = MIMEMultipart()

def make_email(body, subject, to):
    msg['From'] = user
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body,'plain')) 
    text = msg.as_string()
    return text

def send_email(corpo, subject, to, pagina):
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(user,password)
    server.sendmail(user,to,make_email(corpo,subject,to))
    server.quit()
    pagina.destroy()


# --------------------------------------IMAP--------------------


def auth(user,password,imap_url):
    con = imaplib.IMAP4_SSL(imap_url)
    con.login(user,password)
    return con

def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None,True)

def get_from(msg):
    return msg['from']

def get_subject(msg):
    return msg['subject']

def search(key,value,con):
    result, data  = con.search(None,key,'"{}"'.format(value))
    return data

def get_emails(result_bytes):
    msgs = []
    for num in result_bytes[0].split():
        typ, data = con.fetch(num, '(RFC822)')
        msgs.append(data)
    return msgs

def acha_quantidade(con):
    string=str(con.select('INBOX'))
    quantidade=re.findall(r'\d+', string)[0]
    return quantidade

#-------------------------------GUI----------------------------

def envia_email():
    pagina_de_envio = tkinter.Tk()
    tkinter.Frame(pagina_de_envio,width=6,height=10).grid(row=1,column=1)
    tkinter.Label(pagina_de_envio, text='Para:',width=8).grid(row=2,column=1)
    para=tkinter.Entry(pagina_de_envio, width=30)
    para.grid(row=2,column=2)
    tkinter.Label(pagina_de_envio, text='Assunto:',width=8).grid(row=3,column=1)
    assunto=tkinter.Entry(pagina_de_envio, width=30)
    assunto.grid(row=3,column=2)
    tkinter.Frame(pagina_de_envio,width=6,height=80).grid(row=4)
    tkinter.Label(pagina_de_envio, text='Texto:').grid(row=5)
    texto=tkinter.Entry(pagina_de_envio,width=92)
    texto.grid(row=6)
    tkinter.Button(pagina_de_envio, text='Enviar', width=6, command=lambda : send_email(texto.get(),assunto.get(),para.get(),pagina_de_envio))  .grid(row=1,column=2)

def imprime_emails(numero,con): 
    result, data = con.fetch(bytes(str(numero),"ascii"),'(RFC822)')
    raw = str(get_body(email.message_from_bytes(data[0][1])),"utf8")
    texto = tkinter.Tk()
    tkinter.Label(texto, text=raw, width=80).pack()

def lista_de_emails(): #IMAP
    con = auth(user,password,imap_url)
    contador=0
    tkinter.Button(principal,text='atualizar',command=lambda : login(user,password)).grid(row=1,column=1)
    tkinter.Button(principal,text='enviar email',command=envia_email).grid(row=1,column=2)
    tkinter.Frame(principal,bg='blue',height=60).grid(row=2)
    while contador<int(acha_quantidade(con)):
        contador+=1
        result, data = con.fetch(bytes(str(contador),"ascii"),'(RFC822)')
        tkinter.Button(principal, text='De:'+get_from(email.message_from_bytes(data[0][1]))+'    '+'Assunto:'+get_subject(email.message_from_bytes(data[0][1])),width='93',command=lambda i=contador : imprime_emails(i,con)).grid(row=contador+2)

def acha_widgets():
    _list = principal.winfo_children()
    for item in _list :
        if item.winfo_children() :
            _list.extend(item.winfo_children())
    return _list

def end_pagina():
    widget_list = acha_widgets()
    for item in widget_list:
        item.destroy()

def login(usuario, senha):
    global user 
    global password
    user = usuario 
    password = senha
    end_pagina()
    lista_de_emails()

principal.configure(bg='blue',cursor='spider')
for i in range(3):
    tkinter.Frame(principal,bg='blue',height=30).grid(row=i,column=1)
for i in range(4):
    tkinter.Frame(principal,bg='blue',height=10,width=80).grid(row=4,column=i)
for i in range(4):
    tkinter.Frame(principal,bg='blue',height=10,width=80).grid(row=5,column=i)
for i in range(4):
    tkinter.Frame(principal,bg='blue',height=10,width=80).grid(row=6,column=i)
tkinter.Label(principal,text='usuario:',width=15).grid(row=4,column=5)
usuarioE=tkinter.Entry(principal)
usuarioE.grid(row=4,column=6)
tkinter.Label(principal,text='senha:',width=15).grid(row=5,column=5)
senhaE=tkinter.Entry(principal)
senhaE.grid(row=5,column=6)
b1=tkinter.Button(principal,text='login',bg='white',activebackground='red',activeforeground='yellow',command=lambda : login(usuarioE.get(),senhaE.get()))
b1.grid(row=6)

principal.mainloop()
