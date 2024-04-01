from django.db import models

# Create your models here.
class Student(models.Model):
    title=models.CharField(max_length=250)
    body=models.TextField()
class work(models.Model):
    title=models.CharField(max_length=250)
    body=models.TextField()

class Register(models.Model):
    name=models.CharField(max_length=30)
    password = models.TextField(max_length=20)
    email = models.CharField(max_length=30)

class transaction_details(models.Model):
    isSuccess = models.CharField(max_length=20)
    userName = models.CharField(max_length=30)
    phoneNUmber=models.CharField(max_length=30)

class lpg_Customer_Table(models.Model):
    CUST_ID=models.CharField(max_length=50)
    NAME=models.TextField(max_length=50)
    PHONENUMBER=models.CharField(max_length=30)
    SERIAL_NUMBER=models.TextField(max_length=50)
    STARTING_CODE=models.CharField(max_length=50)
    SECRET_KEY=models.CharField(max_length=50)
    DATE=models.DateField()
    GAS_LEAK=models.BooleanField()
    GAS_VALVE=models.BooleanField()
    TAMPER=models.BooleanField()
    DEV_ENABLE=models.BooleanField()
    CYLENDER_TYPE=models.IntegerField()
    PREPAID=models.BooleanField()
    BAT_STATUS=models.IntegerField()
    LOCATION=models.CharField(max_length=50)
    IMEI_NO=models.CharField(max_length=50)
    DEV_STATUS=models.BooleanField()
    DEV_TIME=models.DateTimeField()
    BAL_LPG=models.FloatField()
    BAL_AMOUNT=models.FloatField()
    EMAILS=models.EmailField()
    AREA_LEAD=models.CharField(max_length=50)
    # CONNECTION_STATUS=models.CharField(max_length=50)
    # BATTERY_PERCENTAGE=models.FloatField()
    # CYLINDER_GAS_WEIGHT=models.FloatField()
    # VAlVE_TIME=models.DateTimeField()
    # BATTERY_TIME=models.DateTimeField()

class Lpg_Status_Infos(models.Model):
    SERIAL_NUMBER=models.TextField(max_length=50)
    NAME=models.TextField(max_length=50)
    CONNECTION_STATUS=models.CharField(max_length=50)
    BATTERY_PERCENTAGE=models.FloatField()
    CYLINDER_GAS_WEIGHT=models.FloatField()
    VAlVE_TIME=models.DateTimeField()
    BATTERY_TIME=models.DateTimeField()
    AREA_LEAD=models.CharField(max_length=50)

class Admin(models.Model):
    name=models.CharField(max_length=30)
    password = models.TextField(max_length=20)
    email = models.CharField(max_length=30)

class Area_Lead(models.Model):
    name=models.CharField(max_length=30)
    password = models.TextField(max_length=20)
    email = models.CharField(max_length=30)

class c2bAmountCheck(models.Model):
    name=models.CharField(max_length=50)
    PhoneNumber=models.TextField(max_length=50)
    amount=models.FloatField()

class userHistory(models.Model):
    Name=models.CharField(max_length=50)
    SerialNumber=models.TextField(max_length=50)
    Amount=models.FloatField()
    PhoneNumber=models.CharField(max_length=30)
    Date=models.DateField()
    Time=models.TimeField()
    PreviousAmount=models.FloatField()
    NowAddedAmount=models.FloatField()
    PreviousLPG=models.FloatField()
    NewAddedLPG=models.FloatField()
    Location=models.CharField(max_length=50)
    Area_Lead=models.CharField(max_length=50)



class usersLocationInfo(models.Model):
    Name=models.CharField(max_length=50)
    SerialNumber=models.TextField(max_length=50)
    PhoneNumber=models.CharField(max_length=30)
    State = models.CharField(max_length=50)
    Country = models.CharField(max_length=50)

class userLowBalanceCheck(models.Model):
    Name=models.CharField(max_length=50)
    SerialNumber=models.TextField(max_length=50)
    BAL_AMOUNT=models.FloatField()
    PhoneNumber=models.CharField(max_length=30)
    EMAILS=models.EmailField()
    DATE=models.DateField() 
    Time=models.TimeField()
    State = models.CharField(max_length=50)
    Country = models.CharField(max_length=50) 
    MailStatus=models.CharField(max_length=30)
    

class usageHistory(models.Model):
    SerialNumber=models.TextField(max_length=50)
    Name=models.CharField(max_length=50)
    DATE=models.DateField() 
    Time=models.TimeField()
    BAL_LPG=models.FloatField()
    BAL_AMOUNT=models.FloatField()
    Battery=models.CharField(max_length=50)
    Others=models.CharField(max_length=50)

class GasPrices(models.Model):
    admin_name=models.CharField(max_length=50)
    gas_units=models.IntegerField()
    price=models.FloatField()
    date=models.DateField(default='2023-10-24')
    time=models.TimeField(default='09:37:07.0')


class customerIssues(models.Model):
    user_name=models.CharField(max_length=50)
    problem_one=models.TextField()
    problem_two=models.TextField()
    description=models.TextField()
    date=models.DateField()
    time=models.TimeField()
    phonenumber=models.IntegerField(default="+919703323212")
    email=models.EmailField(default="enerziff@gmail.com")
    token=models.TextField(default="EVM001")
    status=models.BooleanField(default="False")
    Area_Lead=models.CharField(max_length=50)

class solvedIssues(models.Model):
    user_name=models.CharField(max_length=50)
    problem_one=models.TextField()
    problem_two=models.TextField()
    description=models.TextField()
    date=models.DateField()
    time=models.TimeField()
    phonenumber=models.IntegerField(default="+919703323212")
    email=models.EmailField(default="enerziff@gmail.com")
    token=models.TextField(default="EVM001")
    Area_Lead=models.CharField(max_length=50)
    

