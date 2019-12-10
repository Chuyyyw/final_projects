import pygeodesy.ellipsoidalVincenty as ev

class user(object):
    # TODO: create values for each variables based on the Monte Carlo
    def __init__(self, user_line):

        self.user_id = user_line[0]   ## User id could be user also as the order
        self.role = user_line[1]      ## role as rider or driver： Bernoulli distribution,
        self.start = string_to_list(user_line[3], "()", ",")   ## this is the start location of user, used for distance calculation
        self.destination = string_to_list(user_line[4], "()", ",")  ## this is the end location of user(Palo Alto, Sunnyvale, Santa Clara, or Pleasanton)
                                                                    ## Palo Alto(37.468319, -122.143936), Mountain View (37.386051, -122.083855),
                                                                    ## Redwood City(37.487846, -122.236115)
        slots = string_to_list(user_line[2], "[]", ",")
        self.start_slot = int(slots[0])   ## user selected time window start
        self.end_slot = int(slots[-1])    ## user selected time window end, from 3 intervals, more intervals more possibility to be mached
                                          ## 7:30 - 9:30 peak time, 8:00 most serious traffic time

    def toString(self):
        return self.user_id + '| ' + self.role + '| ' + str(self.start_slot) + '| ' + str(self.end_slot) + '| ' + \
               self.start[0] + ', ' + self.start[1] + '| ' + self.destination[0] + ', ' + self.destination[1]


def string_to_list(string, sign, separator):
    string = string.strip(sign)
    list = string.split(separator)
    return list

def match_pair(driver, rider, interval, driver_prefer_time):
    # TODO: Calculate distance from the coordinations of riders and drivers...
    d1 = ev.LatLon(driver.start[1], driver.start[0])
    r1= ev.LatLon(rider.start[1], rider.start[0])
    pickup_distance =d1.distanceTo(r1)*0.00062137 #in miles
    pickup_time = pickup_distance*7
    pickup_slots = pickup_time/interval

    d2 = ev.LatLon(driver.destination[1], driver.destination[0])
    r2= ev.LatLon(rider.destination[1], rider.destination[0])
    dropoff_distance =r2.distanceTo(d2)*0.00062137 #in miles
    dropoff_time = dropoff_distance*7
    dropoff_slots = dropoff_time/interval

    driver_start_slot = driver.start_slot + pickup_slots
    driver_end_slot = driver.end_slot  + pickup_slots
    driver_increase_slots = pickup_slots + dropoff_slots
    if driver_end_slot > rider.start_slot-1 and driver_start_slot-1 <= rider.end_slot \
            and driver_increase_slots<=driver_prefer_time:
        return 'matched'
    else:
        return 'unmatched'


filepath=['output10.txt',]

unmatched_drivers = []
unmatched_riders = []
matches = []
all_users=[]
user_number = 0
for filename in filepath:
    with open(filename, 'r') as users:
        next(users)
        for line in users:
            #line = users.readline()
            user_row = line.split('|')
            user_features = [x.strip() for x in user_row][:5]
            user_object = user(user_features)
            user_number+=1
            all_users.append(user_object)
            # print(user_object.toString())
            # print(user_object.start)
            if user_object.role == 'driver':
                driver = user_object
                matched = False

                for unmatched_rider in unmatched_riders:
                    match_result = match_pair(driver, unmatched_rider, 15, 4)
                    if match_result == 'matched':
                        new_pair = [driver, unmatched_rider]
                        matches.extend(new_pair)
                        unmatched_riders.remove(unmatched_rider)
                        matched = True
                        break
                if matched == False:
                    unmatched_drivers.append(driver)
            else:
                rider = user_object
                matched = False

                for unmatched_driver in unmatched_drivers:
                    match_result = match_pair(unmatched_driver, rider, 15, 4)
                    if match_result == 'matched':
                        new_pair = [unmatched_driver, rider]
                        matches.extend(new_pair)
                        unmatched_drivers.remove(unmatched_driver)
                        break
                if matched == False:
                    unmatched_riders.append(rider)

match_rate = len(matches)/user_number
print(match_rate, len(all_users), user_number)




