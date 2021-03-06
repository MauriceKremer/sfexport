from urllib.parse import urlparse
import requests
from xml.etree import ElementTree
import time
import os

localSessionInfo = {}
jobid = ''
batchid = ''
path = ''
baseUrl = ''

def createjob():
    url = baseUrl + '/services/async/50.0/job'
    data = open('./'+path+'/createImportJob.json', 'r').read()

    headers = {"Content-Type":"application/json;charset=UTF-8","X-SFDC-Session":localSessionInfo['sessionId']} 

    response = requests.post(url,data=data,headers=headers)
    decoded = response.json()

    global jobid
    jobid = decoded["id"]
    print(f'  - Created data import job : {jobid}')


def createBatches(file):
    reader = open(file, 'r')
    header = reader.readline()

    csv = header 
    i = 0
    while(True):
        line = reader.readline()
        i+=1
        if line: # line contains data
            csv += line 
        if not line or i > 10000: #batch limit is 10k records
            adddatabatch(csv)
            if line: # file has more lines
                csv = header 
                i=0
            else:
                break # end of file reached

def adddatabatch(csv):
    url = baseUrl + '/services/async/50.0/job/' + jobid + '/batch'

    headers = {"Content-Type":"text/csv;charset=UTF-8","X-SFDC-Session":localSessionInfo['sessionId']} 
    ns = {'http': 'http://www.force.com/2009/06/asyncapi/dataload'}

    response = requests.post(url,data=csv.encode('UTF-8'),headers=headers)
    decoded = response.content.decode('utf-8')
    root = ElementTree.fromstring(decoded)

    global batchid
    batchid = root.find('.//http:id',ns).text
    print(f'   - Created data import batch : {batchid}')

def closeJob():
    url = baseUrl + '/services/async/50.0/job/' + jobid 
    closejob = '<?xml version="1.0" encoding="UTF-8"?><jobInfo xmlns="http://www.force.com/2009/06/asyncapi/dataload"><state>Closed</state></jobInfo>'

    headers = {"Content-Type":"application/xml;charset=UTF-8","X-SFDC-Session":localSessionInfo['sessionId']} 
    requests.post(url,data=closejob,headers=headers)
    print('  - Job closed.')

def monitorJob():
    url = baseUrl + '/services/async/50.0/job/' + jobid 
    headers = {"Content-Type":"application/json;charset=UTF-8","X-SFDC-Session":localSessionInfo['sessionId']} 
    
    waited = 0
    while (True):
        response = requests.get(url,headers=headers)
        decoded = response.json()
        completed = decoded['numberBatchesCompleted']
        total = decoded['numberBatchesTotal']
        print(f'   - {completed} of {total} batches completed. Waited {waited} seconds.', end = '\r')
        time.sleep(2)
        waited += 2
        if (completed == total):
            print('\n   - Import completed.')
            break


def importdata(sessionInfo,folder):    
    global localSessionInfo
    localSessionInfo = sessionInfo

    global path
    path = folder

    parse = urlparse(localSessionInfo['sessionUrl'])
    scheme = parse.scheme
    netloc = parse.netloc

    global baseUrl
    baseUrl = scheme + '://' + netloc

    createjob()
    
    dirFiles = os.listdir(path)
    for name in dirFiles:
        if (os.path.isfile(path + '/' + name) and name.split('.')[1] == 'csv'):
            print ('\033[94m' + 'Reading file ' + path + '/' + name + '\033[0m')
            createBatches(path + '/' + name)

    closeJob()
    monitorJob()
    #waitForJobToComplete()
    #retrieveResults()