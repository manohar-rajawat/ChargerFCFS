import psycopg2
import datetime
import sys
from collections import deque
from pprint import pprint
DATABASE_URL = 'postgres://jquhqgyhylloea:c80fe3522ab54123e20fbc097cd62c57bf3c4d78302302bd083d67d76940ffe6@ec2-54-211-160-34.compute-1.amazonaws.com:5432/dcia1g3rroe5u7'


class Vehicle:
    def __init__(self, id, arrivalTime, batteryStatus, requestedStatus, batteryCapacity, requestedPower, departureTime):
        self.id = id,
        self.arrivalTime = arrivalTime
        self.batteryStatus = batteryStatus
        self.requestedStatus = requestedStatus
        self.batteryCapacity = batteryCapacity
        self.requestedPower = requestedPower
        self.departureTime = departureTime
        self.chargingEndTime = None


class FCFS:
    # This is the main queue
    entryCharger = 1
    queueList = {
        1: {
            'idle': None,
            'power': 0,
            'vehicle': None,
            'endTime': None,
            'queue': None
        },
        2: {
            'idle': None,
            'power': 0,
            'vehicle': None,
            'endTime': None,
            'queue': None,
        },
        3: {
            'idle': None,
            'power': 0,
            'vehicle': None,
            'endTime': None,
            'queue': None,
        },
        4: {
            'idle': None,
            'power': 0,
            'vehicle': None,
            'endTime': None,
            'queue': None,
        },
        5: {
            'idle': None,
            'power': 0,
            'vehicle': None,
            'endTime': None,
            'queue': None,
        },
        6: {
            'idle': None,
            'power': 0,
            'vehicle': None,
            'endTime': None,
            'queue': None,
        },
        7: {
            'idle': None,
            'power': 0,
            'vehicle': None,
            'endTime': None,
            'queue': None,
        }
    }
    length = len(queueList)

    def getQuery(self, query):
        connection = None
        try:
            connection = psycopg2.connect(DATABASE_URL).cursor()
            connection.execute(query)
            return connection.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if connection is not None:
                connection.close()

    def updateStatus(self, charger, status):
        connection = None
        try:
            query = 'update charger set idle = ' + \
                str(status)+' where id='+str(charger)+';'
            connection = psycopg2.connect(DATABASE_URL)
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            connection.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if connection is not None:
                connection.close()

    def addVehicleToCharger(self, charger, vehicle, addToQueue=None):
        requiredMinutes = int((vehicle.requestedPower * 60) /
                              self.queueList[charger]['power'])
        expectedDepartureTime = datetime.timedelta(
            minutes=requiredMinutes) + vehicle.arrivalTime
        if addToQueue:
            remainingTime = (
                self.queueList[charger]['endTime'] - vehicle.arrivalTime).seconds
            expectedDepartureTime = datetime.timedelta(
                seconds=remainingTime) + self.queueList[charger]['endTime']
        departureTime = vehicle.departureTime.split(':')
        if vehicle.arrivalTime.replace(hour=int(departureTime[0]), minute=int(departureTime[1])) >= expectedDepartureTime:
            if not addToQueue:
                self.queueList[charger]['vehicle'] = vehicle
            else:
                self.queueList[charger]['queue'].append(vehicle)
            self.queueList[charger]['idle'] = False
            self.queueList[charger]['endTime'] = expectedDepartureTime
            vehicle.chargingEndTime = expectedDepartureTime
            return True
        else:
            return False

    def attachToWaitingList(self, charger, vehicle):
        if self.queueList[charger]['queue'] == None:
            self.queueList[charger]['queue'] = deque()
        return self.addVehicleToCharger(charger, vehicle, True)

    def lookWaitingList(self, vehicle):
        lessWaitingTime, attachCharger = self.queueList[self.entryCharger]['endTime'], 1
        for key in self.queueList.keys():
            if self.queueList[key]['endTime'] < lessWaitingTime:
                lessWaitingTime = self.queueList[key]['endTime']
                attachCharger = key
        return self.attachToWaitingList(attachCharger, vehicle)

    def assignCar(self, vehicle):
        idleCharger = self.getIdleStation()
        if idleCharger != None:
            return self.addVehicleToCharger(idleCharger, vehicle)
        else:
            return self.lookWaitingList(vehicle)

    def setupLocalData(self, data):
        for charger in data:
            if charger[0] in self.queueList:
                self.queueList[charger[0]]['power'] = charger[1]
                self.queueList[charger[0]]['idle'] = charger[2]
        for i in self.queueList:
            print(i, self.queueList[i])

    def getIdleStation(self):
        for i in self.queueList.keys():
            if self.queueList[i]['idle']:
                return i
        return None

    def showActiveVehicle(self):
        charger = int(input("Enter the charger number: "))
        if charger <= self.length:
            if not self.queueList[charger]['idle']:
                pprint(vars(self.queueList[charger]['vehicle']))
            else:
                print("There are no vehicles charging yet!")
        else:
            print("Please enter a valid charger")

    def showActiveQueue(self):
        charger = int(input("Enter the charger number: "))
        if charger <= self.length:
            queueList = self.queueList[charger]['queue']
            if not queueList:
                print("There are no queue on this charger")
            else:
                for vehicle in queueList:
                    pprint(vars(vehicle))
        else:
            print("Please enter a valid charger")


if __name__ == "__main__":
    station = FCFS()
    station.setupLocalData(station.getQuery('select * from charger;'))
    input_options = {
        1: ['Please Enter Vehicle Id: ', None],
        2: ['Please Enter Battery Status: ', None],
        3: ['Please Enter Requested Status: ', None],
        4: ['Please Enter Battery Capacity: ', None],
        5: ['Please Enter Departure Date Time: ', None],
    }
    menu_options = {
        1: 'Add a vehicle',
        2: 'Show charger details',
        3: 'Show charger active car',
        4: 'Show charger queue',
        5: 'Exit',
    }

    def print_addcar():
        for key in input_options.keys():
            print(key, '--', input_options[key][0])
            input_options[key][1] = input()
        powerRequested = (
            int(input_options[3][1]) - int(input_options[2][1])) * int(input_options[4][1])/100
        vehicle = Vehicle(
            input_options[1][1], datetime.datetime.now(
            ), input_options[2][1], input_options[3][1],
            input_options[4][1], powerRequested, input_options[5][1])
        if station.assignCar(vehicle):
            print("Car Added")
        else:
            print("Car Not Added")

    def show_charger():
        for key in station.queueList.keys():
            print(station.queueList[key])

    def print_menu():
        for key in menu_options.keys():
            print(key, '--', menu_options[key])

    while True:
        print_menu()
        key = input('Enter your choice : ')
        try:
            intKey = int(key)
            if intKey < 0 or intKey > 5 or intKey == 5:
                raise Exception()
            else:
                if intKey == 1:
                    print_addcar()
                elif intKey == 2:
                    show_charger()
                elif intKey == 3:
                    station.showActiveVehicle()
                elif intKey == 4:
                    station.showActiveQueue()
        except Exception as e:
            print(e)
            print('Thank you!')
            sys.exit(0)
