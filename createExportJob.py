from urllib.parse import urlparse
import requests
from xml.etree import ElementTree
import time

localSessionInfo = {}
jobid = ''
batchid = ''
path = ''

def createjob():
    parse = urlparse(localSessionInfo['sessionUrl'])
    scheme = parse.scheme
    netloc = parse.netloc
    
    url = scheme + '://' + netloc + '/services/async/50.0/job'
    data = open('./'+path+'/createExportJob.json', 'r').read()

    headers = {"Content-Type":"application/json;charset=UTF-8","X-SFDC-Session":localSessionInfo['sessionId']} 

    response = requests.post(url,data=data,headers=headers)
    decoded = response.json()
    global jobid
    jobid = decoded["id"]
    print(f'  - Created data load job : {jobid}')

def addquery():
    parse = urlparse(localSessionInfo['sessionUrl'])
    scheme = parse.scheme
    netloc = parse.netloc
    url = scheme + '://' + netloc + '/services/async/50.0/job/' + jobid + '/batch'
    query = open('./'+path+'/query.soql', 'r').read()

    headers = {"Content-Type":"text/csv;charset=UTF-8","X-SFDC-Session":localSessionInfo['sessionId']} 
    ns = {'http': 'http://www.force.com/2009/06/asyncapi/dataload'}

    response = requests.post(url,data=query,headers=headers)
    decoded = response.content.decode('utf-8')
    root = ElementTree.fromstring(decoded)

    global batchid
    batchid = root.find('.//http:id',ns).text
    print(f'  - Created data load batch : {batchid}')

def waitForJobToComplete():
    parse = urlparse(localSessionInfo['sessionUrl'])
    scheme = parse.scheme
    netloc = parse.netloc
    
    url = scheme + '://' + netloc + '/services/async/50.0/job/' + jobid + '/batch/'+ batchid

    headers = {"Content-Type":"application/xml;charset=UTF-8","X-SFDC-Session":localSessionInfo['sessionId']} 
    ns = {'http': 'http://www.force.com/2009/06/asyncapi/dataload'}

    ready = False
    while (not ready):
        response = requests.get(url,headers=headers)
        decoded = response.content.decode('utf-8')
        root = ElementTree.fromstring(decoded)
        status = root.find('.//http:state',ns).text
        if (status=='Completed'):
            ready = True
            print('   - Batch ready.')
        else:
            print('   - Batch not ready yet. Waiting 5 seconds.')
            time.sleep(5)
    

def retrieveResults():
    parse = urlparse(localSessionInfo['sessionUrl'])
    scheme = parse.scheme
    netloc = parse.netloc
    
    url = scheme + '://' + netloc + '/services/async/50.0/job/' + jobid + '/batch/'+ batchid + '/result'

    headers = {"Content-Type":"application/xml;charset=UTF-8","X-SFDC-Session":localSessionInfo['sessionId']} 
    ns = {'http': 'http://www.force.com/2009/06/asyncapi/dataload'}

    response = requests.get(url,headers=headers)
    decoded = response.content.decode('utf-8')
    root = ElementTree.fromstring(decoded)
    resultid = root.find('.//http:result',ns).text
    url += '/'+resultid

    with open('./' + path + '/result.csv', "wb") as file:
        response = requests.get(url,headers=headers)
        file.write(response.content)
        print('  - Data saved.')


def exportdata(sessionInfo,folder):    
    global localSessionInfo
    localSessionInfo = sessionInfo

    global path
    path = folder

    createjob()
    addquery()
    waitForJobToComplete()
    retrieveResults()




