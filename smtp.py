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
            print(reply.decode() + " reply not received")
            return False
        return True

    def _connect_(self, sock):
        sock.connect((self.mailServer, self.mailPort))
        recv = sock.recv(1024)
        return self._validate_(recv, b'220')

    def _HELO_(self, sock):
        helomsg = "HELO Alice" + self.endmsg
        sock.send(helomsg.encode())
        recv = sock.recv(1024)
        return self._validate_(recv, b'250')

    def _STARTTLS_(self, sock):
        starttls = "STARTTLS" + self.endmsg
        sock.send(starttls.encode())
        recv = sock.recv(1024)
        return self._validate_(recv, b'220')

    def _AUTH_(self, sock):
        authmsg = base64.b64encode(("\00" + self.login + "\00" + self.password).encode())
        authmsg = "AUTH PLAIN " + str(authmsg.decode()) + self.endmsg
        sock.send(authmsg.encode())
        recv = sock.recv(1024)
        return self._validate_(recv, b'235')

    def _MAIL_(self, sock):
        mail = "MAIL FROM: <" + self.login + ">" + self.endmsg
        sock.send(mail.encode())
        recv = sock.recv(1024)
        return self._validate_(recv, b'250')

    def _RCPT_(self, sock):
        rcpt = "rcpt to: <" + self.receiveAdress + ">" + self.endmsg
        sock.send(rcpt.encode())
        recv = sock.recv(1024)
        return self._validate_(recv, b'250')

    def _DATA_(self, sock):
        sock.send(("DATA" + self.endmsg).encode())
        recv = sock.recv(1024)
        return self._validate_(recv, b'354')

    def _MSG_(self, sock):
        msg = "Subject: " + self.subject + self.endmsg + self.message + self.endmsg + "." + self.endmsg
        sock.send(msg.encode())
        recv = sock.recv(1024)
        return self._validate_(recv, b'250')

    def send(self):
        try:
            if not self._connect_(self.clientSocket):
                raise ConnectionRefusedError("[CONNECTION FAILED]")
            print("Connection established")
            if not self._HELO_(self.clientSocket):
                raise ConnectionRefusedError("[NO HELO]")
            print("helo received")
            if not self._STARTTLS_(self.clientSocket):
                raise ConnectionError("[STARTTLS FAILED]")
            self.sslclientSocket = ssl.wrap_socket(self.clientSocket)
            if not self._HELO_(self.sslclientSocket):
                raise ConnectionRefusedError("[NO HELO - TLS SESSION]")
            print("helo received") 
            if not self._AUTH_(self.sslclientSocket ):
                raise ConnectionAbortedError("[AUTHENTICATION FAILED]")
            print("User Authentified")
            if not self._MAIL_(self.sslclientSocket):
                raise ConnectionAbortedError("[MAIL FROM FAILED]")
            if not self._RCPT_(self.sslclientSocket):
                raise ConnectionAbortedError("[RCPT TO FAILED]")
            if not self._DATA_(self.sslclientSocket):
                raise ConnectionAbortedError("[DATA FAILED]")
            if not self._MSG_(self.sslclientSocket):
                raise ConnectionAbortedError("[MSG FAILED]")
        except ConnectionRefusedError as CRerr:
            print("Could not connect to server. Aborting... " + CRerr.args[0])
        except ConnectionError as Cerr:
            print("Could not start secure TLS connection. Aborting... " + Cerr.args[0])
        except ConnectionAbortedError as CAerr:
            print("Could not send mail. Aborting... " + CAerr.args[0])
        else:
            print("Email sent!")
            self.sslclientSocket.send("quit\r\n".encode())
            recv = self.sslclientSocket.recv(1024)
            if not self._validate_(recv, b'221'):
                print("[ERROR] Could not exit session")
                raise ConnectionError
            print("Exited Successfully")
        finally:
            self.sslclientSocket.close()
            self.clientSocket.close()