createChart <- function(query,db,param){
    db='processed'
    query='SELECT TRUNCATE(depth,0), DATE(water_sensors.date), temp FROM water_sensors WHERE  DATE(water_sensors.date) BETWEEN \'2013-08-06\' AND \'2013-11-07\'  and depth is not null GROUP BY TRUNCATE(depth,0), DATE(water_sensors.date) ORDER BY date, depth'
    param = 'temp'
    con <- dbConnect(MySQL(),user="webuser",password="webuserpass",dbname=db,host="doriiie02.ifca.es")
    result <- dbGetQuery(con, query)
    myPanel <- function(x, y, z, ...) {
        panel.levelplot(x,y,z,...)
        #panel.text(x, y, round(z,1))
    }

    #Crear matriz X Y Z : Prof, fecha, valor, agrupados en orden por fecha (y todas las profundidades listadas cada vez)
    colnames(result)[1] <- "X"
    colnames(result)[2] <- "Y"
    colnames(result)[3] <- "Z"

    result$Y <- as.factor(result$Y)
    print('aqui')
    x11()
    #png(filename="lstChrt.png", width = 700)
    range <- max(result$Z)/4
    range
    levelplot(Z ~ Y*X, result, ylim = rev(range(-2:max(result$X)+2)), panel = myPanel, col.regions=colorRampPalette(c("dark blue","cyan", "yellow", "red")), xlab=list(cex=.05), at=c(seq(0,6.0,0.05),seq(12.1,18.0,0.05),seq(18.1,24.0,0.05),seq(24.1,30.0,0.05)),scales=list(x=list(at=seq(1,length(unique(result$Y)),trunc(length(unique(result$Y))*0.05)), rot=90)))
    dev.off()
}

library("lattice")
library("RMySQL")
#png(filename="/home/aguilarf/IFCA/CDP/R/lstChrt.png", width = 700)
#args = commandArgs()
#print(args[length(args)])
#createChart(args[length(args)-2],args[length(args)-1],args[length(args)])
createChart('SELECT TRUNCATE(depth,0), DATE(water_sensors.date), temp FROM water_sensors WHERE  DATE(water_sensors.date) BETWEEN \'2013-08-06\' AND \'2013-11-07\'  and depth is not null GROUP BY TRUNCATE(depth,0), DATE(water_sensors.date) ORDER BY date, depth','processed','temp')
#dev.off()

