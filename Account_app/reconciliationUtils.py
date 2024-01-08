from Account_app.models import *
from GearBox_app.models import *
from django.utils import timezone 
import datetime
from django.shortcuts import get_object_or_404
from CRUD import *
from datetime import datetime

costDict = {
    'rctiCosts': {
        'loadAndKmCost':0,
        'surchargeCost':0,
        'waitingTimeCost':0,
        'standByTotalCost':0        
    },
    'driverDocketCosts':{
        'loadAndKmCost':0,
        'surchargeCost':0,
        'waitingTimeCost':0,
        'standByTotalCost':0
    }
}
def DriverTripCheckWaitingTime(driverDocketNumber,docketDate):
    date_= docketDate
    driverDocketObj = DriverDocket.objects.filter(docketNumber=driverDocketNumber,shiftDate=date_).first()
    tripObj = DriverTrip.objects.filter(pk=driverDocketObj.tripId.id).first()
    if tripObj:
        adminTruckObj = AdminTruck.objects.filter(adminTruckNumber = tripObj.truckNo).first()
        clientTruckObj = ClientTruckConnection.objects.filter(truckNumber = adminTruckObj).first()
        rateCardObj = RateCard.objects.filter(rate_card_name = clientTruckObj.rate_card_name.rate_card_name).first()
        graceObj = Grace.objects.filter(rate_card_name = rateCardObj).first()
       
        totalWaitingTime = timeDifference(driverDocketObj.waitingTimeStart,driverDocketObj.waitingTimeEnd)
        
        if float(totalWaitingTime) > graceObj.chargeable_waiting_time_starts_after:
            totalWaitingTime = totalWaitingTime - graceObj.waiting_time_grace_in_minutes
            if totalWaitingTime < 0:
                totalWaitingTime = 0    
        else:
            totalWaitingTime = 0
        return totalWaitingTime
    
def checkLoadAndKmCost(driverDocketNumber,docketDate):
    try:
        
        # date_= datetime.strptime(docketDate, "%Y-%m-%d").date()
        date_= docketDate
        driverDocketObj = DriverDocket.objects.filter(docketNumber=driverDocketNumber,shiftDate=date_).first()
        driverDocketLoadSize = driverDocketObj.cubicMl 

        tripObj = DriverTrip.objects.filter(pk = driverDocketObj.tripId.id).first()
        adminTruckObj = AdminTruck.objects.filter(adminTruckNumber = tripObj.truckNo).first()
        clientTruckConnectionObj = ClientTruckConnection.objects.filter(truckNumber = adminTruckObj,startDate__lte = date_,endDate__gte = date_, clientId = tripObj.clientName).first()
        
        rateCard = clientTruckConnectionObj.rate_card_name
        costParameterObj = CostParameters.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
        
        graceObj = Grace.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
        driverDocketKm = 0 if driverDocketObj.noOfKm <= graceObj.load_km_grace else driverDocketObj.noOfKm - graceObj.load_km_grace
        driverLoadKmCostTotal = (driverDocketLoadSize * costParameterObj.loading_cost_per_cubic_meter) + (driverDocketKm * costParameterObj.km_cost * driverDocketLoadSize)

        
        if tripObj.shiftType == 'Day':
            shiftType = ThresholdDayShift.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
        else:
            shiftType = ThresholdNightShift.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
            
        if  driverDocketLoadSize < shiftType.min_load_in_cubic_meters :
            driverDocketObj.minimumLoad = (shiftType.min_load_in_cubic_meters - driverDocketLoadSize)*costParameterObj.loading_cost_per_cubic_meter
            driverDocketObj.minimumLoad = driverDocketObj.minimumLoad +  (driverDocketKm * costParameterObj.km_cost * driverDocketLoadSize)
            driverDocketObj.save()
            
        
        return round(driverLoadKmCostTotal,2)
 
 
    except Exception as e :
        with open("scripts/checkLoadAndKmCost.txt", 'a') as f:
            f.write(driverDocketNumber + str(e)+','+'\n')
        return -404.0

def checkMinLoadCost(driverDocketNumber,docketDate):
    try:
        
        # date_= datetime.strptime(docketDate, "%Y-%m-%d").date()
        date_= docketDate

        driverDocketObj = DriverDocket.objects.filter(docketNumber=driverDocketNumber,shiftDate=date_).first()
        driverDocketLoadSize = driverDocketObj.cubicMl 

        tripObj = DriverTrip.objects.filter(pk = driverDocketObj.tripId.id).first()
        adminTruckObj = AdminTruck.objects.filter(adminTruckNumber = tripObj.truckNo).first()
        clientTruckConnectionObj = ClientTruckConnection.objects.filter(truckNumber = adminTruckObj,startDate__lte = date_,endDate__gte = date_, clientId = tripObj.clientName).first()
        
        rateCard = clientTruckConnectionObj.rate_card_name
        costParameterObj = CostParameters.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
        
        graceObj = Grace.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
        driverDocketKm = 0 if driverDocketObj.noOfKm <= graceObj.load_km_grace else driverDocketObj.noOfKm - graceObj.load_km_grace
        if tripObj.shiftType == 'Day':
            shiftType = ThresholdDayShift.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
        else:
            shiftType = ThresholdNightShift.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
        
        # minLoad Cost 
        if  driverDocketLoadSize < shiftType.min_load_in_cubic_meters :
            driverDocketObj.minimumLoad = (shiftType.min_load_in_cubic_meters - driverDocketLoadSize)*costParameterObj.loading_cost_per_cubic_meter
            driverDocketObj.minimumLoad = driverDocketObj.minimumLoad +  (driverDocketKm * costParameterObj.km_cost * (shiftType.min_load_in_cubic_meters - driverDocketLoadSize))
            driverDocketObj.save()
            
            return round(driverDocketObj.minimumLoad,2)
        return 0
        
    except Exception as e : 
        
        return -404.0 

def checkSurcharge(driverDocketNumber,docketDate, costDict = costDict):
    return 0
    # try:
        
    #     # date_= datetime.strptime(docketDate, "%Y-%m-%d").date()
    #     date_= docketDate

    #     driverDocketObj = DriverDocket.objects.filter(docketNumber=driverDocketNumber,shiftDate=date_).first()
        
    #     if 'nosurcharge' in driverDocketObj.surcharge_type.surcharge_Name.lower():
    #         return 0
        
    #     if 'fixed' in  driverDocketObj.surcharge_type.surcharge_Name.lower():
    #         tripObj = DriverTrip.objects.filter(pk = driverDocketObj.tripId.id).first()
    #         adminTruckObj = AdminTruck.objects.filter(adminTruckNumber = tripObj.truckNo).first()
    #         clientTruckConnectionObj = ClientTruckConnection.objects.filter(truckNumber = adminTruckObj,startDate__lte = date_,endDate__gte = date_, clientId = tripObj.clientName).first()
            
    #         rateCard = clientTruckConnectionObj.rate_card_name
    #         costParameterObj = CostParameters.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
          
    #         surchargeAmount = round(costParameterObj.surcharge_cost,2)
    #         if surchargeAmount is None:
    #             return 0
    #         else :
    #             return surchargeAmount
    #     else:
    #         return 0
            

    # except Exception as e :
    #     return -404.0
        
def checkWaitingTime(driverDocketNumber,docketDate):
    try:
        # date_= datetime.strptime(docketDate, "%Y-%m-%d").date()
        date_= docketDate

        driverDocketObj = DriverDocket.objects.filter(docketNumber=driverDocketNumber,shiftDate=date_).first()
        tripObj = DriverTrip.objects.filter(pk = driverDocketObj.tripId.id).first()
        adminTruckObj = AdminTruck.objects.filter(adminTruckNumber = tripObj.truckNo).first()
        clientTruckConnectionObj = ClientTruckConnection.objects.filter(truckNumber = adminTruckObj,startDate__lte = date_,endDate__gte = date_, clientId = tripObj.clientName).first()
        
        rateCard = clientTruckConnectionObj.rate_card_name
        costParameterObj = CostParameters.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
        graceObj = Grace.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
        driverDocketObj.totalWaitingInMinute = timeDifference(driverDocketObj.waitingTimeStart,driverDocketObj.waitingTimeEnd)
        
        totalWaitingTime = driverDocketObj.totalWaitingInMinute + graceObj.waiting_time_grace_in_minutes 
        if totalWaitingTime > graceObj.chargeable_waiting_time_starts_after:
            totalWaitingTime = totalWaitingTime - graceObj.waiting_time_grace_in_minutes
            if totalWaitingTime > 0: 
                totalWaitingCost = totalWaitingTime * costParameterObj.waiting_cost_per_minute        
            else:
                totalWaitingCost = 0
            return round(totalWaitingCost,2) 
        else:
            return 0
        
    except Exception as e :
        return -404.0
    
def DriverTripCheckStandByTotal(driverDocketNumber,docketDate):

    driverDocketObj = DriverDocket.objects.filter(docketNumber=driverDocketNumber,shiftDate=docketDate).first()
    tripObj = DriverTrip.objects.filter(pk=driverDocketObj.tripId.id).first()
    
    if tripObj:
        adminTruckObj = AdminTruck.objects.filter(adminTruckNumber = tripObj.truckNo).first()
        clientTruckObj = ClientTruckConnection.objects.filter(truckNumber = adminTruckObj).first()
        rateCardObj = RateCard.objects.filter(rate_card_name = clientTruckObj.rate_card_name.rate_card_name).first()
        costParameterObj = CostParameters.objects.filter(rate_card_name = rateCardObj).first()
        graceObj = Grace.objects.filter(rate_card_name = rateCardObj).first()
        
        totalStandByTime = getTimeDifference(driverDocketObj.standByStartTime,driverDocketObj.standByEndTime)
        standBySlot = 0
        if totalStandByTime > graceObj.chargeable_standby_time_starts_after:
            totalStandByTime = totalStandByTime - graceObj.standby_time_grace_in_minutes
            standBySlot = totalStandByTime//costParameterObj.standby_time_slot_size
        return standBySlot
    
def checkStandByTotal(driverDocketNumber,docketDate,standBySlot, costDict = costDict):
    try:
        if standBySlot > 0:
            date_= docketDate

            driverDocketObj = DriverDocket.objects.filter(docketNumber=driverDocketNumber,shiftDate=date_).first()
            finalStandByCost = 0
            
            if driverDocketObj.standByStartTime.strip() == '' and driverDocketObj.standByEndTime.strip() == '':
                return 0
            
            elif driverDocketObj.standByStartTime.strip() != '' and driverDocketObj.standByEndTime.strip() != '':
                tripObj = DriverTrip.objects.filter(pk = driverDocketObj.tripId.id).first()
                
                adminTruckObj = AdminTruck.objects.filter(adminTruckNumber = tripObj.truckNo).first()
                clientTruckConnectionObj = ClientTruckConnection.objects.filter(truckNumber = adminTruckObj,startDate__lte = date_,endDate__gte = date_, clientId = tripObj.clientName).first()
                
                rateCard = clientTruckConnectionObj.rate_card_name
                costParameterObj = CostParameters.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
                # graceObj = Grace.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
                
                finalStandByCost = standBySlot * costParameterObj.standby_cost_per_slot
                
                # start = datetime.strptime(driverDocketObj.standByStartTime,'%H:%M:%S')
                # end = datetime.strptime(driverDocketObj.standByEndTime,'%H:%M:%S')
                # DriverStandByTime = ((end-start).total_seconds())/60
                
                # if DriverStandByTime > graceObj.chargeable_standby_time_starts_after:
                #     totalStandByTime = DriverStandByTime - graceObj.standby_time_grace_in_minutes
                #     standBySlot = totalStandByTime//costParameterObj.standby_time_slot_size
                    
                #     if standBySlot >=1:
                #         finalStandByCost =standBySlot * costParameterObj.standby_cost_per_slot
                        
                    
                    # elif standBySlot > 0:
                    #     finalStandByCost = 0.5 * costParameterObj.standby_cost_per_slot
        else:
            finalStandByCost = 0     

            
        return round(finalStandByCost,2)  

    except Exception as e :
        return -404.0
      
def checkTransferCost(driverDocketNumber,docketDate):
    try:
        
        # date_= datetime.strptime(docketDate, "%Y-%m-%d").date()
        date_= docketDate

        driverDocketObj = DriverDocket.objects.filter(docketNumber=driverDocketNumber,shiftDate=date_).first()
        tripObj = DriverTrip.objects.filter(pk = driverDocketObj.tripId.id).first()
        adminTruckObj = AdminTruck.objects.filter(adminTruckNumber = tripObj.truckNo).first()
        clientTruckConnectionObj = ClientTruckConnection.objects.filter(truckNumber = adminTruckObj,startDate__lte = date_,endDate__gte = date_, clientId = tripObj.clientName).first()
        
        rateCard = clientTruckConnectionObj.rate_card_name
        costParameterObj = CostParameters.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
        graceObj = Grace.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
        
        # Transfer Km 
        driverDocketTransferKm = 0 if driverDocketObj.transferKM <= graceObj.transfer_km_grace else driverDocketObj.transferKM - graceObj.transfer_km_grace
        driverDocketTransferKmCostTotal = driverDocketTransferKm * costParameterObj.transfer_cost
        
        return round(driverDocketTransferKmCostTotal,2)
    except Exception as e : 
        return -404.0

def checkReturnCost(driverDocketNumber,docketDate):
    try:
        
        # date_= datetime.strptime(docketDate, "%Y-%m-%d").date()
        date_= docketDate

        driverDocketObj = DriverDocket.objects.filter(docketNumber=driverDocketNumber,shiftDate=date_).first()
        tripObj = DriverTrip.objects.filter(pk = driverDocketObj.tripId.id).first()
        adminTruckObj = AdminTruck.objects.filter(adminTruckNumber = tripObj.truckNo).first()
        clientTruckConnectionObj = ClientTruckConnection.objects.filter(truckNumber = adminTruckObj,startDate__lte = date_,endDate__gte = date_, clientId = tripObj.clientName).first()
        
        rateCard = clientTruckConnectionObj.rate_card_name
        costParameterObj = CostParameters.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
        graceObj = Grace.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
        
        # return Cost 
        driverReturnCostTotal = (driverDocketObj.returnKm -  graceObj.return_km_grace) * driverDocketObj.returnQty 
        
        return round(driverReturnCostTotal,2)
    except Exception as e : 
        return -404.0
    
def checkTotalCost(driverDocketNumber,docketDate ,costDict = costDict):
    try:
        missingComponents = []
        # date_= datetime.strptime(docketDate, "%Y-%m-%d").date()
        date_= docketDate

        driverDocketObj = DriverDocket.objects.filter(docketNumber=driverDocketNumber,shiftDate=date_).first()
        tripObj = DriverTrip.objects.filter(pk = driverDocketObj.tripId.id).first()
        adminTruckObj = AdminTruck.objects.filter(adminTruckNumber = tripObj.truckNo).first()
        clientTruckConnectionObj = ClientTruckConnection.objects.filter(truckNumber = adminTruckObj,startDate__lte = date_,endDate__gte = date_, clientId = tripObj.clientName).first()
        
        rateCard = clientTruckConnectionObj.rate_card_name
        costParameterObj = CostParameters.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
        graceObj = Grace.objects.filter(rate_card_name = rateCard.id,start_date__lte = date_,end_date__gte = date_).first()
        
        rctiObj = RCTI.objects.filter(docketNumber = driverDocketNumber ,docketDate = date_).first()
        
        driverLoadAndKmCostTotal = costDict['driverDocketCosts']['loadAndKmCost']
        driverWaitingCostTotal = costDict['driverDocketCosts']['waitingTimeCost']
        driverStandByTimeCostTotal = costDict['driverDocketCosts']['standByTotalCost']
        
        costDict = {
            'rctiCosts': {
                'loadAndKmCost':0,
                'surchargeCost':0,
                'waitingTimeCost':0,
                'standByTotalCost':0        
            },
            'driverDocketCosts':{
                'loadAndKmCost':0,
                'surchargeCost':0,
                'waitingTimeCost':0,
                'standByTotalCost':0
            }
        }
        # load 
        # driverLoadAndKmCostTotal =   driverDocketObj.cubicMl * costParameterObj.loading_cost_per_cubic_meter 
        
        # no.ofKm 
        # driverDocketKm = 0 if driverDocketObj.noOfKm <= graceObj.load_km_grace else driverDocketObj.noOfKm - graceObj.load_km_grace
        # driverDocketKmCostTotal = driverDocketKm * costParameterObj.loading_cost_per_cubic_meter * costParameterObj.km_cost
        
        # Transfer Km 
        driverDocketTransferKm = 0 if driverDocketObj.transferKM <= graceObj.transfer_km_grace else driverDocketObj.transferKM - graceObj.transfer_km_grace
        driverDocketTransferKmCostTotal = driverDocketTransferKm * costParameterObj.transfer_cost
        
        
        # return Cost 
        driverReturnCostTotal = (driverDocketObj.returnKm -  graceObj.return_km_grace) * driverDocketObj.returnQty 
        
        # waiting Time 
        # driverWaitingCostTotal =  0
        # if driverDocketObj.totalWaitingInMinute > graceObj.chargeable_waiting_time_starts_after:
        #     totalWaitingTime = driverDocketObj.totalWaitingInMinute - graceObj.waiting_time_grace_in_minutes
        #     driverWaitingCostTotal = totalWaitingTime * costParameterObj.waiting_cost_per_minute
        
        # standby Time
        # start = datetime.strptime(driverDocketObj.standByStartTime,'%H:%M:%S')
        # end = datetime.strptime(driverDocketObj.standByEndTime,'%H:%M:%S')
        # DriverStandByTime = ((end-start).total_seconds())/60
        # driverStandByTimeCostTotal = 0
        # if DriverStandByTime > graceObj.chargeable_standby_time_starts_after:
        #     totalStandByTime = DriverStandByTime - graceObj.standby_time_grace_in_minutes
        #     standBySlot = totalStandByTime/costParameterObj.standby_time_slot_size
        #     if standBySlot >=1:
        #         driverStandByTimeCostTotal = (standBySlot//1) * costParameterObj.standby_cost_per_slot

        # otherCost 
        driverOtherCostTotal = driverDocketObj.others
        
        finalDriverCost = driverLoadAndKmCostTotal  + driverDocketTransferKmCostTotal + driverReturnCostTotal + driverWaitingCostTotal + driverStandByTimeCostTotal + driverOtherCostTotal
                           
        rctiTotalCost = rctiObj.cartageTotalExGST + rctiObj.transferKMTotalExGST + rctiObj.returnKmTotalExGST + rctiObj.waitingTimeSCHEDTotalExGST + rctiObj.waitingTimeTotalExGST + rctiObj.standByTotalExGST + rctiObj.minimumLoadTotalExGST + rctiObj.surchargeTotalExGST + rctiObj.othersTotalExGST

        # Missing parameters
        if (driverLoadAndKmCostTotal > 0 and rctiObj.cartageTotalExGST == 0) or (driverLoadAndKmCostTotal == 0 and rctiObj.cartageTotalExGST > 0) :
            missingComponents.append('Load Km Cost')
            
        if (driverDocketTransferKmCostTotal > 0 and rctiObj.transferKMTotalExGST == 0) or (driverDocketTransferKmCostTotal == 0 and rctiObj.transferKMTotalExGST > 0) :
            missingComponents.append('Transfer Cost')
            
        if (driverReturnCostTotal > 0 and rctiObj.returnKmTotalExGST == 0) or (driverReturnCostTotal == 0 and rctiObj.returnKmTotalExGST > 0):
            missingComponents.append('Return Cost')
            
        if (driverStandByTimeCostTotal > 0  and rctiObj.standByTotalExGST == 0) or (driverStandByTimeCostTotal == 0  and rctiObj.standByTotalExGST > 0):
            missingComponents.append('Waiting Cost')
            
        if (driverWaitingCostTotal > 0 and rctiObj.waitingTimeTotalExGST == 0) or (driverWaitingCostTotal == 0 and rctiObj.waitingTimeTotalExGST > 0):
            missingComponents.append('Standby Cost')

        if (driverOtherCostTotal > 0 and rctiObj.minimumLoadTotalExGST == 0) or (driverOtherCostTotal == 0 and rctiObj.minimumLoadTotalExGST > 0):
            missingComponents.append('Minimum Load Cost')
            
        if finalDriverCost == rctiTotalCost:
            return [round(finalDriverCost,2),round(rctiTotalCost,2), True , missingComponents]
        else:
            return [round(finalDriverCost,2),round(rctiTotalCost,2), False , missingComponents]
            
    except Exception as e :

        return ['','Missing Components not calculated']
    
def checkMissingComponents(reconciliationReportObj):

    components = ''
    if reconciliationReportObj.driverLoadAndKmCost > 0 and reconciliationReportObj.rctiLoadAndKmCost == 0:
        components += 'Load Km Cost' + ', '
    if reconciliationReportObj.driverSurchargeCost > 0 and reconciliationReportObj.rctiSurchargeCost == 0:
        components += 'Surcharge Cost' + ', '
    if reconciliationReportObj.driverWaitingTimeCost > 0 and reconciliationReportObj.rctiWaitingTimeCost == 0:
        components += 'Waiting Time Cost' + ', '
    if reconciliationReportObj.driverTransferKmCost > 0 and reconciliationReportObj.rctiTransferKmCost == 0:
        components += 'Transfer Km Cost' + ', '
    if reconciliationReportObj.driverReturnKmCost > 0 and reconciliationReportObj.rctiReturnKmCost == 0:
        components += 'Return Km Cost' + ', '
    if reconciliationReportObj.driverStandByCost > 0 and reconciliationReportObj.rctiStandByCost == 0:
        components += 'Stand By Cost' + ', '
    if reconciliationReportObj.driverLoadDeficit > 0 and reconciliationReportObj.rctiLoadDeficit == 0:
        components += 'Load Deficit Cost' + ', '
    reconciliationReportObj.missingComponent = components
    reconciliationReportObj.save()

    
    

def DriverTripCheckStandByTotal(driverDocketNumber,docketDate):

    driverDocketObj = DriverDocket.objects.filter(docketNumber=driverDocketNumber,shiftDate=docketDate).first()
    tripObj = DriverTrip.objects.filter(pk=driverDocketObj.tripId.id).first()
    
    if tripObj:
        adminTruckObj = AdminTruck.objects.filter(adminTruckNumber = tripObj.truckNo).first()
        clientTruckObj = ClientTruckConnection.objects.filter(truckNumber = adminTruckObj).first()
        rateCardObj = RateCard.objects.filter(rate_card_name = clientTruckObj.rate_card_name.rate_card_name).first()
        costParameterObj = CostParameters.objects.filter(rate_card_name = rateCardObj).first()
        graceObj = Grace.objects.filter(rate_card_name = rateCardObj).first()
        
        totalStandByTime = getTimeDifference(driverDocketObj.standByStartTime,driverDocketObj.standByEndTime)
        standBySlot = 0
        if totalStandByTime > graceObj.chargeable_standby_time_starts_after:
            totalStandByTime = totalStandByTime - graceObj.standby_time_grace_in_minutes
            standBySlot = totalStandByTime//costParameterObj.standby_time_slot_size
        return standBySlot
