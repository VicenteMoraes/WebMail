import socket
import base64
import ssl

class SMTP:
    def __init__(self, mailServer, mailPort, login, password, subject, receiveAdress, message):
        self.receiveAdress = receiveAdress
        self.endmsg = "\r\n"
        self.mailServer = mailServer
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sslclientSocket = None
        self.mailPort = mailPort #Port 587 for STARTTLS, Port 465 for SSL
        self.login = login
        self.password = password
        self.subject = subject
        self.message = message


    def _validate_(self, recv, reply):
        print(recv)
        if recv[:3] != reply:
            print(reply.decode() +" reply not received")
            return False
        return True

    def _connect_(self, socket):
        socket.connect((self.mailServer, self.mailPort))
        recv = socket.recv(1024)
        return self._validate_(recv, b'220')

    def _HELO_(self, socket):
        helomsg = "HELO Alice" + self.endmsg
        socket.send(helomsg.encode())
        recv = socket.recv(1024)
        return self._validate_(recv, b'250')

    def _STARTTLS_(self, socket):
        starttls = "STARTTLS" + self.endmsg
        socket.send(starttls.encode())
        recv = socket.recv(1024)
        return self._validate_(recv, b'220')
        
    def _AUTH_(self, socket):
        authmsg = base64.b64encode(("\00" + self.login + "\00" + self.password).encode())
        authmsg = "AUTH PLAIN " + str(authmsg.decode()) + self.endmsg
        socket.send(authmsg.encode())
        recv = socket.recv(1024)
        return self._validate_(recv, b'235')

    def _MAIL_(self, socket):
        mail = "MAIL FROM: <" + self.login + ">" + self.endmsg
        socket.send(mail.encode())
        recv = socket.recv(1024)
        if not self._validate_(recv, b'250'):
            return False
        rcpt = "rcpt to: <" + self.receiveAdress + ">" + self.endmsg
        socket.send(rcpt.encode())
        recv = socket.recv(1024)
        return self._validate_(recv, b'250')

    def _DATA_(self, socket):
        socket.send("DATA\r\n".encode())
        recv = socket.recv(1024)
        if not self._validate_(recv, b'354'):
            print("Could not send DATA")
            return False
        msg = "Subject: " + self.subject + self.endmsg + self.message + self.endmsg + "." + self.endmsg
        socket.send(msg.encode())
        recv = socket.recv(1024)
        return self._validate_(recv, b'250')

    def send(self):
        if not self._connect_(self.clientSocket):
            print("Could not establish connection")
            return False
        print("Connection established")
        if not self._HELO_(self.clientSocket):
            print("No helo")
            return False
        print("helo received")
        if not self._STARTTLS_(self.clientSocket):
            print("No STARTTTLS")
            return False
        self.sslclientSocket = ssl.wrap_socket(self.clientSocket)
        if not self._HELO_(self.sslclientSocket):
            print("No helo")
            return False
        print("helo received") 
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
        self.sslclientSocket.send("quit\r\n".encode())
        recv = self.sslclientSocket.recv(1024)
        if self._validate_(recv, b'221'):
            print("Email sent!")
            return True
        print("Could not quit")
        return False
