import re,sys,os, shutil , csv
from datetime import datetime
import numpy as np

def checkDate(givenDate):
    pattern = r'\d{2}/\d{2}/\d{2}'
    return True if re.fullmatch(pattern,givenDate) else False

def checkStr(data:str):
    return data.lower().strip().replace(" ","")

def convertIntoFloat(str_):
    if '(' in str_:
        str_ = '-'+str_.strip('()')
        cleaned_string = str_.replace(' ','').replace(',','')
        return str(float(cleaned_string))
    else:
        return str_

def setEarningLine(dataList:list, dateGiven=None, docketNumber=None , basePlant = None):
    float(dataList[-1].replace(',',''))
    tempList = []
    try:
        float(dataList[-6])
    except:
        dataList[-5] = dataList[-6] + dataList[-5] 
        del(dataList[-6])    
    try:
        float(dataList[-7])
    except:
        dataList.insert(-6,'')
    
    if dateGiven == True and docketNumber:
        tempList.extend([docketNumber] + dataList[:2] +  [' '.join(dataList[2:-7])] + dataList[-7:])
    elif dateGiven and docketNumber:
        tempList.extend([docketNumber, dateGiven, dataList[0]] +  [' '.join(dataList[1:-7])] + dataList[-7:])
    else:
        if basePlant:
            tempList.extend(dataList[:3] + [' '.join(dataList[3:-7])] + dataList[-7:])
        else:  
            tempList.extend(dataList[:3] + [' '.join(dataList[3:-7])] + dataList[-7:])
        
    return tempList
   
def setExpenseLine(dataList:list, docketNumber=None, expenseDate=None):
    tempList = []
    if expenseDate and docketNumber:
        tempList.extend([docketNumber, expenseDate, dataList[0]] + [' '.join(dataList[1:-6])] + dataList[-6:])
    elif docketNumber:
        tempList.extend([docketNumber] + dataList[:2] + [' '.join(dataList[2:-6])] + dataList[-6:])
    else:
        tempList.extend(dataList[:3] + [' '.join(dataList[3:-6])] + dataList[-6:])
    return tempList
    
def setTopUp(dataList:list):
    try:
        if float(dataList[-5]):
            dataList.insert(-4, '')
    except:
        pass
    return dataList[:2] + [''] + [' '.join(dataList[2:-6])] + [''] + dataList[-6:]

args = sys.argv[-1]
# args = '20240105051933@_!Boral-30-Jun-2023.csv'

file_path = 'static/Account/RCTI/tempRCTIInvoice/' + args
# file_path = args

converted_earning_file_name = "earning_converted_" + args 
converted_expense_file_name = "expenses_converted_" + args

with open("File_name_file.txt",'w+',encoding='utf-8') as f:
    f.write(f'{converted_earning_file_name}<>{converted_expense_file_name}')
    f.close()

carter_no = r'(\d+)\s+Truck\s+(\w+)'
docket_pattern = r'^\d{8}$|^\d{6}$|^INV-\d+$'
expensePattern = r"^(?!.*\b\d{2}/\d{2}/\d{4}\b)(?:[A-Za-z]+\d+|\d+)$"
expenseDocket = "0000000"

fileData = None
truckNo = None

earningFlag = False
expenseFlag = False

previousLine = []
finalEarningList = []
finalExpenseList = []
docketNumber = None
docketDate = None
lineCount = 0
ignoreKeywords = ["docketdeliverysourcedescription", "no.datekm'squantity", "vendor", "pobox", "page", "document", "date:"]
extraDescriptions = ['kmpercum','cum','m','percum','perkmpercum','perkmpercuum', 'otherperkmpercum','avem']
errorsList = ['topup','adjustmen','jindabyneaccomodation','blowback','minimumpayment']

with open (file_path, 'r') as f:
    fileData = csv.reader(f)
    for data in fileData:
        lineCount+=1
        # if lineCount == 2579:
        #     pass
        data = data[0]
        if any(key in checkStr(data) for key in ignoreKeywords):
            continue
        elif 'totalearnings' in checkStr(data) or 'totalexpenses' in checkStr(data):
            if earningFlag and len(previousLine) > 0:
                if len(finalEarningList) > 0:
                    for line in finalEarningList:
                        if truckNo == line[0] and line[1] == docketNumber and line[2] == docketDate:
                            line.extend(previousLine)
                            previousLine = []
                            break
                    
                if len(previousLine) > 0:
                    finalEarningList.append([truckNo] + previousLine)

            elif expenseFlag and len(previousLine) > 0:
                finalExpenseList.append([truckNo]+previousLine)
            previousLine = []
            earningFlag = False
            expenseFlag = False
            continue
        elif 'carterno' in checkStr(data):
            truckNo = data.split(',')[1].split()[-1]
            continue
        elif 'earnings' in checkStr(data):
            earningFlag = True
            expenseFlag = False
            continue
        elif 'expenses' in checkStr(data):
            earningFlag = False
            expenseFlag = True
            continue
            
        dataList = data.split()
        try:
            if dataList:
                if  any( value in checkStr(data)  for value in errorsList) :
                    if re.match(docket_pattern,dataList[0]):
                        
                        if len(previousLine) > 0:
                            if len(finalEarningList) > 0:
                                for line in finalEarningList:
                                    if truckNo == line[0] and line[1] == docketNumber and line[2] == docketDate:
                                        line.extend(previousLine)
                                        previousLine = []
                                        break
                                
                            if len(previousLine) > 0:
                                finalEarningList.append([truckNo] + previousLine)
                                previousLine = []
                        docketNumber = dataList[0]
                        docketDate = dataList[1]
                    elif checkDate(dataList[0]):
                        docketDate = dataList[0]
                    finalEarningList.append([truckNo +' '+ data])
                elif 'tolls' in checkStr(data):
                    finalEarningList.append([data])
                    
                elif earningFlag:
                    try:
                        dataList[-1] =convertIntoFloat(dataList[-1])
                        dataList[-2] =convertIntoFloat(dataList[-2])
                        dataList[-3] =convertIntoFloat(dataList[-3])
                        if re.match(docket_pattern,dataList[0]):
                            
                            if len(previousLine) > 0:
                                if len(finalEarningList) > 0:
                                    for line in finalEarningList:
                                        if truckNo == line[0] and line[1] == docketNumber and line[2] == docketDate:
                                            line.extend(previousLine)
                                            previousLine = []
                                            break
                                    
                                if len(previousLine) > 0:
                                    finalEarningList.append([truckNo] + previousLine)
                                    previousLine = []
                            docketNumber = dataList[0]
                            docketDate = dataList[1]
                            
                            dataList = setEarningLine(dataList=dataList)
                        elif checkDate(dataList[0]):
                            dataList = setEarningLine(dataList=dataList,dateGiven=True, docketNumber=docketNumber)
                        else:
                            if len(previousLine) > 0:
                                dataList = setEarningLine(dataList=dataList,dateGiven=docketDate, docketNumber=docketNumber)
                            else:
                                dataList = setEarningLine(dataList=dataList,dateGiven=docketDate, docketNumber=docketNumber)
                                
                        previousLine.extend(dataList)  
                    except:
                        if re.match(docket_pattern,dataList[0]):
                            if previousLine:
                                if docketNumber == dataList[0] and docketDate == dataList[1] and previousLine[2] == dataList[2]:
                                    previousLine[-8]+= ' ' + ' '.join(dataList[3:])
                                    dataList = []
                            if len(dataList) > 0:
                                for line in finalEarningList:
                                    if truckNo == line[0] and line[1] == dataList[0] and line[2] == dataList[1]:
                                        line[-8] += ' ' + ' '.join(dataList[3:])
                                        break
                        elif checkDate(dataList[0]):
                            previousLine[-9]+=' '.join(dataList[2:])
                        else:
                            if previousLine[2] == dataList[0]:
                                previousLine[-8] += ' ' + ' '.join(dataList[1:])
                            elif any(checkStr(''.join(dataList)) == value for value in extraDescriptions):
                                previousLine[-8] +=  ' ' + ' '.join(dataList)
                            else:
                                # print('186',dataList)
                                pass
                elif expenseFlag:
                    try:
                        if re.match(expensePattern, dataList[0]):
                            expenseDocket = dataList[0]
                            dataList = setExpenseLine(dataList=dataList)
                        elif checkDate(dataList[0]):
                            dataList = setExpenseLine(dataList=dataList, docketNumber = expenseDocket)
                        else:
                            dataList = setExpenseLine(dataList=dataList, docketNumber=expenseDocket, expenseDate = finalExpenseList[-1][2])
                        
                        finalExpenseList.append([truckNo] + dataList)
                        dataList = []
                    except:
                        # print(f"138{dataList}\n")
                        pass
                
                else:
                    # print(f"140: {dataList}\n")
                    pass
        except:
            # print(f"163:{dataList}\n")
            pass
            
                     
if len(finalEarningList) > 0:
    myFile = open('static/Account/RCTI/RCTIInvoice/' + converted_earning_file_name, 'a', newline='')
    writer = csv.writer(myFile)
    writer.writerows(finalEarningList)
    myFile.close()
if len(finalExpenseList) > 0:
    myFile = open('static/Account/RCTI/RCTIInvoice/' + converted_expense_file_name, 'a', newline='')
    writer = csv.writer(myFile)
    writer.writerows(finalExpenseList)
    myFile.close()
