def _Mfind_(index, msg):
    string = ""
    print(msg, len(msg))
    try:
        while msg[index]  != "\n":
            string += msg[index]
            index += 1
    except IndexError:
        pass
    return string

def date(msg):
    return _Mfind_(msg.find("Date"), msg)

def ffrom(msg):
    return _Mfind_(msg.find("From"), msg)

def subject(msg):
    return _Mfind_(msg.find("Subject"), msg)

def body(msg):
    message = ""
    try:
        index = msg.find("{") + 1
        charnum = ""
        while msg[index] != "}":
            charnum += msg[index]
            index += 1
        charnum = int(charnum)
        for i in range(index+1, index+charnum+1):
            message += msg[i]
    except IndexError:
        pass
    return message

