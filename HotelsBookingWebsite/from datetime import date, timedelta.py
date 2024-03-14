from pymongo import MongoClient
from datetime import datetime,timedelta

client = MongoClient("mongodb+srv://hisham3214:Hisho76403405@351project.khomprh.mongodb.net/test")
db = client.HotelBookings
dt1 = datetime.strptime("2022-11-10","%Y-%m-%d")
dt2 = datetime.strptime("2022-11-15", "%Y-%m-%d")
dater=[]
def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

#i=0

for dt in daterange(dt1, dt2):
    dater.append((dt.strftime("%Y-%m-%d")))
    #i+=1
print(dater)