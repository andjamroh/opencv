import serial
from time import sleep

serialPort = serial.Serial(port="COM7", baudrate=9600, bytesize=8, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)

serialString = ""

while True:
    sleep(1)

    if serialPort.in_waiting > 0:
        serialString = serialPort.readline()
        print(serialString.decode('Ascii'))

    serialPort.write("42069\r".encode())

