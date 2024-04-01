
# import mysql.connector
# import time
# import codecs
# import paho.mqtt.client as mqtt
# from . server_simulator import SingleDeviceServerSimulator
# import schedule
# import json
# #----------end imports --------------
# outDevice= "data/320000001/customer" 
# broker_address="driver.cloudmqtt.com" 

# client = mqtt.Client()
# client.reinitialise()
# #client.tls_insecure_set(False)
# try:
#     client.username_pw_set('iquvvlgs', 'PONUI_uPrhKX')
#     client.connect( broker_address,  18876, 60 )
# except:
#     print("Error MQTT: connection failed")
#     exit(1)

# mydb = mysql.connector.connect(
#   host="mpesa.cd0ernbifwkr.eu-north-1.rds.amazonaws.com",
#   user="admin",
#   password="welcome123",
#   database="CustomerManagement" 
# )

# mycursor = mydb.cursor()
# # mycursor.execute("SELECT * FROM Myapp_c2bamountcheck")

# # myresult = mycursor.fetchall()

# # for x in myresult:
# #   print(x)

# def c2bPaymentCheck():
#     print('check this method')
#     mycursor.execute("SELECT * FROM Myapp_c2bamountcheck")

#     c2bData = mycursor.fetchall()
#     if c2bData:
#         print("the data is present")
#         for i in c2bData:
#             print("**************",i)
#             print("the data is present")
#             #print("C2BData amount",int(i['amount']))
#     # -----------Publish Token -----------------------------------------------------------------

#             secret_key_temp       =  '52fa8d60be23d944a8c4bbe4c0dfff5c'
#             secret_key            =  codecs.decode(secret_key_temp, 'hex_codec') 
#             amt                   =  int(i[3])
#             print("secret key", secret_key )
#             serial_no = i[2]
#             device_starting_code = 302623035
#             print("starting code", device_starting_code )
#             restricted_digit_set =  False

#             print('\n')

#             server_simulator = SingleDeviceServerSimulator(device_starting_code, secret_key,
#                                                    restricted_digit_set=restricted_digit_set)
#             token_1 = server_simulator._generate_extended_value_token(amt)
#             print('Extended Tokens: ', token_1)

#             val2 = {"SERIAL_NUMBER":i[2],
#                     "BAL_AMOUNT" : token_1
#                     }

#             data_out=json.dumps(val2,  default=str)  # encode oject to JSON

#             print("sending data: " +  str(amt))
#             client.publish(outDevice,data_out)
#             print("Just published " + str(token_1) + " to "+str(outDevice)  )
#             ################ END  PUBLISH ##############
#             # deleteing the current user
#             try:
#                 sql = "DELETE FROM Myapp_c2bamountcheck WHERE serialNumber= %s"
#                 val=(i[2],)
#                 mycursor.execute(sql,val)
#                 mydb.commit()
#             except:
#                  print('the data is not present')
#                  pass
# def message():
#      print('this is message method')
#      mycursor.execute("SELECT * FROM Myapp_c2bamountcheck")

#      c2bData = mycursor.fetchall()
#      for i in c2bData:
#         sql = "DELETE FROM Myapp_c2bamountcheck WHERE serialNumber= %s"
#         val=(i[2],)
#         mycursor.execute(sql,val)
#         mydb.commit()
# schedule.every(10).seconds.do(message)
# while True:
#     schedule.run_pending()
#     time.sleep(10)
