import loginsf
import createExportJob

loginresult = loginsf.login()
print (f"  - Current session id: {loginresult['sessionId']}")
print (f"  - Current session url: {loginresult['sessionUrl']}")

createExportJob.exportdata(loginresult,'organization_model__c')