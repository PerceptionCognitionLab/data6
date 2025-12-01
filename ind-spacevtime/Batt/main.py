#imports
import sys
import random
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as exlib
import os

#importing task code
sys.path.insert(0, 'E:/data6/ind-spacevtime/SGabor/')
from SGabor import runSG
sys.path.insert(0, 'E:/data6/ind-spacevtime/SLetter/')
from SLetter import runSL
sys.path.insert(0, 'E:/data6/ind-spacevtime/SPi/')
from SPi import runSP
sys.path.insert(0, 'E:/data6/ind-spacevtime/TGabor/')
from TGabor import runTG
sys.path.insert(0, 'E:/data6/ind-spacevtime/TLetter/')
from TLetter import runTL
sys.path.insert(0, 'E:/data6/ind-spacevtime/TPi/')
from TPi import runTP

seed = random.randrange(1e6)
dbConf=exlib.beta
expName="indSVT"
n_practices = 1
n_trials = 4


refreshRate=60
exlib.setRefreshRate(refreshRate)
[pid,_,_]=exlib.startExp(expName,dbConf,pool=1,lockBox=True,refreshRate=refreshRate)
# pid = 1
session = 0
fileCheck = f"E:/data6/ind-spacevtime/SGabor/Data/{pid}_SGabor.csv"
if os.path.exists(fileCheck):
    with open(f"E:/data6/ind-spacevtime/SGabor/Data/{pid}_SGabor.csv",'r') as f:
        line_count = sum(1 for line in f)
        session = line_count//n_trials + 1
print('Current session: ', session)


functions = [runSG, runSL, runSP, runTG, runTL, runTP]
random.shuffle(functions)
for func in functions:
    func(session, pid, n_practices, n_trials)
