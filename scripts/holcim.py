from Account_app.models import *
import pandas as pd
from GearBox_app.models import *
from CRUD import *
from datetime import datetime
from Account_app.reconciliationUtils import  *
from datetime import time

def dateConvert(dataList,type_):
    try:
        if dataList.lower() != 'nan':
            timestamp_obj = datetime.strptime(dataList, '%d/%m/%Y %I:%M:%S %p')
            if type_ =='date':
                date_only_str = timestamp_obj.strftime('%Y-%m-%d')
                return date_only_str
            elif type_ == 'time':
                time_only_str = timestamp_obj.strftime('%H:%M:%S')
                return time_only_str
        else:
            date_only_str = None  
        return date_only_str
    except Exception as e:
        return None
    

def dateTimeConvert(dataList):
    try:
        if pd.isna(dataList) or str(dataList).lower() == 'nan':
            return None
        else:
            try:
                timestamp_obj = datetime.strptime(str(dataList),  '%Y-%m-%d %H:%M:%S')
            except: 
                timestamp_obj = datetime.strptime(str(dataList), '%d/%m/%Y %I:%M:%S %p')
            formatted_timestamp = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')
            return formatted_timestamp
    except ValueError as e:
        return None
    
    
    
def run():
    f = open(r"pastTrip_entry.txt", 'r')
    file_name = f.read()
    
    monthFileName = open(r"pastTrip_entry_month.txt",'r')
    monthAndYear = monthFileName.read()

    fileName = f'static/Account/PastTripsEntry/{file_name}'

    txtFile = open(r'static/subprocessFiles/errorFromPastTrip.txt','w')
    txtFile.write(f'File:{file_name}\n\n')
    txtFile.close()

    with open(fileName, 'r') as pastData:
        count = 0
        for line in pastData:
            # try:
            if '"' in line:
                line = str(line).replace('"','')
            if "'" in line:
                line =  str(line).replace("'","")
            data = line.split(',')
            # dataList = data
            count+=1
            
            if len(data) == 44 and data[0] != '' and data[2] != '':
                try:
                    tripDate = dateConvert(str(data[8]),'date')
                    if tripDate.split('-')[1] != monthAndYear.split('-')[-1] or tripDate.split('-')[0] != monthAndYear.split('-')[0]:
                        pastTripErrorObj = PastTripError(
                                    clientName = 'holcim',
                                    tripDate = tripDate,
                                    docketNumber = str(data[4]),
                                    truckNo = int(data[0]),
                                    lineNumber = count,
                                    errorFromPastTrip = "Incorrect month/year values present in file.",
                                    fileName = fileName.split('@_!')[-1],
                                    data = data
                                ) 
                        pastTripErrorObj.save()
                        continue
                    driverId = Driver.objects.filter(name = data[40].strip().replace(' ','').lower()).first()
                    # print(driverId,data[40].strip().replace(' ','').lower())
                    # exit()
                    if driverId is None:
                        pastTripErrorObj = PastTripError(
                            clientName = 'holcim',
                            tripDate = tripDate,
                            docketNumber = str(data[4]),
                            truckNo = int(data[0]),
                            lineNumber = count,
                            errorFromPastTrip = 'Driver matching query does not exist.',
                            fileName = fileName.split('@_!')[-1],
                            data = data
                        )
                        pastTripErrorObj.save()
                        continue
                    existingTrip = HolcimTrip.objects.filter(truckNo = int(data[0]) , shiftDate = tripDate).values().first()
                    if existingTrip:
                        holcimTripObj = HolcimTrip.objects.get(pk=existingTrip['id'])
                    else:
                        holcimTripObj = HolcimTrip(
                            truckNo = int(data[0]),
                            shiftDate = tripDate
                        )
                        holcimTripObj.save()
                    existingDockets = HolcimDocket.objects.filter(tripId = holcimTripObj.id).count()
                    currentMatchingDocket = HolcimDocket.objects.filter(tripId =  holcimTripObj.id,jobNo = data[4] ,ticketedDate = tripDate).first()
                    if currentMatchingDocket:
                        pastTripErrorObj = PastTripError(
                        clientName = 'holcim',
                        tripDate = tripDate,
                        docketNumber = str(data[4]),
                        truckNo = int(data[0]),
                        lineNumber = count,
                        errorFromPastTrip = 'Docket already exist.',
                        fileName = fileName.split('@_!')[-1],
                        data = data
                        )
                        pastTripErrorObj.save()
                        continue
                    
                     
                    client = Client.objects.filter(name = 'holcim').first()
                    adminTruckObj = AdminTruck.objects.filter(adminTruckNumber = holcimTripObj.truckNo).first()
                    clientTruckConnectionObj = ClientTruckConnection.objects.filter(truckNumber = adminTruckObj,startDate__lte = holcimTripObj.shiftDate,endDate__gte = holcimTripObj.shiftDate, clientId = client).first()
                    
                    if clientTruckConnectionObj is None:
                        pastTripErrorObj = PastTripError(
                            clientName = 'holcim',
                            tripDate = tripDate,
                            docketNumber = str(data[4]),
                            truckNo = int(data[0]),
                            lineNumber = count,
                            errorFromPastTrip = 'Client truck connection object does not exist.',
                            fileName = fileName.split('@_!')[-1],
                            data = data
                        )
                        pastTripErrorObj.save()
                        continue

                    holcimDocketObj = HolcimDocket()
                    holcimDocketObj.truckNo  = int(data[0])
                    holcimDocketObj.tripId  = holcimTripObj
                    holcimDocketObj.jobNo  =  data[4]
                    if holcimDocketObj.jobNo == 'nan':
                        pastTripErrorObj = PastTripError(
                            clientName = 'holcim',
                            tripDate = tripDate,
                            docketNumber = str(data[4]),
                            truckNo = int(data[0]),
                            lineNumber = count,
                            errorFromPastTrip = 'Job No. Missing.',
                            fileName = fileName.split('@_!')[-1],
                            data = data
                        )
                        pastTripErrorObj.save()
                        continue
                    holcimDocketObj.orderNo  = 0 if str(data[2]) == 'nan' else data[2]
                    holcimDocketObj.status  = 0 if str(data[6]) == 'nan' else data[6]
                    holcimDocketObj.ticketedDate  =  dateConvert(data[8],'date')
                    holcimDocketObj.ticketedTime  =  dateConvert(data[8],'time')
                    if holcimDocketObj.ticketedDate is None:
                        pastTripErrorObj = PastTripError(
                            clientName = 'holcim',
                            tripDate = tripDate,
                            docketNumber = str(data[4]),
                            truckNo = int(data[0]),
                            lineNumber = count,
                            errorFromPastTrip = 'Ticketed Missing.',
                            fileName = fileName.split('@_!')[-1],
                            data = data
                        )
                        pastTripErrorObj.save()
                        continue
                    holcimDocketObj.load  =  dateTimeConvert(data[13])
                    holcimDocketObj.loadComplete  = 0 if str(data[15]) == '' else data[15]
                    holcimDocketObj.toJob  =  dateTimeConvert(data[16])
                    holcimDocketObj.timeToDepart  = 0 if str(data[18]) == '' else data[18]
                    holcimDocketObj.onJob  =  dateTimeConvert(data[19])
                    holcimDocketObj.timeToSite  = 0 if str(data[21]) == '' else data[21]
                    holcimDocketObj.beginUnload  = dateTimeConvert(data[22])
                    holcimDocketObj.waitingTime  = 0 if str(data[24]) == '' else data[24]
                    holcimDocketObj.endPour  = dateTimeConvert(data[25])
                    holcimDocketObj.wash  =dateTimeConvert(data[26])
                    holcimDocketObj.toPlant  =  dateTimeConvert(data[27])
                    holcimDocketObj.timeOnSite  = 0 if str(data[32]) == '' else data[32]
                    holcimDocketObj.atPlant  =  dateTimeConvert(data[33])
                    holcimDocketObj.leadDistance  = 0 if str(data[35]) == '' else data[35]
                    holcimDocketObj.returnDistance  = 0 if str(data[36]) == '' else data[36]
                    holcimDocketObj.totalDistance  = 0 if str(data[37]) == '' else data[37]
                    holcimDocketObj.totalTime  = 0 if str(data[38]) == '' else data[38]
                    holcimDocketObj.waitTimeBetweenJob  = 0 if str(data[39]) == '' else data[39]
                    holcimDocketObj.driverName  = driverId #data[40]
                    holcimDocketObj.quantity  = 0 if str(data[41]) == '' else data[41]
                    holcimDocketObj.slump  = 0 if str(data[42]) == '' else data[42]
                    holcimDocketObj.waterAdded  = 0 if str(data[43]).strip() == '' else str(data[43]).replace('L','').strip()
                    holcimDocketObj.save()
                    holcimTripObj.numberOfLoads = existingDockets + 1
                    holcimTripObj.save()
                except Exception as e:
                    pastTripErrorObj = PastTripError(
                        clientName = 'holcim',
                        tripDate = tripDate,
                        docketNumber = str(data[4]),
                        truckNo = int(data[0]),
                        lineNumber = count,
                        errorFromPastTrip = e,
                        fileName = fileName.split('@_!')[-1],
                        data = data
                    )
                    pastTripErrorObj.save()
            else:
                pass
                
                        
                
