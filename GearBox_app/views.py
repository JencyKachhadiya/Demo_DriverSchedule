from django.shortcuts import render
from Account_app.models import *
from GearBox_app.models import *
from django.conf import settings
from .models import *
from CRUD import *
from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from rest_framework.decorators import api_view
from django.contrib import messages
from django.http import Http404
from django.contrib.auth.models import User , Group
import os, colorama, subprocess
from django.db.models import Q


# Create your views here.
def leaveReq(request):
    leave_requests = LeaveRequest.objects.all()
    return render(request, 'gearBox/table/LeaveReq.html', {'leave_requests': leave_requests})

def natureOfLeaves(request):
    nature_of_leaves = NatureOfLeave.objects.all()
    return render(request, 'gearBox/table/NatureOfLeaves.html', {'nature_of_leaves': nature_of_leaves})

def natureOfLeavesForm(request,id=None):
    data = None
    if id:
        try:
            data = NatureOfLeave.objects.get(id=id)
        except NatureOfLeave.DoesNotExist:
            raise Http404("NatureOfLeave does not exist")
    return render(request,'gearBox/NatureOfLeavesForm.html',{'data': data}) 

@csrf_protect
@api_view(['POST'])
def changeNatureOfLeaves(request,id=None):
    data = {
        'reason' : request.POST.get('Reason'),
    }
    if id == None:
        insert = insertIntoTable(tableName='NatureOfLeave',dataSet=data)
        messages.success(request,'Adding successfully')
    else:
        update = updateIntoTable(id,tableName='NatureOfLeave',dataSet=data)
        messages.success(request, 'Updating successfully')
    return redirect('gearBox:natureOfLeaves')

def leaveReqForm(request,id=None):
    natureOfLeaves = NatureOfLeave.objects.all()
    drivers = Driver.objects.all()
    params = {
            "natureOfLeaves" : natureOfLeaves,
            "drivers" : drivers,
        }
    if id:
        data = LeaveRequest.objects.get(id=id)
        data.start_date = dateConverterFromTableToPageFormate(data.start_date)
        data.end_date = dateConverterFromTableToPageFormate(data.end_date)
        params["data"] = data
        
    return render(request,'gearBox/LeaveReqForm.html',params)
        
@csrf_protect
@api_view(['POST'])
def changeLeaveRequest(request,id=None):
    
    employee = Driver.objects.get(driverId = request.POST.get('driverId'))
    reason = NatureOfLeave.objects.get(id = request.POST.get('Reason'))
    
    data = {
        'employee' : employee,
        'start_date' : request.POST.get('StartDate'),
        'end_date' : request.POST.get('EndDate'),
        'reason' :reason,
    }
    if id == None:
        data['status'] = 'Pending'
        insert = insertIntoTable(tableName='LeaveRequest',dataSet=data)
        messages.success(request,'Adding successfully')
    else:
        data['status'] = request.POST.get('Status')
        update = updateIntoTable(record_id=id,tableName='LeaveRequest',dataSet=data)
        messages.success(request,'Updated successfully')
        
        
    return redirect('gearBox:leaveReq')


def driversView(request):
    drivers = Driver.objects.all()
    params = {
        'drivers' : drivers
    }
    return render(request,'GearBox/table/driverTable.html',params)


def driverForm(request, id=None):
    data = None
    if id:
        data = Driver.objects.get(pk = id)   
    params = {
        'data' : data
    }
    return render(request, 'GearBox/driverForm.html',params)


@csrf_protect
@api_view(['POST'])
def driverFormSave(request, id= None):
    users = User.objects.all()
    drivers = Driver.objects.all()

    usernames = [user.username for user in users]
    email_addresses = [user.email for user in users]
    driver_Id = [driver.driverId for driver in drivers]
    driverName = request.POST.get('name').strip().replace(' ','').lower()
    # Update 
    if id :
        driverObj = Driver.objects.get(pk=id)
        user = User.objects.get(email = driverObj.email)
        if driverObj.name != driverName:
            if driverName in usernames:
                messages.error( request, "Driver Name  already Exist")
                return redirect(request.META.get('HTTP_REFERER'))
            else:
                driverObj.name = driverName
                user.username = driverObj.name
            
        if driverObj.email != request.POST.get('email'):
            if request.POST.get('email') in email_addresses:
                messages.error( request, "Email Address already Exist")
                return redirect(request.META.get('HTTP_REFERER'))
            else:
                driverObj.email = request.POST.get('email')
                user.email = driverObj.email        
        
        if driverObj.phone != request.POST.get('phone'):
            driverObj.phone = request.POST.get('phone') 
            
        user.save()
        driverObj.save()
        
        
        
        messages.success(request,'Updating successfully')
    else:
        if int(request.POST.get('driverId')) in driver_Id :
            messages.error( request, "Driver ID already Exist")
            return redirect(request.META.get('HTTP_REFERER'))
        elif driverName in usernames:
            messages.error( request, "Driver Name  already Exist")
            return redirect(request.META.get('HTTP_REFERER'))
        elif request.POST.get('email') in email_addresses:
            messages.error( request, "Email Address already Exist")
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            DriverObj = Driver()
            DriverObj.driverId = int(request.POST.get('driverId'))
            DriverObj.name = driverName
            DriverObj.phone = request.POST.get('phone') 
            DriverObj.email = request.POST.get('email')
            DriverObj.password = request.POST.get('password')
            
            user_ = User.objects.create(
                username=DriverObj.name,
                email=DriverObj.email,
                password=DriverObj.password,
                is_staff=True,
            )  
            group = Group.objects.get(name='Driver')
            user_.groups.add(group)
            
            user_.set_password(DriverObj.password)
            user_.save()
            DriverObj.save()
            messages.success(request,'Driver Entry successfully')
            
            
            with open("scripts/addPastTripForMissingDriver.txt", 'w') as f:
                f.write(driverName)
            # colorama.AnsiToWin32.stream = None
            # os.environ["DJANGO_SETTINGS_MODULE"] = "Driver_Schedule.settings"
            # cmd = ["python", "manage.py", "runscript", 'addPastTripForMissingDriver','--continue-on-error']
            # subprocess.run(cmd)
            colorama.AnsiToWin32.stream = None
            os.environ["DJANGO_SETTINGS_MODULE"] = "Driver_Schedule.settings"
            cmd = ["python", "manage.py", "runscript", 'addPastTripForMissingDriver','--continue-on-error']
            subprocess.Popen(cmd, stdout=subprocess.PIPE)
            
            

    return redirect('gearBox:driversTable')


# ````````````````````````````````````````

# Truck Section 

# ````````````````````````````````````````````````

def truckTable(request):
    adminTruck = AdminTruck.objects.all()
    params = {
        'adminTrucks' : adminTruck
    }
    return render(request , 'GearBox/truck/table/truckTable.html',params)

def truckForm(request, id=None):
    clientIds = Client.objects.all()
    rateCards = RateCard.objects.all()
    data=connections = None
    count_ = 1
    if id:
        data = AdminTruck.objects.get(pk=id)
        connections = ClientTruckConnection.objects.filter(truckNumber=id).values()

        for i in connections:
            i['count'] = count_
            count_ += 1
            i['startDate'] = dateConverterFromTableToPageFormate(i['startDate'])
            if i['endDate']:
                i['endDate'] = dateConverterFromTableToPageFormate(i['endDate'])
                
    params = {
        'clientIds' : clientIds,
        'rateCards' : rateCards,
        'data' : data,
        'connections' : connections,
    }
    return render(request,'GearBox/truck/truckForm.html',params)

@csrf_protect
@api_view(['POST'])
def truckFormSave(request):
    # return HttpResponse(request.POST.get('truckNo'))
    dataList = {
        'adminTruckNumber' : request.POST.get('truckNo'),
    }
    insertIntoTable(tableName='AdminTruck',dataSet=dataList)

    messages.success(request,'Adding successfully')
    return redirect('gearBox:truckTable')

def truckConnectionForm(request, id):
    clientIds = Client.objects.all()
    rateCards = RateCard.objects.all()
    params = {
        'clientIds' : clientIds,
        'rateCards' : rateCards,
        'truckType' : request.POST.get('truckType'),
        'id' : id
    }
    return render(request,'GearBox/clientTruckConnectionForm.html',params)

@csrf_protect
@api_view(['POST'])
def truckConnectionSave(request,id):
    adminTruck = AdminTruck.objects.get(id=id)
    rateCard = RateCard.objects.get(pk=request.POST.get('rate_card_name'))
    client = Client.objects.get(pk=request.POST.get('clientId'))
    dataList = {
        'truckNumber' : adminTruck,
        'rate_card_name' : rateCard,
        'clientId' : client,
        'clientTruckId' : request.POST.get('clientTruckNumber'),
        'truckType' : request.POST.get('truckType'),
        'startDate' : request.POST.get('startDate'),
        'endDate' : request.POST.get('endDate')
    }

    existingData = ClientTruckConnection.objects.filter(Q(truckNumber = adminTruck,clientId=dataList['clientId'],startDate__gte = dataList['startDate'],startDate__lte = dataList['endDate'])|Q(truckNumber = adminTruck,clientId=dataList['clientId'],endDate__gte = dataList['startDate'],endDate__lte = dataList['endDate'])).first()
    if existingData:
        messages.error( request, "Connection already exist.")
        return redirect(request.META.get('HTTP_REFERER'))
    try:
        oldData = ClientTruckConnection.objects.get(clientId=request.POST.get('clientId'),clientTruckId=request.POST.get('clientTruckNumber'),truckNumber=id)
        if oldData:
            oldData.endDate = getYesterdayDate(request.POST.get('StartDate'))
            oldData.save()
    except:
        pass
    insertIntoTable(tableName='ClientTruckConnection',dataSet=dataList)
    with open("scripts/addPastTripForMissingTruckNo.txt", 'w') as f:
        f.write(str(dataList['truckNumber']))

    colorama.AnsiToWin32.stream = None
    os.environ["DJANGO_SETTINGS_MODULE"] = "Driver_Schedule.settings"
    cmd = ["python", "manage.py", "runscript", 'addPastTripForMissingTruckNo','--continue-on-error']
    subprocess.Popen(cmd, stdout=subprocess.PIPE)
    messages.success(request,'Truck Connection Add Successfully')
    return redirect('gearBox:truckTable')

    # Document 
@csrf_protect
def getRateCard(request):
    clientId = request.POST.get('clientName')
    clientName = Client.objects.filter(pk = clientId).first()
    rateCardList = RateCard.objects.filter(clientName = clientName).values()
    print(rateCardList)
    return JsonResponse({'status': True, 'rateCard': list(rateCardList)})

def documentView(request):
    return render(request,'GearBox/truck/table/document.html')

def documentForm(request):
    return render(request,'GearBox/truck/documentForm.html')

# ```````````````````````````````````
# Client 
# ```````````````````````````````````

def clientTable(request):
    clients = Client.objects.all()
    params = {
        'clients' : clients
    }
    return render(request,'GearBox/table/client.html',params)

def clientForm(request, id=None):
    data = None
    if id:
        data = Client.objects.get(pk=id)

    params = {
        'data' : data
    }
    return render(request, 'GearBox/clientForm.html', params)

@csrf_protect
@api_view(['POST'])
def clientChange(request, id=None):
    
    dataList = {
        'name' : request.POST.get('name').lower().strip(),
        'email' : request.POST.get('email'),
        'docketGiven' : True if request.POST.get('docketGiven') == 'on' else False
    }
    
    if id:
        updateIntoTable(record_id=id,tableName='Client',dataSet=dataList)
        messages.success(request,'Updated successfully')
    else:
        insertIntoTable(tableName='Client',dataSet=dataList)
        messages.success(request,'Added successfully')

    return redirect('gearBox:clientTable')

def addGroups(request):
    return render(request,'GearBox/groupsForm.html')

def addSubGroups(request):
    return render(request, 'GearBox/subgroupsForm.html')
