import serial #Requereix pyserial
import time
import struct
import csv
import datetime
import dropbox #Requereix dropbox

#Initilaizations
data = ""
listValues = []
setDelimiter = str(bytearray.fromhex('FF FF FF FF FF FF FF FF'))

def serial_connect():
	serlocations=['/dev/ttyUSB0','/dev/ttyACM', '/dev/ttyACM0', '/dev/ttyACM1','/dev/ttyACM2', '/dev/ttyACM3','/dev/ttyACM4', '/dev/ttyACM5','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3', '/dev/ttyUSB4', '/dev/ttyUSB5', '/dev/ttyUSB6', '/dev/ttyUSB7', '/dev/ttyUSB8', '/dev/ttyUSB9', '/dev/ttyUSB10','/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9', 'com10', 'com11', 'com12', 'com13', 'com14', 'com15', 'com16', 'com17', 'com18', 'com19', 'com20', 'com21', 'com1', 'end']
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
		x=0
	if device == 'end':
		print "No Device Found"

def check_data_consistency():
	#  In the following lines the program will search the delimiters
	# and will split all the data based on those delimiters
	#print data
	listArrays = {}
	listIndex = 0
	dataShadowCopy = data
	if not setDelimiter in dataShadowCopy:
		 return 0 #FAIL
	while  setDelimiter in dataShadowCopy:
		h = dataShadowCopy.find(setDelimiter)
		dataShadowCopy = dataShadowCopy[h+8:] # Destroy all the data until the first delimiter
		if setDelimiter  in dataShadowCopy:
			listArrays[listIndex] = str(dataShadowCopy[:dataShadowCopy.find(setDelimiter)]) # Keep data in this interval
		else:
			listArrays[listIndex] = str(dataShadowCopy) # Keep data of the last interval
		listIndex += 1

	# Check if all received data has the same size
	desideredLength = len(listArrays[0])
	for x in range(len(listArrays)):
		if not len(listArrays[x]) == desideredLength:
			print "Some of the data received is not complete. Trying to keep as much as possible."
			break
		else:
		# Transform the data received into something
			if (desideredLength % 4 == 0 and desideredLength > 8):
				tempVector = [str(listArrays[x][0:8])]
				topIndex = 12
				while (topIndex <= desideredLength):
					tempVector.append(int(struct.unpack('l', listArrays[x][topIndex-4:topIndex])[0]))
					topIndex +=4
				listValues.append(tempVector)
			else:
				print "Data received seems to have length not divisible by 4"
				return 0
	return 1


def clean_data():
	data = ""
	listValues = []
	setDelimiter = str(bytearray.fromhex('FF FF FF FF FF FF FF FF'))



# Connect!
ser = serial_connect()
timeSinceConnection = time.time()

# If connection stablished...
if ser:
	print "Waiting message..."
	ser.flushInput()
	while True:
		time.sleep(0.5)
		if ser.inWaiting() > 0 :
			data += ser.read(ser.inWaiting())
			t1 = time.time()
		if data.__len__() > 0 :
			timeSinceLastMessage = time.time() - t1
			if timeSinceLastMessage > 1.0:
				print "Some frames received, processing..."
				dataValidity = check_data_consistency()
				if dataValidity == 1:
					print "Data processed succesfully, trying to save it"
					break
				else:
					print "Sorry, there was some noise in the bus"
					print "Waiting more messages..."
					clean_data()


#CSV and Dropbox part
fileName = "/logger_BBB_" + time.strftime("%Y%m%d_%H%M%S", time.gmtime()) + ".csv"
dbxPath = "/Datalogger"

with open(fileName, 'wb') as csvfile:
	spamwriter = csv.writer(csvfile, delimiter=';')
	spamwriter.writerow(["Data taken on", time.strftime("%a - %d %b %Y %H:%M:%S", time.gmtime())])
	spamwriter.writerow(["By the Beagle Black Box"])
	spamwriter.writerow("\n")
	for x in range(len(listValues[0])):
		spamwriter.writerow([elements[x] for elements in listValues])
	print "Data saved in the device"

with open(fileName, 'rb') as f:
	dataFile = f.read()
	print "Trying to push your file in the cloud..."

try:
	with open("passcode.txt", 'r') as code:
		pwd =  code.readline()
		validPwd = pwd.find('\n')
		pwd = pwd[:validPwd]
	dbx = dropbox.Dropbox(pwd) 
	dbxPath += "/"+fileName
	res = dbx.files_upload(dataFile, dbxPath)
except dropbox.exceptions.ApiError as err:
	print('That was too much, check you password file or the internet connection. API error:', err)
print dbxPath
print 'Uploaded as', res.name.encode('utf8')
 
