from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
import shutil ,os ,subprocess ,csv
from django.views.decorators.csrf import csrf_protect
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.contrib import messages
from Account_app.models import *
from GearBox_app.models import *
from Appointment_app.models import *
from django.http import FileResponse
from CRUD import *
from Account_app.reconciliationUtils import *
from django.db.models import Q
import itertools

# ````````````````````````````````````
# Appointment

# ```````````````````````````````````

def convertDateTimeForTemplate(provided_date_string):
    datetime_obj = datetime.strptime(str(provided_date_string), "%Y-%m-%d %H:%M:%S%z")
    formatted_datetime = datetime_obj.strftime("%Y-%m-%dT%H:%M")
    return formatted_datetime

def appointmentForm(request, id=None, update=None):
    currentUser = request.user
    drivers = Driver.objects.all()
    clients = Client.objects.all()
    truckNos = AdminTruck.objects.all()
    params = {
        'drivers' : drivers,
        'truckNos':truckNos,
        'clients' : clients,  
        'currentUser' : currentUser 
    }
    if id:
        data = Appointment.objects.filter(pk=id).first()
        data.Start_Date_Time = convertDateTimeForTemplate(data.Start_Date_Time)
        data.End_Date_Time = convertDateTimeForTemplate(data.End_Date_Time)
        data.report_to_origin = convertDateTimeForTemplate(data.report_to_origin)
        
        appointmentDriver = AppointmentDriver.objects.filter(appointmentId = data.id).last()
        appointmentTruck = AppointmentTruck.objects.filter(appointmentId = data.id).last()

        params['data'] = data
        params['appointmentDriver'] = appointmentDriver
        params['appointmentTruck'] = appointmentTruck
        
        unavailableDriversAndTrucksQrySet = Appointment.objects.filter(Q(Start_Date_Time__gte = data.Start_Date_Time,Start_Date_Time__lte = data.End_Date_Time)|Q(End_Date_Time__gte = data.Start_Date_Time,End_Date_Time__lte = data.End_Date_Time))
        unavailableDriversQrySet = [] 
        unavailableTrucksQrySet = [] 
        

        for obj in unavailableDriversAndTrucksQrySet:            
            tempDriver = AppointmentDriver.objects.filter(appointmentId = obj.id).last()
            tempTruck = AppointmentTruck.objects.filter(appointmentId = obj.id).last()
            if tempDriver:
                unavailableDriversQrySet.append({'driverId':tempDriver.driverName.driverId,'name':tempDriver.driverName.name})
            if tempTruck:
                unavailableTrucksQrySet.append({'adminTruckNumber':tempTruck.truckNo.adminTruckNumber})

        drivers = Driver.objects.values('driverId','name')
        trucks =  AdminTruck.objects.values('adminTruckNumber')

        availableDriversList = list(itertools.filterfalse(lambda x: x in list(drivers), unavailableDriversQrySet)) + list(itertools.filterfalse(lambda x: x in unavailableDriversQrySet, list(drivers)))
        availableTrucksList = list(itertools.filterfalse(lambda x: x in list(trucks), unavailableTrucksQrySet)) + list(itertools.filterfalse(lambda x: x in unavailableTrucksQrySet, list(trucks)))
        
        
        params['availableDriversList'] = availableDriversList
        params['availableTrucksList'] = availableTrucksList
        params['update'] = update
        
        print(availableDriversList,availableTrucksList)
        
        
    return render(request, 'Appointment/appointmentForm.html',params)

@csrf_protect
def appointmentSave(request,id=None):
    appointmentObj = Appointment()
    if id:
        appointmentObj = Appointment.objects.filter(pk=id).first()
        messageStr = "Appointment Updated Successfully."
    else:
    # if not id:
        client = Client.objects.filter(pk=request.POST.get('stopName').strip()).first()
        newOrigin = request.POST.get('originAddVal').strip()
        originObj = None
        if newOrigin == 1:
            originObj = BasePlant()
            originObj.basePlant = request.POST.get('origin')
            originObj.address = request.POST.get('originAddress')
            originObj.phone = request.POST.get('originPhone')
            originObj.personOnName = request.POST.get('originPersonOnName')
            originObj.managerName = request.POST.get('originPersonOnName')
            originObj.lat = request.POST.get('originLatitude')
            originObj.long = request.POST.get('originLongitude')
            originObj.save()
        else:
            originObj = BasePlant.objects.filter(basePlant=request.POST.get('origin').upper().strip()).first()

        appointmentObj.Title = request.POST.get('title')
        appointmentObj.Start_Date_Time = request.POST.get('startDateTime')
        appointmentObj.End_Date_Time = request.POST.get('endDateTime')
        appointmentObj.report_to_origin = request.POST.get('reportToOrigin')
        appointmentObj.Recurring = request.POST.get('recurring')
        appointmentObj.Staff_Notes = request.POST.get('staffNotes')
        appointmentObj.Created_by = request.user
        appointmentObj.stop = client
        appointmentObj.Origin = originObj
        appointmentObj.shiftType = request.POST.get('shiftType')
        appointmentObj.Status = 'Unassigned'
        appointmentObj.save()
        messageStr = "Appointment added successfully."
    
    driver = Driver.objects.filter(pk=request.POST.get('driverName')).first()
    if driver:
        appointmentDriverObj = AppointmentDriver.objects.filter(appointmentId = appointmentObj.id).first()
        if not appointmentDriverObj:
            appointmentDriverObj = AppointmentDriver()
            
        appointmentDriverObj.driverName = driver
        appointmentDriverObj.appointmentId = appointmentObj
        appointmentDriverObj.save()
    
    truck = AdminTruck.objects.filter(adminTruckNumber=request.POST.get('truckNo')).first()

    if truck:
        appointmentTruckObj = AppointmentTruck.objects.filter(appointmentId = appointmentObj.id).first()
        if not appointmentTruckObj:
            appointmentTruckObj = AppointmentTruck()
            
        appointmentTruckObj.truckNo = truck
        appointmentTruckObj.appointmentId = appointmentObj
        appointmentTruckObj.save()
        
    if driver and truck:
        appointmentObj.Status = "Assigned"
        appointmentObj.save()
        
    messages.success(request, messageStr)

    return redirect('Appointment:findJob')        

def findJob(request):
    jobs = Appointment.objects.filter(scheduled = False)
    params = {
        'jobs' : jobs
    }
    return render(request, 'Appointment/findJob.html',params)

@csrf_protect
def getTruckAndDriver(request):
    startDateTime = request.POST.get('startDateTime')
    endDateTime = request.POST.get('endDateTime')
    
    print(startDateTime,endDateTime)
    
    try:
        startDateTime = datetime.strptime(startDateTime, '%Y-%m-%dT%H:%M:%S')
        endDateTime = datetime.strptime(endDateTime, '%Y-%m-%dT%H:%M:%S')
    except ValueError as e:
        startDateTime =  datetime.strptime(startDateTime, '%Y-%m-%dT%H:%M')
        endDateTime =  datetime.strptime(endDateTime, '%Y-%m-%dT%H:%M')
        
    # Qry logic
    # Appointment.objects.get(Q(Start_Date_Time__gte = startDateTime,Start_Date_Time__lte = endDateTime)|Q(End_Date_Time__gte = startDateTime,End_Date_Time__lte = endDateTime))
    #                               03-04              01-04            03-04            04-04               02-04             01-04              02-04             04-04                   
    # job = 1-4, 4-4        Data from form
    # d1 = 25-3 , 02-4      Entry from database
    # d2 = 03-4 , 10-4      Entry from database
    
    
    unavailableDriversAndTrucksQrySet = Appointment.objects.filter(Q(Start_Date_Time__gte = startDateTime,Start_Date_Time__lte = endDateTime)|Q(End_Date_Time__gte = startDateTime,End_Date_Time__lte = endDateTime))
    unavailableDriversQrySet = [] 
    unavailableTrucksQrySet = [] 

    for obj in unavailableDriversAndTrucksQrySet:
        # tempDriver = obj.driver
        # tempTruck = AdminTruck.objects.filter(adminTruckNumber = obj.truckNo).first()
        
        tempDriver = AppointmentDriver.objects.filter(appointmentId = obj.id).first()
        tempTruck = AppointmentTruck.objects.filter(appointmentId = obj.id).first()
        if tempDriver:
            unavailableDriversQrySet.append({'driverId':tempDriver.driverName.driverId,'name':tempDriver.driverName.name})
        if tempTruck:
            unavailableTrucksQrySet.append({'adminTruckNumber':tempTruck.truckNo.adminTruckNumber})

    drivers = Driver.objects.values('driverId','name')
    trucks =  AdminTruck.objects.values('adminTruckNumber')

    availableDriversList = list(itertools.filterfalse(lambda x: x in list(drivers), unavailableDriversQrySet)) + list(itertools.filterfalse(lambda x: x in unavailableDriversQrySet, list(drivers)))
    availableTrucksList = list(itertools.filterfalse(lambda x: x in list(trucks), unavailableTrucksQrySet)) + list(itertools.filterfalse(lambda x: x in unavailableTrucksQrySet, list(trucks)))

    return JsonResponse({'status': True, 'availableTrucksList': availableTrucksList, 'availableDriversList': availableDriversList})

    # Add logic for leave request here
    

@csrf_protect
def getOriginDetails(request):
    originName = request.POST.get('originName').strip().upper()
    status = True
    origin = BasePlant.objects.filter(basePlant=originName).values().first()
    print(originName,origin)
    if not origin:
        status = False
    return JsonResponse({'status': status ,'origin' : origin})
        




