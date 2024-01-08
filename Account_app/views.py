from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
import shutil, os, colorama, subprocess, csv, re, pytz
from django.views.decorators.csrf import csrf_protect
from datetime import datetime , time, timedelta, timezone
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.contrib import messages
from Account_app.models import *
from GearBox_app.models import *
from Appointment_app.models import *
from django.http import FileResponse
from CRUD import *
from .models import RCTI
from Account_app.reconciliationUtils import *
from django.urls import reverse
from django.db.models import Q
from itertools import chain

from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'Account/dashboard.html')

def getForm1(request):
    if request.user.is_authenticated:
        params = {}
        driver = Driver.objects.filter(email=request.user.email).first()
        if driver:
            driver_id = str(driver.driverId) + '-' + str(driver.name)
            preStart_data = PreStart.objects.filter(curDate__date=date.today(), driver=driver).first()
            if preStart_data:
                existingTodayTrip = DriverTrip.objects.filter(driverId=driver, partially=True).first()
                if existingTodayTrip:
                    existingTodayTrip.shiftDate = dateConverterFromTableToPageFormate(existingTodayTrip.shiftDate)
                    params['existingTodayTrip'] = existingTodayTrip
            
                params['driver_ids'] = driver_id
            else:
                messages.error(request,'Please fill up Pre-start first.')
                return redirect('Account:timeOfStart') 
        else:
            params['client_ids'] =  Client.objects.values_list('name', flat=True).distinct()
            params['admin_truck_no'] =  AdminTruck.objects.values_list('adminTruckNumber', flat=True).distinct()
            params['client_truck_no'] =  ClientTruckConnection.objects.values_list('clientTruckId', flat=True).distinct()
            params['drivers'] = Driver.objects.all()
            
        return render(request, 'Trip_details/form1.html', params)
    else:
        return redirect('login')

def getForm2(request, id=None):
    if not id:
        params = {
            'loads': [i+1 for i in range(int(request.session['data'].get('numberOfLoads')))]
        }
    else:
        dockets = DriverDocket.objects.filter(tripId=id)
        params = {
            'dockets': dockets
        }
        
    return render(request, 'Trip_details/Form2.html', params)

def createFormSession(request):
    loadSheet = request.FILES.get('loadSheet')
    driverId = request.POST.get('driverId').split('-')[0]
    truckNo = request.POST.get('truckNum').split('-')[0]
    driverObj = Driver.objects.filter(pk=driverId).first()
    existingTodayTrip = DriverTrip.objects.filter(driverId=driverObj, shiftDate=request.POST.get('shiftDate'), truckNo=truckNo, partially=True).first()
    if existingTodayTrip:
        existingTodayTrip.dispute = True if request.POST.get('dispute') == 'dispute' else False
        existingTodayTrip.save()
    
    data = {}  
    clientName = request.POST.get('clientName')
    if loadSheet:
        load_sheet_folder_path = 'Temp_Load_Sheet'
        fileName = loadSheet.name.replace(" ", "").replace("\t", "")
        time = getCurrentTimeInString()

        load_sheet_new_filename = 'Load_Sheet' + time + '!_@' + fileName
        lfs = FileSystemStorage(location=load_sheet_folder_path)
        lfs.save(load_sheet_new_filename, loadSheet)
           
        data = {
            'driverId': request.POST.get('driverId').split('-')[0],
            'clientName': clientName,
            'truckNum': truckNo,
            'startTime': request.POST.get('startTime'),
            'endTime': request.POST.get('endTime'),
            'shiftDate': request.POST.get('shiftDate'),
            'shiftType': request.POST.get('shiftType'),
            'numberOfLoads': request.POST.get('numberOfLoads'),
            'comments': request.POST.get('comments'),
        }
        
    data['docketGiven'] = not Client.objects.get(name=clientName).docketGiven,
    data['docketGiven'] =  not Client.objects.get(name=clientName).docketGiven,
    data['loadSheet'] = load_sheet_new_filename
    
    request.session['data'] = data
       
    if Client.objects.get(name=clientName).docketGiven:
        return redirect('Account:formsSave') 
    elif existingTodayTrip:
        return redirect('Account:existingForm2', id=existingTodayTrip.id)
    else:
        return redirect('Account:getForm2')

# @csrf_protect
# @api_view(['POST'])
def formsSave(request):
    driverId = request.session['data']['driverId']
    clientName = Client.objects.get(name=request.session['data']['clientName'])
    shiftType = request.session['data']['shiftType']
    numberOfLoads = request.session['data']['numberOfLoads']
    truckNo = request.session['data']['truckNum']
    startTime = request.session['data']['startTime']
    endTime = request.session['data']['endTime']
    shiftDate = request.session['data']['shiftDate']
    loadSheet = request.session['data']['loadSheet']
    comment = request.session['data']['comments']
    temp_loadSheet = ''
    Docket_no, Docket_file = [], []
    time = getCurrentTimeInString()
    driver = Driver.objects.get(driverId=driverId)
    comment2 = request.POST.get('comments')
    
    existingTodayTrip = DriverTrip.objects.filter(driverId=driver, shiftDate=shiftDate, truckNo=truckNo, partially=True).first()
        
    if not os.path.exists('static/img/finalloadSheet/' + loadSheet):
        shutil.move('Temp_Load_Sheet/' + loadSheet, 'static/img/finalloadSheet/' + loadSheet)
        
    if not existingTodayTrip:
        if not request.session['data']['docketGiven']:
            for i in range(1, int(numberOfLoads)+1):
                key = f"docketNumber[{i}]"
                docket_number = request.POST.get(key)
                Docket_no.append(docket_number)
                key_files = f"docketFile[{i}]"
                docket_files = request.FILES.get(key_files)
                temp_loadSheet = temp_loadSheet + '-' + docket_number
                if docket_files:
                    fileName = docketFileSave(docket_files, docket_number, returnVal='file_name')
                    Docket_file.append(fileName)

        tripObj = DriverTrip()
        tripObj.driverId=driver
        tripObj.clientName=clientName
        tripObj.shiftType=shiftType
        tripObj.numberOfLoads=numberOfLoads
        tripObj.truckNo=truckNo
        tripObj.startTime=startTime
        tripObj.endTime=endTime
        tripObj.loadSheet = f'static/img/finalloadSheet/{loadSheet}'
        tripObj.comment=comment
        tripObj.shiftDate=shiftDate  
        tripObj.save()

        if not request.session['data']['docketGiven']:
            BasePlantVal = BasePlant.objects.get_or_create(basePlant="NOT SELECTED")[0]
            for i in range(len(Docket_no)):
                docket_ = DriverDocket(
                    tripId=tripObj,
                    docketNumber=Docket_no[i],
                    docketFile='static/img/docketFiles/' + Docket_file[i],
                    basePlant=BasePlantVal
                )
                docket_.surcharge_type = Surcharge.objects.get_or_create(surcharge_Name = 'No Surcharge')[0]
                docket_.save()

    else:
        existingTodayTrip.loadSheet = f'static/img/finalloadSheet/{loadSheet}'
        existingTodayTrip.comment=comment
        existingTodayTrip.shiftDate=shiftDate        
        existingTodayTrip.partially = False
        existingTodayTrip.comment2 = comment2
        existingTodayTrip.save()
        
    del request.session['data']

    messages.success(request, "Form Successfully Filled Up")
    return redirect('index')


def assignedJobShow(request):
    driverObj = Driver.objects.filter(name = request.user.username).first()
    today = date.today()
    preStart_data = PreStart.objects.filter(curDate__date=today, driver=driverObj).first()

    if preStart_data:
        appointmentObjs = Appointment.objects.filter(Start_Date_Time__date=today,appointmentdriver__driverName__name=driverObj.name).order_by('Start_Date_Time')
        indian_timezone = pytz.timezone('Asia/Kolkata')
        
        currentTime = datetime.now(tz=indian_timezone)

        for obj in appointmentObjs:
            if obj.Status != "Dispatched":
                maxTime = obj.Start_Date_Time + timedelta(minutes=20)
                minTime = obj.Start_Date_Time - timedelta(minutes=20)
                # print(f"startTime:{obj.Start_Date_Time}, max:{maxTime}, min:{minTime}, Current:{datetime.now(tz=indian_timezone)}\n")
                if obj.Status != "Complete" and  str(currentTime) > str(maxTime):
                    obj.lateForStart = True   
                elif obj.Status != "Complete" and  str(currentTime) < str(minTime): 
                    obj.notAcceptable = True  
                
        params = {'jobs':appointmentObjs}
        return render(request, 'Trip_details/assignedJobs.html',params)
    else:
        messages.error(request,'Please fill up Pre-start first.')
        return redirect('Account:timeOfStart')



def assignedJobAccept(request,id):
    # Check wether any job is currently open or not start
    driverObj = Driver.objects.filter(name = request.user.username).first()
    driverAppointments = AppointmentDriver.objects.filter(driverName = driverObj)
    jobs = 0
    today_date = timezone.now().date()
    preStart_data = PreStart.objects.filter(curDate__date=today_date, driver=driverObj).first()
    
    if preStart_data:
        for obj in driverAppointments:
            if obj.appointmentId.Status == "Dispatched":
                jobs += 1 
        if jobs > 0 :
            messages.error(request,'Please finish your current job before starting a new one.')
            return redirect(request.META.get('HTTP_REFERER'))
        
        # Check wether any job is currently open or not end
        appObj = Appointment.objects.filter(pk=id).first()
        appObj.Status = "Dispatched"
        appObj.save()
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request,'You have to filled up pre-start first.')
        return redirect(request.META.get('HTTP_REFERER'))
        
        
def singleJobView(request,id):
    job = Appointment.objects.filter(pk=id).first()
    driver = AppointmentDriver.objects.filter(appointmentId = job).first()
    truck = AppointmentTruck.objects.filter(appointmentId = job).first()
    indian_timezone = pytz.timezone('Asia/Kolkata')
    currentTime = datetime.now(tz=indian_timezone)
    maxTime = job.Start_Date_Time + timedelta(minutes=20)
    minTime = job.Start_Date_Time - timedelta(minutes=20)

    if job.Status != "Complete" and  str(currentTime) > str(maxTime):
        job.lateForStart = True   
    if job.Status != "Complete" and  str(currentTime) < str(minTime): 
        job.notAcceptable = True   
    
    params = {
        'job':job,
        'driver':driver,
        'truck':truck
    }
    return render(request,'Trip_details/jobView.html',params)

# @login_required
def openJobShow(request):
    driverObj = Driver.objects.filter(name = request.user.username).first()
    driverAppointments = AppointmentDriver.objects.filter(driverName = driverObj)
    jobs = []
    for obj in driverAppointments:
        print(obj.appointmentId.Status)
        if obj.appointmentId.Status == "Dispatched":
            jobs.append(obj.appointmentId)
            
    params = {'jobs':jobs}    
    return render(request, 'Trip_details/openJobs.html',params)
    
def finishJob(request, id):
    if id:
        appObj = Appointment.objects.filter(pk=id).first()
        if not appObj.stop.docketGiven:
            return redirect('Account:uploadDocketView', id)
        else:
            return redirect('Account:getHolcimTripDataView', id)

@login_required
def uploadDocketView(request,id):
    params = {'id':id}
    return render(request, 'Trip_details/uploadDocket.html',params)

@csrf_protect
def uploadDocketSave(request, id):
    appointmentObj = Appointment.objects.filter(pk=id).first()
    startDateObj = datetime.strptime(str(appointmentObj.Start_Date_Time), "%Y-%m-%d %H:%M:%S%z")
    endDateObj = datetime.strptime(str(appointmentObj.End_Date_Time), "%Y-%m-%d %H:%M:%S%z")
    AppointmentTruckObject = AppointmentTruck.objects.filter(appointmentId = appointmentObj).first()

    docketFile = request.FILES.get('docketImage')
    docketNumber = request.POST.get('docketNumber')
    comment = request.POST.get('comment')
    driverObj = Driver.objects.filter(name = request.user.username).first()
    
    # Trip save start
    tripObj = DriverTrip.objects.filter(driverId = driverObj, shiftDate=startDateObj.date(),clientName = appointmentObj.stop).first()
    if not tripObj:
        tripObj = DriverTrip()
        tripObj.driverId = driverObj
        tripObj.clientName = appointmentObj.stop
        tripObj.shiftType = appointmentObj.shiftType
        tripObj.truckNo = AppointmentTruckObject.truckNo.adminTruckNumber
        tripObj.shiftDate = startDateObj.date()
        
    tripObj.partially = True
    startTime = tripObj.startTime
    endTime = tripObj.endTime
    time_pattern = re.compile(r'^\d{2}:\d{2}$')
    
    if time_pattern.match(startTime):
        startTime = startTime+":00"
    if time_pattern.match(endTime):
        startTime = startTime+":00"

    # Set startTime  
    if not startTime:
        tripObj.startTime = startDateObj.time()
    else:
        if not isinstance(startTime, datetime):
            startTime = datetime.strptime(startTime, "%H:%M:%S")
        if startTime.time() < startDateObj.time():
            tripObj.startTime = startDateObj.time()
    # Set startTime  

    # Set endTime 
    if not endTime:
        tripObj.endTime = endDateObj.time()
    else:
        if not isinstance(endTime, datetime):
            endTime = datetime.strptime(endTime, "%H:%M:%S")
        if endTime.time() < endDateObj.time():
            tripObj.endTime = endDateObj.time()
    # Set endTime
    
    tripObj.save()    
    # Trip save end

    # Docket save start
    docketObj = DriverDocket.objects.filter(tripId = tripObj ,docketNumber=docketNumber).first()
    if docketObj:
        messages.error(request, "This docket is already exist, please check docket number.")
        return redirect(request.META.get('HTTP_REFERER'))

    else:
        docketObj = DriverDocket()
        docketObj.docketNumber = docketNumber
        if docketFile:
            docketObj.docketFile = docketFileSave(docketFile, docketNumber)
        
        docketObj.basePlant = appointmentObj.Origin
        docketObj.comment = comment
        docketObj.tripId = tripObj
        docketObj.shiftDate = startDateObj.date()

        docketObj.surcharge_type = Surcharge.objects.filter(surcharge_Name = "No Surcharge").first()

        tripObj.numberOfLoads += 1
        tripObj.save()

        docketObj.save()
        
    # Docket save end

    appointmentObj.Status = "Complete"
    appointmentObj.save()
    messages.success(request, "Docket Updated")
    
    return redirect('Account:assignedJobShow')

@login_required
def getHolcimDataView(request,id):
    params = {'id':id}
    return render(request, 'Trip_details/getHolcimData.html',params)

@login_required
def getHolcimDataSave(request,id):
    appointmentObj = Appointment.objects.filter(pk=id).first()
    startDateObj = datetime.strptime(str(appointmentObj.Start_Date_Time), "%Y-%m-%d %H:%M:%S%z")
    endDateObj = datetime.strptime(str(appointmentObj.End_Date_Time), "%Y-%m-%d %H:%M:%S%z")
    AppointmentTruckObject = AppointmentTruck.objects.filter(appointmentId = appointmentObj).first()
    driverObj = Driver.objects.filter(name = request.user.username).first()
    
    tripObj = DriverTrip.objects.filter(driverId = driverObj, shiftDate=startDateObj.date(),clientName = appointmentObj.stop).first()
    if not tripObj:
        tripObj = DriverTrip()
        tripObj.driverId = driverObj
        tripObj.clientName = appointmentObj.stop
        tripObj.shiftType = appointmentObj.shiftType
        tripObj.truckNo = AppointmentTruckObject.truckNo.adminTruckNumber
        tripObj.numberOfLoads = 1
        tripObj.shiftDate = startDateObj.date()
    else:
        tripObj.numberOfLoads += 1

    tripObj.partially = True
    startTime = tripObj.startTime
    endTime = tripObj.endTime
    time_pattern = re.compile(r'^\d{2}:\d{2}$')
    
    if time_pattern.match(startTime):
        startTime = startTime+":00"
    if time_pattern.match(endTime):
        startTime = startTime+":00"
    
    # Set startTime  
    if not startTime:
        tripObj.startTime = startDateObj.time()
    else:
        if not isinstance(startTime, datetime):
            startTime = datetime.strptime(startTime, "%H:%M:%S")
        if startTime.time() < startDateObj.time():
            tripObj.startTime = startDateObj.time()
    # Set startTime  

    # Set endTime 
    if not endTime:
        tripObj.endTime = endDateObj.time()
    else:
        if not isinstance(endTime, datetime):
            endTime = datetime.strptime(endTime, "%H:%M:%S")
        if endTime.time() < endDateObj.time():
            tripObj.endTime = endDateObj.time()
    # Set endTime
    
    tripObj.save()    
    # Trip save end

    appointmentObj.Status = "Complete"
    appointmentObj.save()
    messages.success(request, "Docket Updated")
    return redirect('Account:assignedJobShow')

def timeOfStart(request):
    today_date = timezone.now().date()
    driver = Driver.objects.filter(email=request.user.email).first()

    preStart_data = PreStart.objects.filter(curDate__date=today_date, driver=driver).first()
    if not preStart_data:
        return render(request, 'Trip_details/pre-startForm.html')
    else:
        messages.error(request, "You already filled Pre-start.")
        return redirect(request.META.get('HTTP_REFERER'))


@csrf_protect 
def timeOfStartSave(request):
    driver = Driver.objects.filter(email=request.user.email).first()
    if driver:
        preStart_data = PreStart.objects.filter(curDate__date=datetime.now().date(), driver=driver).first()

        if not preStart_data:
            dataSet = {
                'fitForWork' : True if request.POST.get('fitForWork') == 'Yes' else False,
                'vehicleStatus' : True if request.POST.get('vehicleStatus') == 'Yes' else False,
                'vehiclePaper' : True if request.POST.get('papersReady') == 'Yes' else False,
                'comment' : request.POST.get('comment').strip(),
                'curDate' : datetime.now(),
                'driver' : driver
            }  
        
            insert = insertIntoTable(tableName='PreStart',dataSet=dataSet)
            if insert == True:
                messages.success(request, "Pre-start filled up.")
                return redirect('Account:assignedJobShow')
            else:
                messages.error(request, "something went wrong, please try again")
                return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, "You already filled Pre-start.")
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "You have no access for fill up Pre-start.")
        return redirect(request.META.get('HTTP_REFERER'))

    

@csrf_protect
@api_view(['POST'])
def getTrucks(request):
    clientName = request.POST.get('clientName')
    client = Client.objects.get(name=clientName)
    truckList = []
    truck_connections = ClientTruckConnection.objects.filter(
        clientId=client.clientId)
    docket = client.docketGiven

    for truck_connection in truck_connections:
        truckList.append(str(truck_connection.truckNumber) +
                         '-' + str(truck_connection.clientTruckId))
    return JsonResponse({'status': True, 'trucks': truckList, 'docket': docket})


def rcti(request):
    rctiErrors = RctiErrors.objects.filter(status = False).values()
    rctiSolve = RctiErrors.objects.filter(status = True).values()
    rctiManually = RctiErrors.objects.filter(status = False , errorType = 1).values()
    client = Client.objects.all()
    BasePlant_ = BasePlant.objects.all()
    # return render(request, 'Account/rctiCsvForm.html', {'basePlants': BasePlant_})
    # return HttpResponse(rctiErrors)
    params = {
        'rctiErrors' : rctiErrors,
        'rctiSolve' :rctiSolve,
        'client':client,
        'basePlants': BasePlant_
    }
    
    return render(request, 'Account/rctiForm.html',params)

def rctiErrorSolve(request ,id): 
           
    rctiErrorsObj = RctiErrors.objects.get(id = id)
    rctiErrorsObj.status = True
    rctiErrorsObj.save()
    messages.success(request, "Docket status change ")
    return redirect(request.META.get('HTTP_REFERER'))
    

def rctiForm(request, id= None , holcimDocketId = None):
    rcti = None
    holcimDocket = None
    clientName = Client.objects.all()
    drivers = Driver.objects.all()
    if id:
        rcti = RCTI.objects.filter(pk=id).first()
        rcti.docketDate = rcti.docketDate.strftime("%d-%m-%Y")
    elif holcimDocketId:
        holcimDocket = HolcimDocket.objects.filter(pk = holcimDocketId).first()
    params = {
        'rcti': rcti,
        'clientNames':clientName,
        'docketData':holcimDocket,
        'Driver':drivers,
    }
    return render(request, 'Account/Tables/rctiForm.html', params)

def convertIntoFloat(str):
    cleaned_string = str.strip('()')
    return float(cleaned_string)

@csrf_protect
def rctiFormSave(request):
    RCTIobj = RCTI()
    clientObj = Client.objects.filter(name='boral').first()
    RCTIobj.truckNo = request.POST.get('truckNo')
    RCTIobj.clientName = clientObj
    RCTIobj.docketNumber = request.POST.get('docketNumber')
    RCTIobj.docketDate = request.POST.get('docketDate')
    RCTIobj.docketYard = request.POST.get('docketYard')
    RCTIobj.noOfKm = request.POST.get('noOfKm')
    RCTIobj.cubicMl = request.POST.get('cubicMl')
    RCTIobj.cubicMiAndKmsCost = request.POST.get('cubicMiAndKmsCost')
    RCTIobj.destination = request.POST.get('destination')
    RCTIobj.cartageGSTPayable = request.POST.get('cartageGSTPayable')
    RCTIobj.cartageTotalExGST = request.POST.get('cartageTotalExGST')
    RCTIobj.cartageTotal = request.POST.get('cartageTotal')
    RCTIobj.transferKM = request.POST.get('transferKM')
    RCTIobj.transferKMCost = request.POST.get('transferKMCost')
    RCTIobj.transferKMGSTPayable = request.POST.get('transferKMGSTPayable')
    RCTIobj.transferKMTotalExGST = request.POST.get('transferKMTotalExGST')
    RCTIobj.transferKMTotal = request.POST.get('transferKMTotal')
    RCTIobj.returnKm = request.POST.get('returnKm')
    RCTIobj.returnPerKmPerCubicMeterCost = request.POST.get('returnPerKmPerCubicMeterCost')
    RCTIobj.returnKmGSTPayable = request.POST.get('returnKmGSTPayable')
    RCTIobj.returnKmTotalExGST = request.POST.get('returnKmTotalExGST')
    RCTIobj.returnKmTotal = request.POST.get('returnKmTotal')
    RCTIobj.waitingTimeSCHED = request.POST.get('waitingTimeSCHED')
    RCTIobj.waitingTimeSCHEDCost = request.POST.get('waitingTimeSCHEDCost')
    RCTIobj.waitingTimeSCHEDGSTPayable = request.POST.get('waitingTimeSCHEDGSTPayable')
    RCTIobj.waitingTimeSCHEDTotalExGST = request.POST.get('waitingTimeSCHEDTotalExGST')
    RCTIobj.waitingTimeSCHEDTotal = request.POST.get('waitingTimeSCHEDTotal')
    RCTIobj.waitingTimeInMinutes = request.POST.get('waitingTimeInMinutes')
    RCTIobj.waitingTimeCost = request.POST.get('waitingTimeCost')
    RCTIobj.waitingTimeGSTPayable = request.POST.get('waitingTimeGSTPayable')
    RCTIobj.waitingTimeTotalExGST = request.POST.get('waitingTimeTotalExGST')
    RCTIobj.waitingTimeTotal = request.POST.get('waitingTimeTotal')
    RCTIobj.standByNoSlot = request.POST.get('standByNoSlot')
    RCTIobj.standByPerHalfHourDuration = request.POST.get('standByPerHalfHourDuration')
    RCTIobj.standByUnit = request.POST.get('standByUnit')
    RCTIobj.standByGSTPayable = request.POST.get('standByGSTPayable')
    RCTIobj.standByTotalExGST = request.POST.get('standByTotalExGST')
    RCTIobj.standByTotal = request.POST.get('standByTotal')
    RCTIobj.minimumLoad = request.POST.get('minimumLoad')
    RCTIobj.loadCost = request.POST.get('loadCost')
    RCTIobj.minimumLoadGSTPayable = request.POST.get('minimumLoadGSTPayable')
    RCTIobj.minimumLoadTotalExGST = request.POST.get('minimumLoadTotalExGST')
    RCTIobj.minimumLoadTotal = request.POST.get('minimumLoadTotal')
    RCTIobj.surcharge_fixed_normal = request.POST.get('surcharge_fixed_normal')
    RCTIobj.surcharge_fixed_sunday = request.POST.get('surcharge_fixed_sunday')
    RCTIobj.surcharge_fixed_public_holiday = request.POST.get('surcharge_fixed_public_holiday')
    RCTIobj.surcharge_per_cubic_meters_normal = request.POST.get('surcharge_per_cubic_meters_normal')
    RCTIobj.surcharge_per_cubic_meters_sunday = request.POST.get('surcharge_per_cubic_meters_sunday')
    RCTIobj.surcharge_per_cubic_meters_public_holiday = request.POST.get('surcharge_per_cubic_meters_public_holiday')
    RCTIobj.surcharge_duration = request.POST.get('surcharge_duration')
    RCTIobj.surchargeUnit = request.POST.get('surchargeUnit')
    RCTIobj.surchargeGSTPayable = request.POST.get('surchargeGSTPayable')
    RCTIobj.surchargeTotalExGST = request.POST.get('surchargeTotalExGST')
    RCTIobj.surchargeTotal = request.POST.get('surchargeTotal')
    RCTIobj.others = request.POST.get('others')
    RCTIobj.othersCost = request.POST.get('othersCost')
    RCTIobj.othersGSTPayable = request.POST.get('othersGSTPayable')
    RCTIobj.othersTotalExGST = request.POST.get('othersTotalExGST')
    RCTIobj.othersTotal = request.POST.get('othersTotal')
    
    RCTIobj.save()
    
    reconciliationDocketObj = ReconciliationReport.objects.filter(docketNumber = RCTIobj.docketNumber , docketDate = RCTIobj.docketDate ).first()

    rctiTotalCost =   convertIntoFloat(RCTIobj.cartageTotal) + convertIntoFloat(RCTIobj.waitingTimeTotal) + convertIntoFloat(RCTIobj.transferKMTotal)  +  convertIntoFloat(RCTIobj.returnKmTotal) + convertIntoFloat(RCTIobj.standByTotal) + convertIntoFloat(RCTIobj.minimumLoadTotal)
    
    if not reconciliationDocketObj :
        reconciliationDocketObj = ReconciliationReport()
    
    reconciliationDocketObj.docketNumber =  RCTIobj.docketNumber
    reconciliationDocketObj.docketDate =  RCTIobj.docketDate
    reconciliationDocketObj.rctiLoadAndKmCost =  RCTIobj.cartageTotalExGST
    # reconciliationDocketObj.rctiSurchargeCost =   RCTIobj.docketDate
    reconciliationDocketObj.rctiWaitingTimeCost = RCTIobj.waitingTimeTotal  
    reconciliationDocketObj.rctiTransferKmCost = RCTIobj.transferKMTotal 
    reconciliationDocketObj.rctiReturnKmCost =  RCTIobj.returnKmTotal
    # reconciliationDocketObj.rctiOtherCost =  RCTIobj.docketDate 
    reconciliationDocketObj.rctiStandByCost =  RCTIobj.standByTotal
    reconciliationDocketObj.rctiLoadDeficit =  RCTIobj.minimumLoadTotal
    reconciliationDocketObj.rctiTotalCost =  round(rctiTotalCost,2)
    reconciliationDocketObj.fromRcti = True 
    
    reconciliationDocketObj.save()
    checkMissingComponents(reconciliationDocketObj)
    
    messages.success( request, "RCTI entry successfully done.")
    return redirect('Account:rcti')

@csrf_protect
def rctiHolcimFormSave(request):
    driverObj = Driver.objects.filter(pk = request.POST.get('driverId')).first()
    holcimTripObj = HolcimTrip()
    existingDocket = HolcimDocket.objects.filter(ticketedDate = request.POST.get('ticketedDate'),jobNo = request.POST.get('jobNo'), truckNo = request.POST.get('truckNo')).first()
    if existingDocket:
            messages.error( request, "Job no already exist")
            return redirect(request.META.get('HTTP_REFERER'))
    existingTrip = HolcimTrip.objects.filter(truckNo = request.POST.get('truckNo'),shiftDate = request.POST.get('ticketedDate')).first()
    if existingTrip:
        existingTrip.numberOfLoads = existingTrip.numberOfLoads + 1
        existingTrip.save()
        holcimTripObj = existingTrip
    else:
        holcimTripObj.truckNo = request.POST.get('truckNo')
        holcimTripObj.shiftDate = request.POST.get('ticketedDate')
        holcimTripObj.numberOfLoads = 1
        holcimTripObj.save()
        
        

    holcimDocketObj =HolcimDocket()
    holcimDocketObj.truckNo = request.POST.get('truckNo')
    holcimDocketObj.tripId = holcimTripObj
    holcimDocketObj.orderNo  = request.POST.get('orderNo')
    holcimDocketObj.jobNo = request.POST.get('jobNo')
    holcimDocketObj.status = request.POST.get('status')
    holcimDocketObj.ticketedDate =  request.POST.get('ticketedDate')
    holcimDocketObj.ticketedTime =  request.POST.get('ticketedTime')
    holcimDocketObj.load = holcimDateConvertStr(request.POST.get('load'))
    holcimDocketObj.loadComplete = request.POST.get('loadComplete')
    holcimDocketObj.toJob = holcimDateConvertStr(request.POST.get('toJob'))
    holcimDocketObj.timeToDepart = request.POST.get('timeToDepart')
    holcimDocketObj.onJob = holcimDateConvertStr(request.POST.get('onJob'))
    holcimDocketObj.timeToSite = request.POST.get('timeToSite')
    holcimDocketObj.beginUnload = holcimDateConvertStr(request.POST.get('beginUnload'))
    holcimDocketObj.waitingTime = request.POST.get('waitingTime')
    holcimDocketObj.endPour = holcimDateConvertStr(request.POST.get('endPour'))
    holcimDocketObj.wash = holcimDateConvertStr(request.POST.get('wash'))
    holcimDocketObj.toPlant = holcimDateConvertStr(request.POST.get('toPlant'))
    holcimDocketObj.timeOnSite = request.POST.get('timeOnSite')
    holcimDocketObj.atPlant = holcimDateConvertStr(request.POST.get('atPlant'))
    holcimDocketObj.leadDistance = request.POST.get('leadDistance')
    holcimDocketObj.returnDistance = request.POST.get('returnDistance')
    holcimDocketObj.totalDistance = request.POST.get('totalDistance')
    holcimDocketObj.totalTime = request.POST.get('totalTime')
    holcimDocketObj.waitTimeBetweenJob = request.POST.get('waitTimeBetweenJob')
    holcimDocketObj.driverName = driverObj
    holcimDocketObj.quantity = request.POST.get('quantity')
    holcimDocketObj.slump = request.POST.get('slump')
    holcimDocketObj.waterAdded = request.POST.get('waterAdded')
    holcimDocketObj.save()
    messages.success( request, "RCTI holcim entry successfully done.")
    return redirect('Account:rcti')


@csrf_protect
def rctiSave(request):
    rctiPdf = request.FILES.get('rctiPdf')
    clientName = request.POST.get('clientName')
    time = getCurrentTimeInString()
    location = None
    if rctiPdf:
        rctiPdfName = time + "@_!" + (str(rctiPdf.name)).replace(' ','')
        pdfLocation = 'static/Account/RCTI/uplodedRctiPdf'
        savePdfObj = FileSystemStorage(location=pdfLocation)
        savePdfObj.save(rctiPdfName,rctiPdf)
        
    invoiceFile = request.FILES.get('RctiFile')
    save_data = request.POST.get('save')
    
    if not invoiceFile:
        return HttpResponse("No file uploaded")
    try:
        folderName = None
        newFileName = time + "@_!" + (str(invoiceFile.name)).replace(' ','')
        if clientName == 'boral':
            folderName = 'tempRCTIInvoice'
        elif clientName == 'holcim':
            folderName = 'RCTIInvoice'
            
        location = f'static/Account/RCTI/{folderName}'

        lfs = FileSystemStorage(location=location)
        lfs.save(newFileName, invoiceFile)
        if clientName == 'boral' and save_data == '1':
            cmd = ["python", "Account_app/utils.py", newFileName]
            subprocess.Popen(cmd, stdout=subprocess.PIPE)
        fileDetails = [] 
        date_ = 0
        total = 0
        clientNameID  = Client.objects.filter(name = clientName).first()
        if save_data == '1':
            if clientName == 'boral':
                with open( f'static/Account/RCTI/tempRCTIInvoice/{newFileName}' , 'r') as f:
                    fileData = csv.reader(f)
                    for data in fileData:
                        data = data[0]
                        dataList = data.split()
                        if 'documentnumber' in data.lower().strip().replace(" ",""):
                            date_ += 1
                        elif 'date' in data.lower().strip().replace(" ","") and date_ == 1 :
                            fileDetails.insert(0,str(invoiceFile))
                            fileDetails.insert(1,dataList[-1])
                        elif 'totalexcludinggst' in data.lower().strip().replace(" ","") and date_ == 1:
                            fileDetails.insert(2,float(dataList[-1].replace(",","").replace('$','')))
                        elif 'gstpayable' in data.lower().strip().replace(" ","") and date_ == 1:
                            fileDetails.insert(3,float(dataList[-1].replace(",","").replace('$','')))
                        elif 'total' in data.lower().strip().replace(" ","") and date_ == 1:
                            fileDetails.insert(4,float(dataList[-1].replace(",","").replace('$','')))
                            date_ = 0
                date_object = datetime.strptime(fileDetails[1], '%y/%m/%d').strftime('%Y-%m-%d')
                rctiReport = RctiReport.objects.filter(reportDate= date_object, total= fileDetails[-1] ,  fileName= fileDetails[0]).first()
                if rctiReport:
                    messages.error(request, "This file already exists!")
                    return redirect(request.META.get('HTTP_REFERER'))
                else:
                    rctiReport = RctiReport()
                    rctiReport.fileName = fileDetails[0]
                    rctiReport.clientName = clientNameID
                    rctiReport.reportDate = date_object
                    rctiReport.gstPayable = fileDetails[2]
                    rctiReport.totalExGST = fileDetails[3]
                    rctiReport.total = fileDetails[4]
                    rctiReport.save()
                    with open('rctiReportId.txt','w')as f:
                        f.write(str(rctiReport.id))
                    colorama.AnsiToWin32.stream = None
                    os.environ["DJANGO_SETTINGS_MODULE"] = "Driver_Schedule.settings"
                    cmd = ["python", "manage.py", "runscript", 'csvToModel.py']
                    subprocess.Popen(cmd, stdout=subprocess.PIPE)
            elif clientName == 'holcim':
                with open( f'static/Account/RCTI/RCTIInvoice/{newFileName}' , 'r') as f:
                    fileData = csv.reader(f)
                    for row in fileData:
                        row = row[0]
                        splitRow = row.split()
                        if 'grosscartageincomestatement' in row.lower().strip().replace(" ","") and len(fileDetails) == 0:
                            fileDetails.insert(0,str(invoiceFile))
                            fileDetails.insert(1,splitRow[-2])
                        elif 'totalforvendor' in row.lower().strip().replace(" ",""):
                            total = 1
                        elif total == 1:
                            fileDetails.insert(2,float(splitRow[-1].replace(',','')))
                            total = 0
                date_object = datetime.strptime(fileDetails[1], '%d.%m.%Y').date()
                rctiReport = RctiReport.objects.filter(reportDate= date_object, total= fileDetails[-1] ,  fileName= fileDetails[0]).first()
                if rctiReport:
                    messages.error(request, "This file entry already exists!")
                    return redirect(request.META.get('HTTP_REFERER'))
                else:
                    rctiReport = RctiReport()
                    rctiReport.reportDate = date_object
                    rctiReport.fileName =  fileDetails[0]
                    rctiReport.clientName = clientNameID
                    rctiReport.total = fileDetails[-1]
                    rctiReport.save()
                    with open('rctiReportId.txt','w')as f:
                        f.write(str(rctiReport.id))
                with open("File_name_file.txt",'w+',encoding='utf-8') as f:
                    file_name = f.write(newFileName)
                colorama.AnsiToWin32.stream = None
                os.environ["DJANGO_SETTINGS_MODULE"] = "Driver_Schedule.settings"
                cmd = ["python", "manage.py", "runscript", 'holcimUtils','--continue-on-error']
                
                subprocess.Popen(cmd, stdout=subprocess.PIPE)
        messages.success( request, "Please wait 5 minutes. The data conversion process continues")
        return redirect(request.META.get('HTTP_REFERER'))

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

def uplodedRCTI(request):
   
    rctiFile = os.listdir('static/Account/RCTI/uplodedRctiPdf')
    rctiFileNameLists = []
    for file in rctiFile:
        rctiFileNameLists.append([file.split('@_!')[0],file.split('@_!')[1]])
        
    return render(request, 'Account/uplodedRCTI.html', {'rctiFileNameLists' : rctiFileNameLists})

@csrf_protect
def getRctiError(request):
    rctiErrorData = RctiErrors.objects.filter(pk=request.POST.get('id')).values().first()
    return JsonResponse({'status': True,'data': rctiErrorData})


def expanseForm(request, id = None):
    rctiExpense = None
    if id:
        rctiExpense = RctiExpense.objects.filter(id = id).first()
        rctiExpense.docketDate = dateConverterFromTableToPageFormate(rctiExpense.docketDate)
    params = {
        'rcti' : rctiExpense
    }
    
    return render(request, 'Account/expanseForm.html',params)

@csrf_protect
def expanseSave(request):
    clientNameObj = Client.filter(name = 'boral').first()
    RctiExpenseObj = RctiExpense()
    RctiExpenseObj.clientName  = clientNameObj
    RctiExpenseObj.truckNo = request.POST.get('truckNo')
    RctiExpenseObj.docketNumber = request.POST.get('docketNumber')
    RctiExpenseObj.docketDate = request.POST.get('docketDate')
    RctiExpenseObj.docketYard = request.POST.get('docketYard')
    RctiExpenseObj.description = request.POST.get('description')
    RctiExpenseObj.paidKm = request.POST.get('paidKm')
    RctiExpenseObj.invoiceQuantity = request.POST.get('invoiceQuantity')
    RctiExpenseObj.unit = request.POST.get('unit')
    RctiExpenseObj.unitPrice = request.POST.get('unitPrice')
    RctiExpenseObj.gstPayable = request.POST.get('gstPayable')
    RctiExpenseObj.totalExGST = request.POST.get('totalExGST')
    RctiExpenseObj.total = request.POST.get('total')
    RctiExpenseObj.save()
    
    messages.success( request, "RCTI Expense Entry successfully done.")
    return redirect('Account:rcti')

def driverEntry(request):
    return render(request, 'Account/driverEntryForm.html')

@csrf_protect
def driverEntrySave(request):
    Driver_csv_file = request.FILES.get('driverEntryFile')
    if not Driver_csv_file:
        return HttpResponse("No file uploaded")
    try:
        time = (str(timezone.now())).replace(':', '').replace(
            '-', '').replace(' ', '').split('.')
        time = time[0]
        newFileName = time + "@_!" + str(Driver_csv_file.name)

        location = 'static/Account/DriverEntry'
        lfs = FileSystemStorage(location=location)
        lfs.save(newFileName, Driver_csv_file)
        with open("Driver_reg_file.txt", 'w') as f:
            f.write(newFileName)
            f.close()
        colorama.AnsiToWin32.stream = None
        os.environ["DJANGO_SETTINGS_MODULE"] = "Driver_Schedule.settings"
        cmd = ["python", "manage.py", "runscript", 'DriverCsvToModel','--continue-on-error']
        subprocess.Popen(cmd, stdout=subprocess.PIPE)
        messages.success(
            request, "Please wait 5 minutes. The data conversion process continues")
        return redirect('Account:index')
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")


def driverDocketEntry(request, ids , errorId = None):
    surcharges = Surcharge.objects.all()   
    docketData = None
    if errorId:
        docketData = PastTripError.objects.filter(pk = errorId).first()

    driver_trip_id = DriverTrip.objects.filter(id=ids).first()
    if driver_trip_id:
        base_plant = BasePlant.objects.all().order_by('-id')
        params = {
            'basePlants': base_plant,
            'id': ids,
            'docketData': docketData,
            'surcharges': surcharges,
            'errorId':errorId,
        }
        return render(request, 'Account/driverDocketEntry.html', params)
    else:
        messages.warning(request, "Invalid Request ")
        return redirect('Account:driverTripsTable')


@csrf_protect
def countDocketWaitingTime(request):
    tripId = request.POST.get('tripId')
    waitingTimeStart = request.POST.get('waitingTimeStart')
    waitingTimeEnd = request.POST.get('waitingTimeEnd')
    tripObj = DriverTrip.objects.filter(pk=tripId).first()
    if tripObj:
        adminTruckObj = AdminTruck.objects.filter(adminTruckNumber = tripObj.truckNo).first()
        clientTruckObj = ClientTruckConnection.objects.filter(truckNumber = adminTruckObj).first()
        rateCardObj = RateCard.objects.filter(rate_card_name = clientTruckObj.rate_card_name.rate_card_name).first()
        graceObj = Grace.objects.filter(rate_card_name = rateCardObj).first()

        totalWaitingTime = getTimeDifference(waitingTimeStart,waitingTimeEnd)
        if totalWaitingTime > graceObj.chargeable_waiting_time_starts_after:
            totalWaitingTime = totalWaitingTime - graceObj.waiting_time_grace_in_minutes
            if totalWaitingTime < 0:
                totalWaitingTime = 0
        else:
            totalWaitingTime = 0
                    
    return JsonResponse({'status': True,'totalWaitingTime':totalWaitingTime})


@csrf_protect
def countDocketStandByTime(request):
    tripId = request.POST.get('tripId')
    standByStartTime = request.POST.get('standByStartTime')
    standByEndTime = request.POST.get('standByEndTime')

    tripObj = DriverTrip.objects.filter(pk=tripId).first()
    
    if tripObj:
        adminTruckObj = AdminTruck.objects.filter(adminTruckNumber = tripObj.truckNo).first()
        clientTruckObj = ClientTruckConnection.objects.filter(truckNumber = adminTruckObj).first()
        rateCardObj = RateCard.objects.filter(rate_card_name = clientTruckObj.rate_card_name.rate_card_name).first()
        costParameterObj = CostParameters.objects.filter(rate_card_name = rateCardObj).first()
        graceObj = Grace.objects.filter(rate_card_name = rateCardObj).first()

        totalStandByTime = getTimeDifference(standByStartTime,standByEndTime)
        standBySlot = 0
        if totalStandByTime > graceObj.chargeable_standby_time_starts_after:
            totalStandByTime = totalStandByTime - graceObj.standby_time_grace_in_minutes
            standBySlot = totalStandByTime//costParameterObj.standby_time_slot_size
        
                    
    return JsonResponse({'status': True,'standBySlot':standBySlot})

    
@csrf_protect
def getSinglePastTripError(request):
    pastTripErrorData = PastTripError.objects.filter(pk=request.POST.get('id')).values().first()
    return JsonResponse({'status': True,'data':pastTripErrorData})

def driverDocketEntrySave(request, ids, errorId=None):
    
    # return HttpResponse(errorId)
    driver_trip_id = DriverTrip.objects.filter(id=ids).first()

    docketNumber_ = int(float(request.POST.get('docketNumber')))
    shiftDate_ = request.POST.get('shiftDate')
    surchargeObj = Surcharge.objects.get(pk=request.POST.get('surcharge_type'))
    
    docketNumbers = DriverDocket.objects.filter(docketNumber=docketNumber_, shiftDate=shiftDate_, tripId=driver_trip_id).first()
    if docketNumbers:
        messages.error(request, "This docket number and date already exists!")
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        docketFile = request.FILES.get('docketFile')
        DriverDocketObj = DriverDocket(
            shiftDate=shiftDate_,
            tripId=driver_trip_id,
            docketNumber=docketNumber_,
            docketFile=docketFileSave(docketFile, docketNumber_),
            basePlant=BasePlant.objects.get(pk=request.POST.get('basePlant')),
            noOfKm=request.POST.get('noOfKm'),
            transferKM=request.POST.get('transferKM'),
            surcharge_type=surchargeObj,
            surcharge_duration=request.POST.get('surcharge_duration'),
            cubicMl=request.POST.get('cubicMl'),
            others=request.POST.get('others')
        )
        # return HttpResponse(DriverDocketObj.shiftDate)
        if request.POST.get('returnToYard') == 'returnToYard':
            DriverDocketObj.returnQty = request.POST.get('returnQty')
            DriverDocketObj.returnKm = request.POST.get('returnKm')
            DriverDocketObj.returnToYard = True
        elif request.POST.get('returnToYard') == 'tippingToYard':
            DriverDocketObj.returnQty = request.POST.get('returnQty')
            DriverDocketObj.returnKm = request.POST.get('returnKm')
            DriverDocketObj.tippingToYard = True

        DriverDocketObj.waitingTimeStart = request.POST.get('waitingTimeStart')
        DriverDocketObj.waitingTimeEnd = request.POST.get('waitingTimeEnd')
        # DriverDocketObj.totalWaitingInMinute = getTimeDifference(DriverDocketObj.waitingTimeStart, DriverDocketObj.waitingTimeEnd)
        DriverDocketObj.totalWaitingInMinute = request.POST.get('totalWaitingInMinute')
        DriverDocketObj.standByStartTime = request.POST.get('standByStartTime')
        DriverDocketObj.standByEndTime = request.POST.get('standByEndTime')
        DriverDocketObj.standBySlot = request.POST.get('standBySlot')
        DriverDocketObj.comment = request.POST.get('comment')
        DriverDocketObj.save()
        driver_dockets = DriverDocket.objects.filter(tripId=driver_trip_id)

        # Count the number of objects in the queryset
        no_of_loads = driver_dockets.count()
        driver_trip_id.numberOfLoads = no_of_loads

        driver_trip_id.save()
        if errorId:
            DriverDocketObj.shiftDate = datetime.strptime(DriverDocketObj.shiftDate, "%Y-%m-%d").date()
            driverDocketNumber = DriverDocketObj.docketNumber
            reconciliationDocketObj = ReconciliationReport.objects.filter(docketNumber = driverDocketNumber , docketDate = DriverDocketObj.shiftDate ).first()
                    
            if not  reconciliationDocketObj :
                reconciliationDocketObj = ReconciliationReport()
            reconciliationDocketObj.driverId = driver_trip_id.id  
            reconciliationDocketObj.clientId = driver_trip_id.id 
            reconciliationDocketObj.truckId = driver_trip_id.truckNo 
                
            driverLoadAndKmCost = checkLoadAndKmCost(driverDocketNumber,DriverDocketObj.shiftDate)
            driverSurchargeCost = checkSurcharge(driverDocketNumber,DriverDocketObj.shiftDate)
            # return HttpResponse(driverSurchargeCost)
            driverWaitingTimeCost = checkWaitingTime(driverDocketNumber,DriverDocketObj.shiftDate)
            slotSize = DriverTripCheckStandByTotal(driverDocketNumber,DriverDocketObj.shiftDate)
            driverStandByCost = checkStandByTotal(driverDocketNumber,DriverDocketObj.shiftDate,slotSize)
            driverTransferKmCost = checkTransferCost(driverDocketNumber,DriverDocketObj.shiftDate)
            driverReturnKmCost = checkReturnCost(driverDocketNumber,DriverDocketObj.shiftDate)
            # minLoad 
            driverLoadDeficit = checkMinLoadCost(driverDocketNumber,DriverDocketObj.shiftDate)
            # TotalCost 
            driverTotalCost = driverLoadAndKmCost +driverSurchargeCost + driverWaitingTimeCost + driverStandByCost + driverTransferKmCost + driverReturnKmCost +driverLoadDeficit
            reconciliationDocketObj.docketNumber = driverDocketNumber  
            reconciliationDocketObj.docketDate = DriverDocketObj.shiftDate  
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

            errorObj = PastTripError.objects.filter(pk =errorId).first()
            print(errorObj)
            errorObj.status = True
            errorObj.save()

        url = reverse('Account:DriverTripEdit', kwargs={'id': ids})
        messages.success(request, "Docket Added successfully")
        return redirect(url)


def rctiCsvForm(request):
    BasePlant_ = BasePlant.objects.all()
    return render(request, 'Account/rctiCsvForm.html', {'basePlants': BasePlant_})


def driverSampleCsv(request):
    return FileResponse(open(f'static/Account/sampleDriverEntry.xlsx', 'rb'), as_attachment=True)


@csrf_protect
# @api_view(['POST'])
def rctiTable(request):
    # return HttpResponse(id)
    
    startDate_ = request.POST.get('startDate')
    endDate_ = request.POST.get('endDate')
    clientName = request.POST.get('clientName')
    clientNameObj = Client.objects.filter(name=clientName).first()
    dataType = request.POST.get('RCTI')
    holcimData =None
    rctiData = None
    # return HttpResponse(clientNameObj)
    # print(clientNameObj)
    if clientNameObj:
        if dataType== 'rctiDocket':
            # return HttpResponse('here')
            rctiData = RCTI.objects.filter(docketDate__range=(startDate_, endDate_), clientName = clientNameObj)
        else:
            rctiData = RctiExpense.objects.filter(docketDate__range=(startDate_, endDate_), clientName = clientNameObj)
    else:
            rctiData = RCTI.objects.filter(docketDate__range=(startDate_, endDate_))
        
    # if basePlant_:
    #     if dataType== 'rctiDocket':
    #         rctiData = RCTI.objects.filter(docketDate__range=(startDate_, endDate_) , docketYard = docketYard)
    #         # holcimData = HolcimDocket.objects.filter(ticketedDate__range=(startDate_,endDate_))
    #         # rctiData = list(chain(rctiData, holcimData))
    #     elif dataType == 'rctiExpense':
    #         rctiData = RctiExpense.objects.filter(docketDate__range=(startDate_, endDate_), docketYard = docketYard)
    # else:
    #     if dataType== 'rctiDocket':
    #         rctiData = RCTI.objects.filter(docketDate__range=(startDate_, endDate_))
    #         # holcimData = HolcimDocket.objects.filter(ticketedDate__range=(startDate_,endDate_))
    #         # rctiData = list(chain(rctiData, holcimData))
    #     elif dataType == 'rctiExpense':
    #         rctiData = RctiExpense.objects.filter(docketDate__range=(startDate_, endDate_))
    
    params = {
        'RCTIs': rctiData,
        'dataType':dataType,
        'holcimData':holcimData,
    }
    # return HttpResponse(params['holcimData'])
    return render(request, 'Account/Tables/rctiTable.html', params)
        # except:
            # messages.warning(request, "Invalid Request ")
            # return redirect(request.META.get('HTTP_REFERER'))


def HolcimDocketView(request,id):
    holcimTripObj = HolcimTrip.objects.filter(pk = id).first()
    holcimDocketObj = HolcimDocket.objects.filter(tripId = holcimTripObj.id)
    params = {
        'docketData':holcimDocketObj,
        'holcimTripObj':holcimTripObj,
    }
    return render(request, 'Account/Holcim/docketView.html',params)
def basePlantTable(request):
    basePlants = BasePlant.objects.all()
    # locations = Location.objects.all()
    return render(request, 'Account/Tables/basePlantTable.html', {'basePlants': basePlants})

def basePlantForm(request, id=None):
    
    basePlant = None
    if id:
        basePlant = BasePlant.objects.get(pk=id)
        
    params = {
        'basePlant': basePlant,
    }
    return render(request, "Account/basePlantForm.html", params)

# def locationEditForm(request, id=None):
#     basePlant = location = None
#     if id:
#         location = Location.objects.get(pk=id)
#     params = {
#         'basePlant': basePlant,
#         'location': location,
#     }
#     return render(request, "Account/basePlantForm.html", params)

# def locationTable(request):
#     locations = Location.objects.all()
#     return render(request, 'GearBox/truckForm.html', {'locations': locations})

@csrf_protect
@api_view(['POST'])
def basePlantSave(request, id=None):
    dataList = {
        'basePlant': request.POST.get('basePlant').upper(),
        'address': request.POST.get('address'),
        'phone': request.POST.get('phone'),
        'personOnName': request.POST.get('personOnName'),
        'managerName': request.POST.get('managerName'),
        'lat': request.POST.get('lat'),
        'long': request.POST.get('long'),
        'basePlantType' : False if  request.POST.get('basePlantType') == "typeLocation" else True
    }

    
    result = None
    if id:
        result = updateIntoTable(record_id=id, tableName='BasePlant', dataSet=dataList)
    else:
        result = insertIntoTable(tableName='BasePlant', dataSet=dataList)
        with open("scripts/addPastTripForMissingBasePlant.txt", 'w') as f:
                f.write(dataList['basePlant'])
                
        # colorama.AnsiToWin32.stream = None
        # os.environ["DJANGO_SETTINGS_MODULE"] = "Driver_Schedule.settings"
        # cmd = ["python", "manage.py", "runscript", 'addPastTripForMissingBasePlant','--continue-on-error']
        # subprocess.run(cmd)
        colorama.AnsiToWin32.stream = None
        os.environ["DJANGO_SETTINGS_MODULE"] = "Driver_Schedule.settings"
        cmd = ["python", "manage.py", "runscript", 'addPastTripForMissingBasePlant','--continue-on-error']
        subprocess.Popen(cmd, stdout=subprocess.PIPE)

    if result is not True:
        messages.error(request, 'This location already exist.')
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.success(request, 'Depot Add successfully')
        return redirect('Account:basePlantTable')


# @csrf_protect
# # @api_view(['POST'])
# def locationSave(request, id=None):
#     locationObj = None
#     if id:
#         locationObj = Location.objects.filter(pk=id).first()
#     else:
#         locationObj = Location()
    
#     locationObj.location = request.POST.get('location').upper()
#     locationObj.address = request.POST.get('locationAddress')
#     locationObj.phone = request.POST.get('locationPhone')
#     locationObj.personOnName = request.POST.get('locationPersonOnName')
#     locationObj.managerName = request.POST.get('locationManagerName')
#     locationObj.lat = request.POST.get('locationLat')
#     locationObj.long = request.POST.get('locationLong')
#     locationObj.save()
    
#     if id:
#         messages.success(request, 'Location updated successfully')
#     else:
#         messages.success(request, 'Location added successfully')

#     return redirect('Account:basePlantTable')

def foreignKeySet(dataset):
    for data in dataset:
        data['clientName_id'] = Client.objects.filter(
            pk=data['clientName_id']).first().name
        data['driverId_id'] = Driver.objects.filter(
            pk=data['driverId_id']).first().name
    return dataset

@csrf_protect
@api_view(['POST'])
def verifiedFilter(request):
    verified = int(request.POST.get('verified'))
    if verified == 1:
        dataList = DriverTrip.objects.filter(verified=True).values()
    else:
        dataList = DriverTrip.objects.filter(verified=False).values()
    foreignKeySet(dataList)
    return JsonResponse({'status': True, 'data': list(dataList)})


@csrf_protect
@api_view(['POST'])
def clientFilter(request):
    dataList = DriverTrip.objects.filter(
        clientName=request.POST.get('id')).values()
    foreignKeySet(dataList)
    return JsonResponse({'status': True, 'data': list(dataList)})


@api_view(['POST'])
def dateRangeFilter(request):
    startDate_values = request.POST.getlist('startDate[]')
    endDate_values = request.POST.getlist('endDate[]')
    startDate = date(int(startDate_values[0]), int(
        startDate_values[1]), int(startDate_values[2]))
    endDate = date(int(endDate_values[0]), int(
        endDate_values[1]), int(endDate_values[2]))
    dataList = DriverTrip.objects.filter(
        shiftDate__range=(startDate, endDate)).values()
    foreignKeySet(dataList)
    return JsonResponse({'status': True, 'data': list(dataList)})


@csrf_protect
def DriverTripEditForm(request, id):
    driver_trip = DriverTrip.objects.get(id=id)
    driver = Driver.objects.all()
    clientName = Client.objects.all()
    AdminTrucks = AdminTruck.objects.all()
    driver_trip.shiftDate = str(driver_trip.shiftDate)
    driver_trip.startTime =str(datetime.strptime(driver_trip.startTime, '%H:%M:%S').time())
    

    driver_docket = DriverDocket.objects.filter(tripId=id)
    surcharges = Surcharge.objects.all()
    count_ = 1
    for i in driver_docket:
        i.shiftDate = dateConverterFromTableToPageFormate(i.shiftDate)
        i.count_ = count_
        count_ += 1

        i.totalWaitingInMinute =DriverTripCheckWaitingTime(i.docketNumber,i.shiftDate)
        i.standBySlot = DriverTripCheckStandByTotal(i.docketNumber,i.shiftDate)
        print(i.standBySlot)
        
    base_plant = BasePlant.objects.all()

    params = {
        'driverTrip': driver_trip,
        'driverDocket': driver_docket,
        'basePlants': base_plant,
        'Driver': driver,
        'Client': clientName,
        'trucks': AdminTrucks,
        'surcharges' : surcharges
    }
    return render(request, 'Account/Tables/DriverTrip&Docket/tripEditForm.html', params)


@csrf_protect
def driverEntryUpdate(request, ids):
    # Update Trip Save
    driver_trip = DriverTrip.objects.get(id=ids)

    driver_trip.verified = True if request.POST.get('verified') == 'on' else False
    driver_trip.driverId = Driver.objects.get(pk=request.POST.get('driverId'))
    driver_trip.clientName = Client.objects.get(pk=request.POST.get('clientName'))
    driver_trip.shiftType = request.POST.get('shiftType')
    driver_trip.numberOfLoads = request.POST.get('numberOfLoads')
    driver_trip.truckNo = request.POST.get('truckNo')
    driver_trip.shiftDate = request.POST.get('shiftDate')
    driver_trip.startTime = request.POST.get('startTime')
    driver_trip.endTime = request.POST.get('endTime')
    if request.FILES.get('loadSheet'):
        loadSheet = request.FILES.get('loadSheet')
        driver_trip.loadSheet = loadFileSave(loadSheet)

    driver_trip.comment = request.POST.get('comment')
    driver_trip.save()

    driver_docket = DriverDocket.objects.filter(tripId=ids).values()
    count_ = 1
    for i in driver_docket:
        try:
            docketNumberVal = DriverDocket.objects.get(docketNumber=int(float(request.POST.get(f'docketNumber{count_}'))), shiftDate=request.POST.get(f'shiftDate{count_}'))
            if docketNumberVal.docketId != i['docketId']:
                messages.error(request, "Docket must be unique.")
                return redirect(request.META.get('HTTP_REFERER'))
        except:
            pass
        docketObj = DriverDocket.objects.get(pk=i['docketId'])
        docketObj.shiftDate = request.POST.get(f'shiftDate{count_}')
        docketObj.docketNumber = int(float(request.POST.get(f'docketNumber{count_}')))
        if request.FILES.get(f'docketFile{count_}'):
            docketFiles = request.FILES.get(f'docketFile{count_}')
            docketObj.docketFile = docketFileSave(
                docketFiles, docketObj.docketNumber)
        docketObj.basePlant = BasePlant.objects.get(
            pk=request.POST.get(f'basePlant{count_}'))
        docketObj.noOfKm = request.POST.get(f'noOfKm{count_}')
        docketObj.transferKM = request.POST.get(f'transferKM{count_}')
        surchargeObj = Surcharge.objects.get(pk = request.POST.get(f'surcharge_type{count_}'))
        docketObj.surcharge_type = surchargeObj
        if request.POST.get(f'returnToYard{count_}') == f'returnToYard{count_}':
            docketObj.returnQty = request.POST.get(f'returnQty{count_}')
            docketObj.returnKm = request.POST.get(f'returnKm{count_}')
            docketObj.returnToYard = True
        elif request.POST.get(f'returnToYard{count_}') == f'tippingToYard{count_}':
            docketObj.returnQty = request.POST.get(f'returnQty{count_}')
            docketObj.returnKm = request.POST.get(f'returnKm{count_}')
            docketObj.tippingToYard = True
        
        docketObj.waitingTimeStart = request.POST.get(
            f'waitingTimeStart{count_}')
        docketObj.waitingTimeEnd = request.POST.get(f'waitingTimeEnd{count_}')
        # docketObj.totalWaitingInMinute = request.POST.get(f'totalWaitingInMinute{count_}')
        
        docketObj.surcharge_duration = request.POST.get(
            f'surcharge_duration{count_}')
        docketObj.cubicMl = request.POST.get(f'cubicMl{count_}')
        
        docketObj.standByStartTime = request.POST.get(
            f'standByStartTime{count_}')
        docketObj.standByEndTime = request.POST.get(f'standByEndTime{count_}')
        # docketObj.standBySlot = request.POST.get(f'standBySlot{count_}')
        # print(request.POST.get(f'standBySlot{count_}'))
        docketObj.others = request.POST.get(f'others{count_}')
        docketObj.comment = request.POST.get(f'comment{count_}')
        count_ += 1
        
        docketObj.save()
    # return HttpResponse('here')
        if driver_trip.verified:
            docketObj.shiftDate= datetime.strptime(docketObj.shiftDate, "%Y-%m-%d").date()
            driverDocketNumber = docketObj.docketNumber
            reconciliationDocketObj = ReconciliationReport.objects.filter(docketNumber = driverDocketNumber , docketDate = docketObj.shiftDate ).first()
                    
            if not  reconciliationDocketObj :
                reconciliationDocketObj = ReconciliationReport()
                
             
            reconciliationDocketObj.driverId = request.POST.get('driverId')  
            reconciliationDocketObj.clientId = request.POST.get('clientName') 
            reconciliationDocketObj.truckId = request.POST.get('truckNo') 
                
            driverLoadAndKmCost = checkLoadAndKmCost(driverDocketNumber,docketObj.shiftDate)
            driverSurchargeCost = checkSurcharge(driverDocketNumber,docketObj.shiftDate)
            # return HttpResponse(driverSurchargeCost)
            driverWaitingTimeCost = checkWaitingTime(driverDocketNumber,docketObj.shiftDate)
            slotSize = DriverTripCheckStandByTotal(driverDocketNumber,docketObj.shiftDate)
            driverStandByCost = checkStandByTotal(driverDocketNumber,docketObj.shiftDate,slotSize)
            driverTransferKmCost = checkTransferCost(driverDocketNumber,docketObj.shiftDate)
            driverReturnKmCost = checkReturnCost(driverDocketNumber,docketObj.shiftDate)
            # minLoad 
            driverLoadDeficit = checkMinLoadCost(driverDocketNumber,docketObj.shiftDate)
            # TotalCost 
            driverTotalCost = driverLoadAndKmCost +driverSurchargeCost + driverWaitingTimeCost + driverStandByCost + driverTransferKmCost + driverReturnKmCost +driverLoadDeficit
            reconciliationDocketObj.docketNumber = driverDocketNumber  
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
    
    
    # return HttpResponse('Work')


    url = reverse('Account:DriverTripEdit', kwargs={'id': ids})
    messages.success(request, "Docket Updated successfully")
    return redirect(url)


# ````````````````````````````````````
# Reconciliation

# ```````````````````````````````````

def reconciliationForm(request, dataType):
    
    drivers = Driver.objects.all()
    clients = Client.objects.all()
    trucks = AdminTruck.objects.all()
    
    params = {
        'drivers': drivers,
        'clients': clients,
        'trucks': trucks ,
    }

    if dataType == 0:
        params['dataType'] = 'Reconciliation Report'
        params['dataTypeInt'] = 0
    elif dataType ==  1:
        params['dataType'] = 'Short paid Report'
        params['dataTypeInt'] = 1
        
        
    return render(request, 'Reconciliation/reconciliation.html', params)

@csrf_protect
def reconciliationAnalysis(request,dataType):
    startDate = dateConvert(request.POST.get('startDate'))
    endDate = dateConvert(request.POST.get('endDate'))
    
    params = {}
    if dataType == 0:
        dataList = ReconciliationReport.objects.filter(docketDate__range=(startDate, endDate),reconciliationType = 0).values()
        params['dataType'] = 'Reconciliation'
        params['dataTypeInt'] = 0
    elif dataType == 1:
        dataList = ReconciliationReport.objects.filter(docketDate__range=(startDate, endDate),reconciliationType = 1).values()
        params['dataType'] = 'Short paid'
        params['dataTypeInt'] = 1
        
    params['dataList'] = dataList
    
    return render(request, 'Reconciliation/reconciliation-result.html', params)
     


def reconciliationDocketView(request, docketNumber):
    # try:
    rctiDocket = RCTI.objects.filter(docketNumber=docketNumber).first()
    # for driverDocket view 
    driverDocket = DriverDocket.objects.filter(docketNumber=docketNumber).first()
    surcharges = Surcharge.objects.all()
    base_plant = BasePlant.objects.all()
    # trip_ = DriverTrip.objects.filter(id = driverDocket.tripId).first()
    # return HttpResponse(trip_)
    # AdminTruckNo = AdminTruck.objects.filter(adminTruckNumber = trip_.truckNo).first()
    # clientTruck = ClientTruckConnection.objects.filter(truckNumber = AdminTruckNo.adminTruckNumber).first()
    # return HttpResponse(clientTruck)
    # rateCard = RateCard.objects.filter(rate_card_name = clientTruck.rate_card_name ).first()
    # return HttpResponse(rateCard)
    
    if rctiDocket:
        rctiDocket.docketDate = dateConverterFromTableToPageFormate(rctiDocket.docketDate)
    if driverDocket:
        driverDocket.shiftDate = dateConverterFromTableToPageFormate(driverDocket.shiftDate)
        driverDocket.docketNumber = str(driverDocket.docketNumber)

    params = {
        'rctiDocket': rctiDocket,
        'driverDocket': driverDocket,
        'surcharges': surcharges,
        'basePlants': base_plant,
    }

    return render(request, 'Reconciliation/reconciliation-docket.html', params)

@csrf_protect
@api_view(['POST'])
def reconciliationSetMark(request):
    dockets = request.POST.getlist('dockets[]')
    for docket in dockets:
        getDocket = ReconciliationReport.objects.filter(docketNumber = docket).first()
        getDocket.reconciliationType = 1
        getDocket.save()
    
    return JsonResponse({'status': True})

def reconciliationEscalationForm(request,id):
    
    reconciliationObj = ReconciliationReport.objects.filter(pk=id).first()
    docketObj = DriverDocket.objects.filter(docketNumber=reconciliationObj.docketNumber).first()
    if docketObj:
        docketObj.docketDate = dateConverterFromTableToPageFormate(docketObj.docketDate)

    currentTimezone = pytz.timezone('Asia/Kolkata')
    currentDate = datetime.now(tz=currentTimezone).date()
    
    clientObj = Client.objects.filter(name=reconciliationObj.clientName).first()
    escalationObj = Escalation.objects.filter(docketNumber=reconciliationObj.docketNumber).first()

    if not escalationObj:
        escalationObj = Escalation()
        escalationObj.docketNumber = reconciliationObj.docketNumber
        escalationObj.userId = request.user
        escalationObj.escalationDate = currentDate
        escalationObj.clientName = clientObj
        escalationObj.docketDate = reconciliationObj.docketDate
        escalationObj.escalationAmount = reconciliationObj.driverTotalCost - reconciliationObj.rctiTotalCost
        escalationObj.save()
        
    
    params = {
        'escalationObj' : escalationObj,
        'docketObj' : docketObj
    }
    
    return render(request, 'Reconciliation/escalation-form.html',params)

@csrf_protect
def reconciliationEscalationForm2(request, id):
    escalationObj = Escalation.objects.filter(pk=id).first()
    reconciliationData = ReconciliationReport.objects.filter(docketNumber=escalationObj.docketNumber, docketDate=escalationObj.docketDate).first()

    loadKmCostDifference= reconciliationData.driverLoadAndKmCost - reconciliationData.rctiLoadAndKmCost
    surchargeCostDifference= reconciliationData.driverSurchargeCost - reconciliationData.rctiSurchargeCost
    waitingTimeCostDifference= reconciliationData.driverWaitingTimeCost - reconciliationData.rctiWaitingTimeCost
    transferKmCostDifference= reconciliationData.driverTransferKmCost - reconciliationData.rctiTransferKmCost
    returnKmCostDifference= reconciliationData.driverReturnKmCost - reconciliationData.rctiReturnKmCost
    otherCostDifference= reconciliationData.driverOtherCost - reconciliationData.rctiOtherCost
    standByCostDifference= reconciliationData.driverStandByCost - reconciliationData.rctiStandByCost
    loadDeficitDifference= reconciliationData.driverLoadDeficit - reconciliationData.rctiLoadDeficit
    totalCostDifference= reconciliationData.driverTotalCost - reconciliationData.rctiTotalCost

    if escalationObj.escalationStep < 2:
        escalationObj.escalationStep = 2
        escalationObj.save()

    params = {
        'escalationObj':escalationObj,
        'data': reconciliationData,
        'loadKmCostDifference':round(loadKmCostDifference,2),
        'surchargeCostDifference':round(surchargeCostDifference,2),
        'waitingTimeCostDifference':round(waitingTimeCostDifference,2),
        'transferKmCostDifference':round(transferKmCostDifference,2),
        'returnKmCostDifference':round(returnKmCostDifference,2),
        'otherCostDifference':round(otherCostDifference,2),
        'standByCostDifference':round(standByCostDifference,2),
        'loadDeficitDifference':round(loadDeficitDifference,2),
        'totalCostDifference':round(totalCostDifference,2),
    }
    return render(request, 'Reconciliation/escalation-form2.html',params)

@csrf_protect
def reconciliationEscalationForm3(request ,id):
    params = {}
    escalationObj = Escalation.objects.filter(pk=id).first()
    escalationObj.escalationStep = 3
    if request.POST.get('escalation') == 'internal':
        escalationObj.escalationType = 'Internal'
    elif request.POST.get('escalation') == 'external':
        escalationObj.escalationType = 'External'
    escalationObj.save()
    
    if escalationObj.escalationType == 'External':
        oldMail = EscalationMail.objects.filter(escalationId=escalationObj).order_by('mailCount')
        params['oldMail'] = oldMail
        
    params['escalationObj']=escalationObj
    
    return render(request, 'Reconciliation/escalation-form3.html',params)

@csrf_protect
def reconciliationEscalationMailAdd(request, id):
    escalationObj = Escalation.objects.filter(pk=id).first()
    mailTo = request.POST.get('mailTo')
    mailFrom = request.POST.get('mailFrom')
    mailSubject = request.POST.get('mailSubject')
    mailDescription = request.POST.get('mailDescription')
    mailType = request.POST.get('mailType')
    currentTimezone = pytz.timezone('Asia/Kolkata')
    currentDate = datetime.now(tz=currentTimezone).date()
    oldMailCount = EscalationMail.objects.filter(escalationId=escalationObj).count()
    
    
    escalationMailObj = EscalationMail()
    escalationMailObj.escalationId = escalationObj
    escalationMailObj.userId = request.user
    escalationMailObj.mailTo = mailTo
    escalationMailObj.mailFrom = mailFrom 
    escalationMailObj.mailSubject = mailSubject
    escalationMailObj.mailDescription = mailDescription
    escalationMailObj.mailType = mailType
    escalationMailObj.mailDate = currentDate
    escalationMailObj.mailCount = oldMailCount + 1    

    mailFile = request.FILES.get('mailAttechment')
    if mailFile:
        time = getCurrentTimeInString()
        attachmentPath = 'static/img/mailAttachment'
        fileName = mailFile.name
        convertedFileName = time + '!_@' + fileName
        pfs = FileSystemStorage(location=attachmentPath)
        pfs.save(convertedFileName, mailFile)
        escalationMailObj.mailAttachment = f'static/img/mailAttachment/{convertedFileName}'
    
    escalationMailObj.save()
    messages.success(request, "Mail added successfully.")
    return redirect(request.META.get('HTTP_REFERER'))

@csrf_protect
def reconciliationEscalationForm4(request ,id):
    escalationObj = Escalation.objects.filter(pk=id).first()

    remark = request.POST.get('remark')
    if remark:
        escalationObj.remark = remark
        
    if escalationObj.escalationStep <= 4:
        escalationObj.escalationStep = 4
        
    escalationObj.save()
    params = {
        'escalationObj':escalationObj
    }
    return render(request, 'Reconciliation/escalation-form4.html',params)
    
    
@csrf_protect
def reconciliationEscalationComplete(request, id):
    escalationObj = Escalation.objects.filter(pk=id).first()
    # return HttpResponse(escalationObj.remark)
    escalationObj.escalationStep = 5
    escalationObj.save()
    
    # set short paid 
    reconciliationData = ReconciliationReport.objects.filter(docketNumber=escalationObj.docketNumber, docketDate=escalationObj.docketDate).first()
    reconciliationData.reconciliationType = 1
    reconciliationData.save()
    
    messages.success(request, "Escalation completed successfully.")
    return redirect(request.META.get('HTTP_REFERER'))
    
# ```````````````````````````````````
# Public holiday
# ```````````````````````````````````

def publicHoliday(request):
    data = PublicHoliday.objects.all()
    params = {
        'data': data
    }
    return render(request, 'Account/Tables/PublicHoliday.html', params)


def publicHolidayForm(request, id=None):
    data = None
    if id:
        data = PublicHoliday.objects.get(pk=id)
        data.date = dateConverterFromTableToPageFormate(data.date)
    params = {
        'data': data
    }
    return render(request, 'Account/PublicHolidayForm.html', params)


@csrf_protect
@api_view(['POST'])
def publicHolidaySave(request, id=None):
    dataList = {
        'date': request.POST.get('date'),
        'stateName': request.POST.get('state'),
        'description': request.POST.get('description')
    }
    if id:
        updateIntoTable(
            record_id=id, tableName='PublicHoliday', dataSet=dataList)
        messages.success(request, 'Holiday updated successfully')
    else:
        insertIntoTable(tableName='PublicHoliday', dataSet=dataList)
        messages.success(request, 'Holiday added successfully')

    return redirect('Account:publicHoliday')


# ````````````````````````````````````
# Rate Card

# ```````````````````````````````````

def rateCardTable(request,clientId = None):
    
    RateCards = RateCard.objects.filter(clientName=clientId)
    params = {
        'rateCard': RateCards,
        'clientId':clientId,
    }
    return render(request, 'Account/Tables/rateCardTable.html', params)


def rateCardForm(request, id=None , clientId=None):
    rateCard = rateCardSurcharges = surchargesEntry = costParameters = thresholdDayShift = thresholdNightShift = grace = onLease = tds = startDate = endDate = None
    surchargesEntry =Surcharge.objects.all()
    rateCardDates = []
    if id:
        rateCard = RateCard.objects.get(pk=id)
        tds = rateCard.tds
        
        costParameters = CostParameters.objects.filter(rate_card_name=rateCard.id).order_by('-end_date').values()
       
        for obj in costParameters:
            rateCardDates.append(str(obj['start_date']) + ' to ' + str(obj['end_date']))
        
        getOldRateCard = request.POST.get('rateCard') 
        
        if getOldRateCard:
            oldRateCardStartDate = getOldRateCard.split('to')[0].strip()
            oldRateCardEndDate = getOldRateCard.split('to')[1].strip()

            costParameters = CostParameters.objects.filter(rate_card_name=rateCard.id, start_date = oldRateCardStartDate, end_date = oldRateCardEndDate).values().first()
            thresholdDayShift = ThresholdDayShift.objects.filter(rate_card_name=rateCard.id, start_date = oldRateCardStartDate, end_date = oldRateCardEndDate).values().first()
            thresholdNightShift = ThresholdNightShift.objects.filter(rate_card_name=rateCard.id, start_date = oldRateCardStartDate, end_date = oldRateCardEndDate).values().first()
            grace = Grace.objects.filter(rate_card_name=rateCard.id, start_date = oldRateCardStartDate, end_date = oldRateCardEndDate).values().first()
            rateCardSurcharges =RateCardSurchargeValue.objects.filter(rate_card_name= rateCard.id, start_date=oldRateCardStartDate, end_date= oldRateCardEndDate)
            
        else:
            costParameters = CostParameters.objects.filter(rate_card_name=rateCard.id).order_by('-end_date').values().first()
            thresholdDayShift = ThresholdDayShift.objects.filter(rate_card_name=rateCard.id).order_by('-end_date').values().first()
            thresholdNightShift = ThresholdNightShift.objects.filter(rate_card_name=rateCard.id).order_by('-end_date').values().first()
            grace = Grace.objects.filter(rate_card_name=rateCard.id).order_by('-end_date').values().first()
            rateCardSurcharges =RateCardSurchargeValue.objects.filter(rate_card_name= rateCard.id, start_date=costParameters['start_date'], end_date= costParameters['end_date'])

        # onLease = OnLease.objects.filter(rate_card_name = rateCard.id, end_date = None).values().first()

        startDate = dateConverterFromTableToPageFormate(costParameters['start_date'])
        endDate = dateConverterFromTableToPageFormate(costParameters['end_date'])

    # return HttpResponse(rateCard)
    params = {
        'rateCard': rateCard,
        'costParameters': costParameters,
        'thresholdDayShift': thresholdDayShift,
        'thresholdNightShift': thresholdNightShift,
        'grace': grace,
        'tds': tds,
        'rateCardSurcharges': rateCardSurcharges,
        'surchargesEntry': surchargesEntry,
        'startDate' : startDate,
        'endDate' : endDate,
        'rateCardDates' : rateCardDates,
        'clientId':clientId,
        # 'onLease' : onLease,
    }
    return render(request, 'Account/rateCardForm.html', params)

@csrf_protect
def getOldRateCards(request):
    rateCardDates = []
    startDate = request.POST.get('startDate')
    endDate = request.POST.get('endDate')
    rateCard = RateCard.objects.filter(pk=request.POST.get('rateCardId')).first()
    costParameters = CostParameters.objects.filter(Q(rate_card_name=rateCard,end_date__gte = startDate,start_date__lte = endDate)|Q(rate_card_name=rateCard,start_date__gte = startDate,end_date__lte = endDate)).values()

    for obj in costParameters:
        rateCardDates.append(str(obj['start_date']) + ' to ' + str(obj['end_date']))

    return JsonResponse({'status':True, 'rateCardDates':rateCardDates})

def checkOnOff(val_):
    return True if str(val_) =='on' else False


@csrf_protect
@api_view(['POST'])
def rateCardSave(request, id=None, edit=0):

        # surcharge.id = request.POST.get('surcharge.id')
        # print(surcharge.surcharge_Name)
    # return HttpResponse(request.POST.get('clientName'))
    # print(type(request.POST.get('costParameters_start_date')))
    # return HttpResponse('work')
    # Rate Card
    rateCardID = None
    startDate = request.POST.get('startDate')
    endDate = request.POST.get('endDate')
    surchargeEntry = Surcharge.objects.all()
    if not id:
        rateCard = RateCard()
        rateCard.rate_card_name=request.POST.get('rate_card_name')
        # tds = float(request.POST.get('rate_card_tds'))
        # rateCard.tds = tds
        clientId =request.POST.get('clientName')
        rateCard.clientName = Client.objects.filter(pk = clientId).first()
        rateCard.save()
        rateCardID = RateCard.objects.filter(rate_card_name=request.POST.get('rate_card_name')).first()

    else:
        rateCardID = RateCard.objects.filter(pk=id).first()
        
        # existingCostParameter = CostParameters.objects.filter(Q(rateCard=rateCardID) & (Q(start_date__range=(startDate, endDate)) | Q(end_date__range=(startDate, endDate))))
        if edit == 0:
            existingCostParameter = CostParameters.objects.filter(rate_card_name=rateCardID,start_date__lte = startDate,end_date__gte = startDate).first()
            existingThresholdDayShift = ThresholdDayShift.objects.filter(rate_card_name=rateCardID,start_date__lte = startDate,end_date__gte = startDate).first()
            existingThresholdNightShift = ThresholdNightShift.objects.filter(rate_card_name=rateCardID,start_date__lte = startDate,end_date__gte = startDate).first()
            existingGrace = Grace.objects.filter(rate_card_name=rateCardID,start_date__lte = startDate,end_date__gte = startDate).first()
            rateCardSurchargeObj = RateCardSurchargeValue.objects.filter(rate_card_name = rateCardID,start_date__lte = startDate,end_date__gte = startDate)
            for surcharge in rateCardSurchargeObj:
                surcharge.surchargeValue = request.POST.get(f'{surcharge.id}')
                surcharge.start_date = startDate
                surcharge.end_date = endDate
                surcharge.save()

            if existingCostParameter or existingThresholdDayShift or existingThresholdNightShift or existingGrace:
                messages.error(request, "Rate card rates already exist between given date.")
                return redirect(request.META.get('HTTP_REFERER'))

        # tds = float(request.POST.get('rate_card_tds'))
        # rateCardID.tds = tds
        # rateCardID.save()

        # oldCostParameters = CostParameters.objects.get(
        #     rate_card_name=rateCardID.id, end_date=None)
        # oldCostParameters.end_date = getYesterdayDate(
        #     request.POST.get('costParameters_start_date'))
        # oldCostParameters.save()

        # oldThresholdDayShift = ThresholdDayShift.objects.get(
        #     rate_card_name=rateCardID.id, end_date=None)
        # oldThresholdDayShift.end_date = getYesterdayDate(
        #     request.POST.get('thresholdDayShift_start_date'))
        # oldThresholdDayShift.save()

        # oldThresholdNightShift = ThresholdNightShift.objects.get(
        #     rate_card_name=rateCardID.id, end_date=None)
        # oldThresholdNightShift.end_date = getYesterdayDate(
        #     request.POST.get('thresholdNightShift_start_date'))
        # oldThresholdNightShift.save()

        # oldGrace = Grace.objects.get(
        #     rate_card_name=rateCardID.id, end_date=None)
        # oldGrace.end_date = getYesterdayDate(
        #     request.POST.get('grace_start_date'))
        # oldGrace.save()

        # oldOnLease = OnLease.objects.get(
        #     rate_card_name=rateCardID.id, end_date=None)
        # oldOnLease.end_date = getYesterdayDate(
        #     request.POST.get('onLease_start_date'))
        # oldOnLease.save()

    # CostParameters
    # surchargeObj = Surcharge.objects.get(pk=request.POST.get('costParameters_surcharge_type'))
    updatedValues= []
    
    #  Get object according to type of save
    if edit == 0:
        costParameters = CostParameters()
        thresholdDayShifts = ThresholdDayShift()
        thresholdNightShifts = ThresholdNightShift()
        grace = Grace()
        
        for surcharge in surchargeEntry:
            rateCardSurchargeObj = RateCardSurchargeValue() 
            rateCardSurchargeObj.rate_card_name = rateCardID
            rateCardSurchargeObj.surcharge = surcharge
            rateCardSurchargeObj.surchargeValue = request.POST.get(f'{surcharge.id}')
            rateCardSurchargeObj.start_date = startDate
            rateCardSurchargeObj.end_date = endDate
            rateCardSurchargeObj.save()
        
    else:
        costParameters = CostParameters.objects.filter(rate_card_name = rateCardID,start_date__lte = startDate,end_date__gte = startDate).first()
        thresholdDayShifts = ThresholdDayShift.objects.filter(rate_card_name = rateCardID,start_date__lte = startDate,end_date__gte = startDate).first()
        thresholdNightShifts = ThresholdNightShift.objects.filter(rate_card_name = rateCardID,start_date__lte = startDate,end_date__gte = startDate).first()
        grace = Grace.objects.filter(rate_card_name = rateCardID,start_date__lte = startDate,end_date__gte = startDate).first()
        rateCardSurchargeObj = RateCardSurchargeValue.objects.filter(rate_card_name = rateCardID,start_date__lte = startDate,end_date__gte = startDate)
        for surcharge in rateCardSurchargeObj:
            surcharge.surchargeValue = request.POST.get(f'{surcharge.id}')
            surcharge.start_date = startDate
            surcharge.end_date = endDate
            surcharge.save()

        # Edit Reconciliation and Past trips
        # Cost parameters
        
        updatedValues.append('costParameters_loading_cost_per_cubic_meter') if costParameters.loading_cost_per_cubic_meter != float(request.POST.get('costParameters_loading_cost_per_cubic_meter')) else None
        updatedValues.append('costParameters_km_cost') if costParameters.km_cost != float(request.POST.get('costParameters_km_cost')) else None
        updatedValues.append('costParameters_transfer_cost') if costParameters.transfer_cost != float(request.POST.get('costParameters_transfer_cost')) else None
        updatedValues.append('costParameters_return_load_cost') if costParameters.return_load_cost != float(request.POST.get('costParameters_return_load_cost')) else None
        updatedValues.append('costParameters_return_km_cost') if costParameters.return_km_cost != float(request.POST.get('costParameters_return_km_cost')) else None
        updatedValues.append('costParameters_standby_time_slot_size') if costParameters.standby_time_slot_size != float(request.POST.get('costParameters_standby_time_slot_size')) else None
        updatedValues.append('costParameters_standby_cost_per_slot') if costParameters.standby_cost_per_slot != float(request.POST.get('costParameters_standby_cost_per_slot')) else None
        updatedValues.append('costParameters_waiting_cost_per_minute') if costParameters.waiting_cost_per_minute != float(request.POST.get('costParameters_waiting_cost_per_minute')) else None
        updatedValues.append('costParameters_call_out_fees') if costParameters.call_out_fees != float(request.POST.get('costParameters_call_out_fees')) else None
        updatedValues.append('costParameters_demurrage_fees') if costParameters.demurrage_fees != float(request.POST.get('costParameters_demurrage_fees')) else None
        updatedValues.append('costParameters_cancellation_fees') if costParameters.cancellation_fees != float(request.POST.get('costParameters_cancellation_fees')) else None

        # ThresholdDayShift 
        updatedValues.append('thresholdDayShift_threshold_amount_per_day_shift') if thresholdDayShifts.threshold_amount_per_day_shift != float(request.POST.get('thresholdDayShift_threshold_amount_per_day_shift')) else None
        updatedValues.append('thresholdDayShift_min_load_in_cubic_meters') if thresholdDayShifts.min_load_in_cubic_meters != float(request.POST.get('thresholdDayShift_min_load_in_cubic_meters')) else None
        updatedValues.append('thresholdDayShift_min_load_in_cubic_meters_return_to_yard') if thresholdDayShifts.min_load_in_cubic_meters_return_to_yard != float(request.POST.get('thresholdDayShift_min_load_in_cubic_meters_return_to_yard')) else None
        updatedValues.append('thresholdDayShift_return_to_yard_grace') if thresholdDayShifts.return_to_yard_grace != float(request.POST.get('thresholdDayShift_return_to_yard_grace')) else None
        updatedValues.append('thresholdDayShift_return_to_tipping_grace') if thresholdDayShifts.return_to_tipping_grace != float(request.POST.get('thresholdDayShift_return_to_tipping_grace')) else None
        
        updatedValues.append('thresholdDayShift_loading_cost_per_cubic_meter_included') if thresholdDayShifts.loading_cost_per_cubic_meter_included != checkOnOff(request.POST.get('thresholdDayShift_loading_cost_per_cubic_meter_included')) else None
        updatedValues.append('thresholdDayShift_km_cost_included') if thresholdDayShifts.km_cost_included != checkOnOff(request.POST.get('thresholdDayShift_km_cost_included')) else None
        updatedValues.append('thresholdDayShift_surcharge_included') if thresholdDayShifts.surcharge_included != checkOnOff(request.POST.get('thresholdDayShift_surcharge_included')) else None
        updatedValues.append('thresholdDayShift_transfer_cost_included') if thresholdDayShifts.transfer_cost_included != checkOnOff(request.POST.get('thresholdDayShift_transfer_cost_included')) else None
        updatedValues.append('thresholdDayShift_return_cost_included') if thresholdDayShifts.return_cost_included != checkOnOff(request.POST.get('thresholdDayShift_return_cost_included')) else None
        updatedValues.append('thresholdDayShift_standby_cost_included') if thresholdDayShifts.standby_cost_included != checkOnOff(request.POST.get('thresholdDayShift_standby_cost_included')) else None
        updatedValues.append('thresholdDayShift_waiting_cost_included') if thresholdDayShifts.waiting_cost_included != checkOnOff(request.POST.get('thresholdDayShift_waiting_cost_included')) else None
        updatedValues.append('thresholdDayShift_call_out_fees_included') if thresholdDayShifts.call_out_fees_included != checkOnOff(request.POST.get('thresholdDayShift_call_out_fees_included')) else None
        
        # ThresholdNightShift 
        updatedValues.append('thresholdNightShift_threshold_amount_per_night_shift') if thresholdNightShifts.threshold_amount_per_night_shift != float(request.POST.get('thresholdNightShift_threshold_amount_per_night_shift')) else None
        updatedValues.append('thresholdNightShift_min_load_in_cubic_meters') if thresholdNightShifts.min_load_in_cubic_meters != float(request.POST.get('thresholdNightShift_min_load_in_cubic_meters')) else None
        updatedValues.append('thresholdNightShift_min_load_in_cubic_meters_return_to_yard') if thresholdNightShifts.min_load_in_cubic_meters_return_to_yard != float(request.POST.get('thresholdNightShift_min_load_in_cubic_meters_return_to_yard')) else None
        updatedValues.append('thresholdNightShift_return_to_yard_grace') if thresholdNightShifts.return_to_yard_grace != float(request.POST.get('thresholdNightShift_return_to_yard_grace')) else None
        updatedValues.append('thresholdNightShift_return_to_tipping_grace') if thresholdNightShifts.return_to_tipping_grace != float(request.POST.get('thresholdNightShift_return_to_tipping_grace')) else None
        
        updatedValues.append('thresholdNightShift_loading_cost_per_cubic_meter_included') if thresholdNightShifts.loading_cost_per_cubic_meter_included != checkOnOff(request.POST.get('thresholdNightShift_loading_cost_per_cubic_meter_included')) else None
        updatedValues.append('thresholdNightShift_km_cost_included') if thresholdNightShifts.km_cost_included != checkOnOff(request.POST.get('thresholdNightShift_km_cost_included')) else None
        updatedValues.append('thresholdNightShift_surcharge_included') if thresholdNightShifts.surcharge_included != checkOnOff(request.POST.get('thresholdNightShift_surcharge_included')) else None
        updatedValues.append('thresholdNightShift_transfer_cost_included') if thresholdNightShifts.transfer_cost_included != checkOnOff(request.POST.get('thresholdNightShift_transfer_cost_included')) else None
        updatedValues.append('thresholdNightShift_return_cost_included') if thresholdNightShifts.return_cost_included != checkOnOff(request.POST.get('thresholdNightShift_return_cost_included')) else None
        updatedValues.append('thresholdNightShift_standby_cost_included') if thresholdNightShifts.standby_cost_included != checkOnOff(request.POST.get('thresholdNightShift_standby_cost_included')) else None
        updatedValues.append('thresholdNightShift_waiting_cost_included') if thresholdNightShifts.waiting_cost_included != checkOnOff(request.POST.get('thresholdNightShift_waiting_cost_included')) else None
        updatedValues.append('thresholdNightShift_call_out_fees_included') if thresholdNightShifts.call_out_fees_included != checkOnOff(request.POST.get('thresholdNightShift_call_out_fees_included')) else None
        
        # Grace 
        updatedValues.append('load_km_grace') if grace.load_km_grace != float(request.POST.get('grace_load_km_grace')) else None
        updatedValues.append('transfer_km_grace') if grace.transfer_km_grace != float(request.POST.get('grace_transfer_km_grace')) else None
        updatedValues.append('return_km_grace') if grace.return_km_grace != float(request.POST.get('grace_return_km_grace')) else None
        updatedValues.append('standby_time_grace_in_minutes') if grace.standby_time_grace_in_minutes != float(request.POST.get('grace_standby_time_grace_in_minutes')) else None
        updatedValues.append('chargeable_standby_time_starts_after') if grace.chargeable_standby_time_starts_after != float(request.POST.get('grace_chargeable_standby_time_starts_after')) else None
        updatedValues.append('waiting_time_grace_in_minutes') if grace.waiting_time_grace_in_minutes != float(request.POST.get('grace_waiting_time_grace_in_minutes')) else None
        updatedValues.append('chargeable_waiting_time_starts_after') if grace.chargeable_waiting_time_starts_after != float(request.POST.get('grace_chargeable_waiting_time_starts_after')) else None
        
        # return HttpResponse(updatedValues) 

    costParameters.rate_card_name=rateCardID
    costParameters.loading_cost_per_cubic_meter=float(request.POST.get('costParameters_loading_cost_per_cubic_meter'))
    costParameters.km_cost=float(request.POST.get('costParameters_km_cost'))
    costParameters.transfer_cost=float(request.POST.get('costParameters_transfer_cost'))
    costParameters.return_load_cost=float(request.POST.get('costParameters_return_load_cost'))
    costParameters.return_km_cost=float(request.POST.get('costParameters_return_km_cost'))
    costParameters.standby_time_slot_size=float(request.POST.get('costParameters_standby_time_slot_size'))
    costParameters.standby_cost_per_slot=float(request.POST.get('costParameters_standby_cost_per_slot'))
    costParameters.waiting_cost_per_minute=float(request.POST.get('costParameters_waiting_cost_per_minute'))
    costParameters.call_out_fees=float(request.POST.get('costParameters_call_out_fees'))
    costParameters.demurrage_fees=float(request.POST.get('costParameters_demurrage_fees'))
    costParameters.cancellation_fees=float(request.POST.get('costParameters_cancellation_fees'))
    costParameters.start_date=startDate  
    costParameters.end_date=endDate
    costParameters.save()

    # ThresholdDayShift
    thresholdDayShifts.rate_card_name=rateCardID
    thresholdDayShifts.threshold_amount_per_day_shift=float(request.POST.get('thresholdDayShift_threshold_amount_per_day_shift'))
    thresholdDayShifts.loading_cost_per_cubic_meter_included=True if request.POST.get('thresholdDayShift_loading_cost_per_cubic_meter_included') == 'on' else False
    thresholdDayShifts.km_cost_included=True if request.POST.get('thresholdDayShift_km_cost_included') == 'on' else False
    thresholdDayShifts.surcharge_included=True if request.POST.get('thresholdDayShift_surcharge_included') == 'on' else False
    thresholdDayShifts.transfer_cost_included=True if request.POST.get('thresholdDayShift_transfer_cost_included') == 'on' else False
    thresholdDayShifts.return_cost_included=True if request.POST.get('thresholdDayShift_return_cost_included') == 'on' else False
    thresholdDayShifts.standby_cost_included=True if request.POST.get('thresholdDayShift_standby_cost_included') == 'on' else False
    thresholdDayShifts.waiting_cost_included=True if request.POST.get('thresholdDayShift_waiting_cost_included') == 'on' else False
    thresholdDayShifts.call_out_fees_included=True if request.POST.get('thresholdDayShift_call_out_fees_included') == 'on' else False
    thresholdDayShifts.min_load_in_cubic_meters=float(request.POST.get('thresholdDayShift_min_load_in_cubic_meters'))
    thresholdDayShifts.min_load_in_cubic_meters_return_to_yard=float(request.POST.get('thresholdDayShift_min_load_in_cubic_meters_return_to_yard'))
    thresholdDayShifts.return_to_yard_grace=float(request.POST.get('thresholdDayShift_return_to_yard_grace'))
    thresholdDayShifts.return_to_tipping_grace=float(request.POST.get('thresholdDayShift_return_to_tipping_grace'))
    thresholdDayShifts.start_date=startDate
    thresholdDayShifts.end_date=endDate
    thresholdDayShifts.save()

    # ThresholdNightShift
    thresholdNightShifts.rate_card_name=rateCardID
    thresholdNightShifts.threshold_amount_per_night_shift=float(request.POST.get('thresholdNightShift_threshold_amount_per_night_shift'))
    thresholdNightShifts.loading_cost_per_cubic_meter_included=True if request.POST.get('thresholdNightShift_loading_cost_per_cubic_meter_included') == 'on' else False
    thresholdNightShifts.km_cost_included=True if request.POST.get('thresholdNightShift_km_cost_included') == 'on' else False
    thresholdNightShifts.surcharge_included=True if request.POST.get('thresholdNightShift_surcharge_included') == 'on' else False
    thresholdNightShifts.transfer_cost_included=True if request.POST.get('thresholdNightShift_transfer_cost_included') == 'on' else False
    thresholdNightShifts.return_cost_included=True if request.POST.get('thresholdNightShift_return_cost_included') == 'on' else False
    thresholdNightShifts.standby_cost_included=True if request.POST.get('thresholdNightShift_standby_cost_included') == 'on' else False
    thresholdNightShifts.waiting_cost_included=True if request.POST.get('thresholdNightShift_waiting_cost_included') == 'on' else False
    thresholdNightShifts.call_out_fees_included=True if request.POST.get('thresholdNightShift_call_out_fees_included') == 'on' else False
    thresholdNightShifts.min_load_in_cubic_meters=float(request.POST.get('thresholdNightShift_min_load_in_cubic_meters'))
    thresholdNightShifts.min_load_in_cubic_meters_return_to_yard=float(request.POST.get('thresholdNightShift_min_load_in_cubic_meters_return_to_yard'))
    thresholdNightShifts.return_to_yard_grace=float(request.POST.get('thresholdNightShift_return_to_yard_grace'))
    thresholdNightShifts.return_to_tipping_grace=float(request.POST.get('thresholdNightShift_return_to_tipping_grace'))
    thresholdNightShifts.start_date=startDate
    thresholdNightShifts.end_date=endDate
    thresholdNightShifts.save()

    # Grace
    grace.rate_card_name=rateCardID
    grace.load_km_grace=float(request.POST.get('grace_load_km_grace'))
    grace.transfer_km_grace=float(request.POST.get('grace_transfer_km_grace'))
    grace.return_km_grace=float(request.POST.get('grace_return_km_grace'))
    grace.standby_time_grace_in_minutes=float(request.POST.get('grace_standby_time_grace_in_minutes'))
    grace.chargeable_standby_time_starts_after=float(request.POST.get('grace_chargeable_standby_time_starts_after'))
    grace.waiting_time_grace_in_minutes=float(request.POST.get('grace_waiting_time_grace_in_minutes'))
    grace.chargeable_waiting_time_starts_after=float(request.POST.get('grace_chargeable_waiting_time_starts_after'))
    grace.start_date=startDate
    grace.end_date=endDate
    grace.save()
    

    
    updatedValues.insert(0,rateCardID.id)
    updatedValues.insert(1,startDate)
    updatedValues.insert(2,endDate)

    with open("scripts/updateTripsAndReconciliationData.txt",'w+',encoding='utf-8') as f:
        for val in updatedValues:
            f.write(str(val) + ',')

    if edit != 0:

        colorama.AnsiToWin32.stream = None
        os.environ["DJANGO_SETTINGS_MODULE"] = "Driver_Schedule.settings"
        cmd = ["python", "manage.py", "runscript", 'updateTripsAndReconciliationData','--continue-on-error']
        subprocess.Popen(cmd, stdout=subprocess.PIPE)
    # onLease = OnLease(
    #     rate_card_name=rateCardID,
    #     hourly_subscription_charge = float(request.POST.get('onLease_hourly_subscription_charge')),
    #     daily_subscription_charge = float(request.POST.get('onLease_daily_subscription_charge')),
    #     monthly_subscription_charge = float(request.POST.get('onLease_monthly_subscription_charge')),
    #     quarterly_subscription_charge = float(request.POST.get('onLease_quarterly_subscription_charge')),
    #     surcharge_fixed_normal_cost_included = True if request.POST.get('onLease_surcharge_fixed_normal_cost_included') == 'on' else False,
    #     surcharge_fixed_sunday_cost_included = True if request.POST.get('onLease_surcharge_fixed_sunday_cost_included') == 'on' else False,
    #     surcharge_fixed_public_holiday_cost_included = True if request.POST.get('onLease_surcharge_fixed_public_holiday_cost_included') == 'on' else False,
    #     surcharge_per_cubic_meters_normal_cost_included = True if request.POST.get('onLease_surcharge_per_cubic_meters_normal_cost_included') == 'on' else False,
    #     surcharge_per_cubic_meters_sunday_cost_included = True if request.POST.get('onLease_surcharge_per_cubic_meters_sunday_cost_included') == 'on' else False,
    #     surcharge_per_cubic_meters_public_holiday_cost_included = True if request.POST.get('onLease_surcharge_per_cubic_meters_public_holiday_cost_included') == 'on' else False,
    #     transfer_cost_applicable = True if request.POST.get('onLease_transfer_cost_applicable') == 'on' else False,
    #     return_cost_applicable = True if request.POST.get('onLease_return_cost_applicable') == 'on' else False,
    #     standby_cost_per_slot_applicable = True if request.POST.get('onLease_standby_cost_per_slot_applicable') == 'on' else False,
    #     waiting_cost_per_minute_applicable = True if request.POST.get('onLease_waiting_cost_per_minute_applicable') == 'on' else False,
    #     call_out_fees_applicable = True if request.POST.get('onLease_call_out_fees_applicable') == 'on' else False,
    #     start_date = request.POST.get('onLease_start_date')

    # )
    # onLease.save()

    messages.success(request, 'Data successfully add ')
    return redirect('gearBox:clientTable')



# ```````````````````````````````````
# Past trip
# ```````````````````````````````````


def PastTripForm(request):
    pastTripErrors = PastTripError.objects.filter(status = False).values()
    pastTripSolved = PastTripError.objects.filter(status = True).values()
    params = {
       'pastTripErrors' : pastTripErrors ,
       'pastTripSolved' :pastTripSolved
    }
    return render(request, 'Account/pastTrip.html', params)

def pastTripErrorSolve(request, id):
    # print(f'message{id}')
    errorObj = PastTripError.objects.filter(pk=id).first()

    # Check if errorObj is not None before proceeding
    if errorObj:
        tripObj = DriverTrip.objects.filter(shiftDate=errorObj.tripDate, truckNo=errorObj.truckNo).first()
        if tripObj:
            url_name = reverse('Account:pastTripErrorResolve', kwargs={'ids': tripObj.id, 'errorId': errorObj.id})
            return redirect(url_name)
        else:
            return HttpResponse("Error: Trip not found")
    else:
        return HttpResponse("Error: PastTripError not found")


def resolveError(request, id):
    resolveErrorObj = PastTripError.objects.filter(pk=id).first()
    tripObj = DriverTrip.objects.filter(shiftDate=resolveErrorObj.tripDate, truckNo=resolveErrorObj.truckNo).first()
    # return HttpResponse(tripObj.id)
    # url_name = reverse('Account:DriverTripEditForm', kwargs={'id': tripObj.id})
    return redirect('Account:DriverTripEdit',id=tripObj.id)
    return redirect(url_name)
    


@csrf_protect
@api_view(['POST'])
def pastTripSave(request):

    monthAndYear = str(request.POST.get('monthAndYear'))
    save = int(request.POST.get('save'))
    clientName = request.POST.get('clientName')
    pastTrip_csv_file = request.FILES.get('pastTripFile')
    if not pastTrip_csv_file:
        return HttpResponse("No file uploaded")
    try:
        time = (str(timezone.now())).replace(':', '').replace(
            '-', '').replace(' ', '').split('.')
        time = time[0]
        
        newFileName = time + "@_!" + (str(pastTrip_csv_file.name)).replace(' ','')

        location = 'static/Account/PastTripsEntry'
        lfs = FileSystemStorage(location=location)
        lfs.save(newFileName, pastTrip_csv_file)
        with open("pastTrip_entry_month.txt",'w') as f:
            f.write(monthAndYear)
                        
        with open("pastTrip_entry.txt", 'w') as f:
            f.write(newFileName)
        if save == 1 :
            
            if clientName == 'boral':
                colorama.AnsiToWin32.stream = None
                os.environ["DJANGO_SETTINGS_MODULE"] = "Driver_Schedule.settings"
                cmd = ["python", "manage.py", "runscript", 'PastDataSave','--continue-on-error']
                subprocess.Popen(cmd, stdout=subprocess.PIPE)
            elif clientName == 'holcim':
                colorama.AnsiToWin32.stream = None
                os.environ["DJANGO_SETTINGS_MODULE"] = "Driver_Schedule.settings"
                cmd = ["python", "manage.py", "runscript", 'holcim','--continue-on-error']
                subprocess.Popen(cmd, stdout=subprocess.PIPE)
        messages.success(request, "Please wait for some time, it takes some time to update the data.")
        return redirect(request.META.get('HTTP_REFERER'))
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")


def uplodedPastTrip(request):
   
    pastTripFile = os.listdir('static/Account/PastTripsEntry')
    pasrTripFileNameList = []
    for file in pastTripFile:
        pasrTripFileNameList.append([file.split('@_!')[0],file.split('@_!')[1]])
        
    return render(request, 'Account/uplodedPastTrip.html', {'pasrTripFileNameLists' : pasrTripFileNameList})
# --------------------------------------------
# Surcharge 
# ---------------------------------------------

def surchargeTable(request):
    surcharges = Surcharge.objects.all()
    # return HttpResponse(surcharge_)
    return render(request, 'Account/Tables/surchargeTable.html', {'surcharges': surcharges})


def surchargeForm(request, id=None):
    surcharge = None
    if id:
        surcharge = Surcharge.objects.get(pk=id)

    params = {
        'data': surcharge
    }
    # return HttpResponse(params['data'])
    return render(request, "Account/surchargeForm.html", params)


@csrf_protect
@api_view(['POST'])
def surchargeSave(request, id=None):
    dataList = {
        'surcharge_Name': (request.POST.get('surcharge_Name')).strip()
    }
    if id is not None:
        updateIntoTable(record_id=id, tableName='Surcharge', dataSet=dataList)
        messages.success(request, 'Surcharge updated successfully')
    else:
        # return HttpResponse(dataList['surcharge_Name'])
        insertIntoTable(tableName='Surcharge', dataSet=dataList)
        messages.success(request, 'Surcharge added successfully')

    return redirect('Account:surchargeTable')

def DriverShiftForm(request,id):
    pastTripFile = os.listdir('static/Account/PastTripsEntry')
    pasrTripFileNameList = []
    for file in pastTripFile:
        pasrTripFileNameList.append([file.split('@_!')[0],file.split('@_!')[1]])
        
    # return render(request, 'Account/uplodedPastTrip.html', {'pasrTripFileNameLists' : pasrTripFileNameList})
    client = Client.objects.all()
    pastTripErrors = PastTripError.objects.filter(status = False).values()
    pastTripSolved = PastTripError.objects.filter(status = True).values()
    # docketObj = DriverDocket.objects.filter(docketnumber = pastTripSolved.docketNumber).values9
    params ={
            'clients': client,
            'id':id,
            'pasrTripFileNameLists' : pasrTripFileNameList,
            'pastTripErrors' : pastTripErrors ,
            'pastTripSolved' :pastTripSolved,
        }      
    return render(request, 'Account/driverShiftForm.html',params)


@csrf_protect
def ShiftDetails(request,id):
    startDate = request.POST.get('startDate')
    endDate = request.POST.get('endDate')
    clientNameObj = Client.objects.filter(name=request.POST.get('clients')).first()
    id_ = id
    trips =None
    if id == 0:
        if clientNameObj:
            trips = DriverTrip.objects.filter(shiftDate__range=(startDate, endDate) ,verified = False , clientName = clientNameObj)
        else:
            trips = DriverTrip.objects.filter(shiftDate__range=(startDate, endDate) ,verified = False)
    elif id == 1:
        if clientNameObj:
            trips = DriverTrip.objects.filter(shiftDate__range=(startDate, endDate) ,verified = True , clientName = clientNameObj)
        else:
            trips = DriverTrip.objects.filter(shiftDate__range=(startDate, endDate) ,verified = True)
    #     if clientName == 'boral':
    #         boralTrip = DriverTrip.objects.filter(shiftDate__range=(startDate, endDate) ,verified = False)
    #     elif clientName == 'holcim':
    #         holcimTrip = DriverTrip.objects.filter(shiftDate__range=(startDate,endDate),verified = False)
    #     else:
    #         boralTrip = DriverTrip.objects.filter(shiftDate__range=(startDate, endDate) ,verified = False)
    #         holcimTrip = DriverTrip.objects.filter(shiftDate__range=(startDate,endDate),verified = False)
    # elif id ==1:
    #     if clientName == 'boral':
    #         boralTrip = DriverTrip.objects.filter(shiftDate__range=(startDate, endDate) ,verified = True)
    #     elif clientName == 'holcim':
    #         holcimTrip = HolcimTrip.objects.filter(shiftDate__range=(startDate,endDate) ,verified = True)
    #     else:
    #         boralTrip = DriverTrip.objects.filter(shiftDate__range=(startDate, endDate) ,verified = True)
    #         holcimTrip = HolcimTrip.objects.filter(shiftDate__range=(startDate,endDate),verified = True)
        # return HttpResponse(holcimTrip.driverName)
           

            
        
    else:
        messages.warning( request, "Invalid Request")
        return redirect(request.META.get('HTTP_REFERER'))
    params = {
        'trips': trips,
        'startDate': startDate,
        'endDate': endDate,
        'id_': id_,
        
        }
    return render(request, 'Account/Tables/driverTripsTable.html', params)
    
@csrf_protect
def driverShiftCsv(request):
    data_list = []
    temp_trip_data_list = []
    temp_docket_data_list = []
    startDate = request.POST.get('startDate')
    endDate = request.POST.get('endDate')
    id_ = request.POST.get('id_')
    id_ =True if int(id_) == 1 else False

    # if verified_ == '1':
    #     driver_trip = DriverTrip.objects.filter(verified=True).values()
    # elif verified_ == '0':
    #     driver_trip = DriverTrip.objects.filter(verified=False).values()
    # elif ClientId:
    #     driver_trip = DriverTrip.objects.filter(clientName=ClientId).values()
    #     foreignKeySet(driver_trip)
    if startDate and endDate:
        
        driver_trip = DriverTrip.objects.filter(shiftDate__range=(startDate, endDate),verified = True if id_ ==1 else False).values()
        foreignKeySet(driver_trip)
    else:
        driver_trip = DriverTrip.objects.all().values()

    try:
        for trip in driver_trip:
            temp_trip_data_list.append([
                trip['verified'],
                trip['driverId_id'],
                trip['clientName_id'],
                trip['shiftType'],
                trip['numberOfLoads'],
                trip['truckNo'],
                trip['shiftDate'],
                trip['startTime'],
                trip['endTime'],
                trip['loadSheet'],
                trip['comment'],
            ])
            related_dockets = DriverDocket.objects.filter(
                tripId=trip['id']).values_list()
            if related_dockets:
                for docket in related_dockets:
                    basePlant_ = BasePlant.objects.filter(id = int(docket[5])).first()
                    docket = list(docket)
                    docket[5] = basePlant_.basePlant
                    temp_docket_data_list.append(docket)
                for i in range(len(temp_docket_data_list)):
                    data_list.append(
                        temp_trip_data_list[0] + temp_docket_data_list[i])
                temp_trip_data_list.clear()
                temp_docket_data_list.clear()
            else:
                data_list.extend(temp_trip_data_list)
                temp_trip_data_list.clear()
    except Exception as e:
        return HttpResponse(e)

    time = str(timezone.now()).replace(':', '').replace(
        '-', '').replace(' ', '').split('.')
    newFileName = time[0]
    location = 'static/Account/DriverTripCsvDownload/'
    lfs = FileSystemStorage(location=location)
    csv_filename = newFileName + '.csv'

    header = ['verified', 'driverId', 'clientName', 'shiftType', 'numberOfLoads', 'truckNo', 'shiftDate', 'startTime', 'endTime', 'loadSheet', 'comment', 'docketId', 'shiftDatetripId', 'tripId', 'docketNumber',
              'docketFile', 'basePlant', 'noOfKm', 'transferKM', 'returnToYard', 'tippingToYard', 'returnQty', 'returnKm', 'waitingTimeStart', 'waitingTimeEnd', 'totalWaitingInMinute', 'surcharge_type', 'surcharge_duration',
              'cubicMl', 'standByStartTime', 'standByEndTime','minimumLoad', 'others', 'comment'
            ]

    file_name = location + csv_filename

    # Open the CSV file in append mode ('a')
    myFile = open(file_name, 'a', newline='')
    writer = csv.writer(myFile)
    writer.writerow(header)
    writer.writerows(data_list)
    myFile.close()
    return FileResponse(open(f'static/Account/DriverTripCsvDownload/{csv_filename}', 'rb'), as_attachment=True)

def topUpForm(request,id , topUpDocket = None):
    escalationData = None
    rctiError = None
    client = Client.objects.all()
    startDate = request.POST.get('startDate')
    endDate = request.POST.get('endDate')
    rctiError = RctiErrors.objects.filter(pk=id).first()
    clientNameObj = Client.objects.filter(name = rctiError.clientName).first()
    if topUpDocket:
        escalationData = Escalation.objects.filter(clientName = clientNameObj , escalationDate__range = (startDate , endDate ), escalationType = 'External', escalationStep = 3).values()
    formName = None 
    formName = 'Top Up' if rctiError.data else None
    params = {
        'errorId':rctiError,
        'formName':formName,
        'escalationData':escalationData,
        'client':client,
        'topUpDocket': topUpDocket
    }
    return render(request,'Account/topUpForm.html',params)

def topUpSolve(request):
    errorId  = request.GET.get('topUpId')
    remark  = request.GET.get('remark')
    dockets = request.GET.getlist('dockets[]')
    for docket in dockets:
        getDocket = Escalation.objects.filter(pk = docket).first()
        getDocket.escalationStep = 4
        getDocket.remark = remark
        getDocket.errorId = errorId
        getDocket.save()
    rctiError = RctiErrors.objects.filter(pk=errorId).first()
    rctiError.status = True
    rctiError.save()
        
    return JsonResponse({'status': True})
    
def report(request):
    return render(request,'Account/report.html')

@csrf_protect
def reportSave(request):
    primaryFile = request.FILES.get('primaryFile')
    secondaryFile = request.FILES.get('secondaryFile')

    if primaryFile:
        time = getCurrentTimeInString()
        primaryFileName = time + "@_!" + (str(primaryFile.name)).replace(' ','')
        location = f'static/Account/RCTI/Report'
        lfs = FileSystemStorage(location=location)
        lfs.save(primaryFileName, primaryFile)
    if secondaryFile:
        time = getCurrentTimeInString()
        secondaryFileName = time + "@_!" + (str(secondaryFile.name)).replace(' ','')
        location = f'static/Account/RCTI/Report'
        lfs = FileSystemStorage(location=location)
        lfs.save(secondaryFileName, secondaryFile)
    messages.success(request,'Successfully save')
    return redirect(request.META.get('HTTP_REFERER'))

def EscalationTable(request):
    escalationObj  = Escalation.objects.all()
    params ={
        'escalationObj':escalationObj
    }
    return render(request,'Account/Tables/escalationTable.html' , params)
def EscalationForm(request ,id = None):
    escalationObj  = None
    clientObj = Client.objects.all()
    if id:
        escalationObj  = Escalation.objects.filter(pk = id).first()
        # escalationObj.docketDate = escalationObj.docketDate.strftime('%d-%m-%Y')
        print(type(escalationObj.docketDate), escalationObj.docketDate)
        # return HttpResponse(escalationObj.docketDate)
        
    params ={
        'escalationObj':escalationObj,
        'clientObj':clientObj
    }
    return render(request , 'Account/escalationForm.html' , params)