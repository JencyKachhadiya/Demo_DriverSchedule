import re,csv
from Account_app.models import *
from GearBox_app.models import *
from Appointment_app.models import *
from datetime import datetime

def checkStr(data:str):
    return data.lower().strip().replace(" ","")
rctiReportId = None
with open("rctiReportId.txt", 'r') as f:
    rctiReportId = f.read()  
fileName = None
with open('File_name_file.txt','r')as f:
    fileName = f.read()
# fileName = '20240105153603@_!KIRAT-march-2023.csv'
with open(f'static/Account/RCTI/RCTIInvoice/{fileName}','r') as f:
    csv_reader = csv.reader(f)
    rctiErrorObj = RctiErrors()
    clientName = Client.objects.filter(name = 'holcim').first()
    finalList = []
    prepared = []
    tempData = []
    lineCount = 0
    datePattern = r'\d{2}\.\d{2}\.\d{4}'
    
    docketPattern = r'(\d{5,11}[a-zA-Z]{0,2})'
    truckNo = None
    total = 0
    fileDetails = []
    rctiRepoort = None
    
    try:
        for row in csv_reader:
            lineCount += 1
            errorSolve = str(row) + '@_!'+ str(rctiReportId)
            if row[0].strip() in '':
                continue
            if '@' in row[0]:
                row[0]=row[0].replace(' @ ','@')
            splitRow = row[0].split()
            splitRow = list(filter(lambda x: x.strip() != '', splitRow))
            if 'paymentfortruck' in checkStr(row[0]):
                truckNo = row[0].split(',')[-3]
            elif  re.fullmatch(datePattern, splitRow[0].strip()) and len(splitRow[1].strip()) > 8:
                rctiErrorObj = RctiErrors()
                rctiErrorObj.clientName = 'holcim'
                rctiErrorObj.docketNumber = None
                rctiErrorObj.docketDate = None
                rctiErrorObj.errorDescription = "Manually Manage."
                rctiErrorObj.fileName = fileName.split('@_!')[-1]
                rctiErrorObj.data = str(errorSolve)
                rctiErrorObj.errorType = 1
                rctiErrorObj.save()
            elif len(splitRow) > 0:
                if re.fullmatch(datePattern, splitRow[0].strip()) and re.fullmatch(docketPattern, splitRow[1].strip()):
                    tempData.insert(0,splitRow[0])
                    tempData.insert(1,splitRow[1])
                    try:
                        if '-' in splitRow[2] and float(splitRow[2].replace('-','')):
                            rctiErrorObj = RctiErrors()
                            rctiErrorObj.clientName = 'holcim'
                            rctiErrorObj.docketNumber = None
                            rctiErrorObj.docketDate = None
                            rctiErrorObj.errorDescription = "Manually Manage."
                            rctiErrorObj.fileName = fileName.split('@_!')[-1]
                            rctiErrorObj.data = str(errorSolve)
                            rctiErrorObj.errorType = 1
                            
                            rctiErrorObj.save()
                            continue
                        else:
                            tempData.insert(2,str(float(splitRow[2].strip())))

                            tempData.insert(3,splitRow[3].strip())
                            tempData.insert(4,splitRow[4].strip())
                            tempData.insert(5,splitRow[5].strip())
                            tempData.insert(6,splitRow[6].strip())
                            tempData.insert(7,splitRow[7].strip())
                            tempData.insert(6,' '.join(splitRow[8:]))
                        
                    except:
                        if '-' in splitRow[-1] and float(splitRow[-1].replace('-','')):
                            rctiErrorObj = RctiErrors()
                            rctiErrorObj.clientName = 'holcim'
                            rctiErrorObj.docketNumber = None
                            rctiErrorObj.docketDate = None
                            rctiErrorObj.errorDescription = "Manually Manage."
                            rctiErrorObj.fileName = fileName.split('@_!')[-1]
                            rctiErrorObj.data = str(errorSolve)
                            rctiErrorObj.errorType = 1
                            
                            rctiErrorObj.save()
                            continue
                        else:
                            tempData.insert(3,splitRow[-1])
                            tempData.insert(2,' '.join(splitRow[2:-1]))
                    

                    
                    if len(prepared) > 1 and len(tempData) > 1:
                        if prepared[0] == tempData[0] and prepared[1] == tempData[1]: 
                            prepared.extend(tempData[2:])
                        else:
                                 
                            finalList.append([truckNo] + prepared )
                            prepared = tempData
                    else:
                        prepared = tempData
                    tempData = []
                else:
                    with open('holcimUtils.txt','a')as f:
                        f.write('pattern not match'+ str(row) +'\n')
            else:
                with open('holcimUtils.txt','a')as f:
                    f.write('len is 0'+ str(row) +'\n')
                          
        finalList.append([truckNo] + prepared)
    except Exception as e:
        with open('holcim.txt','a')as f:
            f.write('convert Error' +str(e) +'\n')
    try:
        for data in finalList:
            rctiReportObj = RctiReport.objects.filter(pk = rctiReportId).first()
            
            try:
                if len(data) > 0:
                    rctiObj = RCTI()
                    rctiObj.clientName = clientName
                    rctiObj.truckNo =data[0]
                    rctiObj.docketNumber = data[2]
                    rctiObj.docketDate =  datetime.strptime(data[1], '%d.%m.%Y').date()

                    if len(data) > 5:
                        rctiObj.cubicMl = data[3]
                        rctiObj.paidQty = data[4]
                        rctiObj.unit = data[5]
                        rctiObj.noOfKm = data[6]
                        rctiObj.destination = data[7]
                        rctiObj.cubicMiAndKmsCost = data[9]
                        rctiObj.cartageTotal = data[9]
                        dataList = data[10:]
                    else:
                        dataList = data[3:]
                        
                    while dataList:
                        if 'standby' in dataList[0].lower():
                            rctiObj.standByPerHalfHourDuration = dataList[1]
                            rctiObj.standByTotal =dataList[1]
                        elif 'sat' in dataList[0].lower() or 'mon-fri' in dataList[0].lower():
                            rctiObj.surchargeCost = dataList[1]
                            rctiObj.surchargeTotal = dataList[1]
                        elif 'wait' in dataList[0].lower():
                            rctiObj.waitingTimeCost = dataList[1]
                            rctiObj.waitingTimeTotal = dataList[1]
                        elif 'blowback' in dataList[0].lower():
                            rctiObj.blowBackCost = dataList[1]
                            rctiObj.blowBackTotal = dataList[1]
                        elif 'topup' in dataList[0].lower().replace(' ',''):
                            rctiErrorObj.clientName = 'boral'
                            rctiErrorObj.docketNumber = rctiObj.docketNumber
                            rctiErrorObj.docketDate = rctiObj.docketDate
                            rctiErrorObj.errorDescription = "Manage Top-up."
                            rctiErrorObj.fileName = fileName
                            rctiErrorObj.data = str(data)
                            rctiErrorObj.save()
                            
                        elif 'trucktrf' in dataList[0].lower():
                            rctiObj.transferKMCost = dataList[1]
                            rctiObj.transferKMTotal = dataList[1]
                        elif 'return' in dataList[0].lower():
                            rctiObj.returnPerKmPerCubicMeterCost = dataList[1]
                            rctiObj.returnKmTotal = dataList[1]
                        elif 'callout' in dataList[0].lower():
                            rctiObj.callOutCost = dataList[1]
                            rctiObj.callOutTotal = dataList[1]
                        else:
                            rctiObj.otherDescription = dataList[0]
                            rctiObj.othersCost = dataList[1]
                            rctiObj.othersTotal = dataList[1]
                        dataList = dataList[2:]
                    rctiObj.rctiReport = rctiReportObj
                    rctiObj.save()
                else:
                    with open('holcim.txt','a')as f:
                        f.write('skip'+ str(data) +'\n')
            except Exception as e:
                with open('holcim.txt','a')as f:
                    f.write('error' +str(e) + str(data) +'\n')

    except Exception as e:
        with open('holcim.txt','a')as f:
            f.write('outside error' +str(e) +'\n')
        
        


