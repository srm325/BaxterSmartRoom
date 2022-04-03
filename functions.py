def get_index(i, data, user, care_area, emr_room):
    if data[user][care_area][emr_room] != 1:
        room_n = emr_room
        n_other_pumps = 0 #number of pumps counted so far that are not in this room
        for n in range(room_n - 1):
            n_other_pumps += len(data[user][care_area][n+1]["pumps"])
        pump_ind = i + 1 - n_other_pumps #room dependent pump index
    else:
        pump_ind = i + 1

    return pump_ind

def function(user, care_area): #user and care_area are strings

    # --------------------------------------------------------------------------
    # load data
    # --------------------------------------------------------------------------
    emr = pd.read_csv('emr.csv')
    pumps = pd.read_csv('pumps.csv')
    dlib = pd.read_csv('drug_library.csv')
    alib = pd.read_csv('alarm_flagging.csv')

    # --------------------------------------------------------------------------
    # auto alarm detection
    # --------------------------------------------------------------------------
    human_alerts = []
    alerts = []

    for i in range(len(pumps.pumpID)):
        drug_name = pumps.drug[i]

        j = np.where(dlib.drug == drug_name)[0][0] #dlib index of the drug
                                                   #[0][0] is there bc its a data
                                                   #type conversion

        if pumps.currentRate[i] > dlib.maxRate[j]:
            human_alerts.append('alert!' + ' pump: ' + str(emr.pumpID[i]) + '. importance: tbd')
            alerts.append(emr.pumpID[i])

    # --------------------------------------------------------------------------
    # generate JSON formatted data for front-end
    # --------------------------------------------------------------------------
    data = dict() #pre-define the variable data as a dictionary
    counter = 0 #counts the number of pumps assigned

    for i in range(len(pumps.pumpID)):
        while True:
            if user in data:
                currentPosition = data[user]
                if care_area in currentPosition:
                    currentPosition = currentPosition[care_area]
                    if int(emr.room[i]) in currentPosition:
                        currentPosition = currentPosition[int(emr.room[i])]
                        currentPosition = currentPosition["pumps"]
                        pump_ind = get_index(i, data, user, care_area, int(emr.room[i]))
                        if pump_ind in currentPosition:
                            currentPosition = currentPosition[pump_ind]
                            break
                        else:
                            data[user][care_area][int(emr.room[i])]["pumps"][pump_ind] = {
                            "pumpID" : int(pumps.pumpID[i]),
                            "drug" : pumps.drug[i],
                            "currentRate" : float(pumps.currentRate[i]),
                            "startVolume" : pumps.drug[i],
                            "alarm" : int(pumps.alarm[i]),
                            "alarm_severity" : int(random.randint(0, 3)),
                            "alarm_text" : "No alarm"
                            }
                    else:
                        data[user][care_area][int(emr.room[i])] = {
                        "patientID" : int(emr.patientID[i]),
                        "name" : emr.patient[i],
                        "age" : int(emr.age[i]),
                        "sex" : emr.sex[i],
                        "n_pumps" : "tbd",
                        "pumps" : {}
                        }
                else:
                    data[user][care_area] = {}
            else:
                data[user] = {
                "name" : "Tram Nguyen", #change this after you create user database
                "password" : 123456,
                "n_patients" : len(list(set(emr.patient))) #total number of pumps in care area
                }

    return alerts, human_alerts, data