import loginsf
import createExportJob
import os

loginresult = loginsf.login()
print (f"  - Current session id: {loginresult['sessionId']}")
print (f"  - Current session url: {loginresult['sessionUrl']}")

dirFiles = os.listdir('.') #list of directory files
dirFiles.sort() #good initial sort but doesnt sort numerically very well
sorted(dirFiles) #sort numerically in ascending order

for name in dirFiles:
    if (os.path.isdir(name) and name[0].isdigit()):
        print ('Reading directory ' + name)
        createExportJob.exportdata(loginresult,name)