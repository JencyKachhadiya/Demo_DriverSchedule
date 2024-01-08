from Account_app.models import *
from GearBox_app.models import *
from CRUD import *
from datetime import datetime
from Account_app.reconciliationUtils import  *
from datetime import time
import sys


f = open(r"scripts/addPastTripForMissingDriver.txt", 'r')
driverName = f.read()
# data = data.split(',')[0:-1]

matchingData = PastTripError.objects.filter(errorFromPastTrip="Driver matching query does not exist.", status=False)

for i in matchingData:
    try:
        data = i.data
        data = data.replace('[','').replace(']','').replace('\\n','').replace("'",'')
        data = data.split(',')
        

        pastDriver = data[4].strip().replace(' ','').lower()
        if ' ' in str(data[0]):
            res_ = str(data[0]).split()[0]
        elif '/' in str(data[0]):
            str_ = str(data[0]).split('/')
            res_ = str_[-1]+'-'+str_[-2]+'-'+str_[0]
        else:
            res_ = str(data[0])
        res_pythonDate = datetime.strptime(res_, '%Y-%m-%d')
        driver = Driver.objects.filter(name =pastDriver).first()
        client = Client.objects.filter(name = 'boral').first()

        if pastDriver == driverName:
            i.status = True
            i.save()
            try:
                shiftType = 'Day'
                shiftDate = res_
                existingTrip = DriverTrip.objects.filter(truckNo = data[1],shiftDate = res_pythonDate).values().first()
                tripObj = None
                if existingTrip:
                    tripObj = DriverTrip.objects.filter(pk=existingTrip['id']).first()
                else:
                    shiftType = 'Day'
                    shiftDate =  res_
                    tripObj = DriverTrip(
                        verified = True,
                        driverId = driver,
                        clientName = client,
                        shiftType = shiftType,
                        truckNo = data[1],
                        shiftDate = shiftDate
                    )
                    tripObj.save()

                
                tripObjID = tripObj.id
                # Docket save
                existingDockets = DriverDocket.objects.filter(tripId = tripObj.id).count()
                tripObj.numberOfLoads = existingDockets + 1
                
                if tripObj.startTime and tripObj.endTime :
                    tripObj.startTime = getMaxTimeFromTwoTime(str(tripObj.startTime),str(data[6]),'min').strip()
                    tripObj.endTime = getMaxTimeFromTwoTime(str(tripObj.endTime),str(data[7])).strip()
                else:
                    tripObj.startTime =str(data[6]).strip()
                    tripObj.endTime = str(data[7]).strip()
                                    
                tripObj.save()
                tripObj = DriverTrip.objects.get(pk=tripObjID)
                
                basePlant = BasePlant.objects.filter(basePlant = data[24].strip().upper()).first() 
                # modified for adding 
                if basePlant is None:
                    pastTripErrorObj = PastTripError(
                            clientName = 'boral',
                            tripDate = res_,
                            docketNumber = data[5],
                            truckNo = data[1],
                            lineNumber = i.lineNumber,
                            errorFromPastTrip = "BasePlant does not exist.",
                            fileName = i.fileName.split('@_!')[-1],
                            data = data
                        ) 
                        # print('grace card not found')                   
                    pastTripErrorObj.save()
                    continue
                    # Modification ends
                
                surCharge = Surcharge.objects.filter(surcharge_Name = 'No Surcharge').first()
                    
                docketObj = DriverDocket()                

                adminTruckObj = AdminTruck.objects.filter(adminTruckNumber = tripObj.truckNo).first()
                clientTruckConnectionObj = ClientTruckConnection.objects.filter(truckNumber = adminTruckObj,startDate__lte = tripObj.shiftDate,endDate__gte = tripObj.shiftDate, clientId = tripObj.clientName).first()

                if clientTruckConnectionObj:
                    # print("finding ratecard")
                    rateCard = clientTruckConnectionObj.rate_card_name                        
                    graceObj = Grace.objects.filter(rate_card_name = rateCard,start_date__lte = tripObj.shiftDate,end_date__gte = tripObj.shiftDate).first()
                    if not graceObj:
                        pastTripErrorObj = PastTripError(
                            clientName = 'boral',
                            tripDate = res_,
                            docketNumber = data[5],
                            truckNo = data[1],
                            lineNumber = i.lineNumber,
                            errorFromPastTrip = "No matching grace card for the date.",
                            fileName = i.fileName.split('@_!')[-1],
                            data = data
                        ) 
                        # print('grace card not found')                   
                        pastTripErrorObj.save()
                        continue
                    
                    # print("GRACE found")
                    
                    if int(data[13]) > int(graceObj.waiting_time_grace_in_minutes):
                        totalWaitingTime = int(data[13]) - graceObj.waiting_time_grace_in_minutes
                    else:
                        totalWaitingTime = 0
                    costParameterObj = CostParameters.objects.filter(rate_card_name = rateCard).first()

                    if not costParameterObj:
                        pastTripErrorObj = PastTripError(
                            clientName = 'boral',
                            tripDate = res_,
                            docketNumber = data[5],
                            truckNo = data[1],
                            lineNumber = i.lineNumber,
                            errorFromPastTrip = "No matching cost parameter card for the date.",
                            fileName = i.fileName.split('@_!')[-1],
                            data = data
                        )                    
                        pastTripErrorObj.save()
                        # print('COST PARAMETER not found')
                        continue
                        
                    # print("COST PARAMETER found!!!")
                    standBySlot = 0
                    try:
                        if str(data[20]).strip() != '' or str(data[21]).strip() != '':
                            start = datetime.strptime(str(data[20].strip()),'%H:%M:%S')
                            end = datetime.strptime(str(data[21].strip()),'%H:%M:%S')
                            totalStandByTime = ((end-start).total_seconds())/60
                            if totalStandByTime > graceObj.chargeable_standby_time_starts_after:
                                totalStandByTime = totalStandByTime - graceObj.standby_time_grace_in_minutes
                                standBySlot = totalStandByTime//costParameterObj.standby_time_slot_size
                                
                        else:
                            standBySlot = 0
                    except Exception as e:
                        pastTripErrorObj = PastTripError(
                                        clientName = 'boral',
                                        tripDate = res_,
                                        docketNumber = data[5],
                                        truckNo = data[1],
                                        lineNumber = i.lineNumber,
                                        errorFromPastTrip = 'time convert problem',
                                        fileName = i.fileName.split('@_!')[-1],
                                        data = data
                                    )
                        pastTripErrorObj.save()
                        continue
                        
                    docketObj.shiftDate = ' ' if str(data[0]).strip().lower() == '' else res_
                    docketObj.tripId = tripObj
                    docketObj.docketNumber = data[5]
                    docketObj.noOfKm = 0 if str(data[10]).strip().lower() == '' else data[10]
                    docketObj.transferKM = 0 if str(data[18]).strip().lower() == '' else data[18]
                    docketObj.returnToYard = True if data[16].strip().lower() == 'yes' else False
                    docketObj.returnQty = 0 if str(data[14]).strip().lower() == '' else data[14]
                    docketObj.returnKm = 0 if str(data[15]).strip().lower() == '' else data[15]
                    docketObj.waitingTimeStart = 0 if str(data[11]).strip().lower() == '' else data[11].strip()
                    docketObj.waitingTimeEnd = 0 if str(data[12]).strip().lower() == '' else data[12].strip()
                    docketObj.totalWaitingInMinute = totalWaitingTime
                    docketObj.cubicMl = 0 if str(data[8]).strip().lower() == '' else data[8]
                    docketObj.standByStartTime = 0 if str(data[20]).strip().lower() == '' else data[20].strip()
                    docketObj.standByEndTime = 0 if str(data[21]).strip().lower() == '' else data[21].strip()
                    docketObj.standBySlot = standBySlot
                    docketObj.comment = data[17]
                    # modification for adding blow back and replacement.
                    if data[19].strip().replace(' ','') != None:
                        docketObj.comment = docketObj.comment + 'Blow back comment : ' + data[19].strip() 
                        
                    if data[23].strip().replace(' ','') != None:
                        docketObj.comment = docketObj.comment + 'Replacement comment : ' + data[23].strip() 
                        
                    
                    docketObj.basePlant = basePlant
                    docketObj.surcharge_type = surCharge
                    # surcharge_duration = 
                    # others = 
                    docketObj.save()
                    # print("docket saved!!!")
                        
                    reconciliationDocketObj = ReconciliationReport.objects.filter(docketNumber = int(docketObj.docketNumber) , docketDate = docketObj.shiftDate ).first()
                            
                    if not reconciliationDocketObj :
                        reconciliationDocketObj = ReconciliationReport()
                    
                    driverLoadAndKmCost = checkLoadAndKmCost(int(docketObj.docketNumber),docketObj.shiftDate)
                    driverSurchargeCost = checkSurcharge(int(docketObj.docketNumber),docketObj.shiftDate)
                    driverWaitingTimeCost = round(docketObj.totalWaitingInMinute * costParameterObj.waiting_cost_per_minute,2) 
                    driverStandByCost = round(costParameterObj.standby_cost_per_slot * docketObj.standBySlot,2)
                    driverTransferKmCost = checkTransferCost(int(docketObj.docketNumber),docketObj.shiftDate)
                    driverReturnKmCost = checkReturnCost(int(docketObj.docketNumber),docketObj.shiftDate)
                    # minLoad 
                    driverLoadDeficit = checkMinLoadCost(int(docketObj.docketNumber),docketObj.shiftDate)
                    # TotalCost 
                    driverTotalCost = driverLoadAndKmCost +driverSurchargeCost + driverWaitingTimeCost + driverStandByCost + driverTransferKmCost + driverReturnKmCost +driverLoadDeficit
                    reconciliationDocketObj.driverId = driver.driverId  
                    reconciliationDocketObj.clientId = client.clientId  
                    reconciliationDocketObj.truckId = data[1]   
                    reconciliationDocketObj.docketNumber = int(docketObj.docketNumber) 
                    reconciliationDocketObj.docketDate = docketObj.shiftDate  
                    reconciliationDocketObj.driverLoadAndKmCost = driverLoadAndKmCost 
                    reconciliationDocketObj.driverSurchargeCost = driverSurchargeCost 
                    reconciliationDocketObj.driverWaitingTimeCost = driverWaitingTimeCost 
                    reconciliationDocketObj.driverStandByCost = driverStandByCost 
                    reconciliationDocketObj.driverLoadDeficit = driverLoadDeficit 
                    reconciliationDocketObj.driverTransferKmCost = driverTransferKmCost 
                    reconciliationDocketObj.driverReturnKmCost = driverReturnKmCost  
                    reconciliationDocketObj.driverTotalCost = round(driverTotalCost,2) 
                    reconciliationDocketObj.fromDriver = True 
                    reconciliationDocketObj.save()
                    checkMissingComponents(reconciliationDocketObj)
                    
                else:
                    pastTripErrorObj = PastTripError(
                        clientName = 'boral',
                        tripDate = res_,
                        docketNumber = data[5],
                        truckNo = data[1],
                        lineNumber = i.lineNumber,
                        errorFromPastTrip = "Client truck connection object does not exist.",
                        fileName = i.fileName.split('@_!')[-1],
                        data = data
                    )
                    pastTripErrorObj.save()
                    continue
            except Exception as e:       
                pastTripErrorObj = PastTripError(
                    clientName = 'boral',
                    tripDate = res_,
                    docketNumber = data[5],
                    truckNo = data[1],
                    lineNumber = i.lineNumber,
                    errorFromPastTrip = e,
                    fileName = i.fileName.split('@_!')[-1],
                    data = data
                )
                pastTripErrorObj.save()
                continue
        else:
            continue
    except Exception as e:
        pastTripErrorObj = PastTripError(
            clientName = 'boral',
            tripDate = res_,
            docketNumber = data[5],
            truckNo = data[1],
            lineNumber = i.lineNumber,
            errorFromPastTrip = e,
            fileName = i.fileName.split('@_!')[-1],
            data = data
        )
        pastTripErrorObj.save()
    