import loginsf
import createjob

loginresult = loginsf.login()
print (f"  - Current session id: {loginresult['sessionId']}")
print (f"  - Current session url: {loginresult['sessionUrl']}")

createjob.exportdata(loginresult,'organization_model__c')