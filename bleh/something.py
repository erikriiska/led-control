
import binascii
import serial

def getByteArray(i):
    while len(i) < 10*2*3:
        i += "0"
    c = binascii.unhexlify(i)
    return c, True

with serial.Serial(port='/dev/cu.usbmodem101', baudrate=9600, timeout=10) as ser:
    while True:
        i = input()
        b, ok = getByteArray(i)
        if ok:
            print(ser.write(b))
