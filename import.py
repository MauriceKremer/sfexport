import loginsf
import createImportJob
import os

loginresult = loginsf.login('login-import.xml')
print (f"  - Current session url: {loginresult['sessionUrl']}")

#createImportJob.importdata(loginresult,'01-account')
#createImportJob.importdata(loginresult,'02-organization_model__c')

dirFiles = os.listdir('.') #list of directory files
dirFiles.sort() #good initial sort but doesnt sort numerically very well
sorted(dirFiles) #sort numerically in ascending order

for name in dirFiles:
    if (os.path.isdir(name) and name[0].isdigit()):
        print ('\u001b[44;1m' + 'Reading directory ' + '\033[1m' + name + '\033[0m')
        createImportJob.importdata(loginresult,name)