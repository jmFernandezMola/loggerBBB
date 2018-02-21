import serial  # Requires pyserial: sudo pip install pyserial
import json
import csv
import time
import dropbox # write: sudo pip install dropbox
import sys


def serial_connect():
    ser_locations = ['/dev/ttyUSB0', '/dev/ttyACM', '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2', '/dev/ttyACM3',
                    '/dev/ttyACM4', '/dev/ttyACM5', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3', '/dev/ttyUSB4',
                    '/dev/ttyUSB5', '/dev/ttyUSB6', '/dev/ttyUSB7', '/dev/ttyUSB8', '/dev/ttyUSB9', '/dev/ttyUSB10',
                    '/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8',
                    'com9', 'com10', 'com11', 'com12', 'com13', 'com14', 'com15', 'com16', 'com17', 'com18', 'com19',
                    'com20', 'com21', 'com1', 'end']
    for device in ser_locations:
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
        sys.exit()

def parse_emcy_data():
    list_of_vectors = []
    min_length_of_vectors = 1000000000
    for data in jsonData:
        temp_vector = []
        temp_vector.append(data['Var'])
        for values in data['Values']:
            temp_vector.append(values)
        list_of_vectors.append(temp_vector)
        if len(temp_vector) < min_length_of_vectors:
            min_length_of_vectors = len(temp_vector)
    return min_length_of_vectors,list_of_vectors

def add_flight_vector():
    global flightVector

    if len(flightVector) == 0:
        flightVector.append([data['Var'] for data in jsonData])
        flightVector[0].insert(0, 'time')
        print "First flight vector reported, keep saving until emergency message"

    flightVector.append([data['Values'][0] for data in jsonData])
    flightVector[-1].insert(0, time.strftime("%d/%m/%Y %H:%M:%S", time.gmtime()))

def save_emcy_data():
    # CSV and Dropbox part
    file_path = "/home/circontrol/loggerBBB/data/"
    file_name = "logger_BBB_" + time.strftime("%Y%m%d_%H%M%S", time.gmtime()) + ".csv"
    dbx_path = "/Datalogger"

    with open(file_path + file_name, 'wb') as csvfile:
        spam_writer = csv.writer(csvfile, delimiter=';')
        spam_writer.writerow(["Data taken on", time.strftime("%a - %d %b %Y %H:%M:%S", time.gmtime())])
        spam_writer.writerow(["By the Beagle Black Box"])
        spam_writer.writerow([keyMsg])
        spam_writer.writerow("\n")
        # Extract rows
        for x in xrange(minLengthOfVectors):
            row = [vectors[x] for vectors in listOfVectors]
            spam_writer.writerow(row)
        print "Emergency data saved in the device"

    with open(file_path + file_name, 'rb') as f:
        data_file = f.read()

    with open("passcode.txt", 'r') as code:
        pwd = code.readline()
        valid_pwd = pwd.find('\n')
        pwd = pwd[:valid_pwd]

    dbx = dropbox.Dropbox(pwd)

    try:
        dbx_path += "/" + file_name
        dbx.files_upload(data_file, dbx_path)
        print 'Uploaded in: ', dbx_path,'\n'
    except dropbox.exceptions.ApiError as err:
        print 'That was too much, check you password file or the internet connection. API error:', err


def save_flight_vector():
    # CSV and Dropbox part
    file_path = "/home/circontrol/loggerBBB/data/"
    file_name = "flight_recorder_BBB_" + time.strftime("%Y%m%d_%H%M%S", time.gmtime()) + ".csv"
    dbx_path = "/Datalogger"

    with open(file_path + file_name, 'wb') as csvfile:
        spam_writer = csv.writer(csvfile, delimiter=';')
        spam_writer.writerow(["Data saved on", time.strftime("%a - %d %b %Y %H:%M:%S", time.gmtime())])
        spam_writer.writerow(["By the Beagle Black Flight Recorder"])
        spam_writer.writerow([keyMsg])
        spam_writer.writerow("\n")
        # Extract rows
        for vectors in flightVector:
            spamwriter.writerow(vectors)
        print "Flight record saved in the device"
        flightVector = []

    with open(file_path + file_name, 'rb') as f:
        data_file = f.read()

    with open("passcode.txt", 'r') as code:
        pwd = code.readline()
        valid_pwd = pwd.find('\n')
        pwd = pwd[:valid_pwd]

    dbx = dropbox.Dropbox(pwd)

    try:
        dbx_path += "/" + file_name
        dbx.files_upload(data_file, dbx_path)
        print 'Uploaded in: ', dbx_path, '\n'
    except dropbox.exceptions.ApiError as err:
        print 'That was too much, check you password file or the internet connection. API error:', err


# Connect!
ser = serial_connect()
receivingData = 0
dspData = ""
flightVector = []


# If connection stablished...
if ser:
    print "Waiting message" 
    ser.flushInput()
    receivingData = 0
    while True:
        if (receivingData == 0):
            time.sleep(0.05)
        if ser.inWaiting() > 0:
            dspData += ser.read(ser.inWaiting())
            t1 = time.time()
            receivingData = 1
        if dspData.__len__() > 0:
            timeSinceLastMessage = time.time() - t1
            if timeSinceLastMessage > 0.5:
                receivingData = 0
                try:
                    dspDataParsed = json.loads(dspData)
                    keyMsg = dspDataParsed.keys()[0]
                    jsonData = dspDataParsed[keyMsg]
                    if "Emergency Broadcasting" in keyMsg:
                        print "There is an emergency broadcast"
                        minLengthOfVectors, listOfVectors = parse_emcy_data()
                        save_emcy_data()
                        dspData = ""
                        if len(flightVector) > 0: save_flight_vector()
                    elif "Flight" in keyMsg:
                        add_flight_vector()
                    else:
                        print keyMsg


                except ValueError:
                    print "There was some noise in the bus"
                    print "Waiting more messages"
                    dspData = ""

