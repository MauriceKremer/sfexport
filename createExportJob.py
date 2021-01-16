from urllib.parse import urlparse
import requests
from xml.etree import ElementTree
import time

localSessionInfo = {}
jobid = ''
batchid = ''
path = ''
baseUrl = ''

def createjob():
    url = baseUrl + '/services/async/50.0/job'
    data = open('./'+path+'/createExportJob.json', 'r').read()

    headers = {"Content-Type":"application/json;charset=UTF-8","X-SFDC-Session":localSessionInfo['sessionId']} 

    response = requests.post(url,data=data,headers=headers)
    decoded = response.json()
    global jobid
    jobid = decoded["id"]
    print(f'  - Created data export job : {jobid}')

def addquery():
    url = baseUrl + '/services/async/50.0/job/' + jobid + '/batch'
    query = open('./'+path+'/query.soql', 'r').read()

    headers = {"Content-Type":"text/csv;charset=UTF-8","X-SFDC-Session":localSessionInfo['sessionId']} 
    ns = {'http': 'http://www.force.com/2009/06/asyncapi/dataload'}

    response = requests.post(url,data=query,headers=headers)
    decoded = response.content.decode('utf-8')
    root = ElementTree.fromstring(decoded)

    global batchid
    batchid = root.find('.//http:id',ns).text
    print(f'  - Created data export batch : {batchid}')

def closeJob():
    url = baseUrl + '/services/async/50.0/job/' + jobid 
    closejob = '<?xml version="1.0" encoding="UTF-8"?><jobInfo xmlns="http://www.force.com/2009/06/asyncapi/dataload"><state>Closed</state></jobInfo>'

    headers = {"Content-Type":"application/xml;charset=UTF-8","X-SFDC-Session":localSessionInfo['sessionId']} 
    requests.post(url,data=closejob,headers=headers)
    print('  - Job closed.')

def waitForJobToComplete():
    url = baseUrl + '/services/async/50.0/job/' + jobid + '/batch/'+ batchid

    headers = {"Content-Type":"application/xml;charset=UTF-8","X-SFDC-Session":localSessionInfo['sessionId']} 
    ns = {'http': 'http://www.force.com/2009/06/asyncapi/dataload'}

    ready = False
    waited = 0
    while (not ready):
        response = requests.get(url,headers=headers)
        decoded = response.content.decode('utf-8')
        root = ElementTree.fromstring(decoded)
        status = root.find('.//http:state',ns).text
        if (status=='Failed'):
            ready = True
            print('\u001b[31m   - Batch failed! \033[0m')
        if (status=='Completed'):
            ready = True
            print('\n   - Batch ready.')
        else:
            print(f'   - Batch not ready yet. Waited {waited} seconds. [' + status + ']', end='\r')
            waited += 2
            time.sleep(2)
    
def retrieveResults():
    url = baseUrl + '/services/async/50.0/job/' + jobid + '/batch/'+ batchid + '/result'

    headers = {"Content-Type":"application/xml;charset=UTF-8","X-SFDC-Session":localSessionInfo['sessionId']} 
    ns = {'http': 'http://www.force.com/2009/06/asyncapi/dataload'}

    response = requests.get(url,headers=headers)
    decoded = response.content.decode('utf-8')
    root = ElementTree.fromstring(decoded)
    resultid = root.find('.//http:result',ns).text
    url += '/'+resultid

    with open('./' + path + '/exportresult.csv', "wb") as file:
        response = requests.get(url,headers=headers)
        file.write(response.content)
        print('  - Data saved.')

def exportdata(sessionInfo,folder):    
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
    addquery()
    closeJob()
    waitForJobToComplete()
    retrieveResults()
