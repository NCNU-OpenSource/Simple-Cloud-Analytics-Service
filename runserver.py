import pymysql,threading,os 
from datetime import datetime

def check_worker_status():
    global conn
    global check_time_interval
    try:
        cur = conn.cursor()
        query = "SELECT * FROM tensor_worker_check_time WHERE time_last_check > SUBDATE('"+str(datetime.now())+"' , INTERVAL "+str(check_time_interval)+" SECOND);"
        cur.execute(query)
        conn.commit()
        result = cur.fetchall()
        num_worker = len(result)
        if num_worker == 0:
            print("No worker")
        else:
            for i in range(num_worker):
                print(str(result[i][1])+" is here! ")

        query = "SELECT * FROM tensor_worker_check_time WHERE time_last_check < SUBDATE('"+str(datetime.now())+"' , INTERVAL "+str(check_time_interval)+" SECOND);"
        cur.execute(query)
        conn.commit()
        result = cur.fetchall()
        num_worker_disconnected = len(result)
        if num_worker_disconnected == 0:
            print("None is disconnected")
        else:
            for i in range(num_worker_disconnected):
                print(result[i][1]+" is disconnected! ")
        
        query = "DELETE FROM tensor_worker_check_time WHERE time_last_check < SUBDATE('"+str(datetime.now())+"' , INTERVAL 30 SECOND);"
        cur.execute(query)
        conn.commit()
    except pymysql.OperationalError:
            output = 'Operational error'
    else:
        cur.close()
    threading.Timer(check_time_interval,check_worker_status).start()


check_time_interval = 10

try:
    conn = pymysql.connect(host="127.0.0.1",user="djangouser", passwd="djangopwd", db="fordjango",charset="utf8")
    check_worker_status()
    os.system("uwsgi --ini /etc/uwsgi9000.ini")
except pymysql.OperationalError:
    output = "Connect error"
else:
    conn.close()

