from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator,RegexValidator
from datetime import date
from django.utils import timezone

TRUCK_TYPE_CHOICES = (
    ('Embedded','Embedded'),
    ('Casual','Casual'),
    
)
# -----------------------------------
# Client section
# -----------------------------------

class Client(models.Model):
    clientId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=255,default=None, null=True, blank=True)
    docketGiven = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.name) 
    
# -----------------------------------
# Rate Card
# -----------------------------------   

SURCHARGE_NATURE_CHOICES = (
    ('fixed normal', 'FIXED NORMAL'),
    ('fixed sunday', 'FIXED SUNDAY'),
    ('fixed public holiday', 'FIXED PUBLIC HOLIDAY'),
    ('per cubic meters normal', 'PER CUBIC METERS NORMAL'),
    ('per cubic meters sunday', 'PER CUBIC METERS SUNDAY'),
    ('per cubic meters public holiday', 'PER CUBIC METERS PUBLIC HOLIDAY'),
                           )

standby_time_grace_options = (
    ('per min cost', 'PER MIN COST'),
    ('slots', 'SLOTS')
)

class RateCard(models.Model):
    rate_card_name = models.CharField(max_length=255 , unique=True)
    tds = models.FloatField(default=0)
    clientName = models.ForeignKey(Client,on_delete=models.CASCADE , default=1)

    def __str__(self) -> str:
        return str(self.rate_card_name)

class Surcharge(models.Model):
    surcharge_Name = models.CharField(max_length=255)
    
    def __str__(self) -> str:
        return str(self.surcharge_Name)
    
class CostParameters(models.Model):
    rate_card_name = models.ForeignKey(RateCard, on_delete=models.CASCADE)
    loading_cost_per_cubic_meter = models.FloatField(default=0)
    km_cost = models.FloatField(default=0)
    # surcharge_type = models.ForeignKey(Surcharge, on_delete=models.CASCADE)
    # surcharge_cost = models.FloatField(default=0)
    transfer_cost = models.FloatField(default=0)
    return_load_cost = models.FloatField(default=0)     # change name added
    return_km_cost = models.FloatField(default=0)       # new added
    standby_time_slot_size = models.PositiveIntegerField(default=0)
    standby_cost_per_slot = models.FloatField(default=0)
    waiting_cost_per_minute = models.FloatField(default=0)
    call_out_fees = models.FloatField(default=0)
    demurrage_fees = models.FloatField(default=0)
    cancellation_fees = models.FloatField(default=0) 
    clientPayableGst = models.FloatField(default=10.0)
    start_date = models.DateField(default=timezone.now())
    end_date = models.DateField(default=timezone.now() + timezone.timedelta(days=365*10), null=True, blank=True)

class RateCardSurchargeValue(models.Model):
    rate_card_name = models.ForeignKey(RateCard, on_delete=models.CASCADE)
    surcharge = models.ForeignKey(Surcharge, on_delete=models.CASCADE)
    surchargeValue = models.FloatField(default=0)
    start_date = models.DateField(default=timezone.now())
    end_date = models.DateField(default=timezone.now() + timezone.timedelta(days=365*10), null=True, blank=True)

    def __str__(self) -> str:
        return str(self.rate_card_name)
class ThresholdDayShift(models.Model):
    rate_card_name = models.ForeignKey(RateCard, on_delete=models.CASCADE)
    threshold_amount_per_day_shift = models.FloatField(default=0)
    loading_cost_per_cubic_meter_included = models.BooleanField(default=False)
    km_cost_included = models.BooleanField(default=False)
    surcharge_included  = models.BooleanField(default=False)

    # surcharge_fixed_normal_cost_included = models.BooleanField(default=False)
    # surcharge_fixed_sunday_cost_included = models.BooleanField(default=False)
    # surcharge_fixed_public_holiday_cost_included = models.BooleanField(default=False)
    # surcharge_per_cubic_meters_normal_cost_included = models.BooleanField(default=False)
    # surcharge_per_cubic_meters_sunday_cost_included = models.BooleanField(default=False)
    # surcharge_per_cubic_meters_public_holiday_cost_included = models.BooleanField(default=False)
    
    transfer_cost_included = models.BooleanField(default=False)
    return_cost_included = models.BooleanField(default=False)
    standby_cost_included = models.BooleanField(default=False)
    waiting_cost_included = models.BooleanField(default=False)
    call_out_fees_included = models.BooleanField(default=False)
    # demurrage_fees_included = models.BooleanField(default=False)

    min_load_in_cubic_meters = models.FloatField(default=0)
    min_load_in_cubic_meters_return_to_yard = models.FloatField(default=0)
    # min_load_in_cubic_meters_trip = models.FloatField(default=0)
     
    return_to_yard_grace = models.FloatField(default=0)         # new added
    return_to_tipping_grace = models.FloatField(default=0)      # new added

    start_date = models.DateField(default=timezone.now())
    end_date = models.DateField(default=timezone.now() + timezone.timedelta(days=365*10), null=True, blank=True)


class ThresholdNightShift(models.Model):
    rate_card_name = models.ForeignKey(RateCard, on_delete=models.CASCADE)
    threshold_amount_per_night_shift = models.FloatField(default=0)
    loading_cost_per_cubic_meter_included = models.BooleanField(default=False)
    km_cost_included = models.BooleanField(default=False)
    surcharge_included  = models.BooleanField(default=False)
    transfer_cost_included = models.BooleanField(default=False)
    return_cost_included = models.BooleanField(default=False)
    standby_cost_included = models.BooleanField(default=False)
    waiting_cost_included = models.BooleanField(default=False)
    call_out_fees_included = models.BooleanField(default=False)

    min_load_in_cubic_meters = models.FloatField(default=0)
    min_load_in_cubic_meters_return_to_yard = models.FloatField(default=0)

    return_to_yard_grace = models.FloatField(default=0)         # new added
    return_to_tipping_grace = models.FloatField(default=0)      # new added

    start_date = models.DateField(default=timezone.now())
    end_date = models.DateField(default=timezone.now() + timezone.timedelta(days=365*10), null=True, blank=True)


class Grace(models.Model):
    rate_card_name = models.ForeignKey(RateCard, on_delete=models.CASCADE)
    load_km_grace = models.FloatField(default=0)
    transfer_km_grace = models.FloatField(default=0)
    return_km_grace = models.FloatField(default=0)
    standby_time_grace_in_minutes = models.FloatField(default=0)
    chargeable_standby_time_starts_after = models.FloatField(default=0)
    waiting_time_grace_in_minutes = models.FloatField(default=0)
    chargeable_waiting_time_starts_after = models.FloatField(default=0)

    start_date = models.DateField(default=timezone.now())
    end_date = models.DateField(default=timezone.now() + timezone.timedelta(days=365*10), null=True, blank=True)

class OnLease(models.Model):
    rate_card_name = models.ForeignKey(RateCard, on_delete=models.CASCADE)
    hourly_subscription_charge = models.FloatField(default=0)
    daily_subscription_charge = models.FloatField(default=0)
    weekly_subscription_charge = models.FloatField(default=0)
    # quarterly_subscription_charge = models.FloatField(default=0)
    over_time_charge = models.FloatField(default=0) 
    surcharge_included  = models.BooleanField(default=True)
    transfer_cost_applicable = models.BooleanField(default=True)
    return_cost_applicable = models.BooleanField(default=True)
    standby_cost_per_slot_applicable = models.BooleanField(default=True)
    waiting_cost_per_minute_applicable = models.BooleanField(default=True)
    call_out_fees_applicable = models.BooleanField(default=True)
    start_date = models.DateField(default=timezone.now())
    end_date = models.DateField(default=timezone.now() + timezone.timedelta(days=365*10), null=True, blank=True)
    





    
# -----------------------------------
# Trucks section
# -----------------------------------

class AdminTruck(models.Model):
    # adminTruckNumber = models.PositiveIntegerField(validators=[MaxValueValidator(999999),MinValueValidator(100000)], unique=True)
    adminTruckNumber = models.PositiveIntegerField(unique=True)
    truckStatus = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.adminTruckNumber)


class Driver(models.Model):
    # driverId = models.IntegerField(primary_key=True, unique=True, default=generate_4digit_unique_key, editable=False)
    driverId = models.IntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=100, validators=[
        RegexValidator(
            regex=r'^\d{10}$',  # Match a 10-digit number
            message='Phone number must be a 10-digit number without any special characters or spaces.',
        ),
    ])
    email = models.CharField(max_length=200)
    password = models.CharField(max_length=50)
    
    def __str__(self) -> str:
        return str(self.driverId) + str(self.name)

class ClientTruckConnection(models.Model):
    truckNumber = models.ForeignKey(AdminTruck, on_delete=models.CASCADE)
    truckType = models.CharField(max_length=254 , choices=TRUCK_TYPE_CHOICES, default='Embedded')
    rate_card_name = models.ForeignKey(RateCard, on_delete=models.CASCADE)
    clientId = models.ForeignKey(Client, on_delete=models.CASCADE)
    clientTruckId = models.PositiveIntegerField(default=0)  
    # clientTruckId = models.PositiveIntegerField(validators=[MaxValueValidator(999999)])  
    startDate = models.DateField(default=timezone.now())  
    endDate = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.truckNumber) + str(self.clientId)
    
# -----------------------------------
# Leave section
# -----------------------------------

class NatureOfLeave(models.Model):
    reason = models.CharField(max_length=200)
    
    def __str__(self) -> str:
            return str(self.reason)

class LeaveRequest(models.Model):
    employee = models.ForeignKey(Driver, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, default=None)
    end_date = models.DateField(null=True, default=None)
    reason = models.ForeignKey(NatureOfLeave,on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Denied', 'Denied')], default='Pending')
    # Add other fields as needed

    def __str__(self):
        return f"{self.employee} - {self.start_date} to {self.end_date}"


# -----------------------------------
# Truck Gearbox section
# -----------------------------------

# INFORMATION TAB
class TruckInformation(models.Model):
    fleet = models.CharField(max_length=100)
    group = models.PositiveSmallIntegerField(default=0)
    subGroup = models.PositiveSmallIntegerField(default=0)
    vehicleType = models.CharField(max_length=100, default='', null=True, blank=True)
    serviceGroup = models.CharField(max_length=100, default='', null=True, blank=True)
    truckImg1 = models.FileField(null=True, blank=True)
    truckImg2 = models.FileField(null=True, blank=True)
    truckImg3 = models.FileField(null=True, blank=True)
    informationMake = models.CharField(max_length=100, default='', null=True, blank=True)
    informationModel = models.CharField(max_length=100, default='', null=True, blank=True)
    informationConfiguration = models.CharField(max_length=100, default='', null=True, blank=True)
    informationChassis = models.CharField(max_length=100, default='', null=True, blank=True)
    informationBuildYear = models.PositiveIntegerField(default=0)
    informationIcon = models.CharField(max_length=100, default='', null=True, blank=True)
    customFuelCard = models.CharField(max_length=100, default='', null=True, blank=True)
    customFuelCard = models.CharField(max_length=100, default='', null=True, blank=True)
    customFuelOldFleetNumber = models.CharField(max_length=100, default='', null=True, blank=True)
    customOldRego = models.CharField(max_length=100, default='', null=True, blank=True)
    customRegisteredOwner = models.CharField(max_length=100, default='', null=True, blank=True)
    customRoadsideAssistance = models.CharField(max_length=100, default='', null=True, blank=True)
    customPDDNumber = models.CharField(max_length=100, default='', null=True, blank=True)
    registered = models.BooleanField(default=True)
    registration = models.CharField(max_length=100, default='', null=True, blank=True)
    registrationCode = models.CharField(max_length=100, default='', null=True, blank=True)
    registrationSate = models.CharField(max_length=100, default='', null=True, blank=True)
    registrationDueDate = models.DateField(null=True, blank=True)
    registrationInterval = models.CharField(max_length=100, default='', null=True, blank=True)
    powered = models.BooleanField(default=False)
    engine = models.CharField(max_length=100, default='', null=True, blank=True)
    engineMake = models.CharField(max_length=100, default='', null=True, blank=True)
    engineModel = models.CharField(max_length=100, default='', null=True, blank=True)
    engineCapacity = models.CharField(max_length=100, default='', null=True, blank=True)
    engineGearBox = models.CharField(max_length=100, default='', null=True, blank=True)

# DOCUMENTS TAB
class TruckDocument(models.Model):
    tags = models.CharField(max_length=300)
    filePath = models.FileField(upload_to='static/GearBox/document')
    description = models.TextField()
    
    def __str__(self):
        return str(self.tags)
    