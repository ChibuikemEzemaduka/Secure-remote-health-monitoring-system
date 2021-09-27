
from flask import Flask, render_template, request
import json
import sqlite3
import math


app = Flask(__name__)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route("/patient1")
def main():
   conn=sqlite3.connect('project.db')
   conn.row_factory = dict_factory
   c=conn.cursor()
   c.execute("SELECT * FROM patient1 ORDER BY timestamp DESC LIMIT 20")
   readings = c.fetchall()
   for i in readings:
       i['temp'] = round(10**(math.log(i['temp'] + 14350, 10)/(math.e + 2)))
       i['hum'] = round(10**(math.log(i['hum'] + 14350, 10)/(math.e + 2)))
       i['pulse'] = round(10 **(math.log(i['pulse'] + 14350, 10) / (math.e + 2)))
   return render_template('index.html', readings=readings)

@app.route("/patient2")
def main2():
   conn=sqlite3.connect('project.db')
   conn.row_factory = dict_factory
   c=conn.cursor()
   c.execute("SELECT * FROM patient2 ORDER BY timestamp DESC LIMIT 20")
   readings = c.fetchall()
   for i in readings:
       i['temp'] = round(10**(math.log(i['temp'] + 29862, 10)/(math.e + 2)))
       i['hum'] = round(10**(math.log(i['hum'] + 29862, 10)/(math.e + 2)))
       i['pulse'] = round(10**(math.log(i['pulse'] + 29862, 10)/(math.e + 2)))
   return render_template('index.html', readings=readings)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=81, debug=True)