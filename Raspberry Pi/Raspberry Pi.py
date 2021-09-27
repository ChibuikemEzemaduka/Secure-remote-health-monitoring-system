import RPi.GPIO as GPIO
from DHT11_lib import DHT11
import time
from statistics import mean
import socket
import json
import Number_Package as npkg
import random, string
import math
from Crypto.Cipher import AES
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pulsesensor import Pulsesensor


def RSA_keygen():
    gap = random.randint(2**27, 2**29)
    p = npkg.find_prime_smaller_than_k(2 ** 31 - gap)  
    q = npkg.find_prime_greater_than_k(2 ** 31 + gap)  #
    e = 65537
    N = p * q
    Nphi = (p - 1) * (q - 1)
    d = npkg.mult_inv_mod_N(e, Nphi)
    return e, d, N

def RSA_decrypt(c, d, N):
    m_decrypt = npkg.exp_mod(c, d, N)  
    return m_decrypt

ip = 'include the server IP here'
port = 12000
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
instance = DHT11(pin=27)
lis = []
list2 = []
list3 = []
sensor = {'T': 0, 'H': 0, 'P': 0, 'I': 14350}
dummy = 0

try:
    d = 0
    N = 0
    key = 0
    s = socket.socket()
    p = Pulsesensor()
    p.startAsyncBPM()
    while True:      
        if dummy == 0:
            s = socket.socket()
            s.connect((ip, port))
            e, d, N = RSA_keygen()
            tdata = {'N': N, 'e': e}     
            tdata_byte = json.dumps(tdata).encode()     
            s.send(tdata_byte)                
        elif s.fileno() == -1:
            s = socket.socket()
            s.connect((ip, port))
        else:
            print ("continue")           
        rdata_bytes = s.recv(1024)
        rdata = json.loads(rdata_bytes.decode())
        c = rdata['c']
        v = rdata['v']     
        key = RSA_decrypt(c, d, N)
        iv = RSA_decrypt(v, d, N)
        result = instance.read() 
        P = p.BPM
        print(P)
        if result.temperature is not 0:           
            lis.append(result.temperature)
            list2.append(result.humidity)
            list3.append(P)
            if result.temperature >= (sum(lis)/len(lis)) + 2 or result.temperature <= (sum(lis)/len(lis)) - 2 \
                    or result.temperature >= 30 or P >= 100:
                email = MIMEMultipart()
                host = smtplib.SMTP('smtp.gmail.com', 587)  
                host.starttls()  
                source = 'include sender email address'
                passw = 'put email password'
                destination = 'include destination address'
                host.login(source, passw)  
                email['From'] = 'Remote Health Monitoring System'
                email['To'] = destination
                email['Subject'] = 'Patient1 Health – Alert'
                body = "Patient1 Health Reading is Body Temperature: %d C, Room Humidity: %d, Pulse Rate:%d bpm. Please treat with urgent attention"%(result.temperature, result.humidity, P)
                email.attach(MIMEText(body, 'plain'))
                msg = email.as_string()
                host.sendmail(source, destination, msg)
                print('Mail Sent')
                sensor['T'] = result.temperature
                sensor['P'] = P
                sensor['H'] = result.humidity
                dict_byte = json.dumps(sensor)
                byx = AES.new(key.to_bytes(16, byteorder="big"), AES.MODE_CFB, iv.to_bytes(16, byteorder="big"))
                ciphertext_bytes = byx.encrypt(dict_byte)
                s.send(ciphertext_bytes)
            elif len(lis) >= 20 or len(list2) >= 20:
                sensor['T'] = round(sum(lis)/len(lis))
                sensor['H'] = round(sum(list2)/len(list2))
                sensor ['P'] = P  
                dict_byte = json.dumps(sensor)
                byx = AES.new(key.to_bytes(16, byteorder="big"), AES.MODE_CFB, iv.to_bytes(16, byteorder="big"))
                ciphertext_bytes = byx.encrypt(dict_byte)
                s.send(ciphertext_bytes)
                lis = []
                list2 = []           
            else:
                dummy += 1         
        else:
            sensor['T'] = result.temperature
            sensor['H'] = result.humidity
            sensor['P'] = round(P)
            dict_byte = json.dumps(sensor)
            byx = AES.new(key.to_bytes(16, byteorder="big"), AES.MODE_CFB, iv.to_bytes(16, byteorder="big"))
            ciphertext_bytes = byx.encrypt(dict_byte)
            s.send(ciphertext_bytes)
        dummy += 1
        time.sleep(3)
        s.close()               

except ConnectionRefusedError:
    print("Connection refused. You need to run server program first.")
finally:
    s.close()



