# import pandas as pd
from Account_app.models import *
from GearBox_app.models import *
from CRUD import *
from datetime import datetime
from Account_app.reconciliationUtils import  *
from datetime import time

def run():
    f = open(r"pastTrip_entry.txt", 'r')
    file_name = f.read()
    
    monthFileName = open(r"pastTrip_entry_month.txt",'r')
    monthAndYear = monthFileName.read()

    fileName = f'static/Account/PastTripsEntry/{file_name}'
    # fileName = f'static/Account/PastTripsEntry/20231202141345@_!20231202112629@_!April1-152023.csv'

    txtFile = open(r'static/subprocessFiles/errorFromPastTrip.txt','w')
    txtFile.write(f'File:{file_name}\n\n')
    txtFile.close()

    with open(fileName, 'r') as pastData:
        count = 0
        for line in pastData:
            try:
                if '"' in line:
                   line = str(line).replace('"','')
                if "'" in line:
                   line =  str(line).replace("'","")
                count += 1
                if count == 1:
                    continue
                data = line.split(',')
                
                # if count == 112:
                #     print(data)
                #     exit()
                # else:
                #     continue

                if len(data) != 25:
                    pastTripErrorObj = PastTripError(
                                    clientName = 'boral',
                                    tripDate = res_,
                                    docketNumber = data[5],
                                    truckNo = data[1],
                                    lineNumber = count,
                                    errorFromPastTrip = "File Data in wrong format.",
                                    fileName = fileName.split('@_!')[-1],
                                    data = data
                                )                    
                    pastTripErrorObj.save()
                    continue
                
                        
                
                if ' ' in str(data[0]):
                    res_ = str(data[0]).split()[0]
                elif '/' in str(data[0]):
                    str_ = str(data[0]).split('/')
                    res_ = str_[-1]+'-'+str_[-2]+'-'+str_[0]
                else:
                    res_ = str(data[0])

                # with open(r'pastDataRow.txt','a') as f:
                #     f.write(str(data[0]) + '\n')
                # print(count)
                res_pythonDate = datetime.strptime(res_, '%Y-%m-%d')
                
                if res_.split('-')[1] != monthAndYear.split('-')[-1] or res_.split('-')[0] != monthAndYear.split('-')[0]:
                    pastTripErrorObj = PastTripError(
                                clientName = 'boral',
                                tripDate = res_,
                                docketNumber = data[5],
                                truckNo = data[1],
                                lineNumber = count,
                                errorFromPastTrip = "Incorrect month/year values present in file.",
                                fileName = fileName.split('@_!')[-1],
                                data = data
                            ) 
                            # print('grace card not found')                   
                    pastTripErrorObj.save()
                    continue
                    
                existingTrip = None

                driverName = data[4].strip().replace(' ','').lower()
                client = Client.objects.filter(name = 'boral').first()
                
                driver = Driver.objects.filter(name = driverName).first()
                if driver:
                    # Trip save
                    try:
                        existingTrip = DriverTrip.objects.filter(truckNo = data[1],shiftDate = res_pythonDate).values().first()
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
                                    lineNumber = count,
                                    errorFromPastTrip = "BasePlant does not exist.",
                                    fileName = fileName.split('@_!')[-1],
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
                        # clientTruckConnectionQrySet = ClientTruckConnection.objects.filter(truckNumber = adminTruckObj, clientId = tripObj.clientName)
                        # clientTruckConnectionObj = None
                        
                        # for obj in clientTruckConnectionQrySet:
                        # #     # with open(r'pastDataRow.txt','a') as f:
                        # #     #     f.write(str(type(obj.startDate)) + ' ' + str(type(tripObj.shiftDate)) + '\n')
                        #     if type(tripObj.shiftDate) == type(obj.startDate):
                        #         if obj.startDate.strftime('%Y-%m-%d') <= tripObj.shiftDate.strftime('%Y-%m-%d') and obj.endDate.strftime('%Y-%m-%d') >= tripObj.shiftDate.strftime('%Y-%m-%d'):
                        #             clientTruckConnectionObj = obj  
                        #             # print('Client truck connection found')
                        #             break
                        #         # else:
                        #             # print('Client truck connection NOT found') 
                        #     else:
                        #         if obj.startDate.strftime('%Y-%m-%d') <= tripObj.shiftDate and obj.endDate.strftime('%Y-%m-%d') >= tripObj.shiftDate:
                        #             clientTruckConnectionObj = obj  
                        #             break
                                    
                            
                            
                        # with open(r'pastDataRow.txt','a') as f:
                        #     f.write(str(adminTruckObj.adminTruckNumber) + ' ' + str( tripObj.shiftDate) + ' ' + str(tripObj.clientName.name) + '\n')
                        
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
                                    lineNumber = count,
                                    errorFromPastTrip = "No matching grace card for the date.",
                                    fileName = fileName.split('@_!')[-1],
                                    data = data
                                ) 
                                # print('grace card not found')                   
                                pastTripErrorObj.save()
                                continue
                            
                            # print("GRACE found")
                            
                            # if int(data[13]) > int(graceObj.waiting_time_grace_in_minutes):
                            #     totalWaitingTime = int(data[13]) - graceObj.waiting_time_grace_in_minutes
                            # else:
                            #     totalWaitingTime = 0
                            costParameterObj = CostParameters.objects.filter(rate_card_name = rateCard).first()

                            if not costParameterObj:
                                pastTripErrorObj = PastTripError(
                                    clientName = 'boral',
                                    tripDate = res_,
                                    docketNumber = data[5],
                                    truckNo = data[1],
                                    lineNumber = count,
                                    errorFromPastTrip = "No matching cost parameter card for the date.",
                                    fileName = fileName.split('@_!')[-1],
                                    data = data
                                )                    
                                pastTripErrorObj.save()
                                # print('COST PARAMETER not found')
                                continue
                                
                            # print("COST PARAMETER found!!!")
                            # if str(data[20]).lower() != '' or str(data[21]).lower() != '':
                            #     start = datetime.strptime(str(data[20]),'%H:%M:%S')
                            #     end = datetime.strptime(str(data[21]),'%H:%M:%S')
                            #     totalStandByTime = ((end-start).total_seconds())/60
                            #     # totalStandByTime = getTimeDifference(data[20],data[21])
                            #     if totalStandByTime > graceObj.chargeable_standby_time_starts_after:
                            #         totalStandByTime = totalStandByTime - graceObj.standby_time_grace_in_minutes
                            #         standBySlot = totalStandByTime//costParameterObj.standby_time_slot_size
                            # else:
                            #     standBySlot = 0
                                
                            docketObj.shiftDate = ' ' if str(data[0]).lower() == '' else res_
                            docketObj.tripId = tripObj
                            docketObj.docketNumber = data[5]
                            docketObj.noOfKm = 0 if str(data[10]).lower() == '' else data[10]
                            docketObj.transferKM = 0 if str(data[18]).lower() == '' else data[18]
                            docketObj.returnToYard = True if data[16].lower() == 'yes' else False
                            docketObj.returnQty = 0 if str(data[14]).lower() == '' else data[14]
                            docketObj.returnKm = 0 if str(data[15]).lower() == '' else data[15]
                            docketObj.waitingTimeStart = '00:00:00' if str(data[11]).strip().lower() == '' else str(datetime.strptime(data[11], '%H:%M:%S').time()) 
                            docketObj.waitingTimeEnd = '00:00:00' if str(data[12]).strip().lower() == '' else str(datetime.strptime(data[12], '%H:%M:%S').time())
                            # docketObj.totalWaitingInMinute = totalWaitingTime
                            docketObj.cubicMl = 0 if str(data[8]).lower() == '' else data[8]
                            docketObj.standByStartTime ='00:00:00' if str(data[20]).lower() == '' else str(datetime.strptime(data[20], '%H:%M:%S').time())
                            docketObj.standByEndTime ='00:00:00' if str(data[21]).lower() == '' else str(datetime.strptime(data[21], '%H:%M:%S').time())
                            # docketObj.standBySlot = standBySlot
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
                            slotSize = DriverTripCheckStandByTotal(int(docketObj.docketNumber),docketObj.shiftDate)
                            driverStandByCost = round(costParameterObj.standby_cost_per_slot * slotSize,2)
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
                            # missingComponents 
                            checkMissingComponents(reconciliationDocketObj)
                            # print("reconciliation done!!!!")
                        
                        else:
                            pastTripErrorObj = PastTripError(
                                clientName = 'boral',
                                tripDate = res_,
                                docketNumber = data[5],
                                truckNo = data[1],
                                lineNumber = count,
                                errorFromPastTrip = "Client truck connection object does not exist.",
                                fileName = fileName.split('@_!')[-1],
                                data = data
                            )
                            pastTripErrorObj.save()
                    except Exception as e:       
                        pastTripErrorObj = PastTripError(
                            clientName = 'boral',
                            tripDate = res_,
                            docketNumber = data[5],
                            truckNo = data[1],
                            lineNumber = count,
                            errorFromPastTrip = e,
                            fileName = fileName.split('@_!')[-1],
                            data = data
                        )
                        pastTripErrorObj.save()
                else:
                    pastTripErrorObj = PastTripError(
                            clientName = 'boral',
                            tripDate = res_,
                            docketNumber = data[5],
                            truckNo = data[1],
                            lineNumber = count,
                            errorFromPastTrip = 'Driver matching query does not exist.',
                            fileName = fileName.split('@_!')[-1],
                            data = data
                        )
                    pastTripErrorObj.save()
                    
                    
            except Exception as e:
                pastTripErrorObj = PastTripError(
                        clientName = 'boral',
                        tripDate = res_,
                        docketNumber = data[5],
                        truckNo = data[1],
                        lineNumber = count,
                        errorFromPastTrip = e,
                        fileName = fileName.split('@_!')[-1],
                        data = data
                    )
                pastTripErrorObj.save()
                
