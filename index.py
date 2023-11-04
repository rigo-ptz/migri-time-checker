import requests
import asyncio
import datetime
import os
import schedule
import time

OFICES = {
    "Helsinki": {
        "office_id": "438cd01e-9d81-40d9-b31d-5681c11bd974",
        "hours_start": 0,
        "hours_end": 24
    }
}
SERVICE_ID = "3e03034d-a44b-4771-b1e5-2c4a6f581b7d"

SESSION_ID = "f33307b2-f2ac-452d-a95b-1ff9ac126514"
BODY = {
    "serviceSelections": [
        {
            "values": [
                SERVICE_ID
            ]
        }
    ],
    "extraServices": [ ]
}
URL = "https://migri.vihta.com/public/migri/api/scheduling/offices/{office_id}/{year}/w{week}?end_hours=24&start_hours=0"
HEADERS = {
        "authority": "migri.vihta.com",
        "Vihta-Session": SESSION_ID,
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://migri.vihta.com",
        "Referer": "https://migri.vihta.com/public/migri/",
        "Accept": "application/json, text/plain, */*",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua": 'Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99',
        "Sec-Ch-Ua-Platform": "macOS",
        "authority": "migri.vihta.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }

DAY_DATEIME_FORMAT = "%d-%m-%Y"
SLOT_DATETIME_FORMAT = "%H:%M"
INPUT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

def display_notification(message, title=None, subtitle=None, soundname=None):
    titlePart = ""
    subtitlePart = ""
    soundnamePart = ""
    
    if (not title is None):
        titlePart = f"with title \"{title}\""
    
    if (not subtitle is None): 
        subtitlePart = f"subtitle \"{subtitle}\""
    
    if (not soundname is None): 
        soundnamePart = f"sound name \"{soundname}\""

    appleScriptNotification = f"display notification \"{message}\" {titlePart} {subtitlePart} {soundnamePart}"
    os.system(f"osascript -e '{appleScriptNotification}'")

def get_office_times(office_id, year, week):
    print(f"Get office times for year: {year}, week: {week}")
    url = URL.format(office_id=office_id, year=year, week=week)
    
    r = requests.post(
        url=url,
        json=BODY,
        headers=HEADERS
    )
    return r.json()["dailyTimesByOffice"]

async def print_time(daily_times):
    office_name_printed = False
    
    for index, day in enumerate(daily_times):
        if (len(day) == 0):
            continue
        elif office_name_printed != True:
            print("Migri Helsinki")
            office_name_printed = True
            display_notification(title="Migri Time Checker", message="Time found")
            
        day_date = datetime.datetime.strptime(day[0]["startTimestamp"], INPUT_DATE_FORMAT)
        day_date_formatted = day_date.strftime(DAY_DATEIME_FORMAT)
        print(f"    Day: {day_date_formatted}")
        for slot in day:
            number_of_queues = len(slot["resources"]);
            date_time = datetime.datetime.strptime(slot["startTimestamp"], INPUT_DATE_FORMAT)
            slot_time = date_time.strftime(SLOT_DATETIME_FORMAT)
            print(f"        Time: {slot_time}, windows available: {number_of_queues}")

async def main(loop):
    startTime = datetime.datetime.now()
    endTime = startTime + datetime.timedelta(weeks=4)
    
    tasks = set()
    num_of_coroutines = 3
    
    while startTime < endTime:
        if len(tasks) >= num_of_coroutines:
            _done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        
        year = startTime.year
        week = startTime.strftime("%V")
        
        tasks.add(
            loop.create_task(
                print_time(
                    get_office_times(OFICES["Helsinki"]["office_id"], year, week)
                )
            )
        )
        
        startTime = startTime + datetime.timedelta(weeks=1)

    await asyncio.wait(tasks)
    
def scheduled():
    print("Scheduled started")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))

if __name__ == "__main__":
    scheduled()
    schedule.every(2).minutes.do(scheduled)
    while True:
        schedule.run_pending()
        time.sleep(1)
