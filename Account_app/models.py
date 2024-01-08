from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator,RegexValidator
from datetime import date
from django.utils import timezone
from GearBox_app.models import *
from django.contrib.auth.models import User



# -----------------------------------
# Plants section
# -----------------------------------

class BasePlant(models.Model):
    basePlant = models.CharField(unique= True,max_length=200)
    address = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=20, default='')
    personOnName = models.CharField(max_length=25, default='')
    managerName = models.CharField(max_length=25, default='')
    lat = models.CharField(max_length=20, default='')
    long = models.CharField(max_length=20, default='')
    
    # True = BasePlant, False = Location
    basePlantType = models.BooleanField(default=True) 
    
    class Meta:
        unique_together = (('lat', 'long'),)

    def __str__(self) -> str:
        return str(self.basePlant)
    
# -----------------------------------
# Location 
# -----------------------------------

# class Location(models.Model):
#     location = models.CharField(max_length=200)
#     address = models.CharField(max_length=255, default='')
#     phone = models.CharField(max_length=20, default='')
#     personOnName = models.CharField(max_length=25, default='')
#     managerName = models.CharField(max_length=25, default='')
#     lat = models.CharField(max_length=20, default='')
#     long = models.CharField(max_length=20, default='')

#     class Meta:
#         unique_together = (('lat', 'long'),)

#     def __str__(self) -> str:
#         return str(self.location)

# -----------------------------------
# Trips section
# -----------------------------------

class DriverTrip(models.Model):
    verified = models.BooleanField(default=False)
    partially = models.BooleanField(default=False)
    driverId = models.ForeignKey(Driver, on_delete=models.CASCADE)
    clientName = models.ForeignKey(Client,on_delete=models.CASCADE)
    shiftType = models.CharField(max_length=200,choices=(('Day','Day'),('Night','Night')))
    numberOfLoads = models.FloatField(default=0)
    truckNo = models.IntegerField()
    shiftDate = models.DateField(null=True, default=None)
    startTime = models.CharField(max_length=200)
    endTime = models.CharField(max_length=200)
    dispute = models.BooleanField(default = False)
    loadSheet = models.FileField(upload_to='static/img/finalloadSheet',null=True, blank=True)
    comment = models.CharField(max_length=200, default='None')
    comment2 = models.CharField(max_length=200, default='None')

    def __str__(self) -> str:
        return str(self.id)


class DriverDocket(models.Model):
    docketId = models.AutoField(primary_key=True)
    shiftDate = models.DateField(null=True, default=timezone.now())
    tripId = models.ForeignKey(DriverTrip, on_delete=models.CASCADE)
    docketNumber = models.IntegerField()
    docketFile = models.FileField(upload_to='static/img/docketFiles')
    basePlant = models.ForeignKey(BasePlant,on_delete=models.CASCADE)
    noOfKm = models.FloatField(default=0)
    transferKM = models.FloatField(default=0)
    returnToYard = models.BooleanField(default=False)
    tippingToYard = models.BooleanField(default=False)
    returnQty = models.FloatField(default=0)
    returnKm = models.FloatField(default=0)
    waitingTimeStart = models.CharField(max_length=200)
    waitingTimeEnd = models.CharField(max_length=200)
    totalWaitingInMinute = models.FloatField(default=0)
    surcharge_type = models.ForeignKey(Surcharge, on_delete=models.CASCADE)
    surcharge_duration = models.FloatField(default=0)
    cubicMl = models.FloatField(default=0)
    standByStartTime = models.CharField(max_length=200)
    standByEndTime = models.CharField(max_length=200)
    standBySlot = models.PositiveIntegerField(default=0, null=True)
    minimumLoad = models.FloatField(default=0)
    others = models.FloatField(default=0)
    comment = models.CharField(max_length=255, null=True, default='None')
    
    # Holcim 
    # jobNo = models.FloatField(default=0)
    # orderNo = models.FloatField(default=0)
    # status = models.CharField(max_length=200)
    # ticketedDate = models.DateField(null=True, default=None)
    # ticketedTime = models.TimeField(null=True, blank=True)
    # load = models.CharField(max_length= 100 , default=None, null= True, blank=True)
    # loadComplete = models.CharField(max_length=200)
    # toJob = models.CharField(max_length= 100 , default=None, null= True, blank=True)
    # timeToDepart = models.FloatField(default=0)
    # onJob = models.CharField(max_length= 100 , default=None, null= True, blank=True)
    # timeToSite = models.FloatField(default=0)
    # beginUnload = models.CharField(max_length= 100 , default=None, null= True, blank=True)
    # waitingTime = models.FloatField(default=0)
    # endPour = models.CharField(max_length= 100 , default=None, null= True, blank=True)
    # wash = models.CharField(max_length= 100 , default=None, null= True, blank=True)
    # toPlant = models.CharField(max_length= 100 , default=None, null= True, blank=True)
    # timeOnSite = models.FloatField(default=0)
    # atPlant = models.CharField(max_length= 100 , default=None, null= True, blank=True)
    # leadDistance = models.FloatField(default=0)
    # returnDistance = models.FloatField(default=0)
    # totalDistance = models.FloatField(default=0)
    # totalTime = models.FloatField(default=0)
    # waitTimeBetweenJob = models.FloatField(default=0)
    # driverName = models.ForeignKey(Driver, on_delete=models.CASCADE)
    # quantity = models.FloatField(default=0)
    # slump = models.FloatField(default=0)
    # waterAdded = models.FloatField(max_length=200)
    
    
    def __str__(self) -> str:
        return str(self.docketNumber)

    class Meta:
        unique_together = (('docketNumber', 'shiftDate','tripId'),)

class RctiReport(models.Model):
    reportDate = models.DateField()
    gstPayable = models.FloatField(default=0)
    clientName = models.ForeignKey(Client,on_delete=models.CASCADE ,default = None)
    totalExGST = models.FloatField(default=0)
    total = models.FloatField(default=0)
    fileName = models.CharField(max_length=255 , default='')
    
    def __str__(self) -> str:
        return str(self.id)
    
    class Meta:
        unique_together = (('reportDate', 'total','fileName'))

class RctiAdjustment(models.Model):
    truckNo = models.FloatField(default=0)
    docketNumber = models.CharField(max_length=10,default='')
    docketDate = models.DateField()
    docketYard = models.CharField(default='', max_length=255)
    clientName = models.ForeignKey(Client,on_delete=models.CASCADE)
    rctiReport = models.ForeignKey(RctiReport,on_delete=models.CASCADE , default =None)
    description = models.CharField(max_length=255,default='')
    noOfKm = models.FloatField(default=0)
    invoiceQuantity = models.FloatField(default=0)
    unit = models.CharField(max_length=10,default='')
    unitPrice= models.FloatField(default=0)
    totalExGST = models.FloatField(default=0)
    GSTPayable = models.FloatField(default=0)
    Total = models.FloatField(default=0)
    
    def __str__(self) -> str:
        return str(self.docketNumber)
    
    # class Meta:
    #     unique_together = (('docketNumber', 'docketDate','rctiReport','truckNo'))
    
class RCTI(models.Model):
    
    UNIT_CHOICES = (
        ('minute','MINUTE'),
        ('slot','SLOT'),
    )

    truckNo = models.FloatField(default=0)
    docketNumber = models.CharField(max_length=10,default='')
    docketDate = models.DateField()
    docketYard = models.CharField(default='', max_length=255)
    clientName = models.ForeignKey(Client,on_delete=models.CASCADE)
    rctiReport = models.ForeignKey(RctiReport,on_delete=models.CASCADE , default =None)
    noOfKm = models.FloatField(default=0)
    cubicMl = models.FloatField(default=0)
    cubicMiAndKmsCost= models.FloatField(default=0)
    destination = models.CharField(max_length=255, default='Not given')
    cartageGSTPayable = models.FloatField(default=0)
    cartageTotalExGST = models.FloatField(default=0)
    cartageTotal = models.FloatField(default=0)
    
    # Holcim 
    unit = models.CharField(default='', max_length=10)
    paidQty = models.FloatField(default=0)
    
    
    transferKM = models.FloatField(default=0)
    transferKMCost = models.FloatField(default=0)
    transferKMGSTPayable = models.FloatField(default=0)
    transferKMTotalExGST = models.FloatField(default=0)
    transferKMTotal = models.FloatField(default=0)
    
    returnKm = models.FloatField(default=0)
    returnPerKmPerCubicMeterCost = models.FloatField(default=0)
    returnKmGSTPayable = models.FloatField(default=0)
    returnKmTotalExGST = models.FloatField(default=0)
    returnKmTotal = models.FloatField(default=0)
    
    waitingTimeSCHED = models.FloatField(default=0)
    waitingTimeSCHEDCost = models.FloatField(default=0)
    waitingTimeSCHEDGSTPayable = models.FloatField(default=0)
    waitingTimeSCHEDTotalExGST = models.FloatField(default=0)
    waitingTimeSCHEDTotal = models.FloatField(default=0)
    
    waitingTimeInMinutes = models.FloatField(default=0)
    waitingTimeCost = models.FloatField(default=0)
    waitingTimeGSTPayable = models.FloatField(default=0)
    waitingTimeTotalExGST = models.FloatField(default=0)
    waitingTimeTotal = models.FloatField(default=0)
    
    standByNoSlot = models.FloatField(default=0)
    standByPerHalfHourDuration = models.FloatField(default=0)
    standByUnit = models.CharField(choices=UNIT_CHOICES,default="minute",max_length=6)
    standByGSTPayable = models.FloatField(default=0)
    standByTotalExGST = models.FloatField(default=0)
    standByTotal = models.FloatField(default=0)
    
    
    minimumLoad = models.FloatField(default=0)
    loadCost = models.FloatField(default=0)
    minimumLoadGSTPayable = models.FloatField(default=0)
    minimumLoadTotalExGST = models.FloatField(default=0)
    minimumLoadTotal = models.FloatField(default=0)

    # Holcim 
    blowBack= models.FloatField(default=0)
    blowBackCost = models.FloatField(default=0)
    blowBackGSTPayable = models.FloatField(default=0)
    blowBackTotalExGST = models.FloatField(default=0)
    blowBackTotal = models.FloatField(default=0)
    
    
    # surcharge_fixed_weekend= models.FloatField(default=0)
    # surcharge_fixed_weekendCost = models.FloatField(default=0)
    # surcharge_fixed_weekendGSTPayable = models.FloatField(default=0)
    # surcharge_fixed_weekendTotalExGST = models.FloatField(default=0)
    # surcharge_fixed_weekendTotal = models.FloatField(default=0)
    
    # surcharge_fixed_weekday= models.FloatField(default=0)
    # surcharge_fixed_weekdayCost = models.FloatField(default=0)
    # surcharge_fixed_weekdayGSTPayable = models.FloatField(default=0)
    # surcharge_fixed_weekdayTotalExGST = models.FloatField(default=0)
    # surcharge_fixed_weekdayTotal = models.FloatField(default=0)
    
    callOut= models.FloatField(default=0)
    callOutCost = models.FloatField(default=0)
    callOutGSTPayable = models.FloatField(default=0)
    callOutTotalExGST = models.FloatField(default=0)
    callOutTotal = models.FloatField(default=0)
    
    # surcharge_fixed_normal = models.FloatField(default=0)
    # surcharge_fixed_sunday = models.FloatField(default=0)
    # surcharge_fixed_public_holiday = models.FloatField(default=0)
    # surcharge_per_cubic_meters_normal = models.FloatField(default=0)
    # surcharge_per_cubic_meters_sunday = models.FloatField(default=0)
    # surcharge_per_cubic_meters_public_holiday = models.FloatField(default=0)
    # surcharge_duration = models.FloatField(default=0)
    # surchargeUnit = models.CharField(choices=UNIT_CHOICES,default="minute",max_length=6)
    surcharge = models.FloatField(default=0)
    surchargeCost = models.FloatField(default=0)
    surchargeGSTPayable = models.FloatField(default=0)
    surchargeTotalExGST = models.FloatField(default=0)
    surchargeTotal = models.FloatField(default=0)
   
    otherDescription = models.CharField(max_length=500,default= '', null= True , blank=True)
    others = models.CharField(max_length=255,default= 0, null= True , blank=True)
    othersCost = models.FloatField(default=0)
    othersGSTPayable = models.FloatField(default=0)
    othersTotalExGST = models.FloatField(default=0)
    othersTotal = models.FloatField(default=0)
    
    def _str_(self) -> str:
        return str(self.docketNumber) + str(self.truckNo)

    
# -----------------------------------
# Holiday section
# -----------------------------------

class PublicHoliday(models.Model):
    date = models.DateField()
    stateName = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    
    def __str__(self) -> str:
        return str(self.description)
    
    
# -----------------------------------
# Past trip errors model
# -----------------------------------

class PastTripError(models.Model):
    clientName = models.CharField(max_length=25 ,default=None ,blank=True,null=True)
    tripDate = models.CharField(max_length=255, default=None, null=True, blank=True) 
    truckNo = models.IntegerField(default=0) 
    docketNumber = models.CharField(max_length=255, default=None, null=True, blank=True)
    lineNumber =  models.CharField(max_length=255, default=None, null=True, blank=True)   
    errorFromPastTrip = models.CharField(max_length=255, default=None, null=True, blank=True)
    fileName = models.CharField(max_length=255, default=None, null=True, blank=True)
    status = models.BooleanField(default=False)
    data = models.CharField(max_length=1024, default=' ')

    def __str__(self):
        return str(self.docketNumber)
    
    
# -----------------------------------
# Reconciliation model
# -----------------------------------
    
class ReconciliationReport(models.Model):
    docketNumber = models.CharField(max_length=10, default='')
    docketDate = models.DateField(default=None, null= True, blank=True)
    clientName =  models.CharField(max_length=20,default='')
    driverId = models.PositiveIntegerField(default=0)
    clientId = models.PositiveIntegerField(default=0)
    truckId = models.PositiveIntegerField(default=0)
    
    # 0:reconciliation, 1:Short Paid 2: Top up solved
    reconciliationType = models.PositiveIntegerField(default=0)
    missingComponent = models.CharField(max_length=255, default=None, null=True, blank=True)
    
    # escalationType = models.CharField(max_length=20,default='')
    # # 0:not escalate, 1:1st step, 2:2nd step, 3:3rd step, 4:escalation complete
    # escalationStep = models.PositiveIntegerField(default=0)
    # escalationAmount = models.PositiveIntegerField(default=0)
    # errorId = models.PositiveIntegerField(default=None)

    fromDriver = models.BooleanField(default=False)
    fromRcti = models.BooleanField(default=False)
    
    # loadKmcost 
    driverLoadAndKmCost = models.FloatField(default=0)
    rctiLoadAndKmCost = models.FloatField(default=0)
    
    # SurchargeCost
    driverSurchargeCost = models.FloatField(default=0)
    rctiSurchargeCost = models.FloatField(default=0)

    # WaitingTimeCost 
    driverWaitingTimeCost = models.FloatField(default=0)
    rctiWaitingTimeCost = models.FloatField(default=0)

    # TransferCost
    driverTransferKmCost = models.FloatField(default=0)
    rctiTransferKmCost = models.FloatField(default=0)
    
    # returnKmCost
    driverReturnKmCost = models.FloatField(default=0)
    rctiReturnKmCost = models.FloatField(default=0)
    
    # otherCost 
    driverOtherCost = models.FloatField(default=0)
    rctiOtherCost = models.FloatField(default=0)    
    
    # standByCost 
    driverStandByCost = models.FloatField(default=0)
    rctiStandByCost = models.FloatField(default=0)
    
    # minimum load
    driverLoadDeficit = models.FloatField(default=0)
    rctiLoadDeficit = models.FloatField(default=0)

    # Total 
    driverTotalCost = models.FloatField(default=0)
    rctiTotalCost = models.FloatField(default=0)
        
    def __str__(self):
        return str(self.docketNumber)
    

# -----------------------------------
# Escalation Mail section
# -----------------------------------
class Escalation(models.Model):
    escalationType = [('External', 'External'),('Internal', 'Internal'),]
    
    docketNumber = models.CharField(max_length=10, default=None)
    docketDate = models.DateField(default=None, null=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    escalationDate = models.DateField(default=None, null=True)
    escalationType = models.CharField(max_length=20,choices=escalationType, default='External')
    remark = models.CharField(max_length=1024, default='')
    clientName = models.ForeignKey(Client, on_delete=models.CASCADE, default=None)
    
    # 1:1st step, 2:2nd step, 3:3rd step, 4:4th step, 5:complete
    escalationStep = models.PositiveIntegerField(default=1)
    escalationAmount = models.IntegerField(default=0)
    errorId = models.PositiveIntegerField(default=None, null=True)
    
    def __str__(self) -> str:
        return str(self.docketNumber) + ' ' + str(self.escalationType)
    
    
class EscalationMail(models.Model):
    mailType = [('Send', 'Send'),('Receive', 'Receive'),]
    
    escalationId = models.ForeignKey(Escalation, on_delete=models.CASCADE, default=None)
    userId = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    mailTo = models.CharField(default=None, max_length=50)
    mailFrom = models.CharField(default=None, max_length=50)
    mailSubject = models.CharField(default=None, max_length=255)
    mailDescription = models.CharField(default=None, max_length=1024)    
    mailAttachment = models.FileField(default=None, null=True, blank=True)    
    mailType = models.CharField(max_length=20, choices=mailType, default='Send')
    mailDate = models.DateField(default=None, null=True)
    mailCount = models.PositiveBigIntegerField(default=1)
    
    def __str__(self) -> str:
        return str(self.escalationId) + ' ' + str(self.mailDate)
    
    
# -----------------------------------
# Rcti Error section
# -----------------------------------
class RctiErrors(models.Model):
    clientName = models.CharField(max_length=25 ,default=None ,blank=True,null=True)
    docketNumber = models.CharField(default=None ,blank=True,null=True ,max_length=255)
    docketDate = models.CharField(default=None, blank=True,null=True, max_length=255)
    errorDescription = models.CharField(default=None ,blank=True,null=True ,max_length=255)
    fileName =  models.CharField(default=None ,blank=True,null=True ,max_length=255)
    status = models.BooleanField(default=False)
    data = models.CharField(max_length=1024,default='')
    # 0:Earning, 1 : earning top up manually managed error
    errorType = models.PositiveIntegerField(default=0)
    
    def __str__(self) -> str:
        return str(self.docketNumber) +' '+ str(self.errorDescription)

# -----------------------------------
# Rcti Expense section
# -----------------------------------
class RctiExpense(models.Model):
    clientName = models.ForeignKey(Client,on_delete=models.CASCADE ,default = None)
    truckNo = models.CharField(max_length=10, default='')
    docketNumber = models.CharField( max_length=10,default='')
    docketDate = models.DateField()
    docketYard = models.CharField(default='', max_length=255)
    description = models.CharField(max_length=255)
    paidKm = models.FloatField(default=0)
    invoiceQuantity = models.FloatField(default=0)
    unit = models.CharField(max_length=100 , default= '')
    unitPrice = models.FloatField(default=0)
    gstPayable = models.FloatField(default=0)
    totalExGST = models.FloatField(default=0)
    total = models.FloatField(default=0)
    
    def __str__(self):
        return str(self.docketNumber)
    
# model rename  holcimTripReport
class HolcimTrip(models.Model):
    truckNo = models.PositiveBigIntegerField(default=0)
    shiftDate = models.DateField(null=True, default=None)
    numberOfLoads = models.FloatField(default=0)
    
    def __str__(self):
        return str(self.id)
    
# model rename  holcimDocketReport
class HolcimDocket(models.Model):
    truckNo =  models.FloatField(default=0)
    tripId = models.ForeignKey(HolcimTrip, on_delete=models.CASCADE)
    jobNo = models.FloatField(default=0)
    orderNo = models.FloatField(default=0)
    status = models.CharField(max_length=200)
    ticketedDate = models.DateField(null=True, default=None)
    ticketedTime = models.TimeField(null=True, blank=True)
    load = models.CharField(max_length= 100 , default=None, null= True, blank=True)
    loadComplete = models.CharField(max_length=200)
    toJob = models.CharField(max_length= 100 , default=None, null= True, blank=True)
    timeToDepart = models.FloatField(default=0)
    onJob = models.CharField(max_length= 100 , default=None, null= True, blank=True)
    timeToSite = models.FloatField(default=0)
    beginUnload = models.CharField(max_length= 100 , default=None, null= True, blank=True)
    waitingTime = models.FloatField(default=0)
    endPour = models.CharField(max_length= 100 , default=None, null= True, blank=True)
    wash = models.CharField(max_length= 100 , default=None, null= True, blank=True)
    toPlant = models.CharField(max_length= 100 , default=None, null= True, blank=True)
    timeOnSite = models.FloatField(default=0)
    atPlant = models.CharField(max_length= 100 , default=None, null= True, blank=True)
    leadDistance = models.FloatField(default=0)
    returnDistance = models.FloatField(default=0)
    totalDistance = models.FloatField(default=0)
    totalTime = models.FloatField(default=0)
    waitTimeBetweenJob = models.FloatField(default=0)
    driverName = models.ForeignKey(Driver, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)
    slump = models.FloatField(default=0)
    waterAdded = models.FloatField(max_length=200)
    
    def __str__(self):
        return str(self.jobNo)
    
    class Meta:
        unique_together = (('jobNo', 'ticketedDate','tripId'))