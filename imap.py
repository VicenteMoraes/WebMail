import socket
import base64
import ssl

class IMAP:
    def __init__(self,  mailServer, mailPort, login, password):
        self.login = login
        self.password = password
        self.mailPort = mailPort #143 (non-encrypted), 993 secure connection
        self.mailServer = mailServer
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket = ssl.wrap_socket(self.clientSocket)
        self.endmsg = "\r\n"

    def _validate_(self, recv):
        print(recv)
        return b'OK' in recv

    def _connect_(self, sock):
        sock.connect((self.mailServer, self.mailPort))
        recv = sock.recv(1024)
        return self._validate_(recv)

    def _HELO_(self, sock):
        helomsg = "HELO Alice" + self.endmsg
        sock.send(helomsg.encode())
        recv = sock.recv(1024)
        return self._validate_(recv)

    def _STARTTLS_(self, sock):
        starttls = "STARTTLS" + self.endmsg
        sock.send(starttls.encode())
        recv = sock.recv(1024)
        return self._validate_(recv)
        
    def _AUTH_(self, sock):
        authmsg = base64.b64encode(("\00" + self.login + "\00" + self.password).encode())
        authmsg = "a001 " + "AUTHENTICATE PLAIN " + str(authmsg.decode()) + self.endmsg
        sock.send(authmsg.encode())
        recv = sock.recv(1024)
        return self._validate_(recv)

    def establish_connection(self):
        try:
            if not self._connect_(self.clientSocket):
                raise ConnectionRefusedError("[CONNECTION FAILED]")
            print("Connection established")
            if not self._AUTH_(self.clientSocket):
                raise ConnectionAbortedError("[AUTHENTICATION FAILED]")
            print("User Authenticated")
            while True:
                ans = input()
                if ans == "q":
                    break
                self.clientSocket.send((ans + self.endmsg).encode())
                print(self.clientSocket.recv(1024))
        except ConnectionRefusedError as CRerr:
            print("Could not connect to server. Aborting... " + CRerr.args[0])
        except ConnectionError as Cerr:
            print("Could not start secure TLS connection. Aborting... " + Cerr.args[0])
        except ConnectionAbortedError as CAerr:
            print("Could not send mail. Aborting... " + CAerr.args[0])
        finally:
            self.clientSocket.close()

