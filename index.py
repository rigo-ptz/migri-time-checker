import requests
import asyncio
import datetime

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
# https://migri.vihta.com/public/migri/api/scheduling/offices/438cd01e-9d81-40d9-b31d-5681c11bd974/2024/w2?end_hours=24&start_hours=0
URL = "https://migri.vihta.com/public/migri/api/scheduling/offices/{office_id}/{year}/w{week}?end_hours=24&start_hours=0"

DATETIME_FORMAT = "%Y-%m-%d %H:%M"
INPUT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def get_office_times(office_id, year, week):
    url = URL.format(office_id=office_id, year=year, week=week)
    headers = {
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
    r = requests.post(
        url=url,
        json=BODY,
        headers=headers
    )
    return r.json()["dailyTimesByOffice"]

def print_time(dailyTimes):
    for day in dailyTimes:
        for slot in day:
            number_of_queues = len(slot["resources"]);
            dateTime = datetime.datetime.strptime(slot["startTimestamp"], INPUT_DATE_FORMAT)
            slot_date = dateTime.strftime(DATETIME_FORMAT)
            print(f"Migri Helsinki: {slot_date}, windows available: {number_of_queues}")
    

async def main():
    startTime = datetime.datetime.now()
    endTime = startTime + datetime.timedelta(weeks=4)
    
    while startTime < endTime:
        year = startTime.year
        week = startTime.strftime("%V")
        future = loop.run_in_executor(None, get_office_times, OFICES["Helsinki"]["office_id"], year, week)
        dailyTimes = await future
        print_time(dailyTimes)
        startTime = startTime + datetime.timedelta(weeks=1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
