from Account_app.models import *
from GearBox_app.models import *
from CRUD import *
from datetime import datetime
from Account_app.reconciliationUtils import  *
from datetime import time
import csv , re


f = open(r"scripts/addPastTripForMissingBasePlant.txt", 'r')
basePlantName = f.read()


# data = data.split(',')[0:-1]

# matchingData = PastTripError.objects.filter(errorFromPastTrip="BasePlant does not exist.", status=False)

# # For PastTrip 
# for i in matchingData:
#     try:
#         data = i.data
#         data = data.replace('[','').replace(']','').replace('\\n','').replace("'",'')
#         data = data.split(',')
        

#         pastBasePlant = data[-1].strip().replace(' ','').upper()
#         pastDriver = data[4].strip().replace(' ','').lower()
        
#         if ' ' in str(data[0]):
#             res_ = str(data[0]).split()[0]
#         elif '/' in str(data[0]):
#             str_ = str(data[0]).split('/')
#             res_ = str_[-1]+'-'+str_[-2]+'-'+str_[0]
#         else:
#             res_ = str(data[0])
#         res_pythonDate = datetime.strptime(res_, '%Y-%m-%d')
#         basePlant = BasePlant.objects.filter(basePlant =pastBasePlant).first()
#         driver = Driver.objects.filter(name =pastDriver).first()
#         client = Client.objects.filter(name = 'boral').first()
#         if pastBasePlant == basePlantName:
#             i.status = True
#             i.save()
#             try:
#                 shiftType = 'Day'
#                 shiftDate = res_
#                 existingTrip = DriverTrip.objects.filter(truckNo = data[1],shiftDate = res_pythonDate).values().first()
                
#                 tripObj = None
#                 if existingTrip:
#                     tripObj = DriverTrip.objects.filter(pk=existingTrip['id']).first()
#                 else:
#                     shiftType = 'Day'
#                     shiftDate =  res_
#                     tripObj = DriverTrip(
#                         verified = True,
#                         driverId = driver,
#                         clientName = client,
#                         shiftType = shiftType,
#                         truckNo = data[1],
#                         shiftDate = shiftDate
#                     )
#                     tripObj.save()

                
#                 tripObjID = tripObj.id
#                 # Docket save
#                 existingDockets = DriverDocket.objects.filter(tripId = tripObj.id).count()
#                 tripObj.numberOfLoads = existingDockets + 1
                
#                 if tripObj.startTime and tripObj.endTime :
#                     tripObj.startTime = getMaxTimeFromTwoTime(str(tripObj.startTime),str(data[6]),'min').strip()
#                     tripObj.endTime = getMaxTimeFromTwoTime(str(tripObj.endTime),str(data[7])).strip()
#                 else:
#                     tripObj.startTime =str(data[6]).strip()
#                     tripObj.endTime = str(data[7]).strip()
                                    
#                 tripObj.save()
#                 tripObj = DriverTrip.objects.get(pk=tripObjID)
                
#                 # basePlant = BasePlant.objects.filter(basePlant = data[24].strip().upper()).first() 
#                 # # modified for adding 
#                 # if basePlant is None:
#                 #     pastTripErrorObj = PastTripError(
#                 #             tripDate = res_,
#                 #             docketNumber = data[5],
#                 #             truckNo = data[1],
#                 #             lineNumber = i.lineNumber,
#                 #             errorFromPastTrip = "BasePlant does not exist.",
#                 #             fileName = i.fileName.split('@_!')[-1],
#                 #             data = data
#                 #         ) 
#                 #         # print('grace card not found')                   
#                 #     pastTripErrorObj.save()
#                 #     continue
#                     # Modification ends
                
#                 surCharge = Surcharge.objects.filter(surcharge_Name = 'No Surcharge').first()
                    
#                 docketObj = DriverDocket()                

#                 adminTruckObj = AdminTruck.objects.filter(adminTruckNumber = tripObj.truckNo).first()
#                 clientTruckConnectionObj = ClientTruckConnection.objects.filter(truckNumber = adminTruckObj,startDate__lte = tripObj.shiftDate,endDate__gte = tripObj.shiftDate, clientId = tripObj.clientName).first()

#                 if clientTruckConnectionObj:
#                     rateCard = clientTruckConnectionObj.rate_card_name                        
#                     graceObj = Grace.objects.filter(rate_card_name = rateCard,start_date__lte = tripObj.shiftDate,end_date__gte = tripObj.shiftDate).first()
#                     if not graceObj:
#                         pastTripErrorObj = PastTripError(
#                             clientName = 'boral',
#                             tripDate = res_,
#                             docketNumber = data[5],
#                             truckNo = data[1],
#                             lineNumber = i.lineNumber,
#                             errorFromPastTrip = "No matching grace card for the date.",
#                             fileName = i.fileName.split('@_!')[-1],
#                             data = data
#                         ) 
#                         # print('grace card not found')                   
#                         pastTripErrorObj.save()
#                         continue
                    
#                     # print("GRACE found")
                    
#                     if int(data[13]) > int(graceObj.waiting_time_grace_in_minutes):
#                         totalWaitingTime = int(data[13]) - graceObj.waiting_time_grace_in_minutes
#                     else:
#                         totalWaitingTime = 0
#                     costParameterObj = CostParameters.objects.filter(rate_card_name = rateCard).first()

#                     if not costParameterObj:
#                         pastTripErrorObj = PastTripError(
#                             clientName = 'boral',
#                             tripDate = res_,
#                             docketNumber = data[5],
#                             truckNo = data[1],
#                             lineNumber = i.lineNumber,
#                             errorFromPastTrip = "No matching cost parameter card for the date.",
#                             fileName = i.fileName.split('@_!')[-1],
#                             data = data
#                         )                    
#                         pastTripErrorObj.save()
#                         # print('COST PARAMETER not found')
#                         continue
                        
#                     # print("COST PARAMETER found!!!")
#                     standBySlot = 0
#                     try:
#                         if str(data[20]).strip().lower() != '' or str(data[21]).strip().lower() != '':
#                             start = datetime.strptime(str(data[20].strip()),'%H:%M:%S')
#                             end = datetime.strptime(str(data[21].strip()),'%H:%M:%S')
#                             totalStandByTime = ((end-start).total_seconds())/60
#                             if totalStandByTime > graceObj.chargeable_standby_time_starts_after:
#                                 totalStandByTime = totalStandByTime - graceObj.standby_time_grace_in_minutes
#                                 standBySlot = totalStandByTime//costParameterObj.standby_time_slot_size
#                         else:
#                             standBySlot = 0
#                     except Exception as e:
#                         pastTripErrorObj = PastTripError(
#                                         clientName = 'boral',
#                                         tripDate = res_,
#                                         docketNumber = data[5],
#                                         truckNo = data[1],
#                                         lineNumber = i.lineNumber,
#                                         errorFromPastTrip = 'time convert problem',
#                                         fileName = i.fileName.split('@_!')[-1],
#                                         data = data
#                                     )
#                         pastTripErrorObj.save()
#                         continue
                        
#                     docketObj.shiftDate = ' ' if str(data[0]).strip().lower() == '' else res_
#                     docketObj.tripId = tripObj
#                     docketObj.docketNumber = data[5]
#                     docketObj.noOfKm = 0 if str(data[10]).strip().lower() == '' else data[10]
#                     docketObj.transferKM = 0 if str(data[18]).strip().lower() == '' else data[18]
#                     docketObj.returnToYard = True if data[16].strip().lower() == 'yes' else False
#                     docketObj.returnQty = 0 if str(data[14]).strip().lower() == '' else data[14]
#                     docketObj.returnKm = 0 if str(data[15]).strip().lower() == '' else data[15]
#                     docketObj.waitingTimeStart = 0 if str(data[11]).strip().lower() == '' else data[11].strip()
#                     docketObj.waitingTimeEnd = 0 if str(data[12]).strip().lower() == '' else data[12].strip()
#                     docketObj.totalWaitingInMinute = totalWaitingTime
#                     docketObj.cubicMl = 0 if str(data[8]).strip().lower() == '' else data[8]
#                     docketObj.standByStartTime = 0 if str(data[20]).strip().lower() == '' else data[20].strip()
#                     docketObj.standByEndTime = 0 if str(data[21]).strip().lower() == '' else data[21].strip()
#                     docketObj.standBySlot = standBySlot
#                     docketObj.comment = data[17]
#                     # modification for adding blow back and replacement.
#                     if data[19].strip().replace(' ','') != None:
#                         docketObj.comment = docketObj.comment + 'Blow back comment : ' + data[19].strip() 
                        
#                     if data[23].strip().replace(' ','') != None:
#                         docketObj.comment = docketObj.comment + 'Replacement comment : ' + data[23].strip() 
                        
                    
#                     docketObj.basePlant = basePlant
#                     docketObj.surcharge_type = surCharge
#                     # surcharge_duration = 
#                     # others = 
#                     docketObj.save()
#                     # print("docket saved!!!")
                        
#                     reconciliationDocketObj = ReconciliationReport.objects.filter(docketNumber = int(docketObj.docketNumber) , docketDate = docketObj.shiftDate ).first()
                            
#                     if not reconciliationDocketObj :
#                         reconciliationDocketObj = ReconciliationReport()
                    
#                     driverLoadAndKmCost = checkLoadAndKmCost(int(docketObj.docketNumber),docketObj.shiftDate)
#                     driverSurchargeCost = checkSurcharge(int(docketObj.docketNumber),docketObj.shiftDate)
#                     driverWaitingTimeCost = round(docketObj.totalWaitingInMinute * costParameterObj.waiting_cost_per_minute,2) 
#                     driverStandByCost = round(costParameterObj.standby_cost_per_slot * docketObj.standBySlot,2)
#                     driverTransferKmCost = checkTransferCost(int(docketObj.docketNumber),docketObj.shiftDate)
#                     driverReturnKmCost = checkReturnCost(int(docketObj.docketNumber),docketObj.shiftDate)
#                     # minLoad 
#                     driverLoadDeficit = checkMinLoadCost(int(docketObj.docketNumber),docketObj.shiftDate)
#                     # TotalCost 
#                     driverTotalCost = driverLoadAndKmCost +driverSurchargeCost + driverWaitingTimeCost + driverStandByCost + driverTransferKmCost + driverReturnKmCost +driverLoadDeficit
#                     reconciliationDocketObj.driverId = driver.driverId  
#                     reconciliationDocketObj.clientId = client.clientId  
#                     reconciliationDocketObj.truckId = data[1]   
#                     reconciliationDocketObj.docketNumber = int(docketObj.docketNumber) 
#                     reconciliationDocketObj.docketDate = docketObj.shiftDate  
#                     reconciliationDocketObj.driverLoadAndKmCost = driverLoadAndKmCost 
#                     reconciliationDocketObj.driverSurchargeCost = driverSurchargeCost 
#                     reconciliationDocketObj.driverWaitingTimeCost = driverWaitingTimeCost 
#                     reconciliationDocketObj.driverStandByCost = driverStandByCost 
#                     reconciliationDocketObj.driverLoadDeficit = driverLoadDeficit 
#                     reconciliationDocketObj.driverTransferKmCost = driverTransferKmCost 
#                     reconciliationDocketObj.driverReturnKmCost = driverReturnKmCost  
#                     reconciliationDocketObj.driverTotalCost = round(driverTotalCost,2) 
#                     reconciliationDocketObj.fromDriver = True 
#                     reconciliationDocketObj.save()
#                     checkMissingComponents(reconciliationDocketObj)
                    
#                 else:
#                     pastTripErrorObj = PastTripError(
#                         clientName = 'boral',
#                         tripDate = res_,
#                         docketNumber = data[5],
#                         truckNo = data[1],
#                         lineNumber = i.lineNumber,
#                         errorFromPastTrip = "Client truck connection object does not exist.",
#                         fileName = i.fileName.split('@_!')[-1],
#                         data = data
#                     )
#                     pastTripErrorObj.save()
#                     continue
#             except Exception as e:       
#                 pastTripErrorObj = PastTripError(
#                     clientName = 'boral',
#                     tripDate = res_,
#                     docketNumber = data[5],
#                     truckNo = data[1],
#                     lineNumber = i.lineNumber,
#                     errorFromPastTrip = e,
#                     fileName = i.fileName.split('@_!')[-1],
#                     data = data
#                 )
#                 pastTripErrorObj.save()
#                 continue
#         else:
#             continue
#     except Exception as e:
#         pastTripErrorObj = PastTripError(
#             clientName = 'boral',
#             tripDate = res_,
#             docketNumber = data[5],
#             truckNo = data[1],
#             lineNumber = i.lineNumber,
#             errorFromPastTrip = e,
#             fileName = i.fileName.split('@_!')[-1],
#             data = data
#         )
#         pastTripErrorObj.save()

# # RCTI FUNCTION 
# def convertIntoFloat(str_):
#     if '(' in str_:
#         str_ = '-'+str_.strip('()')
#     cleaned_string = str_.replace(' ','').replace(',','')
#     return float(cleaned_string)


# def checkDate(date_):
#     pattern = r'\d{2}/\d{2}/\d{2}'
#     return True if re.fullmatch(pattern,date_) else False

# def dateConvert(date_):
#     date_ = date_.split('/')
#     year_ = '20' + date_[-1]
#     return year_ .strip()+ '-' + date_[1].strip() + '-' + date_[0].strip()
    
# docket_pattern = r'^\d{8}$|^\d{6}$'
# # For RCTI 
# rctiMatchingData = RctiErrors.objects.filter(errorDescription="Earning Depot/Location does not exist.", status=False)
# # dataList = "['10652', '20527042', '01/08/23', 'BEGA', '151  AUCKLAND ST BEGA CARTAGE OTHERPER KM PER CU M', '4.0000', '3.0000', 'CUBIC ME', '37.1900', '111.57', '11.16', '122.73']"


# for i in rctiMatchingData:
#     fileName = i.fileName
#     dataList = i.data
#     dataList = dataList.replace('[','').replace(']','').replace("'",'')
#     dataList = dataList.split(',')
#     for j in range(len(dataList)):
#         dataList[j] = dataList[j].strip()
#         # if j ==2:
#         #     dataList[2] = dateConvert(dataList[2])
    
#     if str(dataList[3]) == basePlantName:
        
#         try:
#             errorSolve = dataList
#             RCTIobj = None
#             try:
#                 existingDocket = RCTI.objects.get(docketNumber=int(dataList[1]))
#                 if str(existingDocket.docketDate) == dateConvert(dataList[2]):
#                     RCTIobj = existingDocket
#             except:
#                 RCTIobj = RCTI()

#             RCTIobj.truckNo = convertIntoFloat(dataList[0])
#             RCTIobj.clientName = Client.objects.filter(name = 'boral').first()
#             if re.match(docket_pattern ,str(dataList[1])):
#                 RCTIobj.docketNumber = str(dataList[1])
#                 dataList = dataList[2:]
#                 while dataList:

#                     dump = dataList[:10]
#                     description = dump[2].lower().strip()
#                     if 'top up' in description:
#                         # insertTopUpRecord(dump, RCTIobj.truckNo, RCTIobj.docketNumber)
#                         RCTIobj.docketDate = dateConvert(dump[0].split()[-1])
#                         RCTIobj.docketYard = dump[1]
                        
#                         RCTIobj.others = dump[2]
#                         RCTIobj.othersCost = convertIntoFloat(dump[6])
#                         RCTIobj.othersGSTPayable = convertIntoFloat(dump[7])
#                         RCTIobj.othersTotalExGST = convertIntoFloat(dump[8])
#                         RCTIobj.othersTotal = convertIntoFloat(dump[9])
#                         dataList = dataList[10:]
#                         continue
                        
#                     RCTIobj.docketDate = dateConvert(dump[0])
#                     RCTIobj.docketYard = dump[1]
                    
#                     if "truck transfer" in description:
#                         RCTIobj.transferKM = convertIntoFloat(dump[4])
#                         RCTIobj.transferKMCost = convertIntoFloat(dump[6])
#                         RCTIobj.transferKMGSTPayable = convertIntoFloat(dump[-2])
#                         RCTIobj.transferKMTotalExGST = convertIntoFloat(dump[-3])
#                         RCTIobj.transferKMTotal = convertIntoFloat(dump[-1])
#                     elif "cartage" in description:
#                         RCTIobj.noOfKm = convertIntoFloat(dump[3])
#                         RCTIobj.cubicMl = convertIntoFloat(dump[4])
#                         RCTIobj.cubicMiAndKmsCost = convertIntoFloat(dump[6])
#                         RCTIobj.destination = description.split('cartage')[0]
#                         RCTIobj.cartageGSTPayable = convertIntoFloat(dump[-2])
#                         RCTIobj.cartageTotalExGST = convertIntoFloat(dump[-3])
#                         RCTIobj.cartageTotal = convertIntoFloat(dump[-1])
#                     elif "return" in description:
#                         RCTIobj.returnKm = convertIntoFloat(dump[4])
#                         RCTIobj.returnPerKmPerCubicMeterCost = convertIntoFloat(dump[6])
#                         RCTIobj.returnKmGSTPayable = convertIntoFloat(dump[-2])
#                         RCTIobj.returnKmTotalExGST = convertIntoFloat(dump[-3])
#                         RCTIobj.returnKmTotal = convertIntoFloat(dump[-1])
#                     elif "waiting time" in description:
#                         RCTIobj.waitingTimeInMinutes = convertIntoFloat(dump[4])
#                         RCTIobj.waitingTimeCost = convertIntoFloat(dump[6])
#                         RCTIobj.waitingTimeGSTPayable = convertIntoFloat(dump[-2])
#                         RCTIobj.waitingTimeTotalExGST = convertIntoFloat(dump[-3])
#                         RCTIobj.waitingTimeTotal = convertIntoFloat(dump[-1])
#                     elif "minimum load" in description:
#                         RCTIobj.minimumLoad = convertIntoFloat(dump[4])
#                         RCTIobj.loadCost = convertIntoFloat(dump[6])
#                         RCTIobj.minimumLoadGSTPayable = convertIntoFloat(dump[-2])
#                         RCTIobj.minimumLoadTotalExGST = convertIntoFloat(dump[-3])
#                         RCTIobj.minimumLoadTotal = convertIntoFloat(dump[-1])
#                     elif "standby" in description:
#                         RCTIobj.standByNoSlot = convertIntoFloat(dump[4])
#                         RCTIobj.standByUnit = 'slot' if str(
#                             dump[5].lower()) == 'each' else 'minute'
#                         RCTIobj.standByPerHalfHourDuration = convertIntoFloat(dump[6])
#                         RCTIobj.standByGSTPayable = convertIntoFloat(dump[-2])
#                         RCTIobj.standByTotalExGST = convertIntoFloat(dump[-3])
#                         RCTIobj.standByTotal = convertIntoFloat(dump[-1])
#                     elif "surcharge after hours" in description:
#                         RCTIobj.surcharge_duration = convertIntoFloat(dump[4])
#                         if "mon-fri" in description and "each" in str(dump[5].lower()):
#                             RCTIobj.surcharge_fixed_normal = convertIntoFloat(dump[6])
#                         elif "sat" in description and 'mon' in description and "each" in str(dump[5].lower()):
#                             RCTIobj.surcharge_fixed_sunday = convertIntoFloat(dump[6])
#                         RCTIobj.surchargeGSTPayable = convertIntoFloat(dump[-2])
#                         RCTIobj.surchargeTotalExGST = convertIntoFloat(dump[-3])
#                         RCTIobj.surchargeTotal = convertIntoFloat(dump[-1])
#                     elif "waiting time sched" in description:
#                         RCTIobj.waitingTimeSCHED = convertIntoFloat(dump[4])
#                         RCTIobj.waitingTimeSCHEDCost = convertIntoFloat(dump[6])
#                         RCTIobj.waitingTimeSCHEDGSTPayable = convertIntoFloat(dump[-2])
#                         RCTIobj.waitingTimeSCHEDTotalExGST = convertIntoFloat(dump[-3])
#                         RCTIobj.waitingTimeSCHEDTotal = convertIntoFloat(dump[-1])
                        
#                     # surcharge_fixed_public_holiday
#                     # surcharge_per_cubic_meters_normal
#                     # surcharge_per_cubic_meters_sunday
#                     # surcharge_per_cubic_meters_public_holiday

#                     # others
#                     # othersCost

#                     # ------------------------------------------

#                     RCTIobj.GSTPayable = convertIntoFloat(dump[8])
#                     RCTIobj.TotalExGST = convertIntoFloat(dump[7])
#                     RCTIobj.Total = convertIntoFloat(dump[9])

#                     dataList = dataList[10:]
                    
#                 RCTIobj.save()
#                 i.status = True
#                 i.save()
                
#                 reconciliationDocketObj = ReconciliationReport.objects.filter(docketNumber = RCTIobj.docketNumber , docketDate = RCTIobj.docketDate ).first()
#                 rctiTotalCost = RCTIobj.cartageTotalExGST + RCTIobj.transferKMTotalExGST + RCTIobj.returnKmTotalExGST + RCTIobj.waitingTimeSCHEDTotalExGST + RCTIobj.waitingTimeTotalExGST + RCTIobj.standByTotalExGST + RCTIobj.minimumLoadTotalExGST + RCTIobj.surchargeTotalExGST + RCTIobj.othersTotalExGST
                
#                 # rctiTotalCost =   RCTIobj.cartageTotal + RCTIobj.waitingTimeTotal + RCTIobj.transferKMTotal  +  RCTIobj.returnKmTotal + RCTIobj.standByTotal +RCTIobj.minimumLoadTotal
                
#                 if not reconciliationDocketObj :
#                     reconciliationDocketObj = ReconciliationReport()
                
#                 reconciliationDocketObj.docketNumber =  RCTIobj.docketNumber
#                 reconciliationDocketObj.docketDate =  RCTIobj.docketDate
#                 reconciliationDocketObj.rctiLoadAndKmCost =  RCTIobj.cartageTotalExGST
#                 # reconciliationDocketObj.rctiSurchargeCost =   RCTIobj.docketDate
#                 reconciliationDocketObj.rctiWaitingTimeCost = RCTIobj.waitingTimeTotalExGST
#                 reconciliationDocketObj.rctiTransferKmCost = RCTIobj.transferKMTotalExGST
#                 reconciliationDocketObj.rctiReturnKmCost =  RCTIobj.returnKmTotalExGST
#                 # reconciliationDocketObj.rctiOtherCost =  RCTIobj.docketDate 
#                 reconciliationDocketObj.rctiStandByCost =  RCTIobj.standByTotalExGST
#                 reconciliationDocketObj.rctiLoadDeficit =  RCTIobj.minimumLoadTotalExGST
#                 reconciliationDocketObj.rctiTotalCost =  round(rctiTotalCost,2)
#                 reconciliationDocketObj.fromRcti = True 
                
#                 reconciliationDocketObj.save()
#                 checkMissingComponents(reconciliationDocketObj)
                
#             else:
#                 rctiErrorObj = RctiErrors( 
#                                 clientName = 'boral',
#                                 docketNumber = dataList[1],
#                                 docketDate = RCTIobj.docketDate,
#                                 errorDescription = 'To be adjusted manually by admin team',
#                                 fileName = fileName,
#                                 data = str(errorSolve)
#             )
#                 rctiErrorObj.save()

#         except Exception as e:
#             print(f"Error : {e}")
#             rctiErrorObj = RctiErrors( 
#                                 clientName = 'boral',
#                                 docketNumber = RCTIobj.docketNumber,
#                                 docketDate = RCTIobj.docketDate,
#                                 errorDescription = e,
#                                 fileName = fileName,
#                                 data = str(errorSolve)
#             )
#             rctiErrorObj.save()
#             pass
