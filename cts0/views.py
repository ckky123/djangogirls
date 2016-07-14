from django.shortcuts import render
from django.http import HttpResponse
from collections import OrderedDict
import re
import requests
import threading
import pymysql
import time
# Create your views here.


def index(request):
    return render(request, 'cts0/index.html')


#def index(request):
#    return HttpResponse(u"欢迎光临 自强学堂!")

def QueryOneWeek(request):
    Ori = request.GET['from'];
    Dest = request.GET['to'];
    
    cheapest = 10000000;
    
    results = []
    cheapestlist = []
    QueryContDays(Ori, Dest, 7, results)
    for data in results:
        data['Price'] = float(data['Price'])
        if data['Price'] != 0.0 and data['Price'] < cheapest:
            cheapest = data['Price']
           
    for data in results:
        if data['Price'] == cheapest:
            cheapestlist.append(data)
    cheapestlist = sorted(cheapestlist, key=lambda k: k['Date'])  
    
    return render(request, 'cts0/cheapest.html', {'Ori' : Ori, 'Dest' : Dest, 'results' : cheapestlist})
  
def QueryOneDay (Origin, Destination, Month, Day, rs, results):
    url = "https://www.virgintrains.co.uk/api/sitecore/Ec/ValidateStations?fromStationCode=" + Origin + "&toStationCode=" + Destination
    maxRetry = 10
    hour = 0
    minute = 0
    QueryPayload = {
    'onlc':'0000',
    'dnlc':'0000',
    'outm':'01',
    'outd':'01',
    'outh':'00',
    'outmi':'00',
    'outda':'y',
    'nad':'1',
    'nch':'0',
    'cc':'VTWCReDir'
    }
    GetIdPayload = {
    'id0':"00000000",
    'cnt':'1',
    'resend':'Y'
    }
    ExtendPayload = {
    'journeyDir':'O',
    'extensionDir':'L'
    }
    user_agent = {
    'User-agent': 'Mozilla/5.0'
    }

    print ("Start Query :", Origin, "To", Destination, Month, "/", Day)
    #rs = requests.session()
    Response = rs.get(url)
    if Response.status_code != 200:
        print ("status code : ", Response.status_code)
        return False
    else:
        search_code = Response.json()
        if search_code['success'] == True:
            QueryPayload['onlc'] = search_code['stationFromNLCCode']
            QueryPayload['dnlc'] = search_code['stationToNLCCode']
            QueryPayload['outm'] = "%02d" % Month
            QueryPayload['outd'] = "%02d" % Day
            QueryPayload['outh'] = "%02d" % hour
            QueryPayload['outmi'] = "%02d" % minute 
            Response = rs.get("https://tickets.virgintrainseastcoast.com/ec/en/Landing/TISMobile.aspx", params=QueryPayload, headers = user_agent)
            
            if Response.status_code != 200:
                print ("status code : ", Response.status_code)
                return False
            else:
                QueryID = re.findall("ResultsController\(\[[0-9]{1,}\]", Response.text)[0]
                QueryID = re.findall("[0-9]{1,}", QueryID)[0]
                GetIdPayload['id0'] = QueryID
                retry = 0
                while True:
                    try:
                        Response = rs.get("http://tickets.virgintrainseastcoast.com/ec/en/JourneyPlanning/CheckForFTAEnquiryCompletion", params=GetIdPayload, headers = user_agent)
                        
                        if Response.status_code != 200:
                            retry = retry + 1
                            if retry <= maxRetry:
                                print ("Retry", retry, ":", Origin, "To", Destination, Month, "/", Day)
                                continue
                            else:
                                return False
                        else:
                            query_json = Response.json()
                            if query_json['complete'] == True: 
                                if query_json['allServicesDone'] == True:
                                    break
                                else:
                                    Response = rs.get("http://tickets.virgintrainseastcoast.com/ec/en/JourneyPlanning/StartFTAEnquiryExtension", params=ExtendPayload, headers = user_agent)
                                    if Response.status_code != 200:
                                        retry = retry + 1
                                        if retry <= maxRetry:
                                            print ("Retry", retry, ":", Origin, "To", Destination, Month, "/", Day)
                                            continue
                                        else:
                                            return False
                                    else:
                                        query_json = Response.json()
                                        GetIdPayload['id0'] = query_json['enquiryIds'][0]
                            else:
                                time.sleep(0.5)
                    except:
                        retry = retry + 1
                        if retry <= maxRetry:
                            print ("Retry", retry, ":", Origin, "To", Destination, Month, "/", Day)
                            continue
                        else:
                            return False
                
                if Response.status_code == 200:
                    print ("Start Write :", Origin, "To", Destination, Month, "/", Day)
                    sql = "INSERT INTO `Train` (`PrimaryKey`, `Origin`, `Destination`, `DepartDate`, `ArriveDate`, `DepartTime`, `ArriveTime`, `Standard`, `First`, `RecordTime`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP);"
                    db = pymysql.connect(host="myeusql.dur.ac.uk", user="kqpm28", passwd="rudd52er", db="Ikqpm28_CTS", charset='utf8')
                    #db = pymysql.connect(host="localhost", user="root", passwd="z1z1z1z1", db="Ikqpm28_CTS", charset='utf8')
                    cursor = db.cursor()
                
                    query_json = Response.json(object_pairs_hook=OrderedDict)
                    for i in query_json['outwardServices']:
                        Depart = (query_json['outwardServices'][i]['dTime'].replace('@', '') + ':00').split(' ')
                        Arrive = (query_json['outwardServices'][i]['aTime'].replace('@', '') + ':00').split(' ')
                        DepartDate = Depart[0]
                        ArriveDate = Arrive[0]
                        DepartTime = Depart[1]
                        ArriveTime = Arrive[1]
                        Standard = "0.0"
                        First = "0.0"
                        for j in range (0, len(query_json['outwardServices'][i]['serviceFares'])):
                            fgId = query_json['outwardServices'][i]['serviceFares'][j]['fgId']
                            if fgId == '400':
                                Standard = str(float(query_json['outwardServices'][i]['serviceFares'][j]['totFare']) / 100)
                            if fgId == '200':
                                First = str(float(query_json['outwardServices'][i]['serviceFares'][j]['totFare']) / 100)
                        cursor.execute(sql, (Origin, Destination, DepartDate, ArriveDate, DepartTime, ArriveTime, Standard, First))
                        results.append({'Date' : DepartDate, 'Time' : DepartTime, 'Price' : Standard})
                        db.commit()
    return True

def QueryContDays (Origin, Destination, Days, results):
    threads = []
    QueryDay = time.time()
    for i in range (Days):
        QueryDay = QueryDay + 86400
        threads.append(threading.Thread(target=QueryOneDay,args=(Origin, Destination, time.localtime(QueryDay).tm_mon, time.localtime(QueryDay).tm_mday, requests.session(), results)))
    for t in threads:  
        time.sleep(0.1)  
        t.start()
    for t in threads:  
        t.join() 

