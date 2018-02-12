import socket
import dropbox
import time

print("Running...")
lastIP = ""


time.sleep(90.0)
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('volt', 0))    
    IP = s.getsockname()[0]
except:
    IP = "No connection"
    print(IP)

if IP != "No connection" and IP != lastIP:
    lastIP = IP
    fileName = "IP_Sniffer_"+ time.strftime("%Y%m%d_%H%M%S", time.gmtime())+".txt"
    with open(fileName, 'wb') as f:
        dataFile = "New IP address detected: " + IP + "\n"
        f.write(dataFile)
        print("File updated")

    with open("/home/circontrol/loggerBBB/src/passcode.txt", 'r') as code:
        pwd = code.readline()
        validPwd = pwd.find('\n')
        pwd = pwd[:validPwd]

    dbxPath = "/Datalogger"
    dbx = dropbox.Dropbox(pwd)
    dbxPath += "/" + fileName

    try:
        res = dbx.files_upload(dataFile, dbxPath)
        print("The file is in Dropbox")
    except dropbox.exceptions.ApiError as err:
        print('That was too much, check you password file or the internet connection. API error:', err)
