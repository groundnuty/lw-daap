#!/usr/bin/python
import MySQLdb
import matplotlib.pyplot as plt

print "---- Print Chart MySQL ----"
#conexion a db
while True:
    try:
        server = raw_input("Server: ")
        user = raw_input("User: ")
        password = raw_input("Password: ")
        database = raw_input("Database Name: ")

        print " ----- Tablas en servidor %s. Database: %s ----- " % (server,database)
        print ""

        db = MySQLdb.connect(host = server, user = user, passwd = password, db = database)
        cursor = db.cursor()

        sql = 'SHOW TABLES'
        cursor.execute(sql)
        result = cursor.fetchall()

        for row in result:
            print row[0]
        break
    except:
	print("Parametros de entrada incorrectos")
 



print " "
#Seleccion de tabla
while True:
    try:
        table = raw_input("Escribe una tabla: ")
    
        sql = "DESCRIBE %s" % table
        cursor.execute(sql)
        result = cursor.fetchall()

        for row in result:
            print row[0]
        break
    except:
        print("Nombre de tabla incorrecto")


while True:
    try:
        date = raw_input("Nombre parametro fecha: ")
        params = raw_input("Elige parametro(s) [param1, param2, ...] ")

        print "Rango de fechas (yyyy/mm/aa hh:mm:ss)"
        fechaIni = raw_input("Inicial: ")
        fechaFin = raw_input("Final: ")

        sql = "SELECT %s, %s FROM %s WHERE %s BETWEEN '%s' and '%s'" % (params, date, table, date, fechaIni, fechaFin)
        cursor.execute(sql)
        result = cursor.fetchall()

        tst = []
        dates = []

        for row in result:
            tst.append(row[0])
            dates.append(row[len(row)-1])

        break
    except:
        print("Parametros incorrectos")
        
#Print plot
plt.plot(dates,tst)
plt.ylabel('some numbers')
plt.show()

#Cerrar base de datos
db.close()

