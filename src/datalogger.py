import serial  # Requires pyserial: sudo pip install pyserial
import json
import csv
import time
import dropbox # write: sudo pip install dropbox
import sys


def serial_connect():
    serlocations = ['/dev/ttyUSB0', '/dev/ttyACM', '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2', '/dev/ttyACM3',
                    '/dev/ttyACM4', '/dev/ttyACM5', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3', '/dev/ttyUSB4',
                    '/dev/ttyUSB5', '/dev/ttyUSB6', '/dev/ttyUSB7', '/dev/ttyUSB8', '/dev/ttyUSB9', '/dev/ttyUSB10',
                    '/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8',
                    'com9', 'com10', 'com11', 'com12', 'com13', 'com14', 'com15', 'com16', 'com17', 'com18', 'com19',
                    'com20', 'com21', 'com1', 'end']
    for device in serlocations:
        try:
            ser = serial.Serial(
                port=device,
                baudrate=19200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            print "BBB connected to...", device
            return ser
        except:
            x = 0
    if device == 'end':
        print "No Device Found"

# Connect!
ser = serial_connect()
dspData = ""

# If connection stablished...
if ser:
    print "Waiting message" 
    ser.flushInput()
    receivingData = 0
    while True:
        time.sleep(0.2)
        if ser.inWaiting() > 0:
            dspData += ser.read(ser.inWaiting())
            t1 = time.time()
            if receivingData == 0: print "I'm receiving something"
            receivingData = 1
        if dspData.__len__() > 0:
            timeSinceLastMessage = time.time() - t1
            if timeSinceLastMessage > 1.0:
                print "Some frames received, processing..."
                receivingData = 0
                try:
                    dspDataParsed = json.loads(dspData)
                    print "Data processed succesfully, trying to save it"
                    break
                except ValueError:
                    print "Sorry, there was some noise in the bus"
                    print "Waiting more messages"
                    dspData = ""
else:
    sys.exit()

#####
#Acquire data
#dspData = '{"Emergency Broadcasting": [{ "Var": "vBus    ","Values": [4.51660156,4.51660156,4.96826171,4.51660156]}, {"Var": "cpu_tim0","Values": [0,4262,4253,4267]}]}' 
   

#print dspDataParsed.keys()
emergencyData = dspDataParsed['Emergency Broadcasting']

#create a structure to save data
listOfVectors = []
minLengthOfVectors = 1000000000
for data in emergencyData:
    tempVector = []
    tempVector.append(data['Var'])
    for values in data['Values']:
        tempVector.append(values)
    listOfVectors.append(tempVector)
    if len(tempVector) < minLengthOfVectors:
        minLengthOfVectors = len(tempVector)

# CSV and Dropbox part
fileName = "logger_BBB_" + time.strftime("%Y%m%d_%H%M%S", time.gmtime()) + ".csv"
dbxPath = "/Datalogger"

with open(fileName, 'wb') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=';')
    spamwriter.writerow(["Data taken on", time.strftime("%a - %d %b %Y %H:%M:%S", time.gmtime())])
    spamwriter.writerow(["By the Beagle Black Box"])
    spamwriter.writerow("\n")
    #Extract rows
    for x in xrange(minLengthOfVectors):
        row = [vectors[x] for vectors in listOfVectors]
        spamwriter.writerow(row)
    print "Data saved in the device"
    
with open(fileName, 'rb') as f:
    dataFile = f.read()
    print "Trying to push your file in the cloud..."

with open("passcode.txt", 'r') as code:
    pwd = code.readline()
    validPwd = pwd.find('\n')
    pwd = pwd[:validPwd]

dbx = dropbox.Dropbox(pwd)

try:
    dbxPath += "/" + fileName
    res = dbx.files_upload(dataFile, dbxPath)
except dropbox.exceptions.ApiError as err:
    print 'That was too much, check you password file or the internet connection. API error:', err
print 'Uploaded in: ',dbxPath
