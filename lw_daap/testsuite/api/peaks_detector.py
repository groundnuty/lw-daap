#!/usr/bin/python
# -*- coding: UTF-8 -*-
import MySQLdb
from lxml import etree
from datetime import *
import csv
reader = csv.reader(open('./peaks.csv','rb'),delimiter=';')

HOST = raw_input("Server: ")
USER = raw_input("User: ")
PASS = raw_input("Pass: ")
DB   = raw_input("Database: ")


def getIDs(table, attrib, dateType, dateIni, dateEnd, limitInf, limitSup):
    """
        Deletes tuple if a value is a peak. A peak is a value which is higher or lower
           than 3 values to left or right plus/less standar deviation (or a fixed value)
        In: "tablename, attrib"
        Out: [ID's]
    """
    print dateIni
    db = MySQLdb.connect(host = HOST, user = USER, passwd = PASS, db = DB)
    cursor = db.cursor()
    #Si el limite inferior y superior es 0, se calcula la desviacion estandar para el calculo de picos
    if limitInf == 0.0 and limitSup == 0.0:
        #Set profile=1        
      #  sql = 'SELECT startDate, endDate FROM profile where startDate between %s and %s' % (dateIni, dateEnd)
       # cursor.execute(sql)
        #result = cursor.fetchall()
        #desviacion = result[0][0]
        #for item in result:
         #   sql = "UPDATE %s SET profile=1 where date BETWEEN '%s' and '%s'" % (table,item[0],item[1])
          #  print sql
           # cursor.execute(sql)
       


        #Solo estacionario
        sql = 'SELECT %s, %s, profile FROM %s WHERE %s between %s and %s order by %s' % (attrib, dateType, table, dateType, dateIni, dateEnd, dateType)
       # print 'SELECT %s, %s, profile FROM %s WHERE %s between %s and %s order by %s' % (attrib, dateType, table, dateType, dateIni, dateEnd, dateType)
        cursor.execute(sql)
        ids = cursor.fetchall()
        media = 0.0
        i = 4
        picos = 0
        
        while i < (len(ids) - 4):
            #print "Iteracion %d" % (i - 4)
            avg = mediaVecinos(ids,i);
    #Si los datos no son None o si no son todos 0 (que pueden ser erroneos) o si el dato ppal no esta entre anterior y siguiente y si los tres no son perfiles..
            if ids[i][0] != None and ids[i-1][0] != None and ids[i+1][0] != None and (ids[i-1][0] != 0.0 and ids[i+1][0] != 0.0) and (not(ids[i][0] < ids[i-1][0] and ids[i][0] > ids[i+1][0]) or not(ids[i][0] > ids[i-1][0] and ids[i][0] < ids[i+1][0])) and (ids[i][2] == 0 and ids[i-1][2] == 0 and ids[i+1][2] == 0):
                #Si los numeros son negativos                
                if ids[i][0] < 0 and ids[i+1][0] < 0 and ids[i-1][0] < 0:
                    if (ids[i][0] < ids[i+1][0]+ids[i+1][0]*2 and ids[i][0] < ids[i-1][0]+ids[i-1][0]*2) or (ids[i][0] > ids[i+1][0]-ids[i+1][0]*2 and ids[i][0] > ids[i-1][0]-ids[i-1][0]*2) or (ids[i][0] > ids[i+1][0]/3 and ids[i][0] > ids[i-1][0]/3):
                      #  print "Valor: %f Ant: %f Pos: %f Media:  Fecha: %s" % (ids[i][0], ids[i-1][0],ids[i+1][0],ids[i][1])                
                    #print "Posicion %d, fecha %s, valor %f es pico " % (i,ids[i][1], ids[i][0])
                    #print "Nombre campo: %s, Valor: %f, Tabla %s, 'FECHA: %s'," % (attrib, ids[i][0], table, ids[i][1])
                        picos += 1
                        sql = "INSERT INTO platform.FilteredData (NombreCampo,ValorCampo,NombreTabla,date,Automatico,Comentario) VALUES ('%s', %f, '%s', '%s', TRUE,'Pico detectado');" % (attrib, ids[i][0], table, ids[i][1])
                        print sql
                        #disabled #cursor.execute(sql)
                elif (ids[i][0] < 0 and ids[i+1][0] > 0 and ids[i-1][0] < 0) or (ids[i][0] > 0 and ids[i+1][0] > 0 and ids[i-1][0] < 0):
                    if 0:
                        print "no"
                #Si los numeros son positivos
                else: 
                    if (ids[i][0] > ids[i+1][0]+ids[i+1][0]*2 and ids[i][0] > ids[i-1][0]+ids[i-1][0]*2) or (ids[i][0] < ids[i+1][0]-ids[i+1][0]*2 and ids[i][0] < ids[i-1][0]-ids[i-1][0]*2) or (ids[i][0] < ids[i+1][0]/3 and ids[i][0] < ids[i-1][0]/3):
                       # print "Valor: %f Ant: %f Pos: %f Media:  Fecha: %s" % (ids[i][0], ids[i-1][0],ids[i+1][0],ids[i][1])                
                    #print "Posicion %d, fecha %s, valor %f es pico " % (i,ids[i][1], ids[i][0])
                    #print "Nombre campo: %s, Valor: %f, Tabla %s, 'FECHA: %s'," % (attrib, ids[i][0], table, ids[i][1])
                        picos += 1
                        sql = "INSERT INTO platform.FilteredData (NombreCampo,ValorCampo,NombreTabla,date,Automatico,Comentario) VALUES ('%s', %f, '%s', '%s', TRUE,'Pico detectado');" % (attrib, ids[i][0], table, ids[i][1])
                        print sql                        
                        #disabled cursor.execute(sql)
                    
            i += 1

        db.close()
    else :
        sql = 'SELECT %s, %s FROM %s, profile WHERE %s between %s and %s and %s between startDate and endDate and %s is not null order by %s' % (attrib, dateType, table, dateType, dateIni, dateEnd, dateType, attrib, dateType)
        print sql
        cursor.execute(sql)
        ids = cursor.fetchall()
        
        #for item in ids:
        #Si el valor se encuentra fuer
            #if (float(item[0]) < limitInf) or (float(item[0]) > limitSup):
                #print "fecha %s, valor %f es pico " % (item[1], item[0])
                #print "INSERT INTO platform.FilteredData (NombreCampo,ValorCampo,NombreTabla,date,Automatico,Comentario) VALUES (%s, %f, %s, '%s', TRUE,'Pico detectado')" % (attrib, item[0], table, item[1])
               # cursor.execute("INSERT INTO platform.FilteredData (NombreCampo,ValorCampo,NombreTabla,date,Automatico,Comentario) VALUES ('%s', %f, '%s', '%s', TRUE,'Pico detectado')" % (attrib, ids[i][0], table, ids[i][1])) 
        db.close()
    #print 'Picos: %i' % picos
    return 1

def mediaVecinos(values, i):
    avg = 0.0;
    k = i-3;
    while k <= (i + 3):
        if k != i and values[k][0] != None:
            avg += values[k][0]
        k += 1
    #print 'Suma: %f Media%f' % (avg, avg/6)    
    return avg/6

def main():
	print "Leyendo CSV %s" % (date.today() - timedelta(days=1))
   
for index, row in enumerate(reader):
        getIDs(row[0], row[1], 'date', "'%s 00:00:00'" % (date.today() - timedelta(days=5)), "'%s 03:00:00'" % date.today(), float(row[2]), float(row[3]))
               
if __name__ == "__main__":
    main()
