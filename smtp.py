import socket
import base64
import ssl

class SMTP:
    def __init__(self, mailServer, mailPort, login, password, subject, receiveAdress, message):
        self.receiveAdress = receiveAdress
        self.endmsg = "\r\n \r\n"
        self.mailServer = mailServer
        self.clientSocket = socket.socket(AF_INET, SOCK_STREAM)
        self.sslclientSocket = null
        self.mailPort = mailPort
        self.login = login
        self.password = password
        self.subject = subject
        self.message = message


    def _validate_(self, recv, reply):
        print(recv)
        if recv[:3] != reply:
            print(reply+" reply not received")
            return False
        return True

    def _connect_(self, socket):
        socket.connect((self.mailServer, self.mailPort))
        recv = socket.recv(1024)
        return self._validate_(recv, '220')

    def _HELO_(self, socket):
        helomsg = "HELO Alice" + self.endmsg
        socket.send(helomsg)
        recv = socket.recv(1024)
        return self._validate_(recv, '250')

    def _STARTTLS_(self, socket):
        starttls = "STARTTLS" + self.endmsg
        socket.send(starttls)
        recv = socket.recv(1024)
        return self._validate_(recv, '220')
        
    def _AUTH_(self, socket):
        authmsg = "\00" + self.login + "\00" + self.password
        authmsg = "AUTH PLAIN " + base64.b64encode(auth.encode("utf-8")) + self.endmsg
        socket.send(authmsg)
        recv = socket.recv(1024)
        return self._validate_(recv, '235')

    def _MAIL_(self, socket):
        mail = "MAIL FROM: <" + login + ">" + self.endmsg
        socket.send(mail)
        recv = socket.recv(1024)
        if not self._validate_(recv, '250'):
            return False
        rcpt = "rcpt to: <" + self.receiveAdress + ">" + self.endmsg
        socket.send(rcpt)
        recv = socket.recv(1024)
        return self._validate_(recv, '250')

    def _DATA_(self, socket):
        socket.send("DATA" + self.endmsg)
        recv = socket.recv(1024)
        if not self._validate_(recv, '354')
            print("Could not send DATA")
            return False
        msg = "Subject: " + self.subject + self.endmsg + self.message + self.endmsg + "." + self.endmsg
        socket.send(msg)
        recv = socket.recv(1024)
        return self._validate_(recv, '250')

    def send(self):
        if not self._connect_(self.clientSocket):
            print("Could not establish connection")
            return False
        print("Connection established")
        if not self._HELO_(self.clientSocket):
            print("No response from server")
            return False
        print("Connection with server established")
        if not self._STARTTLS_(self.clientSocket):
            print("No response from server")
            return False
        self.sslclientSocket = ssl.wrap_socket(self.clientSocket)
        if not self._HELO_(self.sslclientSocket):
            print("No response from server")
            return False
        print("Server responded") 
        if not self._AUTH_(self.sslclientSocket ):
            print("Could not autenticate credentials")
            return False
        print("User Authentified")
        if not self._MAIL_(self.sslclientSocket):
            print("Could not send mail")
            return False
        if not self._DATA_(self.sslclientSocket):
            print("Could not send data")
            return False
        self.sslclientSocket.send("quit" + self.endmsg)
        recv = self.sslclientSocket.recv(1024)
        if self._validate_(recv, '221'):
            print("Email sent!")
            return True
        print("Could not send email")
        return False
