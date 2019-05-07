import socket
import base64
import ssl
import time

class IMAP:
    def __init__(self,  mailServer, mailPort, login, password):
        self.login = login
        self.password = password
        self.mailPort = mailPort #143 (non-encrypted), 993 secure connection
        self.mailServer = mailServer
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket = ssl.wrap_socket(self.clientSocket)
        self.endmsg = "\r\n"
        self.connection = False

    def _validate_(self, recv, reply):
        print(recv)
        return reply in recv

    def _connect_(self, sock):
        sock.connect((self.mailServer, self.mailPort))
        recv = sock.recv(1024)
        return self._validate_(recv, b'OK')

    def _AUTH_(self, sock, tag):
        authmsg = base64.b64encode(("\00" + self.login + "\00" + self.password).encode())
        authmsg = tag + " " + "AUTHENTICATE PLAIN " + str(authmsg.decode()) + self.endmsg
        sock.send(authmsg.encode())
        recv = sock.recv(1024)
        return self._validate_(recv, b'OK')

    def _NOOP_(self, sock, tag):
        noopmsg = tag + " NOOP" + self.endmsg
        sock.send(noopmsg.encode())
        recv = sock.recv(1024)
        return self._validate_(recv, b'OK')

    def _EXAMINE_(self, sock, tag, mailbox):
        examinemsg = tag + " EXAMINE " + mailbox + self.endmsg
        sock.send(examinemsg.encode())
        recv = sock.recv()
        if not self._validate_(recv, b'(Success)'):
            return False
        else:
            recv = recv.decode()
            uid = ""
            i = recv.find("EXISTS") - 1
            while recv[i] != "\n":
                uid += recv[i]
                i -= 1
            uid = uid.replace(" ", "").replace("*", "")
            uid = int(uid)
            return uid

    def _FETCH_(self, sock, tag, uid, fetch_tags):
        fetchmsg = tag + " FETCH " + str(uid) + " (" + fetch_tags + ")" + self.endmsg
        print(fetchmsg)
        sock.send(fetchmsg.encode())
        response = ""
        recv = sock.recv()
        print(recv)
        while not self._validate_(recv[len(recv)-12:len(recv)], b'OK Success\r\n'):
            response += recv.decode("utf-8")
            time.sleep(0.1)
            recv = sock.recv()
            print(recv)
        return response

    def establish_connection(self):
        try:
            if not self._connect_(self.clientSocket):
                raise ConnectionError("[CONNECTION FAILED]")
            print("Connection established")
            if not self._AUTH_(self.clientSocket, "a001"):
                raise ConnectionAbortedError("[AUTHENTICATION FAILED]")
            print("User Authenticated")
        except ConnectionError as Cerr:
            print("Could not connect to server. Aborting... " + ", ".join(Cerr.args))
        except ConnectionAbortedError as CAerr:
            print("Server connection failed. Aborting... " + ", ".join(CAerr.args))
        else:
            self.connection = True

    def fetch(self):
        try:
            if not self.connection:
                raise ConnectionError("No connection")
            if not self._NOOP_(self.clientSocket, "a002"):
                raise ConnectionRefusedError("[NOOP FAILED]")
            UID = self._EXAMINE_(self.clientSocket, "a003", "inbox")
            if not UID:
                raise ConnectionRefusedError("[EXAMINE FAILED]")
            mails = []
            counter = 0
            for mail_uid in range(1, UID + 1):
                header = self._FETCH_(self.clientSocket, "a{0:03d}".format(3 + mail_uid + counter), mail_uid, "FLAGS BODY[HEADER.FIELDS (DATE FROM SUBJECT)]")
                print("header ok")
                counter += 1
                body = self._FETCH_(self.clientSocket, "a{0:03d}".format(3 + mail_uid + counter), mail_uid, "BODY[TEXT]")
                mails.append((header, body))
                print("body ok")
            return tuple(mails)
        except ConnectionError as Cerr:
            print("No connection to imap server. Aborting... " + ", ".join(Cerr.args))
        except ConnectionRefusedError as CRerr:
            print("Could not feth emails. Aborting... " + ", ".join(CRerr.args))

    def close(self):
        self.clientSocket.close()