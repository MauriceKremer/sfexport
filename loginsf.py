import requests
import fileinput
from xml.etree import ElementTree

def login(loginFile):

    url  = "https://test.salesforce.com/services/Soap/u/50.0"
    data = open(loginFile, 'r').read()
    headers = {"Content-Type":"text/xml;charset=UTF-8","SOAPAction":"login"}
    ns = {'urn': 'urn:partner.soap.sforce.com'}

    response = requests.post(url,data=data,headers=headers)
    decoded = response.content.decode('utf-8')
    root = ElementTree.fromstring(decoded)

    sessionId = root.find('.//urn:sessionId',ns).text
    sessionUrl = root.find('.//urn:serverUrl',ns).text

    session = {'sessionId':sessionId, 'sessionUrl':sessionUrl}
    return session

