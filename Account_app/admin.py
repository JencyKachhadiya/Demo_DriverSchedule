from django.contrib import admin
from .models import *
from Account_app.models import *
from django.core.mail import send_mail, EmailMessage
from GearBox_app.models import *
from Appointment_app.models import *
from django.http import HttpResponse
import csv

class DocketInline(admin.StackedInline):
    model = DriverDocket
    fieldsets=[
        (
            "docket_details",
            {
                "fields" : 
                    
                    [
                        'docketId',
                        'shiftDate',
                        'tripId',
                        'docketNumber',
                        'docketFile',
                        'basePlant',
                        'noOfKm',
                        'transferKM',
                        'returnToYard',
                        'returnQty',
                        'returnKm',
                        'waitingTimeStart',
                        'waitingTimeEnd',
                        'totalWaitingInMinute',
                        'surcharge_type',
                        'surcharge_duration',
                        'cubicMl',
                        'standByStartTime',
                        'standByEndTime',
                        'others',
                        'comment'
                    ]
            } 
        )
    ]
        
    # readonly_fields = ["noOfKm"]
    extra = 0

# def driver_trip_download_csv(modeladmin, request, queryset):
#     # Create a response object with CSV content type
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="DriverTripInfo.csv"'

#     # Create a CSV writer using the response object
#     writer = csv.writer(response)

#     # Write the header row
#     writer.writerow(["verified", "driverId", "clientName", "shiftType",
#                      "numberOfLoads", "truckNo", "shiftDate","startTime", "endTime", "loadSheet",
#                      "comment",
#                         "docketId",
#                         "tripId",
#                         "shiftDate",
#                         "docketNumber",
#                         "docketFile",
#                         "basePlant",
#                         "noOfKm",
#                         "transferKM",
#                         "returnKm",
#                         "waitingTimeInMinutes",
#                         "minimumLoad",
#                         "surcharge_type",
#                         "surcharge_duration",
#                         "cubicMl",
#                         "minLoad",
#                         "standByPerHalfHourDuration",
#                         "others"
#                      ])

#  # Write data rows
#     for driver_trip in queryset:
#         # print(queryset)
#         row_data = [
#             driver_trip.verified,
#             driver_trip.driverId,
#             driver_trip.clientName,
#             driver_trip.shiftType,
#             driver_trip.numberOfLoads,
#             driver_trip.truckNo,
#             driver_trip.shiftDate,
#             driver_trip.startTime,
#             driver_trip.endTime,
#             driver_trip.loadSheet,
#             driver_trip.comment,
#             '', 
#             '', 
#             '',
#             '',
#             '',
#             '',
#             '',
#             '',
#             '',
#             '',
#             '',
#             '',
#             '',
#             '',
#             '',
#             '',
#             '' # Initialize empty placeholders for other fields
#         ]
    
#         for docket in driver_trip.driverdocket_set.all():
#             row_data[11:29] = [ docket.docketId,
#                                 docket.tripId,
#                                 docket.shiftDate,
#                                 docket.docketNumber,
#                                 docket.docketFile,
#                                 docket.basePlant,
#                                 docket.noOfKm,
#                                 docket.transferKM,
#                                 docket.returnKm,
#                                 docket.waitingTimeInMinutes,
#                                 docket.minimumLoad,
#                                 docket.surcharge_type,
#                                 docket.surcharge_duration,
#                                 docket.cubicMl,
#                                 docket.minLoad,
#                                 docket.standByPerHalfHourDuration,
#                                 docket.others
#                                 ]

#         # Only write the row if at least admin truck data is present
#         if driver_trip.driverId:
#             writer.writerow(row_data)

#     return response

class DriverTrip_(admin.ModelAdmin):

    list_display = ['verified',"driverId", "clientName", 'truckNo',"shiftType", "startTime", 'endTime',"shiftDate"]
    # search_fields = ["driverId", 'clientName']
    list_filter = ('shiftType', 'clientName')
    # actions = [driver_trip_download_csv]
    inlines = [DocketInline]

admin.site.register(DriverTrip,DriverTrip_)



# class WaitingTimeCost_(admin.StackedInline):
#     model = WaitingTimeCost
#     extra = 0
    
#     list_display = ["docketNo","deliveryDate","paidKMS","invoiceQuantity","unit","unitPrice","TotalExGST","GSTPayable","TotalInGST",]
#     search_fields = ["docketNo","TotalInGST"]


# class TransferKMSCost_(admin.StackedInline):
#     model = transferKMSCost
#     extra = 0

#     list_display = ["docketNo","deliveryDate","paidKMS","invoiceQuantity","unit","unitPrice","TotalExGST","GSTPayable","TotalInGST",]
#     search_fields = ["docketNo","TotalInGST"]


class clientTripAdmin(admin.ModelAdmin):
    # inlines = [WaitingTimeCost_ ,TransferKMSCost_]
    list_display = ["docketNumber","truckNo","clientName"]
    
    search_fields = ["docketNumber","truckNo"]
     
     
admin.site.register(RCTI, clientTripAdmin)



def download_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ClientName.csv"'

    writer = csv.writer(response)

    writer.writerow(["clientId", "name", "docketGiven"])

    for s in queryset:
        writer.writerow([s.clientId, s.name, s.docketGiven])

    return response

class ClientAdmin(admin.ModelAdmin):
    list_display = ["clientId", "name", 'docketGiven']
    search_fields = ["clientId", "name"]
    actions = [download_csv]

admin.site.register(Client, ClientAdmin)


def download_csv(modeladmin, request, queryset):
    # Create a response object with CSV content type and specify the filename
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="BasePlant.csv"'

    # Create a CSV writer using the response object
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(["BasePlant"])

    # Write data rows
    for s in queryset:
        writer.writerow([s.basePlant])

    return response

class BasePlantAdmin(admin.ModelAdmin):
    list_display = ["basePlant"]
    search_fields = ["basePlant"]
    actions = [download_csv]

admin.site.register(BasePlant, BasePlantAdmin)

# class ClientTruckInline(admin.TabularInline):
#     model = ClientTruckConnection
#     extra = 0
  
# class CostInline_(admin.TabularInline):
#     model =  Cost
#     extra = 0  
    
    


def admin_truck_download_csv(modeladmin, request, queryset):
    # Create a response object with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="AdminTruckInfo.csv"'

    # Create a CSV writer using the response object
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(["adminTruckNumber", "clientId", "clientTruckId",
                     "startDate", "endDate", "is_Active", "basePlant",
                     "startDate", "endDate", "transferKMSCost", "waitingTimeCost",
                     "cartagePerCumCost", "surchargeCost"])

    # Write data rows
    for admin_truck in queryset:
        row_data = [
            admin_truck.adminTruckNumber,
            '', '', '', '', '', '', '', '', '', '', '', '', '', '',  
        ]

        for client_truck in admin_truck.clienttruckconnection_set.all():
            row_data[1:5] = [client_truck.clientId, client_truck.clientTruckId,
                             client_truck.startDate, client_truck.endDate]

        for cost in admin_truck.cost_set.all():
            row_data[5:] = [cost.is_Active, cost.basePlant, cost.startDate, cost.endDate,
                              cost.transferKMSCost, cost.waitingTimeCost, cost.cartagePerCumCost, cost.surchargeCost]

        # Only write the row if at least admin truck data is present
        if admin_truck.adminTruckNumber:
            writer.writerow(row_data)

    return response


admin.site.register(RateCard)
admin.site.register(CostParameters)
admin.site.register(ThresholdDayShift)
admin.site.register(ThresholdNightShift)
admin.site.register(Grace)
admin.site.register(OnLease)
class AdminTruckAdmin(admin.ModelAdmin):
    list_display = ["adminTruckNumber"]
    search_fields = ["adminTruckNumber"]
    actions = [admin_truck_download_csv]
admin.site.register(AdminTruck, AdminTruckAdmin)

    # inlines = [ClientTruckInline]

class ClientTruckConnection_(admin.ModelAdmin):
    list_display =['rate_card_name','clientTruckId','startDate','endDate']
    search_fields = ['clientTruckId']

admin.site.register(ClientTruckConnection,ClientTruckConnection_)
    



def driver_download_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="DriverRegInfo.csv"'

    writer = csv.writer(response)

    writer.writerow(["driverId", "name", "phone" , "email" , "password"])

    for s in queryset:
        writer.writerow([s.driverId, s.name, s.phone, s.email , s.password])

    return response

class Driver_(admin.ModelAdmin):
    # inlines = [LeaveReqAdminDriver]
    list_display = ["driverId", "name", 'phone', 'password']
    search_fields = ["driverId",'name']
    # actions = [driver_download_csv]

    def upcoming_leave_requests(self, obj):
        now = timezone.now()
        upcoming_requests = obj.leaverequest_set.filter(start_date__gte=now).order_by('start_date')[:2]
        return ', '.join([str(request) for request in upcoming_requests])

    upcoming_leave_requests.short_description = 'Upcoming Leave Requests'

admin.site.register(Driver, Driver_)

# admin.site.register(LeaveRequest)

def leave_download_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="DriverLeave.csv"'

    writer = csv.writer(response)

    writer.writerow(["employee", "start_date", "end_date" , "reason" , "status"])

    for s in queryset:
        writer.writerholow([s.employee, s.start_date, s.end_date, s.reason , s.status])

    return response


class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ["employee","start_date","end_date","reason","status"]
    search_fields = ["employee"]
    actions = [leave_download_csv]

admin.site.register(LeaveRequest, LeaveRequestAdmin)


def nature_leave_download_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="NatureLeave.csv"'

    writer = csv.writer(response)

    writer.writerow(["reason"])

    for s in queryset:
        writer.writerow([s.reason])

    return response

class NatureOfLeaveAdmin(admin.ModelAdmin):
    list_display = ["reason"]
    search_fields = ["reason"]
    actions = [nature_leave_download_csv]

admin.site.register(NatureOfLeave, NatureOfLeaveAdmin)


# class DriverDocketAdmin(admin.ModelAdmin):
#     list_display=['Docket_NO']
#     search_fields = ['Docket_NO']
    
# admin.site.register(DriverDocket,DriverDocketAdmin)
# @admin.register(Appointment)
# class AppointmentAdmin(admin.ModelAdmin):
#     search_fields = ('driver', 'client',)
#     list_display = ["Title", "Start_Date_Time", "End_Date_Time", "Status", "driver"]
#     list_filter = ["Status"]
#     actions = ['send_email_action']

#     def send_email_action(self, request, queryset):
#         subject = 'Your job application status'
#         message = 'Your job application status has been updated.'
#         from_email = 'siddhantethansrec@example.com'  # Set your email address
#         recipient_list = [applicant.driver.email for applicant in queryset]
#         print(recipient_list)
        
#         # Send emails to selected applicants
#         for applicant in queryset:
#             send_mail(subject, message, from_email, [applicant.driver.email])
#             # send_notification_email(applicant.progress_set.latest('date_updated'))
        
#         self.message_user(request, f'Emails sent to {len(queryset)} applicants.')
    
#     send_email_action.short_description = 'Send email to selected applicants'

admin.site.register(Surcharge)

admin.site.register(PublicHoliday)


class RctiErrors_(admin.ModelAdmin):

    list_display = ['docketNumber',"status","docketDate","errorDescription"]
    search_fields = ["docketNumber"]


admin.site.register(RctiErrors,RctiErrors_)

class PastTripError_(admin.ModelAdmin):

    list_display = ['docketNumber',"status","errorFromPastTrip"]
    search_fields = ["docketNumber"]


admin.site.register(PastTripError,PastTripError_)


class ReconciliationReportAdmin(admin.ModelAdmin):
    list_display = ["docketNumber","reconciliationType","docketDate"]
    search_fields = ["docketNumber"]

admin.site.register(ReconciliationReport , ReconciliationReportAdmin)

class RctiExpenseAdmin(admin.ModelAdmin):
    list_display = ["docketNumber","docketDate"]
    search_fields = ["docketNumber"]

admin.site.register(RctiExpense , RctiExpenseAdmin)

# admin.site.register(Location)

admin.site.register(TruckInformation)
admin.site.register(TruckDocument)



@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    search_fields = ('client',)
    list_display = ["Title", "Start_Date_Time", "End_Date_Time", "Status","scheduled"]
    list_filter = ["Status"]
    actions = ['send_email_action']

    def send_email_action(self, request, queryset):
        subject = 'Your job application status'
        message = 'Your job application status has been updated.'
        from_email = 'siddhantethansrec@example.com'  # Set your email address
        recipient_list = [applicant.driver.email for applicant in queryset]
        print(recipient_list)
        
        # Send emails to selected applicants
        for applicant in queryset:
            send_mail(subject, message, from_email, [applicant.driver.email])
            # send_notification_email(applicant.progress_set.latest('date_updated'))
        
        self.message_user(request, f'Emails sent to {len(queryset)} applicants.')
    
    send_email_action.short_description = 'Send email to selected applicants'

class HolcimDocket_(admin.ModelAdmin):

    list_display = ['truckNo' ,'jobNo','tripId']
    search_fields = ["jobNo"]


admin.site.register(HolcimDocket,HolcimDocket_)

admin.site.register(RateCardSurchargeValue)

class HolcimTrip_(admin.ModelAdmin):

    list_display = ['truckNo','shiftDate','numberOfLoads']
    search_fields = ["truckNo"]


admin.site.register(HolcimTrip,HolcimTrip_)

admin.site.register(AppointmentTruck)
admin.site.register(AppointmentDriver)

admin.site.register(PreStart)
admin.site.register(RctiReport)
admin.site.register(RctiAdjustment)

admin.site.register(Escalation)
admin.site.register(EscalationMail)



