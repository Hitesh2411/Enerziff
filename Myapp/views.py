from django.shortcuts import render,redirect
from .models import Register,lpg_Customer_Table,transaction_details,Admin,c2bAmountCheck,userHistory,usersLocationInfo,userLowBalanceCheck
from .models import usageHistory,GasPrices,customerIssues,Admin,Lpg_Status_Infos,Area_Lead
from django.http import HttpResponse,JsonResponse
from datetime import datetime,timedelta
from django.utils.safestring import mark_safe
from django.utils import timezone
import csv
import time
import requests
from requests.auth import HTTPBasicAuth
import json

from . mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword
from django.views.decorators.csrf import csrf_exempt
import folium
### Paygo Imports###
import json
from json import dumps
import schedule
import time
import pika
import threading
import paho.mqtt.client as mqtt
import ssl, time, inspect, os, sys
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from django.db.models import Count,Sum
from django.core.mail import send_mail
from django.conf import settings
# from twilio.rest import Client 

from xhtml2pdf import pisa
# Create your views here.
from django.template.loader import get_template
from django.http import FileResponse
import os
from django.core.mail import EmailMessage
import io
from django.template import Context
import random
import secrets,string

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0, parentdir)

from . server_simulator import SingleDeviceServerSimulator, OPAYGOShared
from datetime import datetime, timedelta
import codecs
from django.shortcuts import redirect, reverse
global number
bal_lpg = 0

broker_address="driver.cloudmqtt.com"
serial_no =  " "

QUEUE_THREADS = 1
#
inDevice=  "data/320000001/server"
outDevice= "data/320000001/customer"
#outDevice= "/data/"+serial_no+"/customer"

##print("inDevice Topic: "+inDevice)
##print("")
##print("outDevice Topic: "+outDevice)
##print("")

##print ('  ')


#------------------ MQTT ------------------------------
def on_connect(client, userdata, flags, rc):
    #print("@@@@@@@@@@@@@@@@@",rc,inDevice)
    if rc == 0:
        #print("MQTT: Connected")
        ret, mid = client.subscribe(inDevice)
        if ret == 0:
        
           #print("MQTT: Subscribed to topic : "+inDevice)
            pass
        else:
            
           #print("MQTT: Error subscribing to topic : "+inDevice)
            pass

    else:
        #print("MQTT: Connection failed to MQTT broker= "+rc)
        client.loop_stop()
        exit(1)




def on_disconnect(client, userdata, rc):
   pass
   ###print("client disconnected ok")



def mqttFromDeviceCB(client, userdata, message):

    msg = message.payload
    Time_Value=datetime.now()
    Time_Value=timezone.make_aware(Time_Value)
    Current_Time=Time_Value.strftime("%Y-%M-%D %H:%M:%S")
    print("present date and time",Time_Value)
    

    # ##print("mqttFromDeviceCB-", threading.currentThread().getName() )

    # ##print("Data received from Device "+str(message.payload))
    print(" [x] Received %r" %msg)
    # ##print(type(msg))
    # # insert into database
    val=json.loads(msg)
    print(val)
    ###print("value",val)
    #val=json.loads(message.payload.decode())
    if "GAS_VALVE" in val:
        s_no = val['SERIAL_NUMBER']
        Valve_Status=val['GAS_VALVE']
        print(s_no,Valve_Status)
        if Valve_Status:
                Valve_Update=lpg_Customer_Table.objects.get(SERIAL_NUMBER=s_no)
                Valve_Update.GAS_VALVE=True
                Valve_Update.save()
                Valve_Update2=Lpg_Status_Infos.objects.get(SERIAL_NUMBER=s_no)
                Valve_Update2.VAlVE_TIME=Time_Value
                Valve_Update2.save()
    elif "BATTRY_STATUS" in val:
        s_no = val['SERIAL_NUMBER']
        Bat_Status=val['BATTRY_STATUS']
        if Bat_Status:
                Bat_Update=lpg_Customer_Table.objects.get(SERIAL_NUMBER=s_no)
                Bat_Update.BAT_STATUS=1
                Bat_Update.save()
                Bat_Update2=Lpg_Status_Infos.objects.get(SERIAL_NUMBER=s_no)
                Bat_Update2.BATTERY_TIME=Time_Value
                Bat_Update2.save()
    elif "DEV_STATUS" in val:
        s_no = val['SERIAL_NUMBER']
        Dev_Status=val['DEV_STATUS']
        if Dev_Status:
                Dev_Update=lpg_Customer_Table.objects.get(SERIAL_NUMBER=s_no)
                Dev_Update.DEV_STATUS=True
                Dev_Update.DEV_TIME=Time_Value
                Dev_Update.save()
    elif "GAS_LEAK" in val:
        s_no = val['SERIAL_NUMBER']
       
        print('s_no',s_no)
        bal_amount = val['BAL_AMOUNT']
        bal_gas = val['BAL_LPG']
        gas_leak = val['GAS_LEAK']
        # gas_valve = val['GAS_VALVE']
        gas_tamper = val['TAMPER']
        latitude = val['LATITUDE']
        longitude = val['LONGITUDE']
        # End added code here
        x2=datetime.now()
        val="-"
        val2=":"
        date2=str(x2.year)+val+str(x2.month)+val+str(x2.day)
        time2=str(x2.hour)+val2+str(x2.minute)+val2+str(x2.second)                    
        nameValue=lpg_Customer_Table.objects.filter(SERIAL_NUMBER=s_no)
        print("serialnumber and namevalues data",s_no,nameValue)
        nameValue=nameValue.values()
        ##print("the nnamevalue is",nameValue)
        ## Here we are storing usage history. If the values already present we are not storing
        if nameValue:
            username=nameValue[0]['NAME']
            usagevaluePresent=usageHistory.objects.all().values()
            try:
                if(usagevaluePresent):
                    if(nameValue[0]['BAL_AMOUNT']!=bal_amount):
                        usageHistoryvalues= usageHistory(SerialNumber=s_no,Name=username,DATE=date2,Time=time2,BAL_LPG=bal_gas,
                                         BAL_AMOUNT=bal_amount,Battery="null",Others="null")
                        usageHistoryvalues.save()
                    else:
                        #print("the user already present")
                        pass
                else:
                    usageHistoryvalues= usageHistory(SerialNumber=s_no,Name=username,DATE=date2,Time=time2,BAL_LPG=bal_gas,
                                         BAL_AMOUNT=bal_amount,Battery="null",Others="null")
                    usageHistoryvalues.save()
            except:
                #print("some error is coming ")
                pass

        #if gas_leak == 0:
        if gas_leak == 1:
            #leak_status = False
            leak_status = True
        else:
            #leak_status = True
            leak_status = False
        # if gas_valve == 0:
        #     valve_status = False
        # else:
        #     valve_status = True
        #if gas_tamper == 0:
        if gas_tamper == 1:
            tamper_status = False
        else:
            tamper_status = True
        try:
            ###print("fetching data....",s_no)
            a=lpg_Customer_Table.objects.get(SERIAL_NUMBER=s_no)
            ###print("aaaaaa",a)
            a.GAS_LEAK = leak_status
            # a.GAS_VALVE  = valve_status
            a.TAMPER = tamper_status
            a.BAL_LPG = bal_gas
            a.BAL_AMOUNT = bal_amount
            a.LOCATION = str(latitude)+','+str(longitude)
            a.save()
        except:
            #print('Data Not Found')
            pass
        
    #if(gas_leak):
        if(gas_leak == 0):
            try:
                # Dynamic data to be passed to the HTML template
                x2=datetime.now()
                val="-"
                val2=":"
                date2=str(x2.year)+val+str(x2.month)+val+str(x2.day)
                time2=str(x2.hour)+val2+str(x2.minute)+val2+str(x2.second)
                dynamic_data = {
                    'name': name,
                    'message': 'Thank you for using our service!',
                    'date':date2,
                    'time':time2,
                    'serialnumber':a.SERIAL_NUMBER,
                    'CustomerCode':a.SERIAL_NUMBER, 
                            }
                                
                    # Your HTML template with dynamic data
                template = get_template('GasLeakAlert.html')
                    #template = get_template('/home/ubuntu/7-12/Mpesapoc-latest/Mpesapoc-latest/Mpesapoc-latest/Mpesapoc/Myapp/templates/invoice.html')
                html_content = template.render(dynamic_data)

                    # Generate PDF using xhtml2pdf
                pdf_data = io.BytesIO()
                pisa.CreatePDF(html_content, dest=pdf_data)

                    # Compose email
                subject = '#BalanceAlert  Solutions'
                    #message = 'Dear '+name+',\n Your recharge of amount '+Balence+'KSh sucessfully done. \n\n From,\n Enerziff Solutions'
                message="GasLeak Alert"
                fromEmail=settings.EMAIL_HOST_USER
                to_email = a.EMAILS

                ##print("user email",to_email)
                    # Attach the PDF file to the email
                pdf_data.seek(0)  # Reset the file pointer to the beginning
                email = EmailMessage(subject, message,fromEmail, [to_email])
                email.attach('UsageHistory.pdf', pdf_data.getvalue(), 'application/pdf')

                    # Send the email
                email.send()
                
                    #updating mailstatus   
            except Exception as e:
                    print("some error at gasleak",{e})  
                                                       
            

    #mycursor.execute(sql2, val)
   # mydb.commit()

    ###print(mycursor.rowcount, "record updated.")
    #myresult = mycursor.fetchall()

    #for x in myresult:
    #   ##print(x)

    time.sleep(1)

    ##print('\n')





#  -------------- MQTT ---------------------------------
##print ('Launching MQTT  Thread...')

client = mqtt.Client()
client.reinitialise()
#client.tls_insecure_set(False)
try:
    client.username_pw_set('iquvvlgs', 'PONUI_uPrhKX')
    client.connect( broker_address,  18876, 60 )
except:
    ##print("Error MQTT: connection failed")
    exit(1)

client.on_connect = on_connect
client.on_message = mqttFromDeviceCB
client.on_disconnect = on_disconnect

try:
    #client.loop_forever()
    client.loop_start()
except KeyboardInterrupt:
    logger.info("KeyboardInterrupt seen")

#subscribing all useres from database
usersSerialNumber=lpg_Customer_Table.objects.values('SERIAL_NUMBER')
###print("all users usersserialnumbers",usersSerialNumber[0]['SERIAL_NUMBER'])
for i in range(len(usersSerialNumber)):
    if usersSerialNumber[i]['SERIAL_NUMBER'] == "EVM000000002":
        userIndevice="data/320000002/server"
    else:
        userIndevice="data/"+usersSerialNumber[i]['SERIAL_NUMBER']+"/server"
    ###print("userDevices list is",userIndevice)
    #ret, mid = client.subscribe(inDevice)
    ret, mid = client.subscribe(userIndevice)
    if ret == 0:
        print("MQTT: Subscribed to topic : "+userIndevice)
        pass
    else:
        #print("MQTT: Error subscribing to topic : "+userIndevice)
        pass


#PayGo Integration


name=""
password=""
# Create your views here.
def home(request):
    return render(request,'login.html')
def adminLogin(request):
    return render(request,'adminlogin.html')
def checkAdminLogin(request):
    admindata=Admin.objects.all().values()
    global name2
    name2=request.POST['name']
    password=request.POST['password']
    #decressing loop
    sudhakarcheck=Admin.objects.filter(name=name2,password=password)
    if sudhakarcheck:
        # from admin dashboard we are getting data. that is what we are sending to admin main page.
        data=adminDashBoard()
        Gas_Close=data[0]-data[-1]
        Dev_Close=data[0]-data[-2]
        Gas_Open=data[-1]
        Dev_Open=data[-2]
        Online=data[-5]
        Offline=data[-4]
        Faulty=data[-3]
        return render(request,'adminMainPage.html',{'NAME':name2,"user_type":"admin","mainData":data,'usersLoc':data[2],
                                                        'dailyData':data[3],"gasvalvestatus":Gas_Open,"devstatus":Dev_Open,
                                                        "Gas_Close":Gas_Close,"Dev_Close":Dev_Close,"Online":Online,
                                                        "Offline":Offline,"Faulty":Faulty})
    else:
        #print("you don't go")
        pass
    #decressing loop code ends here

    # for i in range(len(admindata)):
    #     if(admindata[i]['name']==name2 and admindata[i]['password']==password):
    #         data=adminDashBoard()
    #         return render(request,'adminMainPage.html',{'NAME':name2,"mainData":data,'usersLoc':data[2],
    #                                                     'dailyData':data[3],"gasvalvestatus":data[-1],"devstatus":data[-2]})
    return  render(request,'adminlogin.html',{'wrong':"wrong Credentials"})

def adminHome(request,NAME,user_type):
     #this adminhome function we are using for getting recharge data on specific date
     global date3
     if user_type=="admin":
         data=adminDashBoard()
     elif user_type=="Area_Lead":
         leadUsername=NAME
         data=leadDashBoard(leadUsername)
     Gas_Close=data[0]-data[-1]
     Dev_Close=data[0]-data[-2]
     Gas_Open=data[-1]
     Dev_Open=data[-2]
     Online=data[-5]
     Offline=data[-4]
     Faulty=data[-3]
     if request.method == "POST":
            date3=request.POST['date']
            # ##print("date valueadminHome",date3)
            dataByDate=userHistory.objects.filter(Date=date3)
                
            # ##print("these data is given by date",dataByDate)
            # for i in dataByDate:
            #     ##print("the specific data",i.Name)
            if dataByDate:
                # from admin dashboard we are getting data. that is what we are sending to admin main page
                data=adminDashBoard()
                # ##print("the array is ",data[-1])
                return render(request,'adminMainPage.html',{'NAME':name2,"mainData":data,'usersLoc':data[2],
                                                        'dailyData':data[3],"gasvalvestatus":Gas_Open,"devstatus":Dev_Open,
                                                        "Gas_Close":Gas_Close,"Dev_Close":Dev_Close,"Online":Online,
                                                        "Offline":Offline,"Faulty":Faulty,"queryset":dataByDate,})
            else:
                status="no recharge was happend"
                data=adminDashBoard()
                # ##print("the array is ",data[-1])
                return render(request,'adminMainPage.html',{'NAME':name2,"mainData":data,'usersLoc':data[2],
                                                        'dailyData':data[3],"gasvalvestatus":Gas_Open,"devstatus":Dev_Open,
                                                        "Gas_Close":Gas_Close,"Dev_Close":Dev_Close,"Online":Online,
                                                        "Offline":Offline,"Faulty":Faulty,"status":status,})
     
    #  ##print("the array is ",data[-1])

     return render(request,'adminMainPage.html',{'NAME':NAME,"user_type":user_type,"mainData":data,'usersLoc':data[2],
                                                        'dailyData':data[3],"gasvalvestatus":Gas_Open,"devstatus":Dev_Open,
                                                        "Gas_Close":Gas_Close,"Dev_Close":Dev_Close,"Online":Online,
                                                        "Offline":Offline,"Faulty":Faulty})

def adminEdit(request,NAME,user_type):
    #this function will give the list names from main table.we are using this function for admin edit page.
    if user_type=="admin":
        lpgData=lpg_Customer_Table.objects.all().values()
        return render(request,'adminedit.html',{'lpgdata':lpgData, "NAME":NAME,"user_type":user_type})
    elif user_type=="Area_Lead":
        lpgData=lpg_Customer_Table.objects.filter(AREA_LEAD=NAME).values()
        return render(request,'adminedit.html',{'lpgdata':lpgData, "NAME":NAME,"user_type":user_type})

def selectEdit(request,NAME,user_type,name):
    global ExactUserName
    
    lpgData=lpg_Customer_Table.objects.all().values()
    # lpgcheck=lpg_Customer_Table.objects.filter(PHONENUMBER=number)
    # lpgcheck=lpgcheck.values()
    # ##print("these is lpgcheck",lpgcheck)
    for i in range(len(lpgData)):
        if(lpgData[i]['NAME']==name):
            date=lpgData[i]['DATE']
            Day=date.day
            ##print("DAY",Day)
            #we are converting dates here because dates are not printing in html pages if we don't use this conversion
            Month=date.month
            Year=date.year
            DEV_DATE=lpgData[i]['DEV_TIME']
            Dev_Day=DEV_DATE.day
            Dev_Month=DEV_DATE.month
            Dev_Year=DEV_DATE.year     
            return render(request,'editdetails.html',{"data":lpgData[i],"NAME":NAME,"user_type":user_type,
                                                          "Day":Day,"Month":Month,"Year":Year,"Dev_Day":Dev_Day,
                                                          "Dev_Month":Dev_Month,"Dev_Year":Dev_Year, "name":name})
    ###print(phoneNumber)
    return HttpResponse("success")
def login(request):
    """
    Handles login credentials.

    :param request: The HTTP request object.
    :return: Renders the login page or redirects to the main page based on login credentials.
    """
    global name,password 
    ##print('aging',name)
    # edited by hitesh
    if request.method == "POST":
        name=request.POST['name'].lower()
        password=request.POST['password']
        profile=request.POST['profile'].lower()
        
        if profile == "user":
            user = Register.objects.filter(name=name, password=password).values()
            if user:
                lpgUser = lpg_Customer_Table.objects.filter(NAME=name).values()
                if lpgUser:
                    return render(request,'mainpage.html',{"data":lpgUser[0],"name":name})
                return render(request,'mainpage.html',{"name":name})
        elif profile == "admin":
            sudhakarcheck=Admin.objects.filter(name=name,password=password)
            if sudhakarcheck:
                # from admin dashboard we are getting data. that is what we are sending to admin main page.
                data=adminDashBoard()
                Gas_Close=data[0]-data[-1]
                Dev_Close=data[0]-data[-2]
                Gas_Open=data[-1]
                Dev_Open=data[-2]
                Online=data[-5]
                Offline=data[-4]
                Faulty=data[-3]
                return render(request,'adminMainPage.html',{'NAME':name,"user_type":"admin","mainData":data,'usersLoc':data[2],
                                                                'dailyData':data[3],"gasvalvestatus":Gas_Open,"devstatus":Dev_Open,
                                                                "Gas_Close":Gas_Close,"Dev_Close":Dev_Close,"Online":Online,
                                                                "Offline":Offline,"Faulty":Faulty})
            return  render(request,'adminlogin.html',{'wrong':"wrong Credentials"})
        elif profile == "areaLead":
            areaLead = Area_Lead.objects.filter(name=name, password=password)
            print(areaLead)
            if areaLead:
                data=leadDashBoard(name)
                return render(request,'adminMainPage.html',{'NAME':name,"user_type":"Area_Lead","mainData":data,'usersLoc':data[2],
                                                            'dailyData':data[3],"gasvalvestatus":data[-1],"devstatus":data[-2]})
        
        return render(request,'login.html',{'wrong':"Invalid Login Credentials"})
    
    return render(request, 'login.html')
        
    #     user = Register.objects.filter(name=name).values()
    #     if user:
    #         if password == user[0]["password"]:
    #             #if user updated all information and we have that info in lpg main table. then we are sending that data.
    #             lpgUser = lpg_Customer_Table.objects.filter(NAME=name).values()
    #             if lpgUser:
    #                 return render(request,'mainpage.html',{"data":lpgUser[0],"name":name})
    #             # if user is first time and data not present in lpg customer table then we are just sending name to mainpage.
    #             return render(request,'mainpage.html',{"name":name})
    #         #if password is wrong but name is present in our register table. then we are showing wrong password.
    #         return render(request,'login.html',{'wrong':"Incorrect password"})
    #     #if the name is not present  in our register table then we are showing invalid username.
    #     return render(request,'login.html',{'wrong':"Invalid username"})
    # return render(request, 'login.html')

# def login(request):
#     datagetting=Register.objects.all().values()
#     lpgData=lpg_Customer_Table.objects.all().values()
#     global name,password
#     ##print('aging',name)
#     name=request.POST['name']
#     password=request.POST['password']
#    #decressing loop
#     datagettingcheck=Register.objects.filter(name=name,password=password)
#     lpgDatacheck=lpg_Customer_Table.objects.filter(NAME=name)
#     lpgDatacheck=lpgDatacheck.values()
#     ##print("lpg data chekcing",lpgDatacheck)
#     datagettingcheck=datagettingcheck.values() 
#     try:
#         if(datagettingcheck[0]['name']==name and datagettingcheck[0]['password']==password):
#             try:
#                 if(lpgDatacheck[0]['NAME']==name):
#                     return render(request,'mainpage.html',{"data":lpgDatacheck[0],"name":name})
#             except:
#                  return render(request,'mainpage.html',{'name':name})
#     except:
#      return  render(request,'login.html',{'wrong':"wrong Credentials"})
    #decressing loop code ends here
        # if(datagettingcheck[0]['name']==name and datagettingcheck[0]['password']==password):
        #     return render(request,'mainpage.html',{'name':name})
    # for i in range(len(datagetting)):
    #     if(datagetting[i]['name']==name and datagetting[i]['password']==password):
    #         for j in range(len(lpgData)):
    #             if(lpgData[j]['NAME']==name):
    #                 ##print("this is lpgdata[j]",lpgData[j])
    #                 return render(request,'mainpage.html',{"data":lpgDatacheck[0],"name":name})
                
    #     if(datagetting[i]['name']==name and datagetting[i]['password']==password):
    #        return render(request,'mainpage.html',{'name':name})     
    #     else:
    #         ##print('wrong details')
   
    #return  render(request,'login.html',{'wrong':"wrong Credentials"})

# def isValidEmail(email):
#     """
#     Validates whether the given email address is in a correct format or not.

#     :param email: The email address to be validated.
#     :type email: str
#     :return: True if the email is in a valid format, False otherwise.
#     :rtype: bool
#     """
#     regex = "^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"
#     if re.search(regex, email):
#         return True
#     return False

# # Validating Password
# def isValidPassword(password):
   
#     """
#     Validates the strength of a password based on certain criteria.

#     The function checks whether the provided password meets the following conditions:
#     - Length of the password should be between 8 to 15 characters.
#     - Should contain at least one digit.
#     - Should contain at least one lowercase letter.
#     - Should contain at least one uppercase letter.
#     - Should contain at least one special character among '@', '#', '$', '%'.

#     :param password: The password string to be validated.
#     :type password: str
#     :return: True if the password meets the criteria, False otherwise.
#     :rtype: bool
#     """
#     special_sym = ['@', '#', '$', '%']
#     if len(password) < 8 and len(password) > 15:
#         return False
#     elif not any(x.isdigit() for x in password):
#         return False
#     elif not any(x.islower() for x in password):
#         return False
#     elif not any(x.isupper() for x in password):
#         return False
#     elif not any(x for x in special_sym):
#         return False
#     return True

# def datapicking(request):
  
#     name = request.POST['name']
#     password=request.POST['password']
#     email=request.POST['email']
#     ##print("NAME",name)
#     us=Register(name=name,password=password,email=email)
#     us.save()
#     return redirect(home)
# def reg(request):

    """ 
    Handles user registration and validates input data
:param request: The HTTP request object.
:type request: HttpRequest 
:return: A redirect to the admin login page or the home page, or an HTML response with validation messages. 
:rtype: HttpResponse """
   
    if request.method == "POST":
        name = request.POST['name'].lower()
        password=request.POST['password']
        email=request.POST['email']
        user = request.POST.get('profile')
        # checking validity of registration
        isUser = Register.objects.filter(name=name)
        if not isUser:
            # login for admin
            if user == 'admin':
                adminUser = Admin.objects.filter(name=name, password=password, email=email)
                if not adminUser:
                    admin = Admin(name=name, password=password, email=email)
                    admin.save()
                    # if admin doesn't exist
                    return redirect(adminLogin)
                # if admin already exist
                return render(request, "reg.html", {"validation":"Admin already exists"})
            # login for user
            registerUser = Register(name=name,password=password,email=email)
            registerUser.save()
            return redirect("home")
        # if user already exist
        return render(request, "reg.html", {"validation":"User already exists"})
    # if method is get
    data = request.GET.get('validation')
    # render registration page for any validation corrections for registration process
    if data:
        return  render(request,'reg.html',{"validation":data})
    # render registration page for new registration
    else:
        return render(request,"reg.html")
def reg(request):
    
    """ 
    Handles user registration and validates input data
:param request: The HTTP request object.
:type request: HttpRequest 
:return: A redirect to the admin login page or the home page, or an HTML response with validation messages. 
:rtype: HttpResponse """
   
    if request.method == "POST":
        name = request.POST['name'].lower()
        password=request.POST['password']
        email=request.POST['email']
        user = request.POST.get('profile')
        # checking validity of registration
        isUser = Register.objects.filter(name=name)
        if not isUser:
            # login for admin
            if user == 'admin':
                adminUser = Admin.objects.filter(name=name, password=password, email=email)
                if not adminUser:
                    admin = Admin(name=name, password=password, email=email)
                    admin.save()
                    # if admin doesn't exist
                    return redirect(adminLogin)
                # if admin already exist
                return render(request, "reg.html", {"validation":"Admin already exists"})
            # login for area lead
            if user == 'area lead':
                areaLead = Area_Lead.objects.filter(name=name, password=password)
                if not areaLead:
                    lead = Area_Lead(name=name, password=password, email=email)
                    lead.save()
                    return redirect(areaLeadLogin)
                return render(request, "reg.html", {"validation":"Area Lead already exists"})
            # login for user
            registerUser = Register(name=name,password=password,email=email)
            registerUser.save()
            return redirect("home")
        # if user already exist
        return render(request, "reg.html", {"validation":"User already exists"})
    # if method is get
    data = request.GET.get('validation')
    # render registration page for any validation corrections for registration process
    if data:
        return  render(request,'reg.html',{"validation":data})
    # render registration page for new registration
    else:
        return render(request,"reg.html")
# def reg(request):
    
#     name=""
#     password=""
#     email=""
#     user=""
#     """ 
#     Handles user registration and validates input data
# :param request: The HTTP request object.
# :type request: HttpRequest 
# :return: A redirect to the admin login page or the home page, or an HTML response with validation messages. 
# :rtype: HttpResponse """
   
#     if request.method == "POST":
       
#         name = request.POST['name'].lower()
#         password=request.POST['password']
#         email=request.POST['email']
#         user = request.POST['profile'].lower()
#         # checking validity of registration
#         isUser = Register.objects.filter(name=name, password=password, email=email)
#         if (not isUser) and (len(name) > 0):
#             if isValidEmail(email):
#                 if isValidPassword(password):
#                     # login for admin
#                     if user == 'admin':
#                         adminUser = Admin.objects.filter(name=name, password=password, email=email)
#                         if not adminUser:
#                             admin = Admin(name=name, password=password, email=email)
#                             admin.save()
#                             # if admin doesn't exist
#                             return redirect(adminLogin)
#                         # if admin already exist
#                         return render(request, "reg.html", {"validation":"Admin already exists","name":name,"email":email})
#                     # login for user
#                     registerUser = Register(name=name,password=password,email=email)
#                     registerUser.save()
#                     return redirect("home")
#                 # if password is not following proper security conditions
#                 return render(request, "reg.html", {"validation":mark_safe(
#                                                         "Password should contain:<br>"
#                                                         "* One Capital case letter<br>"
#                                                         "* One Lower case letter<br>"
#                                                         "* One digit<br>"
#                                                         "* One Special character<br>"
#                                                         "* Length of password should be between 8-15 characters"
#                                                         ),"name":name,"email":""})
#             # if email is not valid
#             return render(request, "reg.html", {"validation":"Enter valid email","name":name,"email":" "})
#         # if name is empty
#         elif not name:
#             return render(request, "reg.html", {"validation":"Enter username"})
#         # if user already exist
#         return render(request, "reg.html", {"validation":"User already exists"})
#     # if method is get
#     data = request.GET.get('validation')
#     # render registration page for any validation corrections for registration process
#     if data:
#         return  render(request,'reg.html',{"validation":mark_safe(data)})
#     # render registration page for new registration
#     else:
#         return render(request,"reg.html",{"name":name,"email":email,"password":password,"user":user})
   
# def reg(request):
#     return  render(request,'reg.html')

def addDetails(request,userName):
    #In this function when ever user click add details if the details are already present in main table then we are showing that detail.
    ##print("this is username of sudhakar",userName)
    #decressing loop
    lpgData=lpg_Customer_Table.objects.filter(NAME=userName).values()
    
    try:
        if(lpgData[0]['NAME'].lower()==userName):
            date=lpgData[0]['DATE']
            Day=date.day
                    
            Month=date.month
            Year=date.year
            DEV_DATE=lpgData[0]['DEV_TIME']
            Dev_Day=DEV_DATE.day
            Dev_Month=DEV_DATE.month
            Dev_Year=DEV_DATE.year
            return render(request,'addDetails.html',{"data":lpgData[0],"Day":Day,"Month":Month,"Year":Year,"Dev_Day":Dev_Day,"Dev_Month":Dev_Month,"Dev_Year":Dev_Year, "name":userName})
    except:
        #if not present in main table we are showing only name,password values in that input tags. remaining all are empty.
        return render(request,'addDetails.html',{"name":userName,"password":password})
    

    # datagetting=Register.objects.all().values()
    #lpgData=lpg_Customer_Table.objects.all().values()
    # for i in range(len(datagetting)):
    #         if(datagetting[i]['name']==name and datagetting[i]['password']==password):
    #           for j in range(len(lpgData)):
    #             if(lpgData[j]['NAME']==name):
    #                 ##print("this is loop lpgdataj",lpgData[j])
    #                 ##print(lpgData[0]['DATE'])
    #                 date=lpgData[0]['DATE']
    #                 Day=date.day
    #                 ##print("DAY",Day)
    #                 Month=date.month
    #                 Year=date.year
    #                 DEV_DATE=lpgData[0]['DEV_TIME']
    #                 Dev_Day=DEV_DATE.day
    #                 Dev_Month=DEV_DATE.month
    #                 Dev_Year=DEV_DATE.year
    #                 return render(request,'addDetails.html',{"data":lpgData[0],"Day":Day,"Month":Month,"Year":Year,"Dev_Day":Dev_Day,"Dev_Month":Dev_Month,"Dev_Year":Dev_Year, "name":name})
                
    #         if(datagetting[i]['name']==name and datagetting[i]['password']==password):
    #             return render(request,'addDetails.html',{"name":name,"password":password})
    
    #return HttpResponse("SUCCESS")    
def editDetails(request):

   
    datagetting=Register.objects.all().values()
    lpgData=lpg_Customer_Table.objects.all().values()
    for i in range(len(datagetting)):
            if(datagetting[i]['name']==name and datagetting[i]['password']==password):
              for j in range(len(lpgData)):
                if(lpgData[j]['NAME']==name):
                    ##print(lpgData[j]['DATE'])
                    date=lpgData[j]['DATE']
                    Day=date.day
                    ##print("DAY",Day)
                    Month=date.month
                    Year=date.year
                    DEV_DATE=lpgData[j]['DEV_TIME']
                    Dev_Day=DEV_DATE.day
                    Dev_Month=DEV_DATE.month
                    Dev_Year=DEV_DATE.year
                    return render(request,'editdetails.html',{"data":lpgData[j],"Day":Day,"Month":Month,"Year":Year,"Dev_Day":Dev_Day,"Dev_Month":Dev_Month,"Dev_Year":Dev_Year, "name":name})
                
            if(datagetting[i]['name']==name and datagetting[i]['password']==password):
                return render(request,'editdetails.html',{"name":name,"password":password})
    
    return HttpResponse("SUCCESS")
#class declartion for validations
# class Handle:
#     def __init__(self, name):
#         self.a = lpg_Customer_Table.objects.get(NAME=name)

#     def customerId(self, c_id):
#         self.c_id = c_id.strip()
#         if self.c_id.isalnum():
#             return self.c_id.upper()
#         return self.a.CUST_ID
    
#     def serialNumber(self, serialnumber):
#         self.serial_num = serialnumber.strip()
#         if self.serial_num.isalnum():
#             return self.serial_num.upper()
#         return self.a.SERIAL_NUMBER
    
#     def phoneNumber(self, phone_number):
#         self.phone_number = phone_number.strip()
#         if self.phone_number.isdigit():
#             if self.phone_number[:3] == "254" and len(self.phone_number) == 12:
#                 return self.phone_number
#         return self.a.PHONENUMBER
            
#     def startingCode(self, startingcode):
#         self.start_code = startingcode.strip()
#         if self.start_code.isdigit() and len(self.start_code) == 9:
#             return self.start_code
#         return self.a.STARTING_CODE
    
#     def secretKey(self, secretkey):
#         self.secret_key = secretkey.strip()
#         if self.secret_key.isalnum():
#             return self.secret_key.lower()
#         return self.a.SECRET_KEY
    
#class completed
    

def editall(request,userName):
    #this function gonna call when first time user enters his total data.
    global inDevice
    c_id = request.POST['c_id']
    name = request.POST['name']
    phone_number=request.POST['phonenumber']
    serialnumber = request.POST['serialnumber'] 
    startingcode = request.POST['startingcode']
    secretkey = request.POST['secretkey']
    #subscribing mqtt
    inDevice="data/"+str(serialnumber)+"/server"
    ret, mid = client.subscribe(inDevice)
    if ret == 0:
        #print("MQTT: Subscribed to topic : "+inDevice)
        pass
    else:
        #print("MQTT: Error subscribing to topic : "+inDevice)
        pass

    date = request.POST['date']
    gasleak = request.POST.get('gasleak')
    gasleakvaluebro= request.POST.get('gasleak')
    ##print("this is the gasleak from selettag", gasleakvaluebro)
    gasvalve  = request.POST.get('gasvalve')
    tamper = request.POST.get('tamper')
    devenable = request.POST.get('devenable')
    cylendertype = request.POST['cylendertype']
    perpaid = request.POST.get('prepaid')
    # gasleak = request.POST['gasleak']
    # gasvalve = request.POST['gasvalve']
    # tamper = request.POST['tamper']
    # devenable = request.POST['devenable']
    # cylendertype = request.POST['cylendertype']
    # perpaid = request.POST['perpaid']
    batstatus = request.POST['batstatus']
    location = request.POST['location']
    imeinumber = request.POST['imeinumber']
    devstatus = request.POST.get('devstatus')
    devtype = request.POST['devtype']
    ballpg = request.POST['ballpg']
    balamount = request.POST['balamount']
    User_Email = request.POST['user_email']
    # Connection_Status=request.POST['connection_status']
    # Battery_Percentage=request.POST['Battery_Percentage']
    # Cylinder_Gas_Weight=request.POST['Cylinder_Gas_Weight']
    # print("connection status value is",Connection_Status)
    ##print("phnenumber",phone_number)
    us=lpg_Customer_Table(CUST_ID=c_id,NAME= userName,SERIAL_NUMBER=serialnumber,PHONENUMBER=phone_number,STARTING_CODE= startingcode ,
                     SECRET_KEY=secretkey,DATE=date,GAS_LEAK=gasleak,GAS_VALVE=gasvalve,
                     TAMPER=tamper,DEV_ENABLE=devenable,CYLENDER_TYPE=cylendertype,PREPAID=perpaid
                     ,BAT_STATUS=batstatus,LOCATION=location,IMEI_NO=imeinumber,DEV_STATUS=devstatus,
                     DEV_TIME=devtype,BAL_LPG= ballpg,BAL_AMOUNT=balamount,EMAILS=User_Email,
                     )
    us.save()
    relogin_url = reverse('relogin', kwargs={'userName': userName})
    return redirect(relogin_url)


def update(request,userName):
    #when user want to update his data. there we are calling this function
    # a =lpg_Customer.objects.get(NAME=='cit');
    a=lpg_Customer_Table.objects.get(NAME=userName)
    try:
        lowBalance_data=userLowBalanceCheck.objects.get(Name=userName)
        lowBalance_data.PhoneNumber=a.PHONENUMBER
        lowBalance_data.save()
    except:
        print("low balance alert")
    a.CUST_ID= request.POST['c_id']
    a.NAME = request.POST['name']
    Previous_SerialNumber=a.SERIAL_NUMBER
    a.SERIAL_NUMBER = request.POST['serialnumber']
    a.PHONENUMBER =request.POST['phonenumber']
    a.STARTING_CODE  = request.POST['startingcode']
    a.SECRET_KEY = request.POST['secretkey']
    #subscribing mqtt
    inDevice="data/"+str(a.SERIAL_NUMBER)+"/server"
    if(Previous_SerialNumber!=inDevice):
        ret, mid = client.subscribe(inDevice)
        if ret == 0:
            #print("MQTT: Subscribed to topic : "+inDevice)
            pass
        else:
            #print("MQTT: Error subscribing to topic : "+inDevice)
            pass
    
        
    # hnd = Handle(name)
    # a=lpg_Customer_Table.objects.get(NAME=name)
    # a.CUST_ID= hnd.customerId(request.POST['c_id'])
    # a.NAME = request.POST['name']
    # a.SERIAL_NUMBER = hnd.serialNumber(request.POST['serialnumber'])
    # a.PHONENUMBER = hnd.phoneNumber(request.POST['phonenumber'])
    # a.STARTING_CODE  = hnd.startingCode(request.POST['startingcode'])
    # a.SECRET_KEY = hnd.secretKey(request.POST['secretkey'])
    a.DATE = request.POST['date']
    a.GAS_LEAK = request.POST.get('gasleak')
    gasleakvaluebro= request.POST.get('gasleak')
    ##print("this is the gasleak from selettag", gasleakvaluebro)
    a.GAS_VALVE  = request.POST.get('gasvalve')
    a.TAMPER = request.POST.get('tamper')
    a.DEV_ENABLE = request.POST.get('devenable')
    a.CYLENDER_TYPE = request.POST['cylendertype']
    a.PREPAID = request.POST.get('prepaid')
    a.BAT_STATUS = request.POST['batstatus']
    a.LOCATION = request.POST['location']
    a.IMEI_NO = request.POST['imeinumber']
    a.DEV_STATUS = request.POST.get('devstatus')
    a.DEV_TIME = request.POST['devtype']
    a.BAL_LPG = request.POST['ballpg']
    a.BAL_AMOUNT = request.POST['balamount']
    ##print("the user mail is",request.POST['user_email'])
    a.EMAILS = request.POST['user_email']
    # a.CONNECTION_STATUS=request.POST['connection_status']
    # a.BATTERY_PERCENTAGE=request.POST['Battery_Percentage']
    # a.CYLINDER_GAS_WEIGHT=request.POST['Cylinder_Gas_Weight']
    ##print("this is cylinder",request.POST['cylendertype'])
    a.save()
    relogin_url = reverse('relogin', kwargs={'userName': userName})
    return redirect(relogin_url)

def adminupdate(request, userName,NAME,user_type):
    #if admin want to update the usre information then this function gonna call.
    # a =lpg_Customer.objects.get(NAME=='cit');
    # a=lpg_Customer_Table.objects.get(PHONENUMBER=phoneNumber2)
    #a=lpg_Customer_Table.objects.get(NAME=ExactUserName)
    a=lpg_Customer_Table.objects.get(NAME=userName)
    try:
        lowBalance_data=userLowBalanceCheck.objects.get(Name=userName)
        lowBalance_data.PhoneNumber=a.PHONENUMBER
        lowBalance_data.save()
    except:
        print("admin upadate error")
    Previous_SerialNumber=a.SERIAL_NUMBER
    a.CUST_ID= request.POST['c_id']
    a.NAME = request.POST['name']
    a.SERIAL_NUMBER = request.POST['serialnumber']
    a.PHONENUMBER =request.POST['phonenumber']
    a.STARTING_CODE  = request.POST['startingcode']
    a.SECRET_KEY = request.POST['secretkey']
    #subscribing mqtt
    inDevice="data"+str(a.SERIAL_NUMBER)+"/server"
    if(Previous_SerialNumber!=inDevice):
        ret, mid = client.subscribe(inDevice)
        if ret == 0:
            #print("MQTT: Subscribed to topic : "+inDevice)
            pass
        else:
            #print("MQTT: Error subscribing to topic : "+inDevice)
            pass
    # hnd = Handle(name)
    # a=lpg_Customer_Table.objects.get(PHONENUMBER=phoneNumber2)
    # a.CUST_ID= hnd.customerId(request.POST['c_id'])
    # a.NAME = request.POST['name']
    # a.SERIAL_NUMBER = hnd.serialNumber(request.POST['serialnumber'])
    # a.PHONENUMBER = hnd.phoneNumber(request.POST['phonenumber'])
    # a.STARTING_CODE  = hnd.startingCode(request.POST['startingcode'])
    # a.SECRET_KEY = hnd.secretKey(request.POST['secretkey'])
    a.DATE = request.POST['date']
    a.GAS_LEAK = request.POST.get('gasleak')
    gasleakvaluebro= request.POST.get('gasleak')
    ##print("this is the gasleak from selettag", gasleakvaluebro)
    a.GAS_VALVE  = request.POST.get('gasvalve')
    a.TAMPER = request.POST.get('tamper')
    a.DEV_ENABLE = request.POST.get('devenable')
    a.CYLENDER_TYPE = request.POST['cylendertype']
    a.PREPAID = request.POST.get('prepaid')
    a.BAT_STATUS = request.POST['batstatus']
    a.LOCATION = request.POST['location']
    a.IMEI_NO = request.POST['imeinumber']
    a.DEV_STATUS = request.POST.get('devstatus')
    a.DEV_TIME = request.POST['devtype']
    a.BAL_LPG = request.POST['ballpg']
    a.BAL_AMOUNT = request.POST['balamount']
    a.EMAILS = request.POST['user_email']
    ##print("this is cylinder",name2)
    a.save()
    # return render(request,'adminMainPage.html',{'NAME':name2,'status':"DATA UPDATED"})
    return redirect('adminHome',NAME=NAME,user_type=user_type)


def amountinput(request,userName):
    #this function we are calling when usre click recharge option in user side.
    #decressing loop code starts here
    lpgData=lpg_Customer_Table.objects.filter(NAME=userName).values()
    try:
        if(lpgData[0]['NAME'].lower()==userName):
            return render(request,'amountinput.html', {"name":userName})
    except:
        return render(request,'amountinput.html',{'status':'Please Provide details in Edit Details Page', "name":userName})
    #decressing loop code ends here 

    # lpgData=lpg_Customer_Table.objects.all().values()
    # for j in range(len(lpgData)):
    #     if(lpgData[j]['NAME']==name):
    #         return render(request,'amountinput.html', {"name":name})
    # return render(request,'amountinput.html',{'status':'Please Provide details in Edit Details Page', "name":name})
def checkPaymentStatus(request,userName,counter,phoneNum,amount):
    #this function we are using for stk push. we are calling this function in payment method.
    #transactiondata=transaction_details.objects.filter(phoneNUmber=phoneNumber).values()
    ##print("Counter....",counter)
    ##print("userName",userName)
    ##print("phonenumber",phoneNum)
    if counter <=0:
        #transactiondata=transaction_details.objects.filter(phoneNUmber=phoneNum).values()
        #a=lpg_Customer_Table.objects.get(PHONENUMBER=transactiondata[i]['phoneNUmber'])                   
        transactionData=transaction_details.objects.get(phoneNUmber=phoneNum)
        ##print("this is data about data",transactionData.phoneNUmber)
        transactionData.delete()
        status="Failed"
        ##print("...............ussrNAme",userName)
        ##print("statissss",status)
        return userName,status
        #return render(request,'amountinput.html',{"status":"Transaction Failed Please try again after some time","name":userName})

    transactiondata=transaction_details.objects.all().values()
    ##print(".......",len(transactiondata))
    ##print("*******",transactiondata)
    for i in range(len(transactiondata)):
        ##print("i value",i)
        ##print("trans phone",transactiondata[i]['phoneNUmber'])
        if (transactiondata[i]['isSuccess']=="success" and transactiondata[i]['phoneNUmber']==phoneNum):
            userHistory1(phoneNum,amount)
            a=lpg_Customer_Table.objects.get(NAME=userName)
            ##print("aaa",a)
            ##print("a.BAL_AMOUNT before", a.BAL_AMOUNT)
            # -----------Publish Token -----------------------------------------------------------------
            secret_key_temp       =  '52fa8d60be23d944a8c4bbe4c0dfff5c'
            secret_key            =  codecs.decode(secret_key_temp, 'hex_codec') 
            Taxamount=int(amount)*(5/100)
            #amt                   =  int(amount)-Taxamount
            amt                   =  int(amount)
            gasUnits=int(amount)/100
            gasUnits=str(gasUnits)+" KG"
            #amt                   =  a.BAL_AMOUNT 
            ##print("secret key", secret_key )
            serial_no = 320000001
            device_starting_code = 302623035
            ##print("starting code", device_starting_code )
            restricted_digit_set =  False
            ##print('\n')
            server_simulator = SingleDeviceServerSimulator(device_starting_code, secret_key,
                                                restricted_digit_set=restricted_digit_set)
            token_1 = server_simulator._generate_extended_value_token(int(amt))
            ##print('Extended Tokens: ', token_1)

            val2 = {"SERIAL_NUMBER":a.SERIAL_NUMBER,
                        "BAL_AMOUNT" : token_1
            }
            data_out=json.dumps(val2,  default=str)  # encode oject to JSON
            ##print("sending data: " +  str(amt))

            outDevice="data/"+a.SERIAL_NUMBER+"/customer"
            if a.SERIAL_NUMBER == 'EVM000000001':
               outDevice = "data/320000001/customer"

            if a.SERIAL_NUMBER == 'EVM000000002':
               outDevice = "data/320000002/customer"
            client.publish(outDevice,data_out)
            ##print("Just published " + str(token_1) + " to "+str(outDevice)  )
		################# END  PUBLISH ##############
		
            ##print("this email only working")
            try:
			# Dynamic data to be passed to the HTML template
                    ##print("this email only working")
                    x2=datetime.now()
                    val="-"
                    val2=":"
                    date2=str(x2.year)+val+str(x2.month)+val+str(x2.day)
                    time2=str(x2.hour)+val2+str(x2.minute)+val2+str(x2.second)
                    dynamic_data = {
                        'name': a.NAME,
                        'message': 'Thank you for using our service!',
                        'date':date2,
                        'time':time2,
                        'amount':amount,
                        'serialnumber':a.SERIAL_NUMBER,
                        'cutomerCode':a.SERIAL_NUMBER,
                        'TaxAmount':Taxamount,
                        'unitsPurchased':gasUnits,
                        'Email':a.EMAILS,
                        "imagepath":'/Myapp/static/greenWellEngeries-Logo.png',
                        'RemainingAmount':amt,
                        'phoneNumber':a.PHONENUMBER
                        
                    }
                    dynamic_data2={
                        "date":"20-3-1243"
                    }

				
				# Your HTML template with dynamic data
                    template = get_template('Invoice.html')
                    #template = get_template('/home/ubuntu/7-12/Mpesapoc-latest/Mpesapoc-latest/Mpesapoc-latest/Mpesapoc/Myapp/templates/invoice.html')
                    html_content = template.render(dynamic_data)

                    # Generate PDF using xhtml2pdf
                    pdf_data = io.BytesIO()
                    pisa.CreatePDF(html_content, dest=pdf_data)

                    # Compose email
                    subject = '#Invoice Enerziff Solutions'
                    message = 'Dear '+userName+',\n Your recharge of amount '+str(amount)+'KSh sucessfully done. \n\n From,\n Enerziff Solutions'
                    fromEmail=settings.EMAIL_HOST_USER
                    to_email = a.EMAILS

                    ##print("user email",to_email)
                    # Attach the PDF file to the email
                    pdf_data.seek(0)  # Reset the file pointer to the beginning
                    email = EmailMessage(subject, message,fromEmail, [to_email])
                    email.attach('Invoice.pdf', pdf_data.getvalue(), 'application/pdf')

                    # Send the email
                    #email.send()

				

            except Exception as e:
                    print(f"An error occurred: {e}")

            try:
                if(amount+a.BAL_AMOUNT >= 100):
                    mailDeleteValues = userLowBalanceCheck.objects.get(SerialNumber=a.SERIAL_NUMBER)
                    mailDeleteValues.delete()
            except:
                print("the value is not present")
            #transaction success
            transactionData=transaction_details.objects.get(phoneNUmber=a.PHONENUMBER)
            transactionData.delete()
            ##print("before return")
            status="Completed"
            return userName,status
            #return render(request,'amountinput.html',{"status":userName+", Transaction Sucessfully Completed","name":userName})

    time.sleep(10)
    return checkPaymentStatus(request,userName,counter-1,phoneNum,amount)
        

def payment(request,userName):
    #insert data into transaction_details table Eg : username: cit && isSuccess = started
    #global phoneNumber
    phoneNumber = 0
    ##print("payment userss list",userName)
    #decressing loop code starts here
    lpgData=lpg_Customer_Table.objects.filter(NAME=userName).values()
    ##print("this is payment lpgdata",lpgData[0]['NAME'].lower())
    try:
        if(lpgData[0]['NAME'].lower()==userName.strip()):
            phoneNumber=lpgData[0]['PHONENUMBER']
            ##print("users phonenumbers are",phoneNumber)
    except:
        print('I didn"t get phonenumber')
        #decressing loop code ends here 

    ###print("this is user phonenumber",phoneNumber)
    # lpgData=lpg_Customer_Table.objects.all().values()
    # for j in range(len(lpgData)):
    #     if(lpgData[j]['NAME']==name):
    #         phoneNumber  = lpgData[j]['PHONENUMBER']
    #         # ##print(lpgData[j]['PHONENUMBER'])
    #global amount
    amount=request.POST['amount']
    amount=int(amount)
    # ##print(amount)
      #decressing loop code starts here
    try:
        transactionData=transaction_details.objects.filter(phoneNUmber=phoneNumber).values()
        if not transactionData:
             us=transaction_details(isSuccess="started",userName=userName,phoneNUmber=phoneNumber)
             #userHistory1(phoneNumber)
             us.save()
    except:
        print("the Recharge is already processing")
     #decressing loop code ends here 
        
    # transactionData=transaction_details.objects.all().values()
    # ##print("changing data",transactionData)
    
    # count=0
    # if transactionData:
    #     for i in transactionData:
    #         ##print("changing phonenumber",i['phoneNUmber'])
    #         if(i['phoneNUmber']==phoneNumber):
    #             count=1
    #             ##print('the phonenumber is already present');
               
    #     if(count==0):
    #         us=transaction_details(isSuccess="started",userName=name,phoneNUmber=phoneNumber)  
    #         #userHistory1(phoneNumber)   
    #         us.save()
    # else:
    #     us=transaction_details(isSuccess="started",userName=name,phoneNUmber=phoneNumber)
    #     #userHistory1(phoneNumber)
    #     us.save()
        
    #Intergrate STK PUSH
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}
    requests_s = {
        "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
        "Password": LipanaMpesaPpassword.decode_password,
        "Timestamp": LipanaMpesaPpassword.lipa_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phoneNumber,  # replace with your phone number to get stk push
        "PartyB": LipanaMpesaPpassword.Business_short_code,
        "PhoneNumber": phoneNumber,  # replace with your phone number to get stk push
        "CallBackURL": "http://crimsoninnovative.com/mpesa/index.php",
        "AccountReference": userName,
        "TransactionDesc": "GWEL_PAYBILL_LPG_SMARTMETER stk push"
    }
    response = requests.post(api_url, json=requests_s, headers=headers)
    ##print(response.json())

    #check from the database whether transaction is success 

    #recursive function to check for one min and if we get success in "isSuccess"
    #sleep 10 sec
    #time.sleep(10)
    phoneNum=phoneNumber
    userName,paymentStatus = checkPaymentStatus(request,userName,6, phoneNum,amount)
    ##print("paymentStatus",paymentStatus)
    
    
    if paymentStatus == "Completed":
        return render(request,'amountinput.html',{"status":userName+", Transaction Sucessfully Completed","name":userName})
    else:
        return render(request,'amountinput.html',{"status":"Transaction Failed Please try again after some time","name":userName})
    

def deleteUser(request):
        #this function we are calling for logout.
        return redirect("/")

def relogin(request,userName):
    #if user go to recharge or any other option and back to clicks the dashboard or home page then this function we are calling
      #decressing loop code starts here 
    lpgData=lpg_Customer_Table.objects.filter(NAME=userName).values()
    try:
        if lpgData:
            return render(request,'mainpage.html',{"data":lpgData[0],'name':userName})
        else:
            return render(request,'mainpage.html',{'name':name})
    except Exception as e:

        print(f"just to put: {e}")
    #decressing loop code ends here 
        
    # lpgData=lpg_Customer_Table.objects.all().values()
    # datagetting=Register.objects.all().values()

    # for i in range(len(datagetting)):
    #     if(datagetting[i]['name']==name and datagetting[i]['password']==password):
    #         for j in range(len(lpgData)):
    #             if(lpgData[j]['NAME']==name):
    #                 ##print("actual use name is"+name)
    #                 ##print(lpgData[j]['NAME'])
    #                 return render(request,'mainpage.html',{"data":lpgData[j],'name':name})
     
    #     if(datagetting[i]['name']==name and datagetting[i]['password']==password):
    #        ##print("actual use name is"+name)
    #        return render(request,'mainpage.html',{'name':name})

def UserLocation(request,location,NAME,user_type):
    #this function we are using the showing meter on map in admin side.
    ##print("locations",location)
    l1=location.split(',')
    ##print("location list",l1)
    m=folium.Map(location=[float(l1[0]),float(l1[1])],zoom_start=8)
    folium.Marker([float(l1[0]),float(l1[1])]).add_to(m)
    m=m._repr_html_()
    m = m[:90] + '150' + m[92:]
    context={
        'm':m,
        'NAME':NAME,
        "user_type":user_type
    }
    return render(request,'map.html',context)

def historydata(request,userName):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        print(start_date)
        print(end_date)
        history_data = userHistory.objects.filter(Name=userName, Date__range=(start_date, end_date))
        return render(request, 'userhistory.html', {"name":userName, "userhistory":history_data, "start_date":start_date, "end_date":end_date})
    #this function we are using for user side. when click user hisotry it shows recharge hisotry.
    hisdata=userHistory.objects.filter(Name=userName)
    return render(request,'userhistory.html',{"name":userName,"userhistory":hisdata})
def customerHelp(request):
    return render(request,'customerHelp.html',{"name":name})

def c2bPaymentCheck():
    ##print('check this method')
    
    removeUserLowBalence=userLowBalanceCheck.objects.all().values()
    if removeUserLowBalence:
        for i in removeUserLowBalence:
            
            checkAmount=lpg_Customer_Table.objects.get(PHONENUMBER=i['PhoneNumber'])
            
            if(checkAmount.BAL_AMOUNT>100):
                DeleteUser=userLowBalanceCheck.objects.get(PhoneNumber=i['PhoneNumber'])
                DeleteUser.delete()
            ##print("this is checkAmount",checkAmount.BAL_AMOUNT)
    #userLowBalance = lpg_Customer_Table.objects.filter(BAL_AMOUNT__lt=100)
    userLowBalance = lpg_Customer_Table.objects.filter(BAL_AMOUNT__lt=-1)
    uservalues2=userLowBalance.values()
    x=datetime.now()
    val="-"
    val2=":"
    date=str(x.year)+val+str(x.month)+val+str(x.day)
    time=str(x.hour)+val2+str(x.minute)+val2+str(x.second)
    userLowBalanceCheckValues=userLowBalanceCheck.objects.all().values_list('SerialNumber',flat=True)
    all_my_Field_values_list = list(userLowBalanceCheckValues)
    ##print(all_my_Field_values_list)
    username=""
    SerialNumber=""
    Balence=""
    Phonenumber=""
    Emailid=""
    for i in uservalues2:
        username=i['NAME']
        SerialNumber=i['SERIAL_NUMBER']
        Balence=i['BAL_AMOUNT']
        Phonenumber=i['PHONENUMBER']
        Emailid=i['EMAILS']
        if SerialNumber not in all_my_Field_values_list:

            LowBalance_Save=userLowBalanceCheck(Name=username,SerialNumber=SerialNumber,
                                            BAL_AMOUNT=Balence,PhoneNumber=Phonenumber,EMAILS=Emailid,
                                            DATE=date,Time=time, State="null",Country='null',MailStatus="False")
            LowBalance_Save.save()
        MailSendingValues = userLowBalanceCheck.objects.all().values()
    MailSendingValues = []    
    for i in MailSendingValues:
        if i['MailStatus']=='False':
            username=i['Name']
            SerialNumber=i['SerialNumber']
            Balence=i['BAL_AMOUNT']
            Phonenumber=i['PhoneNumber']
            Emailid=i['EMAILS']
            
            
            #sending Email
            try:
                                MailSendingFunction(username,SerialNumber,Phonenumber,Balence,Emailid,value="BalanceAlert")               
            #         # Dynamic data to be passed to the HTML template
            #                     x2=datetime.now()
            #                     val="-"
            #                     val2=":"
            #                     date2=str(x2.year)+val+str(x2.month)+val+str(x2.day)
            #                     time2=str(x2.hour)+val2+str(x2.minute)+val2+str(x2.second)
            #                     dynamic_data = {
            #                         'name': username,
            #                         'message': 'Thank you for using our service!',
            #                         'date':date2,
            #                         'time':time2,
            #                         'amount':Balence,
            #                         'serialnumber':SerialNumber,
            #                         'CustomerCode':SerialNumber    
            #                     }
                               
            #                     # Your HTML template with dynamic data
            #                     template = get_template('BalanceAlert.html')
            #                     #template = get_template('/home/ubuntu/7-12/Mpesapoc-latest/Mpesapoc-latest/Mpesapoc-latest/Mpesapoc/Myapp/templates/invoice.html')
            #                     html_content = template.render(dynamic_data)

            #                     # Generate PDF using xhtml2pdf
            #                     pdf_data = io.BytesIO()
            #                     pisa.CreatePDF(html_content, dest=pdf_data)

            #                     # Compose email
            #                     subject = '#BalanceAlert  Solutions'
            #                     #message = 'Dear '+name+',\n Your recharge of amount '+Balence+'KSh sucessfully done. \n\n From,\n Enerziff Solutions'
            #                     message="Balance alert message"
            #                     fromEmail=settings.EMAIL_HOST_USER
            #                     to_email = Emailid

            #                     ##print("user email",to_email)
            #                     # Attach the PDF file to the email
            #                     pdf_data.seek(0)  # Reset the file pointer to the beginning
            #                     email = EmailMessage(subject, message,fromEmail, [to_email])
            #                     email.attach('BalanceAlert.pdf', pdf_data.getvalue(), 'application/pdf')

            #                     # Send the email
            #                     email.send()
            #                     #updating mailstatus
            #                     #sending sms
                                mailDeleteValues = userLowBalanceCheck.objects.get(SerialNumber=i['SerialNumber'])
                                mailDeleteValues.MailStatus="True"
                                mailDeleteValues.save() 
                                account_sid = 'AC979edcba3714497157bbd9bc1b0e738c'
                                auth_token = 'fd49326d3578971b8189c5a83390e9ac'
                                twilio_phone_number = '++12177545789'


                                # Recipient's phone number (you can replace this with the actual recipient's phone number)
                                to_phone_number = "+919820565918"
                                #to_phone_number = "+919703321705"

                                # Message to be sent
                                message_body = "Your Balance is low "+str(Balence)+".\nPlease go the Enerziff Account and Recharge. \n\n From,\n Enerziff Solutions"

                                # Initialize Twilio client
                                clientSMS = Client(account_sid, auth_token)

                                # Send SMS
                                #message = clientSMS.messages.create(
                                #    body=message_body,
                                #    from_=twilio_phone_number,
                                #    to=to_phone_number
                                #)                               
                                # return HttpResponse("Email sent successfully.")
            except Exception as e:
                    print(f"An error occurred: {e}")
                    # return HttpResponse("Error sending email.")
             
    c2bData=c2bAmountCheck.objects.all().values()
    if c2bData:
        ##print("the data is present")
        for i in c2bData:
            ##print("C2BData amount",i['amount'])
    # -----------Publish Token -----------------------------------------------------------------

            secret_key_temp       =  '52fa8d60be23d944a8c4bbe4c0dfff5c'
            secret_key            =  codecs.decode(secret_key_temp, 'hex_codec') 
            Taxamount             =int(i['amount'])*(5/100)
            #amt                   =  int(i['amount'])-Taxamount ### TAX AMOUNT
            amt                   =  int(i['amount'])
            ##print("what is amount",amt)
            gasUnits              =int(i['amount'])/10
            New_Add_LPG=gasUnits
            gasUnits              =str(gasUnits)+" KG"
            ##print("secret key", secret_key )
            serial_no = i['PhoneNumber']
            device_starting_code = 302623035
            ##print("starting code", device_starting_code )
            restricted_digit_set =  False
            ##print('\n')
            server_simulator = SingleDeviceServerSimulator(device_starting_code, secret_key,
                                                   restricted_digit_set=restricted_digit_set)
            token_1 = server_simulator._generate_extended_value_token(int(amt))
            
            ## 2547 ****** 746
            #Compare first 4 digits and last 3 digits and get coressponding SERIAL NUMBER
            # ##print("Here we are slicing the phonenumber",i['PhoneNumber'][:4],i['PhoneNumber'][-3:])
            # number1=i['PhoneNumber'][:4]+i['PhoneNumber'][-3:]
            # ##print("number 1 is",number1)
            # lpgNumberCheck=lpg_Customer_Table.objects.all().values()
            # for j in lpgNumberCheck:
            #     number=j['PHONENUMBER'].replace(" ","")
            #     number2=number[:4]+number[-3:]
            #     if(number1==number2):
            #         ##print("both are equal")
            #     else:
            #         ##print("both are not equal")
            # ##print('Extended Tokens: ', token_1)
            val2 = {"SERIAL_NUMBER":i['PhoneNumber'],
                    "BAL_AMOUNT" : token_1
                    }
            data_out=json.dumps(val2,  default=str)  # encode oject to JSON
            ##print("sending data: " +  str(amt))
            outDevice="data/"+i['PhoneNumber']+"/customer"
            if i['PhoneNumber'] == 'EVM000000001':
               outDevice = "data/320000001/customer"

            if i['PhoneNumber'] == 'EVM000000002':
               outDevice = "data/320000002/customer"
            client.publish(outDevice,data_out)
            ##print("Just published " + str(token_1) + " to "+str(outDevice)  )
            ################# END  PUBLISH ##############
            
            #deleteing the current user
            try:
                # ##print("phone numbers are",i['PhoneNumber'])
                lpgDataamount=lpg_Customer_Table.objects.get(SERIAL_NUMBER=i['PhoneNumber'])
                # # ##print("this is serial nuber",i['PhoneNumber'])
                # ##print("this is lpgdatamaount",lpgDataamount.PHONENUMBER)
                # lpgDataamount.BAL_AMOUNT=lpgDataamount.BAL_AMOUNT+amt
                # lpgDataamount.save()
                c2bHistory=userHistory(Name=lpgDataamount.NAME,SerialNumber=lpgDataamount.SERIAL_NUMBER,
                                       Amount=i['amount'],PhoneNumber=lpgDataamount.PHONENUMBER,Date=date,
                                       Time=time,PreviousAmount=lpgDataamount.BAL_AMOUNT,NowAddedAmount=i['amount'],
                                       PreviousLPG=lpgDataamount.BAL_LPG,NewAddedLPG=New_Add_LPG)
                c2bHistory.save()
                transactiondata=c2bAmountCheck.objects.get(PhoneNumber=i['PhoneNumber'])
                transactiondata.delete()
                
                # Dynamic data to be passed to the HTML template
                ##print("c2bphonenumber and email",lpgDataamount.EMAILS,lpgDataamount.PHONENUMBER)
                x2=datetime.now()
                val="-"
                val2=":"
                date2=str(x2.year)+val+str(x2.month)+val+str(x2.day)
                time2=str(x2.hour)+val2+str(x2.minute)+val2+str(x2.second)
                dynamic_data = {
                'name':i['name'] ,
                'message': 'Thank you for using our service!',
                'date':date2,
                'time':time2,
                'amount':i['amount'],
                'serialnumber':lpgDataamount.SERIAL_NUMBER,
                'cutomerCode':lpgDataamount.SERIAL_NUMBER,
                'TaxAmount':Taxamount,
                'unitsPurchased':gasUnits,
                'Email':lpgDataamount.EMAILS,
                'RemainingAmount':amt,
                'phoneNumber':lpgDataamount.PHONENUMBER,
                
                }
                # Your HTML template with dynamic data
                template = get_template('Invoice.html')
                #template = get_template('/home/ubuntu/7-12/Mpesapoc-latest/Mpesapoc-latest/Mpesapoc-latest/Mpesapoc/Myapp/templates/invoice.html')
                html_content = template.render(dynamic_data)
                # Generate PDF using xhtml2pdf
                pdf_data = io.BytesIO()
                
                pisa.CreatePDF(html_content, dest=pdf_data)
                ##print("useremail", lpgDataamount.EMAILS)
            # Compose email
                subject = '#Invoice Enerziff Solutions'
                message = 'Dear '+i['name']+',\n Your recharge of amount '+str(i['amount'])+'KSh sucessfully done. \n\n From,\n Enerziff Solutions'
                fromEmail=settings.EMAIL_HOST_USER
                to_email = lpgDataamount.EMAILS
                
                # Attach the PDF file to the email
                pdf_data.seek(0)  # Reset the file pointer to the beginning
                
                email = EmailMessage(subject, message,fromEmail, [to_email])
                email.attach('C2b_Invoice.pdf', pdf_data.getvalue(), 'application/pdf')
  
                account_sid = 'AC979edcba3714497157bbd9bc1b0e738c'
                auth_token = 'fd49326d3578971b8189c5a83390e9ac'
                twilio_phone_number = '++12177545789'


                to_phone_number = "+919820565918"
                # Message to be sent
                message_body = "Your recharge of amount "+str(i['amount'])+" KSh sucessfully done. \n\n From,\n Enerziff Solutions"

                # Initialize Twilio client
                clientSMS = Client(account_sid, auth_token)

               
                
            except Exception as e:
                print("try didn't executed",{e})
            


def userHistory1(number4,amount):
   
    a=lpg_Customer_Table.objects.get(PHONENUMBER=number4)
    Gas_Value=amount/10
    New_Added_Gas=Gas_Value
    print("gas value is",New_Added_Gas)
    ##print("this is Makr detials",a.NAME,a.PHONENUMBER)
    x=datetime.now()
    val="-"
    val2=":"
    date=str(x.year)+val+str(x.month)+val+str(x.day)
    time=str(x.hour)+val2+str(x.minute)+val2+str(x.second)
    ##print("the date and time is",date,time)
    historydata=userHistory(Name=a.NAME,SerialNumber=a.SERIAL_NUMBER,Amount=amount,PhoneNumber=a.PHONENUMBER,
                  Date=date,Time=time,PreviousAmount=a.BAL_AMOUNT,NowAddedAmount=amount,PreviousLPG=a.BAL_LPG,NewAddedLPG=New_Added_Gas)
    historydata.save()

def adminDashBoard():
    # here we are getting data to show that data on admin dashboard. we are calling this function some other functions also.
    numberOfUsers = lpg_Customer_Table.objects.all().values()
    countOfusers=len(numberOfUsers)
    startDate_0=datetime.now()-timedelta(days=7)
    endDate=datetime.now()
    historyData_by_dates=userHistory.objects.filter(Date__range=(startDate_0,endDate))
    dailyData = userHistory.objects.values('Date').annotate(sum=Sum('Amount')).order_by()
    amount_7days=0
    for i in historyData_by_dates:
        amount_7days=amount_7days+i.Amount
    Time_Value=datetime.now()-timedelta(hours=24)
    Users_Values=Lpg_Status_Infos.objects.values_list('SERIAL_NUMBER',flat=True)
    
    Gas_Values = Lpg_Status_Infos.objects.filter(VAlVE_TIME__range=[Time_Value,datetime.now()]).values_list('SERIAL_NUMBER',flat=True)
    print(Gas_Values)
    
    for i in Users_Values:
        if i in Gas_Values:
            Lpg_Status_Infos.objects.filter(SERIAL_NUMBER=i).update(CONNECTION_STATUS="online")
        else:
            Lpg_Status_Infos.objects.filter(SERIAL_NUMBER=i).update(CONNECTION_STATUS="offline")
    # Lpg_Status_Infos.objects.filter(SERIAL_NUMBER="EVM000000001").update(CONNECTION_STATUS="online")
    GAS_COUNT=len(Gas_Values)
    User_Online_Count=Lpg_Status_Infos.objects.filter(CONNECTION_STATUS="online").count()
    User_Offline_Count=Lpg_Status_Infos.objects.filter(CONNECTION_STATUS="offline").count()
    User_Faulty_Count=Lpg_Status_Infos.objects.filter(CONNECTION_STATUS="faulty").count()
    print("count is",User_Online_Count,User_Offline_Count)
    Battery_Count=Lpg_Status_Infos.objects.filter(BATTERY_TIME__range=[Time_Value,datetime.now()]).count()
    DEV_COUNT=lpg_Customer_Table.objects.filter(DEV_TIME__range=[Time_Value,datetime.now()]).count()
    # print("values counts are",Valve_Count,Battery_Count,Dev_Count)
    # ##print("last 7 days amount is ",amount_7days);
    # ##print("this is user history",historyData_by_dates)
    # ##print("number of users data",numberOfUsers)
   
    # for i in numberOfUsers:
    #     if(i['LOCATION']=="Kenya"):
    #         state="Meru"
    #         country="Kenya"
    #     else:
    #         ll=numberOfUsers[0]['LOCATION']
        
    #         geolocator = Nominatim(user_agent="MyApp")
    #         location = geolocator.reverse(ll)
    #         address = location.raw['address']
    #         ##print(address)
    #         country = address.get('country')
    #         state =address.get('state')
            
    #     ##print("location of user",state,country)
    #     us=usersLocationInfo(Name=i['NAME'],SerialNumber=i['SERIAL_NUMBER'],PhoneNumber=i['PHONENUMBER'],
    #                          State=state,Country=country)
    #     us.save()

    State_COUNT =  usersLocationInfo.objects.values('State').annotate(count=Count('State')).order_by()
    # GAS_COUNT = lpg_Customer_Table.objects.values('GAS_VALVE').annotate(count=Count('GAS_VALVE')).order_by()
    # DEV_COUNT = lpg_Customer_Table.objects.values('DEV_ENABLE').annotate(count=Count('DEV_ENABLE')).order_by()
   
    return countOfusers,amount_7days,State_COUNT,dailyData,User_Online_Count,User_Offline_Count,User_Faulty_Count,DEV_COUNT,GAS_COUNT
 
def usage_same_code(showUsageHistory):
    diffsum=0
    count=0
    gasdiffsum=dict()
    global gasdiffsum2
    gasdiffsum2=list()
    for i in range(len(showUsageHistory)):
        lastValue=len(showUsageHistory)-i
        starttime=showUsageHistory[i]['Time']
        if((i+1)<len(showUsageHistory)):
            lastTime=showUsageHistory[i+1]['Time']
        else:
            break
        starttime=starttime.hour *3600 +starttime.minute *60 + starttime.second
        lastTime=lastTime.hour *3600 + lastTime.minute *60 + lastTime.second
        # ##print("time difference",(lastTime-starttime))
        if((lastTime-starttime)==60):
            gasdiff=showUsageHistory[i]['BAL_LPG']-showUsageHistory[i+1]['BAL_LPG']
            # ##print("this is gasdiff",gasdiff)
            diffsum=diffsum+gasdiff
            count=count+1
            ##print(lastValue)
            if(lastValue==2):
                 diffsum="{:.3f}".format(diffsum)
                 beginTime2=showUsageHistory[i-(count-1)]['Time']
                 ##print("this is last begintime",beginTime2)
                 beginTime2=beginTime2.strftime("%H:%M:%S")
                 endTime2=showUsageHistory[i+1]['Time']
                 endTime2=endTime2.strftime("%H:%M:%S")
                 
                #  ##print("this is begin time",beginTime)
                #  ##print("this is end time",endTime)
                 if(beginTime!=endTime):
                    gasdiffsum['beginTime']=beginTime2
                    gasdiffsum['endTime']=endTime2
                    gasdiffsum['gasConsumption']=str(diffsum)+" units"
                    gasdiffsum2.append(gasdiffsum)
                   
                    # gasdiffsum2.append(beginTime)
                    # gasdiffsum2.append(endTime)
                    # gasdiffsum2.append(diffsum)
        else:
            diffsum="{:.3f}".format(diffsum)
            beginTime=showUsageHistory[i-count]['Time']
            beginTime=beginTime.strftime("%H:%M:%S")
            endTime=showUsageHistory[i]['Time']
            endTime=endTime.strftime("%H:%M:%S")
            
            # ##print("this is begin time",beginTime)
            # ##print("this is end time",endTime)
            if(beginTime!=endTime):
                
                gasdiffsum['beginTime']=beginTime
                gasdiffsum['endTime']=endTime
                gasdiffsum['gasConsumption']=str(diffsum)+" units"
                gasdiffsum2.append(gasdiffsum)
                gasdiffsum=dict()
                count=0
                # gasdiffsum2.append(beginTime)
                # gasdiffsum2.append(endTime)
                # gasdiffsum2.append(diffsum)
                # gasdiffsum2.append(gasdiffsum)
            diffsum=0
    return gasdiffsum2
def download_csv(request,userName):
    showUsageHistory = usageHistory.objects.filter(Name=userName)
    ##print("if length of showusagehistory",len(showUsageHistory))
    if(len(showUsageHistory)==0):
        ##print("it might can work for usagehistory")
        pass
    showUsageHistory=showUsageHistory.values()
    gasdiffsum2=usage_same_code(showUsageHistory)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Usage_History.csv"'

    writer = csv.writer(response)
    writer.writerow([
            'Meter Start_Time', 'Meter End_Time', 'Gas Consumption', 
    ])

    
    for i in gasdiffsum2:
        writer.writerow([
               i['beginTime'],i['endTime'],i['gasConsumption']
        ])
    return response



def usedHistory(request,userName):
    #this function is used to show the data how much gas they have used and time also. we are using this function for usage history.
    showUsageHistory = usageHistory.objects.filter(Name=userName)
    ##print("if length of showusagehistory",len(showUsageHistory))
    if(len(showUsageHistory)==0):
        ##print("it might can work for usagehistory")
        pass
    showUsageHistory=showUsageHistory.values()
    gasdiffsum2=usage_same_code(showUsageHistory)
    print("this is another data",gasdiffsum2)
    # diffsum=0
    # count=0
    # gasdiffsum=dict()
    # global gasdiffsum2
    # gasdiffsum2=list()
    # for i in range(len(showUsageHistory)):
    #     lastValue=len(showUsageHistory)-i
    #     starttime=showUsageHistory[i]['Time']
    #     if((i+1)<len(showUsageHistory)):
    #         lastTime=showUsageHistory[i+1]['Time']
    #     else:
    #         break
    #     starttime=starttime.hour *3600 +starttime.minute *60 + starttime.second
    #     lastTime=lastTime.hour *3600 + lastTime.minute *60 + lastTime.second
    #     # ##print("time difference",(lastTime-starttime))
    #     if((lastTime-starttime)==60):
    #         gasdiff=showUsageHistory[i]['BAL_LPG']-showUsageHistory[i+1]['BAL_LPG']
    #         # ##print("this is gasdiff",gasdiff)
    #         diffsum=diffsum+gasdiff
    #         count=count+1
    #         ##print(lastValue)
    #         if(lastValue==2):
    #              diffsum="{:.3f}".format(diffsum)
    #              beginTime2=showUsageHistory[i-(count-1)]['Time']
    #              ##print("this is last begintime",beginTime2)
    #              beginTime2=beginTime2.strftime("%H:%M:%S")
    #              endTime2=showUsageHistory[i+1]['Time']
    #              endTime2=endTime2.strftime("%H:%M:%S")
                 
    #             #  ##print("this is begin time",beginTime)
    #             #  ##print("this is end time",endTime)
    #              if(beginTime!=endTime):
    #                 gasdiffsum['beginTime']=beginTime2
    #                 gasdiffsum['endTime']=endTime2
    #                 gasdiffsum['gasConsumption']=str(diffsum)+" units"
    #                 gasdiffsum2.append(gasdiffsum)
                   
    #                 # gasdiffsum2.append(beginTime)
    #                 # gasdiffsum2.append(endTime)
    #                 # gasdiffsum2.append(diffsum)
    #     else:
    #         diffsum="{:.3f}".format(diffsum)
    #         beginTime=showUsageHistory[i-count]['Time']
    #         beginTime=beginTime.strftime("%H:%M:%S")
    #         endTime=showUsageHistory[i]['Time']
    #         endTime=endTime.strftime("%H:%M:%S")
            
    #         # ##print("this is begin time",beginTime)
    #         # ##print("this is end time",endTime)
    #         if(beginTime!=endTime):
                
    #             gasdiffsum['beginTime']=beginTime
    #             gasdiffsum['endTime']=endTime
    #             gasdiffsum['gasConsumption']=str(diffsum)+" units"
    #             gasdiffsum2.append(gasdiffsum)
    #             gasdiffsum=dict()
    #             count=0
    #             # gasdiffsum2.append(beginTime)
    #             # gasdiffsum2.append(endTime)
    #             # gasdiffsum2.append(diffsum)
    #             # gasdiffsum2.append(gasdiffsum)
    #         diffsum=0
           
        

    ##print(gasdiffsum2)  
    return render(request,'usageHistoryUser.html',{"usageHistory":gasdiffsum2,"name":userName})
def usedHistoryMailSend(request,userName):
    MailSendLpgData=lpg_Customer_Table.objects.get(NAME=userName)
    try:
        message="Thank you from Enerziff Solutions."
        serialNumber=MailSendLpgData.SERIAL_NUMBER
        EmailId=MailSendLpgData.EMAILS
        phonenumber=MailSendLpgData.PHONENUMBER
        ##print("this is gasfiddlentht",gasdiffsum2)
        if(gasdiffsum2):
            usageMailSend(userName,serialNumber,phonenumber,gasdiffsum2,EmailId,value="userSendingMail")
        else:
            return render(request,'usageHistoryUser.html',{"usageHistory":gasdiffsum2,"name":userName,"status":"you do not have any history to send mail"})
    # Dynamic data to be passed to the HTML template
        # x2=datetime.now()
        # val="-"
        # val2=":"
        # date2=str(x2.year)+val+str(x2.month)+val+str(x2.day)
        # time2=str(x2.hour)+val2+str(x2.minute)+val2+str(x2.second)
        # dynamic_data = {
        #         'name': name,
        #         'message': 'Thank you for using our service!',
        #         'date':date2,
        #         'time':time2,
        #         'serialnumber':MailSendLpgData.SERIAL_NUMBER,
        #         'CustomerCode':MailSendLpgData.SERIAL_NUMBER,
        #         'usageHistory':gasdiffsum2    
        #                 }
                               
        # # Your HTML template with dynamic data
        # template = get_template('UsageHisotyrMail.html')
        # #template = get_template('/home/ubuntu/7-12/Mpesapoc-latest/Mpesapoc-latest/Mpesapoc-latest/Mpesapoc/Myapp/templates/invoice.html')
        # html_content = template.render(dynamic_data)

        # # Generate PDF using xhtml2pdf
        # pdf_data = io.BytesIO()
        # pisa.CreatePDF(html_content, dest=pdf_data)

        #  # Compose email
        # subject = '#BalanceAlert  Solutions'
        # #message = 'Dear '+name+',\n Your recharge of amount '+Balence+'KSh sucessfully done. \n\n From,\n Enerziff Solutions'
        # message="Balance alert message"
        # fromEmail=settings.EMAIL_HOST_USER
        # to_email = MailSendLpgData.EMAILS

        # ##print("user email",to_email)
        # # Attach the PDF file to the email
        # pdf_data.seek(0)  # Reset the file pointer to the beginning
        # email = EmailMessage(subject, message,fromEmail, [to_email])
        # email.attach('UsageHistory.pdf', pdf_data.getvalue(), 'application/pdf')

        # # Send the email
        # email.send()
        ##print("this is the typeof gasdiffsum2",type(gasdiffsum2))
        return render(request,'usageHistoryUser.html',{"usageHistory":gasdiffsum2,"name":userName,"status":"Mail Sent Successfully"})
        #updating mailstatus   
    except Exception as e:
        print("some error occured",{e})                                             
    return render(request,'usageHistoryUser.html',{"usageHistory":gasdiffsum2,"name":userName})
    pass

def usedHistoryAdmin1(request,UserName,NAME,user_type):
    global adminUserUsage
    global adminGasDiffSum
    adminUserUsage=UserName
    showUsageHistory = usageHistory.objects.filter(Name=UserName)
    showUsageHistory=showUsageHistory.values()
    adminGasDiffSum=usage_same_code(showUsageHistory)
    # diffsum=0
    # count=0
    # gasdiffsum=dict()
    # adminGasDiffSum=list()
    # for i in range(len(showUsageHistory)):
    #     lastValue=len(showUsageHistory)-i
    #     starttime=showUsageHistory[i]['Time']
    #     if((i+1)<len(showUsageHistory)):
    #         lastTime=showUsageHistory[i+1]['Time']
    #     else:
    #         break
    #     starttime=starttime.hour *3600 +starttime.minute *60 + starttime.second
    #     lastTime=lastTime.hour *3600 + lastTime.minute *60 + lastTime.second
    #     # ##print("time difference",(lastTime-starttime))
    #     if((lastTime-starttime)==60):
    #         gasdiff=showUsageHistory[i]['BAL_LPG']-showUsageHistory[i+1]['BAL_LPG']
    #         # ##print("this is gasdiff",gasdiff)
    #         diffsum=diffsum+gasdiff
    #         count=count+1
    #         ##print(lastValue)
    #         if(lastValue==2):
    #              diffsum="{:.3f}".format(diffsum)
    #              beginTime2=showUsageHistory[i-(count-1)]['Time']
    #              ##print("this is last begintime",beginTime2)
    #              beginTime2=beginTime2.strftime("%H:%M:%S")
    #              endTime2=showUsageHistory[i+1]['Time']
    #              endTime2=endTime2.strftime("%H:%M:%S")
                 
    #             #  ##print("this is begin time",beginTime)
    #             #  ##print("this is end time",endTime)
    #              if(beginTime!=endTime):
    #                 gasdiffsum['beginTime']=beginTime2
    #                 gasdiffsum['endTime']=endTime2
    #                 gasdiffsum['gasConsumption']=str(diffsum)+" units"
    #                 adminGasDiffSum.append(gasdiffsum)
                   
    #                 # gasdiffsum2.append(beginTime)
    #                 # gasdiffsum2.append(endTime)
    #                 # gasdiffsum2.append(diffsum)
    #     else:
    #         diffsum="{:.3f}".format(diffsum)
    #         beginTime=showUsageHistory[i-count]['Time']
    #         beginTime=beginTime.strftime("%H:%M:%S")
    #         endTime=showUsageHistory[i]['Time']
    #         endTime=endTime.strftime("%H:%M:%S")
            
    #         # ##print("this is begin time",beginTime)
    #         # ##print("this is end time",endTime)
    #         if(beginTime!=endTime):
                
    #             gasdiffsum['beginTime']=beginTime
    #             gasdiffsum['endTime']=endTime
    #             gasdiffsum['gasConsumption']=str(diffsum)+" units"
    #             adminGasDiffSum.append(gasdiffsum)
    #             gasdiffsum=dict()
    #             count=0
    #             # gasdiffsum2.append(beginTime)
    #             # gasdiffsum2.append(endTime)
    #             # gasdiffsum2.append(diffsum)
    #             # gasdiffsum2.append(gasdiffsum)
    #         diffsum=0
            ##print("not getting name2 in varun page",name2)
    return render(request,'usageHistoryAdmin.html',{"usageHistory":adminGasDiffSum,"NAME":NAME,"user_type":user_type})
def AdminHistoryMailSend(request):
    MailSendLpgData=lpg_Customer_Table.objects.get(NAME=adminUserUsage)
    try:
        serialNumber=MailSendLpgData.SERIAL_NUMBER
        EmailId=MailSendLpgData.EMAILS,
        phonenumber=MailSendLpgData.PHONENUMBER
        ##print("how admin useremail is look like",EmailId[0])
        EmailId=EmailId[0]
        usageMailSend(adminUserUsage,serialNumber, phonenumber,adminGasDiffSum,EmailId,value="adminSendingMail")
    # Dynamic data to be passed to the HTML template
        # x2=datetime.now()
        # val="-"
        # val2=":"
        # date2=str(x2.year)+val+str(x2.month)+val+str(x2.day)
        # time2=str(x2.hour)+val2+str(x2.minute)+val2+str(x2.second)
        # dynamic_data = {
        #         'name': name,
        #         'message': 'Thank you for using our service!',
        #         'date':date2,
        #         'time':time2,
        #         'serialnumber':MailSendLpgData.SERIAL_NUMBER,
        #         'CustomerCode':MailSendLpgData.SERIAL_NUMBER,
        #         'usageHistory':adminGasDiffSum    
        #                 }
                               
        # # Your HTML template with dynamic data
        # template = get_template('UsageHisotyrMail.html')
        # #template = get_template('/home/ubuntu/7-12/Mpesapoc-latest/Mpesapoc-latest/Mpesapoc-latest/Mpesapoc/Myapp/templates/invoice.html')
        # html_content = template.render(dynamic_data)

        # # Generate PDF using xhtml2pdf
        # pdf_data = io.BytesIO()
        # pisa.CreatePDF(html_content, dest=pdf_data)

        #  # Compose email
        # subject = '#BalanceAlert  Solutions'
        # #message = 'Dear '+name+',\n Your recharge of amount '+Balence+'KSh sucessfully done. \n\n From,\n Enerziff Solutions'
        # message="Balance alert message"
        # fromEmail=settings.EMAIL_HOST_USER
        # to_email = MailSendLpgData.EMAILS

        # ##print("admin user email",to_email)
        # # Attach the PDF file to the email
        # pdf_data.seek(0)  # Reset the file pointer to the beginning
        # email = EmailMessage(subject, message,fromEmail, [to_email])
        # email.attach('UsageHistory.pdf', pdf_data.getvalue(), 'application/pdf')

        # # Send the email
        # email.send()
        ##print("not getting name2 in varun page",name2)
        return render(request,'usageHistoryAdmin.html',{"usageHistory":adminGasDiffSum,"NAME":name2,"status":"Mail Sent Successfully"})
        #updating mailstatus   
    except Exception as e:
        print("some error occured",{e}) 
    ##print("not getting name2 in varun page",name2)                                            
    return render(request,'usageHistoryAdmin.html',{"usageHistory":adminGasDiffSum,"NAME":name2})
    pass
def MeterStatus(request,PhoneNumber):
    ##print("this is meterstatus person phonenumber",PhoneNumber)
    client.publish(outDevice,"status")
    return HttpResponse("success")

def usedHistoryAdmin():
    return HttpResponse("successs")

def MailSendingFunction(username,SerialNumber,Phonenumber,Balence,Emailid,value):
    if(value=="BalanceAlert"):
        htmlPage="BalanceAlert.html"
        pdfPage="BalanceAlert.pdf"
    try:
        # Dynamic data to be passed to the HTML template
        x2=datetime.now()
        val="-"
        val2=":"
        date2=str(x2.year)+val+str(x2.month)+val+str(x2.day)
        time2=str(x2.hour)+val2+str(x2.minute)+val2+str(x2.second)
        dynamic_data = {
                'name': username,
                'message': 'Thank you for using our service!',
                'date':date2,
                'time':time2,
                'balence':Balence,
                'serialnumber':SerialNumber,
                'CustomerCode':SerialNumber,
                'Email':Emailid ,
                'phoneNumber':Phonenumber 
                    }
                               
         # Your HTML template with dynamic data
        template = get_template(htmlPage)
        #template = get_template('/home/ubuntu/7-12/Mpesapoc-latest/Mpesapoc-latest/Mpesapoc-latest/Mpesapoc/Myapp/templates/invoice.html')
        html_content = template.render(dynamic_data)

        # Generate PDF using xhtml2pdf
        pdf_data = io.BytesIO()
        pisa.CreatePDF(html_content, dest=pdf_data)

                                # Compose email
        subject = '#BalanceAlert  Solutions'
         #message = 'Dear '+name+',\n Your recharge of amount '+Balence+'KSh sucessfully done. \n\n From,\n Enerziff Solutions'
        message="Balance alert message"
        fromEmail=settings.EMAIL_HOST_USER
        to_email = Emailid

        ##print("user email",to_email)
        # Attach the PDF file to the email
        pdf_data.seek(0)  # Reset the file pointer to the beginning
        email = EmailMessage(subject, message,fromEmail, [to_email])
        email.attach(pdfPage, pdf_data.getvalue(), 'application/pdf')

        # Send the email
        email.send()
        #updating mailstatus
        
    except Exception as e:
        print(f"An error occurred: {e}")
        # return HttpResponse("Error sending email.")
    pass

def usageMailSend(name1,serialNumber,phonenumber,Usagesum,EmailId,value):
    x2=datetime.now()
    val="-"
    val2=":"
    date2=str(x2.year)+val+str(x2.month)+val+str(x2.day)
    time2=str(x2.hour)+val2+str(x2.minute)+val2+str(x2.second)

    if value=="userSendingMail":
      diffSum=Usagesum
      htmlPage="UsageHisotyrMail.html"
      pdfPage='UsageHistory.pdf'
      Subject="#Gas Usage History Request"
      Message="The below attached file is having the information about your Usage of gas."
      
    elif value=="adminSendingMail":
      diffSum=Usagesum
      htmlPage="UsageHisotyrMail.html"
      pdfPage='AdminSendUsage.pdf'
      Subject="#Gas Usage History Send By Admin"
      Message="The below attached file is having the information about your Usage of gas. This mail is sent by Enerziff Solution Admin"
    
    ##print("this is sudhakarEmail",EmailId)
    try:
        
        dynamic_data = {
                'name': name1,
                'message': 'Thank you for using our service!',
                'date':date2,
                'time':time2,
                'serialnumber':serialNumber,
                'CustomerCode':serialNumber,
                'usageHistory':diffSum,
                'Email':EmailId,
                'phoneNumber':phonenumber    
                        }
                               
        # Your HTML template with dynamic data
        template = get_template(htmlPage)
        #template = get_template('/home/ubuntu/7-12/Mpesapoc-latest/Mpesapoc-latest/Mpesapoc-latest/Mpesapoc/Myapp/templates/invoice.html')
        html_content = template.render(dynamic_data)

        # Generate PDF using xhtml2pdf
        pdf_data = io.BytesIO()
        pisa.CreatePDF(html_content, dest=pdf_data)

         # Compose email
        subject = Subject
        #message = 'Dear '+name+',\n Your recharge of amount '+Balence+'KSh sucessfully done. \n\n From,\n Enerziff Solutions'
        message=Message
        fromEmail=settings.EMAIL_HOST_USER
        to_email = EmailId

        ##print("user email",to_email)
        # Attach the PDF file to the email
        pdf_data.seek(0)  # Reset the file pointer to the beginning
        email = EmailMessage(subject, message,fromEmail, [to_email])
        email.attach(pdfPage, pdf_data.getvalue(), 'application/pdf')

        # Send the email
        email.send()
        #updating mailstatus
        
    except Exception as e:
        print(f"An error occurred: {e}")
        # return HttpResponse("Error sending email.")
    
def checking():
    ##print("this is for chekcing weather another method can run cuncurrntly")
    pass


def setPrices(request,NAME,user_type):
    x2=datetime.now()
    val="-"
    val2=":"
    date2=str(x2.year)+val+str(x2.month)+val+str(x2.day)
    time2=str(x2.hour)+val2+str(x2.minute)+val2+str(x2.second)
    Latest_Price=" "
    Latest_Units=" "
    GasPrices_Details=GasPrices.objects.all().values()
    try:
        
        ##print(GasPrices_Details)
        GasPrices_latestPrice=GasPrices.objects.latest('price')
        Latest_Price=GasPrices_latestPrice.price
        Latest_Units=GasPrices_latestPrice.gas_units
    except Exception as e:
        print("error is",{e})
    if request.method == 'POST':
        Units=request.POST['units']
        Unit_Price=request.POST['price']
       
        ##print("Units and Unit Prices is",Units,Unit_Price)
        GasPrices_Values=GasPrices(admin_name=NAME,gas_units=Units,price=Unit_Price,date=date2,time=time2)
        GasPrices_Values.save()
        return render(request,'setPrices.html',{"NAME":NAME,"user_type":user_type,"status":"Changes Applied Succesfuly",
                                                "latestPrice":Unit_Price,"latestUnits":Units,
                                                "gaspriceDetails":GasPrices_Details})
    return render(request,'setPrices.html',{"NAME":NAME,"user_type":user_type,"latestPrice":Latest_Price,"latestUnits":Latest_Units,
                                            "gaspriceDetails":GasPrices_Details})
def generate_random_token():
    characters = string.ascii_letters + string.digits
    random_token = ''.join(secrets.choice(characters) for _ in range(8))
    return random_token

def raiseComplaint(request,userName):
    if request.method == "POST":
        x2=datetime.now()
        val="-"
        val2=":"    
        date2=str(x2.year)+val+str(x2.month)+val+str(x2.day)
        time2=str(x2.hour)+val2+str(x2.minute)+val2+str(x2.second)
        userData=lpg_Customer_Table.objects.get(NAME=userName)
        token = generate_random_token()
        FirstProblem=request.POST.get('selected_problem','')
        SecondProblem=request.POST.get('selected_problem1','')
        Description=request.POST.get('description')
        ##print("the problems are ", FirstProblem,SecondProblem)
        ##print("the problems are ", Description)
        UserIssues=customerIssues(user_name=userName,problem_one=FirstProblem,problem_two=SecondProblem,
                                  description=Description,date=date2,time=time2,phonenumber=userData.PHONENUMBER,email=userData.EMAILS, token=token, status = False)
        UserIssues.save()
        return render(request,'userComplaints.html',{"name":userName,"status":"You problem is updated."})
    return render(request,'userComplaints.html',{"name":userName})


def userComplainHistory(request,userName):
    complaints = customerIssues.objects.filter(user_name=userName).values()
    return render(request, 'userComplaintHistory.html', {"complaints":complaints,"name":userName})
    
def adminComplaintHistory(request,NAME,user_type):
    if user_type=="admin":
        try:
            issues = customerIssues.objects.all().values()
        except:
            issues=""
            print("in admin complaintHistory data may be not found")
    elif user_type=="Area_Lead":
        try:
            issues = customerIssues.objects.filter(Area_Lead=NAME).values()
        except:
            issues=""
            print("in admin complaintHistory data may be not found")
    return render(request, 'admin_ShowComplaints.html', {"compalintHistory":issues,"NAME":NAME,"user_type":user_type})

def issuesSolving(request):
    Issues_Data=customerIssues.objects.all().values()
    ##print("this is present data we have in issues",Issues_Data)
    return render(request,'issuesSolving.html',{"NAME":name2,"userissues":Issues_Data})

def forgotPassword(request):
    global OtpNumber
    global Forgot_UserData
    global Forgot_UserName
    if request.method == 'POST':
        Forgot_UserName=request.POST['name']
        Forgot_UserData=Admin.objects.get(name=Forgot_UserName)
        if Forgot_UserData:
            OtpNumber=random.randint(100000,999999)
            subject = 'Email with Template'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = ['indlasudhakar13@gmail.com',]
            message=" your request to change password is accepted \n Your 6 digit otp is"+str(OtpNumber)
            context = {'name': 'John Doe'}
            send_mail(subject, message, from_email, recipient_list, )
            return render(request,'forgotPassword.html',{"status":"OTP sent to your mail","username":Forgot_UserName})
        else:
            return render(request,'forgotPassword.html',{"status":"wrong username\n please go and register","username":Forgot_UserName})
        

    return render(request,'forgotPassword.html')
def validatePassword(request):
    if request.method=='POST':
        OtpCheck=request.POST['otpnumber']
        Password=request.POST['password']
        ConfirmPassword=request.POST['confirmpassword']
        if(Password!=ConfirmPassword):
            return render(request,'forgotPassword.html',{"status":"password and comfirm password not matched","username":Forgot_UserName,
                                                         "otp":OtpCheck,"password":Password,"confirmpassword":ConfirmPassword})
        if(int(OtpCheck)==int(OtpNumber)):
            ##print("passwrod and confirm password is ",Password,ConfirmPassword)
            ##print("otp validation successfully completed")
            Forgot_UserData.password=Password
            Forgot_UserData.save()
            return render(request,'forgotPassword.html',{"status":"password change successfully"})
        else:
            return render(request,'forgotPassword.html',{"status":"wrong OTP","username":Forgot_UserName,
                                                         "otp":OtpCheck,"password":Password,"confirmpassword":ConfirmPassword})
    return render(request,'forgotPassword.html')

def userForgotPassword(request):
    global OtpNumber
    global Forgot_UserData
    global Forgot_UserName
    if request.method == 'POST':
        Forgot_UserName=request.POST['name']
        Forgot_UserData=Register.objects.get(name=Forgot_UserName)
        if Forgot_UserData:
            OtpNumber=random.randint(100000,999999)
            subject = 'Email with Template'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = ['indlasudhakar13@gmail.com',]
            message=" your request to change password is accepted \n Your 6 digit otp is"+str(OtpNumber)
            context = {'name': 'John Doe'}
            send_mail(subject, message, from_email, recipient_list, )
            return render(request,'forgotPassword.html',{"status":"OTP sent to your mail","username":Forgot_UserName})
        else:
            return render(request,'forgotPassword.html',{"status":"wrong username\n please go and register","username":Forgot_UserName})
    return render(request,'userForgotPassword.html')

def userValidatePassword(request):
    if request.method=='POST':
        OtpCheck=request.POST['otpnumber']
        Password=request.POST['password']
        ConfirmPassword=request.POST['confirmpassword']
        if(Password!=ConfirmPassword):
            return render(request,'forgotPassword.html',{"status":"password and comfirm password not matched","username":Forgot_UserName,
                                                         "otp":OtpCheck,"password":Password,"confirmpassword":ConfirmPassword})
        if(int(OtpCheck)==int(OtpNumber)):
            ##print("passwrod and confirm password is ",Password,ConfirmPassword)
            ##print("otp validation successfully completed")
            Forgot_UserData.password=Password
            Forgot_UserData.save()
            return render(request,'forgotPassword.html',{"status":"password change successfully"})
        else:
            return render(request,'forgotPassword.html',{"status":"wrong OTP","username":Forgot_UserName,
                                                         "otp":OtpCheck,"password":Password,"confirmpassword":ConfirmPassword})
    return render(request,'userForgotPassword.html')
def getAdmin_message(request):
    if request.method=='POST':
        data=request.POST.get('admin_message')
        ##print("the requested data is ",data)
    return HttpResponse("scueess")
def chatBot(request):
    responses = {
    "greeting": "Hello! How can I help you today?",
    "order_status": "To check your order status, please visit the 'Order Status' page on our website.",
    "payment_issue": "For payment-related issues, please contact our support team at support@example.com.",
    # Add more responses as needed
}
    return render(request,'chatBot.html',{"NAME":name})
    
    return HttpResponse("Success")
    
def checking():
    print("sudhakar")

def Customer_Reports(request,NAME,user_type):
    User_Names=lpg_Customer_Table.objects.values_list('NAME', flat=True)
    City_names=userHistory.objects.values_list('Location',flat=True).distinct()
    print("city names are",City_names)
    All_Meters=userHistory.objects.aggregate(total_amount=Sum('NowAddedAmount'))['total_amount']
    data=adminDashBoard()
    return render(request,'DisplayRechargeAmount.html',{'NAME':NAME,"user_type":user_type,"mainData":data,'usersLoc':data[2],
                                                        'dailyData':data[3],"gasvalvestatus":data[-1],"devstatus":data[-2],
                                                        "usernames":User_Names,"City_Names":City_names,
                                                        "All_Recharge":All_Meters})
def Per_Day(date3):
     print("this function is calling",date3)
 
     dataByDate=userHistory.objects.filter(Date=date3).aggregate(total_amount=Sum('NowAddedAmount'))['total_amount']
     Totaldata_By_Date=userHistory.objects.filter(Date=date3).values()
     return dataByDate,Totaldata_By_Date
def Per_Month(Month_Number,Year):
    Month_Data = userHistory.objects.filter(Date__year=Year,Date__month=Month_Number).aggregate(total_amount=Sum('NowAddedAmount'))['total_amount']
    Totaldata_By_Date=userHistory.objects.filter(Date__year=Year,Date__month=Month_Number).values()
    return Month_Data,Totaldata_By_Date
def Individual(name):
     Indevidual_Values = userHistory.objects.filter(Name=name).values_list('NowAddedAmount', flat=True).aggregate(total_amount=Sum('NowAddedAmount'))['total_amount']
     Totaldata_By_Date=userHistory.objects.filter(Name=name).values()
     return Indevidual_Values,Totaldata_By_Date
def Individual_MonthWise(name,Year,Month_Number):
      Indevidual_Values = userHistory.objects.filter(Date__year=Year,Date__month=Month_Number,Name=name).values_list('NowAddedAmount', flat=True).aggregate(total_amount=Sum('NowAddedAmount'))['total_amount']
      Totaldata_By_Date=userHistory.objects.filter(Date__year=Year,Date__month=Month_Number,Name=name).values()
      return Indevidual_Values,Totaldata_By_Date
def City_Wise(City_Name):
    city_wise = userHistory.objects.filter(Location=City_Name).values_list('NowAddedAmount', flat=True).aggregate(total_amount=Sum('NowAddedAmount'))['total_amount']
    Totaldata_By_Date=userHistory.objects.filter(Location=City_Name).values()
    return city_wise,Totaldata_By_Date
def City_Month_Wise(City_Name,Month_Number,Year):
    
    city_wise = userHistory.objects.filter(Date__year=Year,Date__month=Month_Number,Location=City_Name).values_list('NowAddedAmount', flat=True).aggregate(total_amount=Sum('NowAddedAmount'))['total_amount']
    Totaldata_By_Date=userHistory.objects.filter(Date__year=Year,Date__month=Month_Number,Location=City_Name).values()
    return city_wise,Totaldata_By_Date
def Date_Betweens(Start_Date,End_Date):
    Between_Dates=userHistory.objects.filter(Date__range=(Start_Date,End_Date)).values_list('NowAddedAmount',flat=True).aggregate(total_amount=Sum('NowAddedAmount'))['total_amount']
    Totaldata_By_Date=userHistory.objects.filter(Date__range=(Start_Date,End_Date)).values()
    return Between_Dates,Totaldata_By_Date
def Download_Per_Day(request,input1,request_type):
    date3=input1
    if request_type=="per_day":
        data=Per_Day(date3)
    data=data[1]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Specifid_Date.csv"'

    writer = csv.writer(response)
    writer.writerow([
            'SerialNumber', 'Name', 'Previous Amount', 'Recharged Amount','Previous LPG',
            'Now Added LPG','Phone Number','Time'
    ])
    
    print("data is",data)
    for i in data:
        print("loop in",i)    
        writer.writerow([
               i['SerialNumber'],i['Name'],i['PreviousAmount'],
               i['NowAddedAmount'],i['PreviousLPG'],i['NewAddedLPG'],i['PhoneNumber'],
               i['Time']
        ])
    return response
def Download_Individual(request,input1):
    name=input1
   
    data=Individual(name)
    data=data[1]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Specific_Persion.csv"'

    writer = csv.writer(response)
    writer.writerow([
            'SerialNumber', 'Name', 'Previous Amount', 'Recharged Amount','Previous LPG',
            'Now Added LPG','Phone Number','Time'
    ])
    
    print("data is",data)
    for i in data:
        
        writer.writerow([
               i['SerialNumber'],i['Name'],i['PreviousAmount'],
               i['NowAddedAmount'],i['PreviousLPG'],i['NewAddedLPG'],i['PhoneNumber'],
               i['Time']
        ])
    return response
def Download_Month_Individual(request,input1,input2,input3):
    name=input1
    Year=input2
    Month_Number=input3
   
    data=Individual_MonthWise(name,Year,Month_Number)
    data=data[1]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Person_Month.csv"'

    writer = csv.writer(response)
    writer.writerow([
            'SerialNumber', 'Name', 'Previous Amount', 'Recharged Amount','Previous LPG',
            'Now Added LPG','Phone Number','Time'
    ])
    
    print("data is",data)
    for i in data:
        
        writer.writerow([
               i['SerialNumber'],i['Name'],i['PreviousAmount'],
               i['NowAddedAmount'],i['PreviousLPG'],i['NewAddedLPG'],i['PhoneNumber'],
               i['Time']
        ])
    return response
def Download_Location(request,input1):
    City_Name=input1
   
    data=City_Wise(City_Name)
    data=data[1]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Specific_Location.csv"'

    writer = csv.writer(response)
    writer.writerow([
            'SerialNumber', 'Name', 'Previous Amount', 'Recharged Amount','Previous LPG',
            'Now Added LPG','Phone Number','Time'
    ])
    
    print("data is",data)
    for i in data:
        
        writer.writerow([
               i['SerialNumber'],i['Name'],i['PreviousAmount'],
               i['NowAddedAmount'],i['PreviousLPG'],i['NewAddedLPG'],i['PhoneNumber'],
               i['Time']
        ])
    return response
def Download_Location_Month(request,input1,input2,input3):
    City_Name=input1
    Year=input2
    Month_Number=input3
    data=City_Month_Wise(City_Name,Month_Number,Year)
    data=data[1]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Location_Month.csv"'

    writer = csv.writer(response)
    writer.writerow([
            'SerialNumber', 'Name', 'Previous Amount', 'Recharged Amount','Previous LPG',
            'Now Added LPG','Phone Number','Time'
    ])
    
    print("data is",data)
    for i in data:
        
        writer.writerow([
               i['SerialNumber'],i['Name'],i['PreviousAmount'],
               i['NowAddedAmount'],i['PreviousLPG'],i['NewAddedLPG'],i['PhoneNumber'],
               i['Time']
        ])
    return response
def Download_Between_Dates(request,input1,input2):
    Start_Date=input1
    End_Date=input2
    
    data=Date_Betweens(Start_Date,End_Date)
    data=data[1]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Date_Betweens.csv"'

    writer = csv.writer(response)
    writer.writerow([
            'SerialNumber', 'Name', 'Previous Amount', 'Recharged Amount','Previous LPG',
            'Now Added LPG','Phone Number','Time'
    ])
    
    print("data is",data)
    for i in data:
        
        writer.writerow([
               i['SerialNumber'],i['Name'],i['PreviousAmount'],
               i['NowAddedAmount'],i['PreviousLPG'],i['NewAddedLPG'],i['PhoneNumber'],
               i['Time']
        ])
    return response
def Download_Per_Month(request,input1,input2):
    Month_Number=input1
    Year=input2
    data=Per_Month(Month_Number,Year)
    data=data[1]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Specific_Month.csv"'

    writer = csv.writer(response)
    writer.writerow([
            'SerialNumber', 'Name', 'Previous Amount', 'Recharged Amount','Previous LPG',
            'Now Added LPG','Phone Number','Time'
    ])
    
    
    for i in data:
        
        writer.writerow([
               i['SerialNumber'],i['Name'],i['PreviousAmount'],
               i['NowAddedAmount'],i['PreviousLPG'],i['NewAddedLPG'],i['PhoneNumber'],
               i['Time']
        ])
    return response  
def DisplayRecharge_Amount(request,request_type,NAME,user_type):
    User_Names=lpg_Customer_Table.objects.values_list('NAME', flat=True)
    City_names=userHistory.objects.values_list('Location',flat=True).distinct()
    print("city names are",City_names)
    All_Meters=userHistory.objects.aggregate(total_amount=Sum('NowAddedAmount'))['total_amount']
    print("all meters amount is",All_Meters)
    print("usernames are",User_Names)
    print("this is request_type",request_type)
    name2="sudhakar"
    if request.method == "POST":
            request_name=request_type
            if request_name=="per_day":
                date3=request.POST['date']
                Data_From_Method=Per_Day(date3)
                print("Datafrommethod",Data_From_Method)
                dataByDate=Data_From_Method[0]
                Totaldata_By_Date=Data_From_Method[1]
                
                # ##print("date valueadminHome",date3)
                # dataByDate=userHistory.objects.filter(Date=date3).aggregate(total_amount=Sum('NowAddedAmount'))['total_amount']
                # Totaldata_By_Date=userHistory.objects.filter(Date=date3).values()
                # print("totaldatais",Totaldata_By_Date)
                # ##print("these data is given by date",dataByDate)
                # for i in dataByDate:
                #     ##print("the specific data",i.Name)
                if dataByDate:
                    data=adminDashBoard()
                    # ##print("the array is ",data[-1])
                    return render(request,'DisplayRechargeAmount.html',{'NAME':NAME,"user_type":user_type,"mainData":data,'usersLoc':data[2],
                                                            'dailyData':data[3],"gasvalvestatus":data[-1],"devstatus":data[-2],"queryset":dataByDate,
                                                            "usernames":User_Names,"City_Names":City_names,
                                                        "All_Recharge":All_Meters,"TotalData":Totaldata_By_Date,"input1":date3})
                
            elif request_name=="per_month":
                Month_Number=request.POST.get('month_number')
                Year=request.POST.get('year')
              
                Data_From_Method= Per_Month(Month_Number,Year)
                print("Datafrommethod",Data_From_Method)
                Month_Data=Data_From_Method[0]
                Totaldata_By_Date=Data_From_Method[1]
                # Month_Data = userHistory.objects.filter(Date__year=Year,Date__month=Month_Number).aggregate(total_amount=Sum('NowAddedAmount'))['total_amount']
                # Totaldata_By_Date=userHistory.objects.filter(Date__year=Year,Date__month=Month_Number).values()
        #         print("month number is",Month_Data)
        #         time_threshold = datetime.now() - timedelta(days=30)
        #         print("time is",time_threshold)
        # # Retrieve all rows created in the last 24 hours
        #         rows_last_24_hours = userHistory.objects.filter(Date__range=(time_threshold, datetime.now()))
        #         print("data is ",rows_last_24_hours)
                data=adminDashBoard()
                try:
                    if Month_Data:
                            print("year is",Year)
                            # ##print("the array is ",data[-1])
                            return render(request,'DisplayRechargeAmount.html',{'NAME':NAME,"user_type":user_type,"mainData":data,'usersLoc':data[2],
                                                                   'dailyData':data[3],"gasvalvestatus":data[-1],"devstatus":data[-2],
                                                                   "queryset":Month_Data,"usernames":User_Names,"City_Names":City_names,
                                                        "All_Recharge":All_Meters,"TotalData":Totaldata_By_Date,
                                                                  "MONTH":Month_Number,"YEAR":Year})
                    else:
                         return render(request,'DisplayRechargeAmount.html',{'NAME':NAME,"user_type":user_type,"mainData":data,'usersLoc':data[2],
                                                                   'dailyData':data[3],"gasvalvestatus":data[-1],"devstatus":data[-2],
                                                                   "queryset":"no data present","usernames":User_Names,"City_Names":City_names,
                                                        "All_Recharge":All_Meters})
                except:
                    print("data not found in month year wise")
                    Month_Data="not found"
                    return render(request,'DisplayRechargeAmount.html',{'NAME':NAME,"user_type":user_type,"mainData":data,'usersLoc':data[2],
                                                                    'dailyData':data[3],"gasvalvestatus":data[-1],
                                                                    "devstatus":data[-2],"queryset":Month_Data,"usernames":User_Names,"City_Names":City_names,
                                                        "All_Recharge":All_Meters})
            elif request_name=="individual":
                name=request.POST.get("name")
                Data_From_Method= Individual(name)
                print("Datafrommethod",Data_From_Method)
                Indevidual_Values=Data_From_Method[0]
                Totaldata_By_Date=Data_From_Method[1]
                data=adminDashBoard()
                print("name is ",name)
                # Indevidual_Values = userHistory.objects.filter(Name=name).values_list('NowAddedAmount', flat=True).aggregate(total_amount=Sum('NowAddedAmount'))['total_amount']
                # Totaldata_By_Date=userHistory.objects.filter(Name=name).values
                print("indivudual values are",Indevidual_Values)
                return render(request,'DisplayRechargeAmount.html',{'NAME':NAME,"user_type":user_type,"mainData":data,'usersLoc':data[2],
                                                        'dailyData':data[3],"gasvalvestatus":data[-1],"devstatus":data[-2],
                                                        "usernames":User_Names,"queryset":Indevidual_Values,"City_Names":City_names,
                                                        "TotalData":Totaldata_By_Date,"person":name,"All_Recharge":All_Meters})
            elif request_name=="individual_monthwise":
                name=request.POST.get("name")
                Month_Number=request.POST.get('month_number')
                Year=request.POST.get('year')
                Data_From_Method= Individual_MonthWise(name,Year,Month_Number)
                print("Datafrommethod",Data_From_Method)
                Indevidual_Values=Data_From_Method[0]
                Totaldata_By_Date=Data_From_Method[1]
                data=adminDashBoard()
                print("name is ",name)
                # Indevidual_Values = userHistory.objects.filter(Date__year=Year,Date__month=Month_Number,Name=name).values_list('NowAddedAmount', flat=True).aggregate(total_amount=Sum('NowAddedAmount'))['total_amount']
                # Totaldata_By_Date=userHistory.objects.filter(Date__year=Year,Date__month=Month_Number,Name=name).values()
                print("indivudual values are",Indevidual_Values)
                return render(request,'DisplayRechargeAmount.html',{'NAME':NAME,"user_type":user_type,"mainData":data,'usersLoc':data[2],
                                                        'dailyData':data[3],"gasvalvestatus":data[-1],"devstatus":data[-2],
                                                        "usernames":User_Names,"queryset":Indevidual_Values,"City_Names":City_names,
                                                        "TotalData":Totaldata_By_Date,"person":name,"MONTH":Month_Number,"YEAR":Year,"All_Recharge":All_Meters})
            elif request_name=="city_wise":
                City_Name=request.POST.get("Location_Name")
                Data_From_Method= City_Wise(City_Name)
                print("Datafrommethod",Data_From_Method)
                city_wise=Data_From_Method[0]
                Totaldata_By_Date=Data_From_Method[1]
                data=adminDashBoard()
                # city_wise = userHistory.objects.filter(Location=City_Name).values_list('NowAddedAmount', flat=True).aggregate(total_amount=Sum('NowAddedAmount'))['total_amount']
                # Totaldata_By_Date=userHistory.objects.filter(Location=City_Name).values()
                print("indivudual values are",city_wise)
                return render(request,'DisplayRechargeAmount.html',{'NAME':NAME,"user_type":user_type,"mainData":data,'usersLoc':data[2],
                                                        'dailyData':data[3],"gasvalvestatus":data[-1],"devstatus":data[-2],
                                                        "usernames":User_Names,"queryset":city_wise,"City_Names":City_names,
                                                        "TotalData":Totaldata_By_Date,"location":City_Name,"All_Recharge":All_Meters})
            elif request_name=="city_month_wise":
                    City_Name=request.POST.get("Location_Name")
                    Month_Number=request.POST.get('month_number')
                    Year=request.POST.get('year')
                    Data_From_Method= City_Month_Wise(City_Name,Month_Number,Year)
                    print("Datafrommethod",Data_From_Method)
                    city_wise=Data_From_Method[0]
                    Totaldata_By_Date=Data_From_Method[1]
                    data=adminDashBoard()
                    # city_wise = userHistory.objects.filter(Date__year=Year,Date__month=Month_Number,Location=City_Name).values_list('NowAddedAmount', flat=True).aggregate(total_amount=Sum('NowAddedAmount'))['total_amount']
                    # Totaldata_By_Date=userHistory.objects.filter(Date__year=Year,Date__month=Month_Number,Location=City_Name).values()
                    print("indivudual values are",city_wise)
                    return render(request,'DisplayRechargeAmount.html',{'NAME':NAME,"user_type":user_type,"mainData":data,'usersLoc':data[2],
                                                            'dailyData':data[3],"gasvalvestatus":data[-1],"devstatus":data[-2],
                                                            "usernames":User_Names,"queryset":city_wise,"City_Names":City_names,
                                                            "TotalData":Totaldata_By_Date,"All_Recharge":All_Meters,"location":City_Name,'MONTH':Month_Number,"YEAR":Year})
            elif request_name=="date_between":
                Start_Date=request.POST.get('Start_Date')
                End_Date=request.POST.get('End_Date')
                Data_From_Method= Date_Betweens(Start_Date,End_Date)
                print("Datafrommethod",Data_From_Method)
                Between_Dates=Data_From_Method[0]
                Totaldata_By_Date=Data_From_Method[1]
                # Between_Dates=userHistory.objects.filter(Date__range=(Start_Date,End_Date)).values_list('NowAddedAmount',flat=True).aggregate(total_amount=Sum('NowAddedAmount'))['total_amount']
                # Totaldata_By_Date=userHistory.objects.filter(Date__range=(Start_Date,End_Date)).values()
                data=adminDashBoard()
                return render(request,'DisplayRechargeAmount.html',{'NAME':NAME,"user_type":user_type,"mainData":data,'usersLoc':data[2],
                                                            'dailyData':data[3],"gasvalvestatus":data[-1],"devstatus":data[-2],
                                                            "usernames":User_Names,"queryset":Between_Dates,"City_Names":City_names,
                                                            "TotalData":Totaldata_By_Date,"start_date":Start_Date,"end_date":End_Date,"All_Recharge":All_Meters})
    data=adminDashBoard()
    #  ##print("the array is ",data[-1])

    return render(request,'DisplayRechargeAmount.html',{'NAME':NAME,"user_type":user_type,"mainData":data,'usersLoc':data[2],
                                                        'dailyData':data[3],"gasvalvestatus":data[-1],"devstatus":data[-2],
                                                        "usernames":User_Names,"City_Names":City_names,
                                                        "All_Recharge":All_Meters})

def leadDashBoard(name):
    numberOfUsers = lpg_Customer_Table.objects.filter(AREA_LEAD=name).values()
    countOfusers=len(numberOfUsers)
    startDate_0=datetime.now()-timedelta(days=7)
    endDate=datetime.now()
    historyData_by_dates=userHistory.objects.filter(Area_Lead=name, Date__range=(startDate_0,endDate))
    dailyData = userHistory.objects.filter(Area_Lead=name).values('Date').annotate(sum=Sum('Amount')).order_by()
    amount_7days=0
    for i in historyData_by_dates:
        amount_7days=amount_7days+i.Amount

    Time_Value=datetime.now()-timedelta(hours=24)
    Users_Values=Lpg_Status_Infos.objects.filter(AREA_LEAD=name).values_list('SERIAL_NUMBER',flat=True)
    
    Gas_Values = Lpg_Status_Infos.objects.filter(AREA_LEAD=name, VAlVE_TIME__range=[Time_Value,datetime.now()]).values_list('SERIAL_NUMBER',flat=True)
    
    for i in Users_Values:
        if i in Gas_Values:
            Lpg_Status_Infos.objects.filter(AREA_LEAD=name, SERIAL_NUMBER=i).update(CONNECTION_STATUS="online")
        else:
            Lpg_Status_Infos.objects.filter(AREA_LEAD=name, SERIAL_NUMBER=i).update(CONNECTION_STATUS="offline")
    
    User_Online_Count=Lpg_Status_Infos.objects.filter(AREA_LEAD=name, CONNECTION_STATUS="online").count()
    User_Offline_Count=Lpg_Status_Infos.objects.filter(AREA_LEAD=name, CONNECTION_STATUS="offline").count()
    User_Faulty_Count=Lpg_Status_Infos.objects.filter(AREA_LEAD=name, CONNECTION_STATUS="faulty").count()
    print("count is",User_Online_Count,User_Offline_Count)
    Battery_Count=Lpg_Status_Infos.objects.filter(AREA_LEAD=name, BATTERY_TIME__range=[Time_Value,datetime.now()]).count()

    State_COUNT =  usersLocationInfo.objects.filter(AREA_LEAD = name).values('State').annotate(count=Count('State')).order_by()
    GAS_COUNT = len(Gas_Values)
    DEV_COUNT = lpg_Customer_Table.objects.filter(AREA_LEAD = name, DEV_TIME__range=[Time_Value,datetime.now()]).count()
   
    return countOfusers,amount_7days,State_COUNT,dailyData,User_Online_Count,User_Offline_Count,User_Faulty_Count,DEV_COUNT,GAS_COUNT
    
def areaLeadLogin(request):
    if request.method == 'POST':
        leadUsername = request.POST.get('username')
        leadPassword = request.POST.get('password')
        
        areaLead = Area_Lead.objects.filter(name=leadUsername, password=leadPassword)
        
        if areaLead:
            data=leadDashBoard(leadUsername)
            return render(request,'adminMainPage.html',{'NAME':leadUsername,"user_type":"Area_Lead","mainData":data,'usersLoc':data[2],
                                                        'dailyData':data[3],"gasvalvestatus":data[-1],"devstatus":data[-2]})
        else:
            return render(request, 'leadLogin.html', {'error':"Invalid Login Details"})
    return render(request ,'leadLogin.html')
def Configuration(request,NAME,user_type,request_type):
    if request_type=="gas_info":
        CostPerKg=request.POST.get('CostPerKg')
        RechargeAmount=request.POST.get('RechargeAmount')
        ValueControl=request.POST.get('ValueControl')
        SerialNumber=request.POST.get('SerialNumber')
        print(CostPerKg,RechargeAmount,ValueControl,SerialNumber)
        val2 = {"CostPerKg":CostPerKg,
                "RechargeAmount" : RechargeAmount,
                "ValueControl" : ValueControl,
                "SerialNumber" : SerialNumber
            }
        try:
            data_out=json.dumps(val2,  default=str)
            outDevice = "data/320000002/customer"
            client.publish(outDevice,data_out)
            return render(request,'Configration.html',{"NAME":NAME,"user_type":user_type,"message":"data send successfully"})
        except Exception as e:
             print(e)
             return render(request,'Configration.html',{"NAME":NAME,"user_type":user_type,"message":"some error coming"})
    elif request_type=="mqtt_info":
        MqttHost=request.POST.get('MqttHost')
        MqttPort=request.POST.get('MqttPort')
        MqttUser=request.POST.get('MqttUser')
        MqttPassword=request.POST.get('MqttPassword')
        print(MqttHost,MqttPassword,MqttPort,MqttUser)
        val2 = {"MqttHost":MqttHost,
                "MqttPort" : MqttPort,
                "MqttUser" : MqttUser,
                "MqttPassword" : MqttPassword
            }
        try:
            data_out=json.dumps(val2,  default=str)
            outDevice = "data/320000002/customer"
            client.publish(outDevice,data_out)
            return render(request,'Configration.html',{"NAME":NAME,"user_type":user_type,"message":"data send successfully"})
        except Exception as e:
             print(e)
             return render(request,'Configration.html',{"NAME":NAME,"user_type":user_type,"message":"some error coming"})
    return render(request,'Configration.html',{"NAME":NAME,"user_type":user_type})
def history_download_csv(request, userName, start_date, end_date):
    history_data=userHistory.objects.filter(Name=userName, Date__range=(start_date, end_date)).values()
    # for i in history_data:
    #     print(i)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Recharge_History.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Serail Number', 'Name', 'PhoneNumber', 'Amount', 'Added_LPG', 'Date', 'Time',
    ])
    
    for i in history_data:
        writer.writerow([
            i['SerialNumber'], i['Name'], i['PhoneNumber'], i['Amount'], i['NewAddedLPG'], i['Date'], i['Time'],
        ])
    return response
    

def history_data_pdf(request, userName, start_date, end_date):
    history_data = userHistory.objects.filter(Name=userName, Date__range=(start_date, end_date)).values()
    template = get_template('pdf_convert.html')
    
    html_content = template.render({'history_data':history_data})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Recharge_History.pdf"'
    
    pisa_status = pisa.CreatePDF(html_content, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF: %s' % pisa_status.err)

    return response