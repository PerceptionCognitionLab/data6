import pymysql.cursors
import sys
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as exlib
from sshtunnel import SSHTunnelForwarder


#[pid,_,_]=exlib.startExp(expName,dbConf,pool=1,lockBox=True,refreshRate=refreshRate)

data5 = {'user':'exp',
         'password':'q1w2e3r4t5Why6',
         'database':'data5'}

beta = {'user':'exp',
         'password':'q1w2e3r4t5Why6',
         'database':'beta'}

server=SSHTunnelForwarder(
 	('specl.socsci.uci.edu',22),
	ssh_username='exp', 
	ssh_password='q1w2e3r4t5Why6',
	remote_bind_address=('127.0.0.1', 3306)
    )
server.start()

def getCon(db) :
	cnx=pymysql.connect(
		user=db['user'],
		password=db['password'],
		database=db['database'],
		host='127.0.0.1',
		port=server.local_bind_port)
	return(cnx)


dbConf = beta
task = 'Matrix'
refreshRate = 165
pid = 1
NortheasternID = 100


cnx = getCon(dbConf)
cursor = cnx.cursor()
addSession = ('INSERT INTO indSVT'
              '(participantID, task, NortheasternID)'
              'VALUES (%s, %s, %s)')
sessionPre = (pid, task, NortheasternID)
cursor.execute(addSession, sessionPre)
cnx.commit()
cursor.close()
cnx.close()