import tkinter
import imap
import smtp
import ddparser

user = 'aa' # 1miranhamail9@gmail.com
password = 'bc' # Um2Tres4
imap_url = 'imap.gmail.com'
smtp_url = 'smtp.gmail.com'
principal = tkinter.Tk()
mailclient = None
# --------------------------------------SMTP--------------------

def send_email(corpo, subject, to, pagina):
    server = smtp.SMTP(smtp_url,587,user,password,subject,to,corpo)
    server.send()
    pagina.destroy()

# --------------------------------------IMAP--------------------


# def auth(user,password,imap_url):
#     con = imaplib.IMAP4_SSL(imap_url)
#     con.login(user,password)
#     return con

# def get_body(msg):
#     if msg.is_multipart():
#         return get_body(msg.get_payload(0))
#     else:
#         return msg.get_payload(None,True)

# def get_from(msg):
#     return msg['from']

# def get_subject(msg):
#     return msg['subject']

# def search(key,value,con):
#     result, data  = con.search(None,key,'"{}"'.format(value))
#     return data

# def get_emails(result_bytes):
#     msgs = []
#     for num in result_bytes[0].split():
#         typ, data = con.fetch(num, '(RFC822)')
#         msgs.append(data)
#     return msgs

# def acha_quantidade(con):
#     string=str(con.select('INBOX'))
#     quantidade=re.findall(r'\d+', string)[0]
#     return quantidade

#-------------------------------GUI----------------------------

def close(pagina):
    mailclient.close()
    pagina.destroy()

def envia_email(): # SMTP
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
    tkinter.Button(pagina_de_envio, text='Enviar', width=6, command=lambda : send_email(texto.get(),
    assunto.get(),para.get(),pagina_de_envio))  .grid(row=1,column=2)

def imprime_emails(raw): 
    texto = tkinter.Tk()
    tkinter.Label(texto, text=ddparser.body(raw), width=80).pack()

def atualiza():
    mailclient.close()
    login(user,password)

def lista_de_emails(): #IMAP
    # mailclient=imap.IMAP(imap_url,993,user,password)
    # mailclient.establish_connection()
    mailList = mailclient.fetch()
    tkinter.Button(principal,text='Atualizar',command=atualiza).grid(row=1,column=1)
    tkinter.Button(principal,text='Enviar Email',command=envia_email).grid(row=1,column=2)
    tkinter.Button(principal,text='Fechar Cliente',command=lambda : close(principal)).grid(row=1,column=4)
    tkinter.Frame(principal,bg='blue',height=60).grid(row=2)
    for counter, mail in enumerate(mailList):
        tkinter.Button(principal, text=ddparser.date(mail[0])+'    '+ddparser.ffrom(mail[0])+'    '+
        ddparser.subject(mail[0]),width='93',command=lambda i=mail[1] : imprime_emails(i)).grid(row=counter+2)

def acha_widgets():
    llist = principal.winfo_children()
    for item in llist :
        if item.winfo_children() :
            llist.extend(item.winfo_children())
    return llist

def end_pagina():
    widget_list = acha_widgets()
    for item in widget_list:
        item.destroy()

def login(usuario, senha):
    global user 
    global password
    global mailclient
    user = usuario 
    password = senha
    mailclient=imap.IMAP(imap_url,993,user,password)
    mailclient.establish_connection()
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
usuarioE=tkinter.Entry(principal,width=25)
usuarioE.grid(row=4,column=6)
tkinter.Label(principal,text='senha:',width=15).grid(row=5,column=5)
senhaE=tkinter.Entry(principal,width=25)
senhaE.grid(row=5,column=6)
b1=tkinter.Button(principal,text='login',bg='white',activebackground='red',activeforeground='yellow',command=lambda : login(usuarioE.get(),senhaE.get()))
b1.grid(row=6)

principal.mainloop()
