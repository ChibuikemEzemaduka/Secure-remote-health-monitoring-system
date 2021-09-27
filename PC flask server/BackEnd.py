
import socket
import json
import Number_Package as npkg
import random, string
import math
import sqlite3
from Crypto.Cipher import AES

def RSA_encrypt(m, e, N):
    c = npkg.exp_mod(m, e, N)
    return c

conn = sqlite3.connect('project.db')
curs = conn.cursor()
port = 12000
s = socket.socket()
s.bind(('', port))
print("Server is listening to port %d" %(port))

try:
    e = 0
    N = 0
    dummy = 0
    key = 0
    print("=" * 30)
    print("waiting for connection")
    while True:
        s.listen(4)
        if dummy == 0:
            c, addr = s.accept()
            print('Got connection from', addr)
            rdata_bytes = c.recv(1024)
            rdata = json.loads(rdata_bytes.decode())
            e, N = rdata['e'], rdata['N']
        else:
            c, addr = s.accept()

        dummy += 1
        key = int(''.join(random.choice(string.digits) for x in range(16)))
        iv = int(''.join(random.choice(string.digits) for x in range(16)))
        decry = AES.new(key.to_bytes(16, byteorder="big"), AES.MODE_CFB, iv.to_bytes(16, byteorder="big"))
        tdata = {'c': RSA_encrypt(key, e, N), 'v': RSA_encrypt(iv, e, N)}
        tdata_byte = json.dumps(tdata).encode()
        c.send(tdata_byte)
        ciphertext_bytes = c.recv(1024)
        print(ciphertext_bytes)
        if len(ciphertext_bytes) <= 0:
            dummy += 1
        else:
            sensor_data = json.loads((decry.decrypt(ciphertext_bytes)))
            if sensor_data['P'] == 0:
                sensor_data['P'] = 70
            else:
                pass
            print (sensor_data)
            if sensor_data['I'] == 14350:
                if sensor_data['T'] == 0:
                    print ("Zero value")
                else:
                    print(sensor_data['P'])
                    curs.execute("INSERT INTO patient1 VALUES(datetime('now'),(?),(?),(?),(?))",
                             ((sensor_data['T']**(math.e + 2)) - sensor_data['I'], (sensor_data['H']**(math.e + 2)) - sensor_data['I'],
                              (sensor_data['P']**(math.e + 2)) - sensor_data['I'], 1))

            else:
                if sensor_data['T'] == 0:
                     print ("Zero value")
                else:
                     curs.execute("INSERT INTO patient2 VALUES(datetime('now'),(?),(?),(?),(?))",
                                  ((sensor_data['T'] ** (math.e + 2)) - sensor_data['I'],
                                   (sensor_data['H'] ** (math.e + 2)) - sensor_data['I'],
                                   (sensor_data['P'] ** (math.e + 2)) - sensor_data['I'], 2))
        conn.commit()
        c.close()

except ConnectionRefusedError:
    print("Connection refused. You need to run server program first.")
finally: # must have
    print("free socket")
    s.close()
