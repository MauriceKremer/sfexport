import loginsf
import createExportJob
import os

loginresult = loginsf.login('login-export.xml')
print (f"  - Current session url: {loginresult['sessionUrl']}")

dirFiles = os.listdir('.') #list of directory files
dirFiles.sort() #good initial sort but doesnt sort numerically very well
sorted(dirFiles) #sort numerically in ascending order

for name in dirFiles:
    if (os.path.isdir(name) and name[0].isdigit()):
        print ('\u001b[44;1m' + 'Reading directory ' + '\033[1m' + name.rjust(80) + '\033[0m')
        createExportJob.exportdata(loginresult,name)