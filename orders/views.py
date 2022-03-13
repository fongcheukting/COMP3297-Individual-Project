from django.shortcuts import render
import json
import requests
import ast
import datetime
# Create your views here.
def QDD(request):
    connected = True
    #retrieve API2
    try:
        API2 = {
            "resource": "http://www.chp.gov.hk/files/misc/no_of_confines_by_types_in_quarantine_centres_eng.csv",
            "section": 1,
            "format": "json",
            "filters": []
        }
        par2 = {'q': json.dumps(API2)}
        r2 = requests.get('https://api.data.gov.hk/v2/filter', params=par2)
    except:
        connected = False
    API2_string = r2.text
    #replace column's title to fit the html template
    API2_string = API2_string.replace("As of date", "date")
    API2_string = API2_string.replace("As of time", "time")
    API2_string = API2_string.replace("Current number of non-close contacts", "non_close_contacts")

    API2_data = ast.literal_eval(API2_string)[-1] #only use the most recent day
    most_recent_day = API2_data["date"]

    # check if the most recent data is within the past 7 days
    has_data = True
    last_week = datetime.date.today() - datetime.timedelta(days=6)
    #convert dd/mm/yyyy to datetime for the most_recent_day
    format_str = '%d/%m/%Y'
    datetime_obj = datetime.datetime.strptime(most_recent_day, format_str).date()
    if datetime_obj < last_week:
        has_data = False

    #retrieve API1
    try:
        API1 = {
            "resource": "http://www.chp.gov.hk/files/misc/occupancy_of_quarantine_centres_eng.csv",
            "section": 1,
            "format": "json",
            "filters": [
                [1, "eq", most_recent_day]
            ]
        }
        par1 = {'q': json.dumps(API1)}
        r1 = requests.get('https://api.data.gov.hk/v2/filter', params=par1)
    except:
        connected = False

    API1_string = r1.text
    #replace column's title to fit the html template
    API1_string = API1_string.replace("Quarantine centres", "name")
    API1_string = API1_string.replace("Capacity (unit)", "capacity")
    API1_string = API1_string.replace("Current unit in use", "used_unit")
    API1_string = API1_string.replace("Ready to be used (unit)", "available_unit")
    API1_string = API1_string.replace("Current person in use", "person")
    API1_data = ast.literal_eval(API1_string)
    #sort API1 with respect to highest availability centres
    highest_3centres = sorted(API1_data, key=lambda d: d['available_unit'], reverse=True)[:3]
    #calculate important data
    total_occupied_units = 0
    total_available_units = 0
    total_quarantined_person = 0
    for centre in API1_data:
        total_occupied_units += centre["used_unit"]
        total_available_units += centre["available_unit"]
        total_quarantined_person += centre["person"]

    data_consistent = True
    API2_total_case = API2_data["non_close_contacts"] + API2_data["Current number of close contacts of confirmed cases"]
    if API2_total_case != total_quarantined_person:
        data_consistent = False



    context = {"highest_3centres": highest_3centres,
               "API2": API2_data,
               "connected": connected,
               "has_data": has_data,
               "total_occupied_units": total_occupied_units,
               "total_available_units": total_available_units,
               "total_quarantined_person": total_quarantined_person,
               "data_consistent": data_consistent}

    return render(request, 'QDD.html', context=context)
