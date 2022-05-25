from flask import Flask, render_template, request, send_file
import pandas as pd
from datetime import date, datetime
import pickle 
import os
from twilio.rest import Client
from threading import Thread
import pytz
import time


app = Flask(__name__)
global phys_dictionary
global pharm_dictionary
global patient_dictionary

phys_dictionary = {'physician@gmail.com':['John Doe', 'password1']}
pharm_dictionary = {'CVS Pharmacy, 3999 Santa Rita Rd, Pleasanton, CA 94588':['CVS', 'password1', '9254608552'], 'Safeway Pharmacy, 4440 Tassajara Rd, Dublin, CA 94568':['Safeway', 'password1', '9254608552']}
patient_dictionary = {}

    
a_file = open("pharm_dictionary.pkl", "rb")
if os.stat("pharm_dictionary.pkl").st_size != 0:
  pharm_dictionary = pickle.load(a_file)

aa_file = open("patient_dictionary.pkl", "rb")
if os.stat("patient_dictionary.pkl").st_size != 0:
  patient_dictionary = pickle.load(aa_file)
  
account_sid = "AC370d2bc15cbc6244c55b57f2d86511d8"
auth_token = "2da130afb77a5f5cdc2b0fb15ec12e2e"
client = Client(account_sid, auth_token)

  
def message(email):
  while True:
    day = datetime.today().weekday()
    for prescription in patient_dictionary[email][1:]:
      if day in prescription[1]:
        curr_time = datetime.now(pytz.timezone('US/Pacific'))
        curr_time = curr_time.strftime("%H:%M")
        print(curr_time)
        print(prescription[0])
        if curr_time == prescription[0]:
          print("Success!")
          
          message = client.messages \
              .create(
                   body="It's time to take your medication!",
                   from_='+18304654934',
                   to='+1'+patient_dictionary[email][0]
               )
          print(message.sid)
          time.sleep(60)

for email in patient_dictionary.keys():
  if len(patient_dictionary[email])>=2:
    print("uy")
    thread = Thread(target = message, args = [email])
    thread.start()



@app.route('/', methods = ["POST", "GET"])
def home():
  return render_template('home.html')

@app.route('/sign_in_pharm', methods = ["POST", "GET"])
def sign_in_pharm():
  return render_template('sign_in_pharm.html', pharm_dictionary = pharm_dictionary)

@app.route('/sign_in_physician', methods = ["POST", "GET"])
def sign_in_phys():
  return render_template('sign_in_physician.html')
  
@app.route('/signed_in', methods = ["POST"])
def signed_in():  
  email = request.form.get("email")
  password = request.form.get("password")
  if email in phys_dictionary.keys():
    if phys_dictionary[email][1] == password:
        return render_template('prescription.html', email = email, pharm_dictionary=pharm_dictionary)
    else:
      feedback = "Incorrect Password"
  else:
    feedback = "Incorrect Username"
  return render_template('sign_in_physician.html', feedback = feedback, email = email)

@app.route('/signed_in_pharm', methods = ["POST"])
def signed_in_pharm():  
  address = request.form.get("pharmacy_address")
  print(address)
  password = request.form.get("password")
  print(password)
  if address in pharm_dictionary.keys():
    if pharm_dictionary[address][1] == password:
      pharmpatient_list = []
      for prescription in pharm_dictionary[address][3:]:
        pharmpatient_list.append(prescription)
      return render_template('prescription_pharm.html', pharmpatient_list = pharmpatient_list)
    else:
      feedback = "Incorrect Password"
  else:
    feedback = "Incorrect Username"
  return render_template('sign_in_pharm.html', feedback = feedback, pharm_dictionary = pharm_dictionary)
  
@app.route('/form', methods = ["POST", "GET"])
def form():
  email = request.form.get("email")
  password = request.form.get("password")
  list.append(email)
  list.append(password)
  print(list)
  df = pd.DataFrame(list)
  df.to_csv('patients.txt')
  return render_template('index.html')

@app.route('/prescription/<email>', methods = ["GET", "POST"])
def prescription(email):
  patient_name = request.form.get("patient_name")
  patient_email = request.form.get("patient_email")
  patient_phone = request.form.get("patient_phone")
  medication_name = request.form.get("medication_name")
  generic_for = request.form.get("generic_for")
  medication_time = request.form.get("time")
  Sunday = request.form.get("Sunday")
  Monday = request.form.get("Monday")
  Tuesday = request.form.get("Tuesday")
  Wednesday = request.form.get("Wednesday")
  Thursday = request.form.get("Thursday")
  Friday = request.form.get("Friday")
  Saturday = request.form.get("Saturday")
  days = [Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday]
  days = [i for i in days if i]
  days = [int(i) for i in days]
  pharmacy_address = request.form.get("pharmacy_address")
  pharmacy_name = pharm_dictionary[pharmacy_address][0]
  pharmacy_phone = pharm_dictionary[pharmacy_address][2]
  RX = request.form.get("RX")
  QTY = request.form.get("QTY")
  refill_by = request.form.get("Refill")
  physician_email = email
  physician_name = phys_dictionary[email][0]
  current_date = date.today()
  manufacturer = request.form.get("manufacturer")
  directions = request.form.get("directions")
  if patient_email in patient_dictionary.keys():
    patient_dictionary[patient_email].append([medication_time, days])
  else: 
    patient_dictionary[patient_email] = [patient_phone, [medication_time, days]]
  print(patient_dictionary)
  df = pd.DataFrame([patient_name, patient_email, medication_name, generic_for, medication_time,  list(days), directions, pharmacy_name, pharmacy_address, pharmacy_phone, RX, QTY, refill_by, physician_name, physician_email, current_date, manufacturer])
  df.to_csv(patient_email + "_" + medication_name + ".txt", header = False, index=False, line_terminator='\n')
  
  pharm_dictionary[pharmacy_address].append(patient_email+"_"+medication_name+".txt")
  a_file = open("pharm_dictionary.pkl", "wb")
  pickle.dump(pharm_dictionary, a_file)
  a_file.close()

  aa_file = open("patient_dictionary.pkl", "wb")
  pickle.dump(patient_dictionary, aa_file)
  aa_file.close()
  for email in patient_dictionary.keys():
    if len(patient_dictionary[patient_email])>=2:
      thread = Thread(target = message, args = [email])
      thread.start()
  return render_template('prescription.html')

@app.route('/prescription_pharm/<email>', methods = ["GET", "POST"])
def prescription_pharm(email):
  return render_template('prescription_pharm.html', pharm_dictionary=pharm_dictionary)

@app.route('/download', methods = ["GET", "POST"])
def download():
  file = request.form.get("file")
  return send_file(file, as_attachment=True)

@app.route('/sign_in_patient', methods = ["POST", "GET"])
def sign_in_patient():
  return render_template('sign_in_patient.html')

@app.route('/product_desc', methods = ["POST", "GET"])
def product_desc():
  return render_template('product_desc.html')

@app.route('/our_team', methods = ["POST", "GET"])
def our_team():
  return render_template('our_team.html')

@app.route('/contact_me', methods = ["POST", "GET"])
def contact_me():
  return render_template('contact_me.html')
                                     

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)