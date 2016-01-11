#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Importamos smtplib
import smtplib
import MySQLdb
from lxml import etree
from datetime import *

from email.mime.text import MIMEText

MAIN_HOST = raw_input("Server: ")
REPL_HOST = raw_input("Replica Server: ")
USER = raw_input("User: ")
PASS = raw_input("Password: ")
DB_1   = raw_input("Raw DB: ")
DB_2   = raw_input("Curated DB: ")
message = ''

msg = MIMEText("Contenido del e-mail a enviar")
recipients = ['aguilarf@ifca.unican.es', 'tamara@ecohydros.com', 'apmonteoliva@ecohydros.com','acriado@ecohydros.com']
msg['Subject'] = 'Alerta Base de Datos'
msg['From'] = 'cdp.alertas@gmail.com'
msg['To'] = ", ".join(recipients)

print msg


#Comprobación de tablas
db = MySQLdb.connect(host = MAIN_HOST, user = USER, passwd = PASS, db = DB_1)
cursor = db.cursor()

#AMT
print 'Comprobando AMT en 87.'
sql = 'SELECT date FROM AMT WHERE date > DATE_SUB(NOW(), INTERVAL 4 HOUR)'
cursor.execute(sql)
result = cursor.fetchall()
if len(result)<1:
    sql = 'SELECT date FROM AMT ORDER BY date DESC LIMIT 1'
    cursor.execute(sql)
    result = cursor.fetchall()
    message = message + 'CdP: No entran datos en AMT - platform db [Ultimo dato: '+ str(result[0][0]) +']\n'

#CNR2
print 'Comprobando CNR2 en 87.'
sql = 'SELECT date FROM CNR2 WHERE date > DATE_SUB(NOW(), INTERVAL 4 HOUR)'
cursor.execute(sql)
result = cursor.fetchall()
if len(result)<1:
    sql = 'SELECT date FROM CNR2 ORDER BY date DESC LIMIT 1'
    cursor.execute(sql)
    result = cursor.fetchall()
    message = message + 'CdP: No entran datos en CNR2 - platform db [Ultimo dato: '+ str(result[0][0]) +']\n'

#SAM_825E
print 'Comprobando Radiómetros en 87.'
sql = 'SELECT date FROM SAM_825E WHERE date > DATE_SUB(NOW(), INTERVAL 7 HOUR)'
cursor.execute(sql)
result = cursor.fetchall()
if len(result)<1:
    sql = 'SELECT date FROM SAM_825E ORDER BY date DESC LIMIT 1'
    cursor.execute(sql)
    result = cursor.fetchall()
    message = message + 'CdP: No entran datos en Radiómetros - platform db [Ultimo dato: '+ str(result[0][0]) +']\n'

#Vaisala
print 'Comprobando meteo en 87.'
sql = 'SELECT date FROM VaisalaWind WHERE date > DATE_SUB(NOW(), INTERVAL 4 HOUR)'
cursor.execute(sql)
result = cursor.fetchall()
if len(result)<1:
    sql = 'SELECT date FROM VaisalaWind ORDER BY date DESC LIMIT 1'
    cursor.execute(sql)
    result = cursor.fetchall()
    message = message + 'CdP: No entran datos en Meteorológicos - platform db [Ultimo dato: '+ str(result[0][0]) +']\n'

#PROPS
print 'Comprobando PROPS en 87.'
sql = 'SELECT date FROM PROPS WHERE date > DATE_SUB(NOW(), INTERVAL 9 HOUR)'
cursor.execute(sql)
result = cursor.fetchall()
if len(result)<1:
    sql = 'SELECT date FROM PROPS ORDER BY date DESC LIMIT 1'
    cursor.execute(sql)
    result = cursor.fetchall()
    message = message + 'CdP: No entran datos en PROPS - platform db [Ultimo dato: '+ str(result[0][0]) +']\n'

##processed
db = MySQLdb.connect(host = MAIN_HOST, user = USER, passwd = PASS, db = DB_2)
cursor = db.cursor()
#AMT
print 'Comprobando AMT - processed en 87.'
sql = 'SELECT date FROM AMT WHERE date > DATE_SUB(NOW(), INTERVAL 4 HOUR)'
cursor.execute(sql)
result = cursor.fetchall()
if len(result)<1:
    message = message + 'CdP: Fallo platform - processed en AMT\n'

#SAM_825E
print 'Comprobando Radiómetros - processed en 87.'
sql = 'SELECT date FROM SAM_825E WHERE date > DATE_SUB(NOW(), INTERVAL 8 HOUR)'
cursor.execute(sql)
result = cursor.fetchall()
if len(result)<1:
    message = message + 'CdP: Fallo platform - processed en Radiometros\n'

#PROPS
print 'Comprobando PROPS - processed en 87.'
sql = 'SELECT date FROM PROPS WHERE date > DATE_SUB(NOW(), INTERVAL 9 HOUR)'
cursor.execute(sql)
result = cursor.fetchall()
if len(result)<1:
    message = message + 'CdP: Fallo platform - processed en PROPS\n'

#Ficocianinas
print 'Comprobando AMT - processed en 87.'
sql = 'SELECT date FROM mFlu_blue WHERE date > DATE_SUB(NOW(), INTERVAL 4 HOUR) and value > 12'
cursor.execute(sql)
result = cursor.fetchall()
if len(result)>0:
    message = message + 'CdP: ALERTA!! - Valor Ficocianinas > 12\n'

#Master - Slave
print 'Comprobando sincronización'
db = MySQLdb.connect(host = REPL_HOST, user = 'webuser', passwd = 'webuserpass', db = DB_2)
cursor = db.cursor()

sql = 'SELECT date FROM AMT WHERE date > DATE_SUB(NOW(), INTERVAL 6 HOUR)'
cursor.execute(sql)
result = cursor.fetchall()
if len(result)<1:
    message = message + 'CdP: Fallo master - slave\n'

db.close();

# Enviamos si hay algun fallo
if len(message)>0:
    # Autenticamos
    mailServer = smtplib.SMTP('smtp.gmail.com',587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login("correo@gmail.com","password")
    print 'Enviando correo electrónico'
    msg = MIMEText("El sistema de monitorizacion CdP - Cogotas ha detectado los siguientes fallos: \n\n" + message)
    mailServer.sendmail(msg["From"], recipients, msg.as_string())
else:
    print 'Correo electrónico no enviado - Status OK'

mailServer.close()
