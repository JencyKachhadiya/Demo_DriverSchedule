from Account_app.models import *
from GearBox_app.models import *
from django.utils import timezone 
import datetime

# # ------------------------------
# # Admin trucks
# # ------------------------------


# # trucks = [653, 654, 783, 784, 785, 786, 787, 782, 789, 550, 551, 552, 553, 554, 700, 701, 702, 703, 707, 708, 709, 719, 722, 723, 725, 726, 727, 728, 473, 470, 730, 471, 472, 731,
# #           474, 475, 477]
trucks = [
    {'id': 1, 'adminTruckNumber': 653, 'truckStatus': False},
    {'id': 2, 'adminTruckNumber': 654, 'truckStatus': False},
    {'id': 3, 'adminTruckNumber': 783, 'truckStatus': False},
    {'id': 4, 'adminTruckNumber': 784, 'truckStatus': False},
    {'id': 5, 'adminTruckNumber': 785, 'truckStatus': False},
    {'id': 6, 'adminTruckNumber': 786, 'truckStatus': False},
    {'id': 7, 'adminTruckNumber': 787, 'truckStatus': False},
    {'id': 8, 'adminTruckNumber': 782, 'truckStatus': False},
    {'id': 9, 'adminTruckNumber': 789, 'truckStatus': False},
    {'id': 10, 'adminTruckNumber': 550, 'truckStatus': False},
    {'id': 11, 'adminTruckNumber': 551, 'truckStatus': False},
    {'id': 12, 'adminTruckNumber': 552, 'truckStatus': False},
    {'id': 13, 'adminTruckNumber': 553, 'truckStatus': False},
    {'id': 14, 'adminTruckNumber': 554, 'truckStatus': False},
    {'id': 15, 'adminTruckNumber': 700, 'truckStatus': False},
    {'id': 16, 'adminTruckNumber': 701, 'truckStatus': False},
    {'id': 17, 'adminTruckNumber': 702, 'truckStatus': False},
    {'id': 18, 'adminTruckNumber': 703, 'truckStatus': False},
    {'id': 19, 'adminTruckNumber': 707, 'truckStatus': False},
    {'id': 20, 'adminTruckNumber': 708, 'truckStatus': False},
    {'id': 21, 'adminTruckNumber': 709, 'truckStatus': False},
    {'id': 22, 'adminTruckNumber': 719, 'truckStatus': False},
    {'id': 23, 'adminTruckNumber': 722, 'truckStatus': False},
    {'id': 24, 'adminTruckNumber': 723, 'truckStatus': False},
    {'id': 25, 'adminTruckNumber': 725, 'truckStatus': False},
    {'id': 26, 'adminTruckNumber': 726, 'truckStatus': False},
    {'id': 27, 'adminTruckNumber': 727, 'truckStatus': False},
    {'id': 28, 'adminTruckNumber': 728, 'truckStatus': False},
    {'id': 29, 'adminTruckNumber': 473, 'truckStatus': False},
    {'id': 30, 'adminTruckNumber': 470, 'truckStatus': False},
    {'id': 31, 'adminTruckNumber': 730, 'truckStatus': False},
    {'id': 32, 'adminTruckNumber': 471, 'truckStatus': False},
    {'id': 33, 'adminTruckNumber': 472, 'truckStatus': False},
    {'id': 34, 'adminTruckNumber': 731, 'truckStatus': False},
    {'id': 35, 'adminTruckNumber': 474, 'truckStatus': False},
    {'id': 36, 'adminTruckNumber': 475, 'truckStatus': False},
    {'id': 37, 'adminTruckNumber': 477, 'truckStatus': False},
    {'id': 38, 'adminTruckNumber': 651, 'truckStatus': True},
    {'id': 39, 'adminTruckNumber': 652, 'truckStatus': True},

]

for truck in trucks:
    try:
        obj = AdminTruck(id =  truck['id'], adminTruckNumber = truck['adminTruckNumber'], truckStatus = truck['truckStatus'])
        # obj = AdminTruck(adminTruckNumber = truck)
        obj.save()
    except Exception as e:
        print(f"Error : {e}")


# # ------------------------------
# # Client truck connection
# # ------------------------------


def truckConnectionInsert(data):
    print(str(data))
    try:
        print(data['id'])
        adminTruckObj = AdminTruck.objects.get(pk = data['truckNumber'])
        rateCardObj = RateCard.objects.filter(pk=data['rate_card_name']).first()
        clientObj = Client.objects.get(pk = data['clientId'])
        
        clientTruckConnectionObj = ClientTruckConnection(
            truckNumber =  adminTruckObj,
            truckType =  data['truckType'],
            rate_card_name =  rateCardObj,
            clientId =  clientObj,
            clientTruckId =  data['clientTruckId'],
            startDate =  data['startDate'],
            endDate =  data['endDate']
        )
        clientTruckConnectionObj.save()
        return
    except Exception as e :
        print(f'Truck Number : {data}, {e}')
        return
    




connections = [ {'id': 692, 'truckNumber': 37, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 477, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 693, 'truckNumber': 36, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 477, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 694, 'truckNumber': 35, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 1, 'clientTruckId': 474, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 695, 'truckNumber': 34, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 731, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 696, 'truckNumber': 33, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 472, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 697, 'truckNumber': 32, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 1, 'clientTruckId': 471, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 698, 'truckNumber': 31, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 730, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 699, 'truckNumber': 30, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 1, 'clientTruckId': 470, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 700, 'truckNumber': 29, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 1, 'clientTruckId': 473, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 701, 'truckNumber': 10, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 550, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 702, 'truckNumber': 11, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 551, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 703, 'truckNumber': 12, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 552, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 704, 'truckNumber': 13, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 553, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 705, 'truckNumber': 14, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 554, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 706, 'truckNumber': 1, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 653, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 707, 'truckNumber': 2, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 654, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 708, 'truckNumber': 15, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 700, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 709, 'truckNumber': 16, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 701, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 710, 'truckNumber': 17, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 702, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 711, 'truckNumber': 18, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 703, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 712, 'truckNumber': 19, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 707, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 713, 'truckNumber': 20, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 708, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 714, 'truckNumber': 21, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 709, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 715, 'truckNumber': 22, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 719, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 716, 'truckNumber': 23, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 722, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 717, 'truckNumber': 24, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 723, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 718, 'truckNumber': 25, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 725, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 719, 'truckNumber': 26, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 726, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 30)},
    {'id': 720, 'truckNumber': 27, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 727, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 721, 'truckNumber': 28, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 728, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 722, 'truckNumber': 8, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 782, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 723, 'truckNumber': 3, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 784, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 724, 'truckNumber': 4, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 784, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 725, 'truckNumber': 5, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 785, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 726, 'truckNumber': 6, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 786, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 727, 'truckNumber': 7, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 784, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 728, 'truckNumber': 9, 'truckType': 'Embedded', 'rate_card_name': 1, 'clientId': 1, 'clientTruckId': 789, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 729, 'truckNumber': 33, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 1, 'clientTruckId': 472, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 730, 'truckNumber': 36, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 1, 'clientTruckId': 475, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 731, 'truckNumber': 37, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 1, 'clientTruckId': 477, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 732, 'truckNumber': 14, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 1, 'clientTruckId': 554, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 733, 'truckNumber': 11, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 2, 'clientTruckId': 551, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 734, 'truckNumber': 38, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 1, 'clientTruckId': 651, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 735, 'truckNumber': 2, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 1, 'clientTruckId': 654, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 736, 'truckNumber': 22, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 1, 'clientTruckId': 719, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 737, 'truckNumber': 22, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 1, 'clientTruckId': 719, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 738, 'truckNumber': 23, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 1, 'clientTruckId': 722, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 739, 'truckNumber': 24, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 1, 'clientTruckId': 723, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 740, 'truckNumber': 31, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 1, 'clientTruckId': 730, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 741, 'truckNumber': 34, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 1, 'clientTruckId': 731, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)},
    {'id': 742, 'truckNumber': 115, 'truckType': 'Casual', 'rate_card_name': 3, 'clientId': 1, 'clientTruckId': 788, 'startDate': datetime.date(2023, 1, 1), 'endDate': datetime.date(2023, 12, 31)}
    ]

for connection in connections:
    truckConnectionInsert(connection)
    
# def run():
#     data = ClientTruckConnection.objects.all().values()

#     with open('pastTrip_entry.txt','a') as f:
        
#         for i in data:
#             f.write('\n' + str(i))
    