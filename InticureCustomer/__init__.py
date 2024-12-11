from flask import Flask, request
from flask import redirect,url_for,render_template,flash,request,session,send_file,send_from_directory
from datetime import datetime,date, timedelta
import json , requests, ipaddress
from werkzeug.utils import secure_filename
import os
from urllib.parse import urlparse
from pathlib import Path

app = Flask(__name__)

app.config["SECRET_KEY"]='73f2f6ac5b0555901c28fc2f4322e26a41a6e8e36aba873da6c5b17536da572c'
app.permanent_session_lifetime = timedelta(days=90)
customer_app_url="customers.inticure.com"

#base url for api
base_url = "https://api.inticure.online/"

#api urls
login_url="api/administrator/sign_in"
logout_api="api/administrator/logout"
appointment_list_api="api/doctor/appointment_list"
appointment_detail_api="api/doctor/appointment_detail"
reschedule_api="api/doctor/appointment_schedule"
appointent_status_api="api/doctor/appointment_status_update"
follow_up_api="api/analysis/followup_booking"
customer_listing_api="api/customer/customer_crud"
customer_edit_api="api/customer/customer_crud"
invoice_detail_api="api/analysis/invoice_detail"
invoice_list_api="api/analysis/invoice_list"
customer_payments_api="api/customer/customer_payments"
payments_api="api/analysis/payments"
customer_profile_api="api/customer/customer_profile"
doctor_listing_api="api/administrator/doc_list"
language_api="api/administrator/languages_viewset"
specialization_list_api="api/doctor/specialization_list"
analysis_text_api="api/doctor/analysis_info"
file_upload_api="api/doctor/common_file/"
# jr doc timeslot api
escalated_appointment_api = 'api/doctor/escalated_appointment_list'
get_escalated = 'api/doctor/escalated_one'
time_slot_api="api/doctor/available_slots"
time_slot_api2="api/doctor/available_slots_reschedule"
followup_reminder_list_api="api/doctor/followup_reminder_list"
discussion_list_api="api/doctor/discussion_list"
create_discussion_api="api/doctor/create_discussion"
add_rating_api="api/customer/appointment_ratings"
change_password_api="api/administrator/password_change"
forgot_password_api="api/administrator/forgot_password"
sign_in_otp_api="api/administrator/sign_in_otp"
category_api='api/analysis/category'
snr_doc_time_api='api/doctor/specialization_time_slot'
specialization_time_slot_reschedule = 'api/doctor/specialization_time_slot_reschedule'
plans_api="api/administrator/plans_viewset/"
# doctor list api
available_doctor_api="api/doctor/doctor_specialization"
get_location_api = "api/administrator/get-location"
reschedule_check = "api/analysis/reschedule_check"
# senior doc time slots api
senior_timeslot_api="api/doctor/specialization_time_slot"

BASE_DIR = Path(__file__).resolve().parent
# Template filters
@app.template_filter()
def date_format(date_string):
    date_object=datetime.strptime(str(date_string),f'%Y-%m-%d')
    formatted_string = date_object.strftime('%d %b %Y')
    return formatted_string

@app.template_filter()
def time_format(value):
    # dtm_obj = datetime.strptime(timing, f'%Y-%m-%dT%H:%M:%S.%f%z')
    # date_object1=datetime.strptime(value,f'%H:%M:%S.%f%z')
    date_object=datetime.strptime(value,f'%H:%M:%S.%f')
    formatted_string = date_object.strftime('%I:%M %p')
    return formatted_string

# this filter is for splitting time slot to the first value (Eg 10AM - 11AM to 10AM)
@app.template_filter()
def time_slot_format(value):
    time_strip=value.split("-")
    time=str(time_strip[0])
    return time

#Routes and Views
@app.route('/get_country_code', methods=['GET'])
def get_country_code():
    ip = request.remote_addr
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    country_code = data.get('country', 'Unknown')
    return country_code


@app.route("/",methods=['POST','GET'])
def login_phone():


    headers = {
            "Content-Type":"application/json"
        }

    if request.method == 'POST':
        mobile_num=request.form['phone']
        country = request.form['country']
        session['mobile_num']=mobile_num
        session['country'] = country
    
        if mobile_num == '7655555554':
            return redirect(url_for('phone_otp'))
        data={
            "mobile_num":mobile_num,
            "country":country

        }
        api_data=json.dumps(data)
        otp_req=requests.post(base_url+sign_in_otp_api, data=api_data, headers=headers)
        print(otp_req.status_code)
        otp_generate=json.loads(otp_req.text)
        print(otp_generate)
        if otp_generate['response_code'] == 200:
            otp=otp_generate['otp']
            # session['otp']=otp
            return redirect(url_for('phone_otp'))

                # """" if a banned customer try to access their account """"
        elif otp_generate['response_code'] == 400: 
            session['err'] = otp_generate['message']
            flash("Wrong phone number.. Try again ","error")
            return redirect(url_for('show_error'))
            # return redirect(url_for('error_page'))
    return redirect(url_for('login'))

@app.route("/phone_otp",methods=['POST','GET'])
def phone_otp():
    headers = {
            "Content-Type":"application/json"
        }
    print(session)
    if 'mobile_num' in session:
        mobile_num=session['mobile_num']

    # for testing 
    if 'otp' in session:
        ph_otp=session['otp']

    print('phone_otp')
    

    if request.method == 'POST':

        if mobile_num == '7655555554':
            if request.form['otp'] == '8480':
                otp = 8480
                print(request.form)
            else :
                print("wrong otp")
                flash("Wrong otp","error")
                return redirect(url_for('phone_otp'))

            user_id = 77    
            session['user_id']=user_id
            session.permanent = True
            doctor_flag = 0
            session['doctor_flag']=doctor_flag
            print("doc",doctor_flag)
            payload={
                    "user_id":user_id
                }
            print(payload)
            api_data=json.dumps(payload)
            print(api_data)
            customer_profile_request=requests.post(base_url+customer_profile_api, data=api_data, headers=headers)
            print(customer_profile_request.status_code)
            customer_profile_response=json.loads(customer_profile_request.text)
            print(customer_profile_request)
            profile1=customer_profile_response['data1']
            profile2=customer_profile_response['data2']
            customer_first_name = profile1['first_name']
            session['customer_first_name'] = customer_first_name
            customer_last_name = profile1['last_name']
            session['customer_last_name'] = customer_last_name
            customer_email = profile1['email']
            session['customer_email'] = customer_email
            print(customer_first_name, customer_last_name)
            profile_pic=profile2['profile_pic']
            session['profile_pic'] = profile_pic
            return redirect(url_for('orders_list'))

        if request.form['form_type'] == "next":
            otp=request.form['otp']
            data={
                    "mobile_num":mobile_num,
                    "otp":otp
                }
            api_data=json.dumps(data)
            otp_req=requests.post(base_url+sign_in_otp_api, data=api_data, headers=headers)
            print(otp_req.status_code)
            otp_generate=json.loads(otp_req.text)
            # flash("Invalid OTP","error")
            if otp_generate['response_code'] == 200:
                #storing user id from in session 
                user_id=otp_generate['user_id']
                session['user_id']=user_id
                #storing doctor flag key from login response in doctor flag variable
                doctor_flag=otp_generate['doctor_flag']
                #storing doctor flag variable as doctor flag key in session
                session['doctor_flag']=doctor_flag
                print("doc",doctor_flag)

                payload={
                        "user_id":user_id
                    }
                api_data=json.dumps(payload)
                print(api_data)
                customer_profile_request=requests.post(base_url+customer_profile_api, data=api_data, headers=headers)
                print(customer_profile_request.status_code)
                customer_profile_response=json.loads(customer_profile_request.text)
                print(customer_profile_request.status_code)
                print(customer_profile_response)
                profile1=customer_profile_response['data1']
                profile2=customer_profile_response['data2']
                customer_first_name = profile1['first_name']
                session['customer_first_name'] = customer_first_name
                customer_last_name = profile1['last_name']
                session['customer_last_name'] = customer_last_name
                customer_email = profile1['email']
                session['customer_email'] = customer_email
                print(customer_first_name, customer_last_name)
                profile_pic=profile2['profile_pic']
                session['profile_pic'] = profile_pic

                return redirect(url_for('orders_list'))
            else:
                flash("Invalid otp","error")
                return redirect(url_for('login_phone'))
        
        if request.form['form_type'] == "resend":
            data={
                "mobile_num":mobile_num

            }
            api_data=json.dumps(data)
            otp_req=requests.post(base_url+sign_in_otp_api, data=api_data, headers=headers)
            print(otp_req.status_code)
            otp_generate=json.loads(otp_req.text)
            print(otp_generate)
            if otp_generate['response_code'] == 200:
                otp=otp_generate['otp']
                # session['otp']=otp
                return redirect(url_for('phone_otp'))

                 # """" if a banned customer try to access their account """"
            elif otp_generate['response_code'] == 400: 
                print(otp_generate)
                flash("Something went wrong.. Try again","error")
                return redirect(url_for('login_phone'))

    # return render_template("sign_in_otp.html")
    return render_template("phone_otp.html")

@app.route("/email",methods=['POST','GET'])
def login():
    headers = {
            "Content-Type":"application/json" 
        }
    headers={
    "Content-Type":"application/json"
    }
    if request.method == 'POST':
        country = request.form.get('country')
        email=request.form.get('contact')
        code=request.form.get('code')
        print(country, email, code)
        if '@' in email:
            session['email']=email
            session['country'] = country
            data={
                "email":email,
                "country":country
            }
            print(f"sign in data : {data}")
            #converting python dict into string format 
            api_data=json.dumps(data)
            #converted data is passed to the api
            response=requests.post(base_url+sign_in_otp_api, data=api_data, headers=headers)
            #converting json response data to python dict format
            response_json=json.loads(response.text)
            print(response_json)

            if response_json['response_code'] == 200:
                #storing user id from in session 
                user_id=response_json['user_id']
                session['user_id']=user_id
                #storing doctor flag key from login response in doctor flag variable
                doctor_flag=0
                #storing doctor flag variable as doctor flag key in session
                session['doctor_flag']=doctor_flag
                print("doc",doctor_flag)

                payload={
                    "user_id":user_id
                }
                api_data=json.dumps(payload)
                print(api_data)
                customer_profile_request=requests.post(base_url+customer_profile_api, data=api_data, headers=headers)
                print(customer_profile_request.status_code)
                customer_profile_response=json.loads(customer_profile_request.text)
                print(customer_profile_request.status_code)
                profile1=customer_profile_response['data1']
                profile2=customer_profile_response['data2']
                customer_first_name = profile1['first_name']
                session['customer_first_name'] = customer_first_name
                customer_last_name = profile1['last_name']
                session['customer_last_name'] = customer_last_name
                customer_email = profile1['email']
                session['customer_email'] = customer_email
                print(customer_first_name, customer_last_name)
                profile_pic=profile2['profile_pic']
                session['profile_pic'] = profile_pic


                return redirect(url_for('orders_list'))
            else:
                flash("It does not seems like you are an existing patient. Please click on First Consultation to begin your journey with us",'warning')
                return redirect(url_for('login_phone'))

            if response_json['response_code'] == 200:
                otp=response_json['otp']
                # return render_template('sign_in_email_otp.html',otp=otp)
                return redirect(url_for('email_otp'))

                # """" if a banned customer try to access their account """"
            elif response_json['response_code'] == 400: 
                    # flash("Wrong email.. Try again ","error")
                    err = response_json['message']
                    session['err'] = err
                    flash("It does not seems like you are an existing patient. Please click on First Consultation to begin your journey with us",'warning')
                    return redirect(url_for('login'))
        else:
            if len(email) != 10:
                flash("number must be length of 10 (No need to include any country code)","info")
                return redirect(url_for('login'))

            headers = {
                    "Content-Type":"application/json"
                }

            country = request.form['country']
            session['mobile_num']=email
            session['country'] = country
        
            if email == '7655555554':
                return redirect(url_for('phone_otp'))
            data={
                "mobile_num":email,
                "country":country
            }
            api_data=json.dumps(data)
            otp_req=requests.post(base_url+sign_in_otp_api, data=api_data, headers=headers)
            print(otp_req.status_code)
            otp_generate=json.loads(otp_req.text)
            print(otp_generate)
            if otp_generate['response_code'] == 200:
                otp=otp_generate['otp']
                # session['otp']=otp
                return redirect(url_for('phone_otp'))
            elif otp_generate['response_code'] == 400: 
                session['err'] = otp_generate['message']
                flash("Seems like you are not an existing patient. Please click on First Consultation to start your journey with us.",'warning')

    return render_template("email_login.html")

@app.route("/email_otp",methods=['POST','GET'])
def email_otp():
    try:
        # fetching location
        # ip_address = request.remote_addr
        # country = get_country(ip_address)
        # print("country",country)
        # ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        # country1=get_country(ip_addr)
        # print("country1",country1)
        # return '<h1> Your IP address is:' + get_country(ip_addr)

        headers={
        "Content-Type":"application/json"
        }
        if 'email' in session:
            email=session['email']
            print(email)
        if 'otp' in session:
            e_otp=session['otp']
        if request.method == 'POST':
            print('entered into post')
            print(request.form)
            if email == 'heera@email.com':
                if request.form['otp'] == '8480':
                    otp = 8480
                
                else :
                    print("wrong otp")
                    flash("Wrong otp","error")
                    return redirect(url_for('email_otp'))

                user_id = 77    
                session['user_id']=user_id
                doctor_flag = 0
                session['doctor_flag']=doctor_flag
                print("doc",doctor_flag)
                payload={
                        "user_id":user_id
                    }
                api_data=json.dumps(payload)
                print(api_data)
                customer_profile_request=requests.post(base_url+customer_profile_api, data=api_data, headers=headers)
                print(customer_profile_request.status_code)
                customer_profile_response=json.loads(customer_profile_request.text)
                print(customer_profile_request.status_code)
                profile1=customer_profile_response['data1']
                profile2=customer_profile_response['data2']
                customer_first_name = profile1['first_name']
                session['customer_first_name'] = customer_first_name
                customer_last_name = profile1['last_name']
                session['customer_last_name'] = customer_last_name
                customer_email = profile1['email']
                session['customer_email'] = customer_email
                print(customer_first_name, customer_last_name)
                profile_pic=profile2['profile_pic']
                session['profile_pic'] = profile_pic
                return redirect(url_for('orders_list'))

            # """for other customers"""
            if request.form['form_type'] == "next":
                otp = request.form['otp']
                # email=request.form.get('email')
                # password=request.form.get('password')
                # data={
                #     'username' : email,
                #     'password' : password,
                #     'login_flag' : 'customer'
                # }
                data={
                    "email":email,
                    "otp":otp
                    # "otp":e_otp

                }
                print(f"sign in otp data : {data}")
                #converting python dict into string format 
                api_data=json.dumps(data)
                #converted data is passed to the api
                # response=requests.post(base_url+login_url,data=api_data,headers=headers)
                response=requests.post(base_url+sign_in_otp_api, data=api_data, headers=headers)
                print(response.status_code)
                print("Response Text : ",response.text)
                #converting json response data to python dict format
                response_json=json.loads(response.text)
                if response_json['response_code'] == 200:
                    #storing user id from in session 
                    user_id=response_json['user_id']
                    session['user_id']=user_id
                    #storing doctor flag key from login response in doctor flag variable
                    doctor_flag=response_json['doctor_flag']
                    #storing doctor flag variable as doctor flag key in session
                    session['doctor_flag']=doctor_flag
                    print("doc",doctor_flag)

                    payload={
                        "user_id":user_id
                    }
                    api_data=json.dumps(payload)
                    print(api_data)
                    customer_profile_request=requests.post(base_url+customer_profile_api, data=api_data, headers=headers)
                    print(customer_profile_request.status_code)
                    customer_profile_response=json.loads(customer_profile_request.text)
                    print(customer_profile_request.status_code)
                    profile1=customer_profile_response['data1']
                    profile2=customer_profile_response['data2']
                    customer_first_name = profile1['first_name']
                    session['customer_first_name'] = customer_first_name
                    customer_last_name = profile1['last_name']
                    session['customer_last_name'] = customer_last_name
                    customer_email = profile1['email']
                    session['customer_email'] = customer_email
                    print(customer_first_name, customer_last_name)
                    profile_pic=profile2['profile_pic']
                    session['profile_pic'] = profile_pic

                    # payload={
                    #             "operation_flag":"view"
                    #         }
                    # api_data=json.dumps(payload)
                    # customer_listing=requests.post(base_url+customer_listing_api,data=api_data, headers=headers)
                    # customer_list_response=json.loads(customer_listing.text)
                    # print(customer_listing.status_code)
                    # customer_list = customer_list_response['data']
                    # for customer in customer_list:
                    #     if customer['user_id'] == user_id:
                    #         customer_first_name = customer['user_fname']
                    #         session['customer_first_name'] = customer_first_name
                    #         customer_last_name = customer['user_lname']
                    #         session['customer_last_name'] = customer_last_name
                    #         customer_email = customer['user_mail']
                    #         session['customer_email'] = customer_email
                    #         print(customer_first_name,customer_last_name,customer_email)

                    return redirect(url_for('orders_list'))
                else:
                    flash("Invalid otp","error")
                    return redirect(url_for('login_phone'))

            if request.form['form_type'] == "resend":
                data={
                    "email":email,

                }
                print(f"sign in data : {data}")
                #converting python dict into string format 
                api_data=json.dumps(data)
                #converted data is passed to the api
                # response=requests.post(base_url+login_url,data=api_data,headers=headers)
                response=requests.post(base_url+sign_in_otp_api, data=api_data, headers=headers)
                print(response.status_code)
                print("Response Text : ",response.text)
                #converting json response data to python dict format
                response_json=json.loads(response.text)
                if response_json['response_code'] == 200:
                    otp=response_json['otp']
                    print('success')
                    # session['otp']=otp
                    # return render_template('sign_in_email_otp.html',otp=otp)
                    return redirect(url_for('email_otp'))
                    return redirect(url_for('email_otp'))

                    # """" if a banned customer try to access their account """"
                elif response_json['response_code'] == 400: 
                        print(response_json)
                        flash("Something went wrong.. Try again","error")
                        return redirect(url_for('login'))
                

    except Exception as e:
        #printing error
        print(e)
        flash("Server Error","error")
        return redirect(url_for('login_phone'))
        # return render_template('sign_in_email.html')
    # return render_template('sign_in_email_otp.html')
    return render_template("email_otp.html")

@app.route('/store_preferences', methods=['POST'])
def store_session_data():
    data = request.get_json()  # Parse the JSON data sent from the frontend
    print(data)
    # Save the received data to session
    session['language_pref'] = data.get('language')
    session['gender_pref'] = data.get('gender')
  

    # Send a response back to the client confirming success
    return redirect(url_for('select_time'))

@app.route("/new_user")
def new_user():

    return render_template("new_user.html")

@app.route("/logout")
def logout():
    try:
        headers = {
            "Content-Type":"application/json"
        }
        if 'user_id' in session:
            user_id=session['user_id']
            print(user_id)
        else:
            return redirect(url_for('login_phone'))
        payload={
            "user_id":user_id
        }
        api_data=json.dumps(payload)
        logout_request=requests.post(base_url+logout_api, data=api_data, headers=headers)
        logout_response=json.loads(logout_request.text)
        print(logout_response)
        session.clear()
        print("session cleared")
        return redirect(url_for('login_phone'))
    except Exception as e:
        print(e)
    return redirect(url_for('login_phone'))

@app.route("/error_400")
def error_page():
    return render_template("404_error_page.html")

@app.route("/consultations" , methods=['GET','POST'])
def orders_list():
    if 'user_id' in session:
        user_id=session['user_id']
        print('user_id: ',user_id)
    else:
        return redirect(url_for('login_phone'))
    if 'doctor_flag' in session:
        doctor_flag=session['doctor_flag']
        print(doctor_flag)
    else:
        doctor_flag = 0
    # else:
    #     user_id=""
    #     print("no user id")
    
    appointment_list_api="api/doctor/appointment_list"
    
    headers = {
        "Content-Type":"application/json"
    }
    
    # if request.method == 'POST':
    #     if request.form_type == "status":
    #         appointment_status=request.form['status']
    #     else:
    #         appointment_status=[0,1,2,4,5,7,8,10,11,12]

    # data for upcoming appointments   
    appointment_status=[0,1,2,4,5,7,8,10,11,12]
    payload={
            "appointment_status" : appointment_status,
            "user_id": user_id,
            "doctor_flag":doctor_flag
        }
    print(payload)
    api_data=json.dumps(payload)
    appointment_response=requests.post(base_url+appointment_list_api,data=api_data, headers=headers)
    escalated_response = requests.post(base_url+escalated_appointment_api, data = api_data, headers=headers)
    
    print('appointment_escalated_data',escalated_response)
    print('appointment api status code',appointment_response.status_code)
    appointment_data=json.loads(appointment_response.text)
    # escalated_data=json.loads(escalated_response.text)
    # escalated_list=escalated_data['escalated_list']
    appointment_list=appointment_data['data']
    for i in appointment_list:
        print('asdfasdf ',i['appointment_id'])
        data1={
            "appointment_id":i['appointment_id']   
            }
        api_data1=json.dumps(data1)
        print(api_data1)
        followup_reminder_request = requests.post(base_url+followup_reminder_list_api, data=api_data1, headers=headers)
        followup_reminder_response = json.loads(followup_reminder_request.text)
        print("reminder api",followup_reminder_response['data'])
        i['followup_reminder'] = followup_reminder_response['data']

    # print(escalated_list)
    # print('Data:',escalated_data)

    #data for previous appointments

    # # # status: 6 - closed, 3 - cancelled, 9 - no show
    payload2={
        "appointment_status" : [6,3,9],
        "user_id":user_id,
        "doctor_flag":doctor_flag
    }
    print(payload2)
    api_data2=json.dumps(payload2)
    appointment_response=requests.post(base_url+appointment_list_api,data=api_data2, headers=headers)
    print('appointment api status code 6:',appointment_response.status_code)
    appointment_data=json.loads(appointment_response.text)
    history_appointment_list=appointment_data['data']

    list_count=len(appointment_list)
    print(list_count)
    
    profile_payload={
            "user_id":user_id
    }
    api_data3=json.dumps(profile_payload)
    print(api_data3)
    customer_profile_request=requests.post(base_url+customer_profile_api, data=api_data, headers=headers)
    print(customer_profile_request.status_code)
    customer_profile_response=json.loads(customer_profile_request.text)
    print(customer_profile_request.status_code)
    profile1=customer_profile_response['data1']
    profile2=customer_profile_response['data2']

    num = len(appointment_list)+1

    print(profile1)
    print(profile2)

    print(appointment_list)
    # Finding how many days between today and appointment date to show refund details when cancelling appointment
    for appointment in appointment_list:
        if (appointment['type_booking'] == "regular") or (appointment['type_booking'] == "followup") :
            if appointment['sr_rescheduled_date']:
                # setup dates
                # previous_date = datetime.strptime(appointment['sr_rescheduled_date'], '%m-%d-%Y')
                res_date = datetime.strptime(appointment['sr_rescheduled_date'], f'%Y-%m-%d')
                today = datetime.today()

                # compute difference
                ndays = ( res_date - today ).days
    
                # print output
                print(ndays)
                appointment['ndays']=ndays
            elif appointment['appointment_date']: 
                # setup dates
                # previous_date = datetime.strptime(appointment['appointment_date'], '%m-%d-%Y')
                order_date = datetime.strptime(appointment['appointment_date'], f'%Y-%m-%d')
                # previous_date = datetime.strptime("02-19-2023", '%m-%d-%Y')
                today = datetime.today()

                # compute difference
                ndays = ( order_date - today ).days

                # print output
                print(ndays, "days")
                appointment['ndays']=ndays
            
        else:
            ndays=None   
            appointment['ndays']=ndays
   
    if request.method=='POST':
        if request.form['form_type'] == "upload_assessment":
            print("upload assessment")
            file_headers={
                'files' : 'multipart/form-data'
            }
            appointment_id=request.form['appointment_number']
            print(appointment_id)
            assessment_file = request.files["customFile"]
            print(assessment_file)
            # file_read=assessment_file.read()
            # size=len(file_read)
            # print(size)
            sourceFileName = secure_filename(assessment_file.filename)
            print(sourceFileName)
            
            # cwd = os.getcwd()+'/'
            # print(cwd)
            print("BASE_DIR : ",BASE_DIR)
            if 'temp' not in os.listdir(BASE_DIR):
                os.mkdir(str(BASE_DIR) + '/' + 'temp')
            assessment_file.save(os.path.join(str(BASE_DIR) +'/' + 'temp', sourceFileName))

            file_stats = os.stat(str(BASE_DIR) + '/' + 'temp/'+ sourceFileName)
            # print(file_stats)
            file_size=f'{round(file_stats.st_size / (1024 * 1024),2)} MB'
            print(file_size)
            print(f'{file_stats.st_size / (1024)} KB')
            print(f'{file_stats.st_size / (1024 * 1024)} MB')

            with open(str(BASE_DIR) + '/' + 'temp/'+ sourceFileName, 'rb') as f:
                # data_file = {
                #     "common_file":(sourceFileName, 'rb')
                # }
                data_file = {
                    "common_file":(sourceFileName, f)
                }
                print(data_file)
                file_uploader_api=base_url+file_upload_api
                file_upload_submit = requests.post(file_uploader_api,files=data_file,)
                                    
                file_upload_response=json.loads(file_upload_submit.text)
                print(file_upload_response)
                if file_upload_response['common_file']:
                    # delete the photo file from the temporary directory
                    os.remove(os.path.join(str(BASE_DIR) +'/' + 'temp', sourceFileName))
                print(file_upload_submit.status_code)
                # ""  Fetching File Path From Response and Passing it to Analysis info API  ""
                analysis_path=file_upload_response['common_file']
                print(analysis_path)
                print(base_url+analysis_text_api)
                data={
                    "appointment_id":appointment_id,
                    "doctor_id":user_id,
                    "analysis_path":str(analysis_path),
                    "file_size":file_size,
                    "file_name":sourceFileName,
                    "operation_flag":"file"
                }
                api_data=json.dumps(data)
                print(api_data)
                assessment_submit=requests.post(base_url+analysis_text_api,data=api_data,headers=headers)
                print(assessment_submit.status_code)
                assessment_response=json.loads(assessment_submit.text)
                print(assessment_response)
                if assessment_response['response_code']== 200:
                    flash("File uploaded","success")
                    
                else:
                    flash("Sorry.. Something went wrong","error")
                return redirect(url_for('orders_list'))

         # """"" RESCHEDULE APPOINTMENT """""       
        if request.form['form_type'] == 'reschedule':
            print('732',request.form)
            appointment_id=request.form['appointment_id']
            print("appointment_id:",appointment_id)
            type_booking = request.form['type_booking']
            print(type_booking)
            if type_booking == "new":
                reschedule_date=request.form[f'reschedule_date_jr{appointment_id}']
                reschedule_time=request.form[f'reschedule_time_jr{appointment_id}']
            else:
                reschedule_date=request.form[f'reschedule_date{appointment_id}']
                reschedule_time=request.form[f'reschedule_time_{appointment_id}']
            # remarks=request.form['remarks']
            
            reschedule_data={
                "appointment_id":appointment_id,
                "appointment_date":reschedule_date,
                "appointment_time":reschedule_time,
                # "appointment_status":5,
                "appointment_status":7,
                "user_id": user_id,
                "doctor_flag":doctor_flag,
                "doctor_id":""
            }
            reschedule_data_json=json.dumps(reschedule_data)
            print(reschedule_data_json)
            reschedule_submit=requests.post(base_url+reschedule_api, data=reschedule_data_json, headers=headers)
            reschedule_submit_response=json.loads(reschedule_submit.text)
            print(reschedule_submit_response)
            print(reschedule_submit.status_code)
            flash("Appointment rescheduled","success")  
            return redirect(url_for('orders_list'))  

            # """"" CANCEL APPOINTMENT """"" 
        if request.form['form_type'] == "cancel":
            print("cancel appointment")
            appointment_id=request.form['appointment_number']
            actions=3
            print(appointment_id)
            print(actions)
            payload={
                'appointment_id':appointment_id,
                'appointment_status':actions
            }
            api_data=json.dumps(payload)
            print(api_data)
            action=requests.post(base_url+appointent_status_api,data=api_data,headers=headers)
            action_button_response=json.loads(action.text)
            print(action.status_code)
            print(action_button_response)
            flash("appointment cancelled","success")
            return redirect(url_for('orders_list')) 

            # """"" EDIT CUSTOMER PROFILE """"" 
        if request.form['form_type'] == "edit_profile":
            first_name=request.form['first_name']
            last_name=request.form['last_name']
            date_of_birth=request.form['date_of_birth']
            gender=request.form['gender']
            phone_number=request.form['phone_number']
            email_address=request.form['email']
            photo_file_path=''

            data={
                "user_id":user_id,
                "user_fname":first_name,
                "user_lname":last_name,
                "mobile_num":phone_number,
                "dob":date_of_birth,
                "gender":gender,
                "user_mail":email_address,
                "profile_pic":photo_file_path,
                "operation_flag":"edit"
            }
            json_data=json.dumps(data)
            print(json_data)
            customer_edit_submit=requests.post(base_url+customer_edit_api, data=json_data, headers=headers)
            print(customer_edit_submit.status_code)
            customer_edit_submit_response=json.loads(customer_edit_submit.text)
            print("post response:",customer_edit_submit.status_code)
            print(customer_edit_submit_response)
            if customer_edit_submit_response['response_code'] == 200:
                flash("profile updated","success")
                # return redirect(url_for('orders_list'))
            else:
                flash("Sorry .. something went wrong","error")
            return redirect(url_for('orders_list'))
        if request.form['form_type'] == 'add_payment':
            print('entered into add payment')
    print(appointment_list)
    print('profile1 ' ,profile1)
    print('profile2 ',profile2)
    now = datetime.now()
    return render_template('orders_list.html',appointment_list=appointment_list,history_appointment_list=history_appointment_list,
    profile1=profile1,profile2=profile2,now=now, timedelta=timedelta)

@app.template_filter('strptime')
def strptime_filter(value, fmt):
    return datetime.strptime(value, fmt)
#  DOWNLOAD FILES
@app.route('/user_download/<int:appointment_id>')
def user_download(appointment_id):
    file_path=request.args.get('file_path')
    print(file_path)
    try:
        print("download file")
        print("file url:",file_path)
        print("app id:",appointment_id)
        url=file_path
        print("line 1")
        #"" url="http://"+file_path ""
        # ""print(url)""
        # u=urlparse(file_path)
        # print(u)
        # uc=base_url+u.path
        # print("uc :", uc)
        # r = requests.get(uc)

        r = requests.get(url)        
        # ""r = requests.get(url)""
        print("print error1")
        # """this removes http and website part from url"""
        url_split_1 = urlparse(url)
        print(url_split_1)
        #""""this will split rest of the path from file name"""""
        file_name=os.path.basename(url_split_1.path)
        # file_name=os.path.basename(u.path)
        print("filename",file_name)
        # cwd = os.getcwd()+'/'
        # print(cwd)
        # if 'temp' not in os.listdir(cwd):
        #     os.mkdir(cwd + 'temp')
        # # """""saving file in flask app"""""
        # file_temp_save=open(cwd + 'temp/'+ file_name, "wb").write(r.content)
        # print("saved in temp")

        # cwd = os.getcwd()+'/'
        print("Base dir: ", BASE_DIR)
        if 'temp' not in os.listdir(BASE_DIR):
            os.mkdir(str(BASE_DIR) + 'temp')
        # """""saving file in flask app"""""
        file_temp_save=open(str(BASE_DIR) + '/' + 'temp/'+ file_name, "wb").write(r.content)
        print("saved in temp")

        # """""file_temp_save=open(f"{file_name}", "wb").write(r.content)""""""
        
        #""""""send file and as attachment downloads the file to desktop"""""""
        # return send_file(f"{str(BASE_DIR) + '/' + 'temp/'+ file_name}", as_attachment=True)
        response = send_file(f"{str(BASE_DIR) + '/' + 'temp/'+ file_name}", as_attachment=True)
        # delete the file from the temporary directory
        file_path = f"{str(BASE_DIR)}/temp/{file_name}"
        if os.path.exists(file_path):
            os.remove(file_path)
            print("removed from temp")
        return response
        
        # write to a file in the app's instance folder
        # come up with a better file name
        # with app.open_instance_resource('downloaded_file', 'wb') as f:
        #     f.write(r.content)
        # return redirect(url_for('order_details',appointment_id=appointment_id))
    except Exception as e:
        print("exception",e)
        flash("Sorry.. Could not download the file","error")
        return redirect(url_for("order_details",appointment_id=appointment_id))

@app.route("/orders_list/order_detail/<int:appointment_id>", methods=['GET','POST'])
def order_details(appointment_id):
    print(appointment_id)
    active_tab=request.args.get('active_tab')
    print("active",active_tab)
    
    if 'doctor_flag' in session:
        doctor_flag=session['doctor_flag']
        print(doctor_flag)
    else:
        print('returning to login')
        return redirect(url_for('login'))

    session['appointment_id']=appointment_id

    headers={
        "Content-Type":"application/json"
        }
    data={
        "appointment_id":appointment_id,
        "user_id":"",
        "file_flag":"",
        "doctor_id":""
    }
    api_data=json.dumps(data)
    print(api_data)
    appointment_detail=requests.post(base_url+appointment_detail_api,data=api_data,headers=headers)
    appointment_detail_response=json.loads(appointment_detail.text)
    print("detail api :",appointment_detail.status_code)
    appointment_details=appointment_detail_response['data']
    # print(appointment_details)
    user_id=appointment_details['user_id']
    category_id=appointment_details['category_id']
    follow_ups = appointment_details['followup']
    observations=appointment_details['observations']
    attachments = appointment_details['analysis_info']
    print(attachments)

    # Finding how many days between today and appointment date to show refund details when cancelling appointment
    if (appointment_details['type_booking'] == "regular") or (appointment_details['type_booking'] == "followup") :
        if appointment_details['sr_rescheduled_date']:
            # setup dates
            # previous_date = datetime.strptime(appointment_details['sr_rescheduled_date'], '%m-%d-%Y')
            order_date = datetime.strptime(appointment_details['sr_rescheduled_date'], f'%Y-%m-%d')
            today = datetime.today()

            # compute difference
            ndays = ( order_date - today ).days

            # print output
            print(ndays)
        elif appointment_details['appointment_date']: 
            # setup dates
            # previous_date = datetime.strptime(appointment_details['appointment_date'], '%m-%d-%Y')
            order_date = datetime.strptime(appointment_details['appointment_date'], f'%Y-%m-%d')
            # previous_date = datetime.strptime("02-19-2023", '%m-%d-%Y')
            today = datetime.today()

            # compute difference
            # ndays = (today - previous_date).days
            ndays = ( order_date - today ).days

            # print output
            print(ndays, "days")
    else:
        ndays=None        
    print(ndays)
    
    # """ Taking file name from attachments"""
    # for attachment in attachments:
    #     url_path=attachment['analysis_info_path']
    #     print(url_path)
    #     r = requests.get(url_path)
    #      # """this removes http and website part from url"""
    #     url_split_1 = urlparse(url_path)
    #     print(url_split_1)
    #     #""""this will split rest of the path from file name"""""
    #     file_name=os.path.basename(url_split_1.path)
    #     print("filename",file_name)

    
    # for attach in attachments:
    #     url_path=attach['analysis_info_path']
    #     print(url_path)
    # url="http://"+url_path
    # print(url)
    # r=requests.get(url)
    # abc=open("assessment.pdf", "wb").write(r.content)
    # return send_file("assessment.pdf", as_attachment=True)
    # r=requests.get(url)
    # open(url)
    # with app.open_instance_resource('downloaded_file','wb') as f:
    #     print(f)
    #     f.write(r.content)
        
    # follow up reminder list api call
    data1={
        "appointment_id":appointment_id   
        }
    api_data1=json.dumps(data1)
    print(api_data1)
    followup_reminder_request = requests.post(base_url+followup_reminder_list_api, data=api_data1, headers=headers)
    followup_reminder_response = json.loads(followup_reminder_request.text)
    print("reminder api",followup_reminder_request.status_code)
    followup_reminder = followup_reminder_response['data']
    # print(followup_reminder)
    # followup_reminder_list_api="api/doctor/followup_reminder_list"

    if request.method == 'POST':

        if request.form['form_type'] == 'edit_customer_info': 
            print("edit_customer_info")     
            
            photo_file = request.files["photo_file"]
            if photo_file.filename == '':
                photo_file_path=''
                print("no photo file")
            else:
                sourceFileName = secure_filename(photo_file.filename)
                print(sourceFileName)
                # cwd = os.getcwd()+'/'
                # print(cwd)
                # if 'temp' not in os.listdir(cwd):
                #     os.mkdir(cwd + 'temp')
                # photo_file.save(os.path.join(cwd + 'temp', sourceFileName))

                # with open(cwd + 'temp/'+ sourceFileName, 'rb') as f:
                    # data_file = {
                    #     "common_file":(sourceFileName, 'rb')
                    # }
                print("BASE_DIR : ",BASE_DIR)
                if 'temp' not in os.listdir(BASE_DIR):
                    os.mkdir(str(BASE_DIR) + '/' + 'temp')
                photo_file.save(os.path.join(str(BASE_DIR) +'/' + 'temp', sourceFileName))

                with open(str(BASE_DIR) + '/' + 'temp/'+ sourceFileName, 'rb') as f:    
                    data_file = {
                        "common_file":(sourceFileName, f)
                    }
                    print(data_file)
                    file_uploader_api=base_url+file_upload_api
                    file_upload_submit = requests.post(file_uploader_api,files=data_file,)
                    print(file_upload_submit.status_code)                    
                    file_upload_response=json.loads(file_upload_submit.text)
                    print(file_upload_response)
                    print(file_upload_submit.status_code)
                    photo_file_path=file_upload_response['common_file']
                    if file_upload_response['common_file']:
                        flash(f"{sourceFileName} uploaded","success")
                        # delete the photo file from the temporary directory
                        os.remove(os.path.join(str(BASE_DIR) +'/' + 'temp', sourceFileName))
                    else:
                        flash("Something went wrong","error")

            first_name=request.form['first_name']
            last_name=request.form['last_name']
            date_of_birth=request.form['date_of_birth']
            phone_number=request.form['phone_number']
            email_address=request.form['email_address']
            gender=request.form['gender']

            data={
                "user_id":user_id,
                "user_fname":first_name,
                "user_lname":last_name,
                "mobile_num":phone_number,
                "dob":date_of_birth,
                "gender":gender,
                "user_mail":email_address,
                "profile_pic":photo_file_path,
                "operation_flag":"edit"
            }
            json_data=json.dumps(data)
            print(json_data)
            customer_edit_submit=requests.post(base_url+customer_edit_api, data=json_data, headers=headers)
            print(customer_edit_submit.status_code)
            customer_edit_submit_response=json.loads(customer_edit_submit.text)
            print("post response:",customer_edit_submit.status_code)
            print(customer_edit_submit_response)
            if customer_edit_submit_response['response_code'] == 200:
                flash("profile updated","success")
            else:
                flash("Sorry .. something went wrong","error")
            return redirect(url_for('order_details',appointment_id=appointment_id))

        if request.form['form_type'] == 'reschedule':
            # reschedule_date=request.form['reschedule_date']
            # reschedule_time=request.form['reschedule_time']
            type_booking = request.form['type_booking']
            print(type_booking)
            if type_booking == "new":
                reschedule_date=request.form[f'reschedule_date_jr']
                reschedule_time=request.form[f'reschedule_time_jr{appointment_id}']
            else:
                reschedule_date=request.form[f'reschedule_date']
                reschedule_time=request.form[f'reschedule_time_{appointment_id}']
            # remarks=request.form['remarks']
            reschedule_data={
                "appointment_id":appointment_id,
                "appointment_date":reschedule_date,
                "appointment_time":reschedule_time,
                # "appointment_status":5,
                "appointment_status":7,
                "user_id": user_id,
                "doctor_flag":doctor_flag,
                "doctor_id":""
            }
            reschedule_data_json=json.dumps(reschedule_data)
            print(reschedule_data_json)
            reschedule_submit=requests.post(base_url+reschedule_api, data=reschedule_data_json, headers=headers)
            reschedule_submit_response=json.loads(reschedule_submit.text)
            print(reschedule_submit_response)
            print(reschedule_submit.status_code)

        # if request.form['form_type'] == 'follow_up':
        #     appointment_date=request.form['follow_up_date']
        #     appointment_time=request.form['follow_up_time']
        #     remarks=request.form['remarks']
        #     payload={
        #                 "new_user":1,
        #                 "user_id":user_id,
        #                 "appointment_date":appointment_date,
        #                 "appointment_time":appointment_time,
        #                 "followup_id":appointment_id,
        #                 "category_id":category_id,
        #                 "type_booking":"followup"
        #     }
        #     api_data=json.dumps(payload)
        #     follow_up_submit=requests.post(base_url+follow_up_api, data=api_data, headers=headers)
        #     follow_up_response=json.loads(follow_up_submit.text)
        #     print(follow_up_submit.status_code)
        #     print(follow_up_response)

        if request.form['form_type'] == 'analysis': 
            print("analysis")       
            active_tab="attachment"
            analysis_text=request.form['analysis']
            data={
                "appointment_id":appointment_id,
                "analysis_text":analysis_text,
                "doctor_id":user_id
            }
            json_data=json.dumps(data)
            print(json_data)
            analysis_text_submit=requests.post(base_url+analysis_text_api, data=json_data, headers=headers)
            analysis_text_submit_response=json.loads(analysis_text_submit.text)
            print(analysis_text_submit_response)
            print(analysis_text_submit.status_code)

        if request.form['form_type'] == 'upload_assessment':
            print("upload assessment")
            active_tab="attachment"
            print("active tab :attachment")
            file_headers={
                'files' : 'multipart/form-data'
            }
            assessment_file = request.files["customFile"]
            
            sourceFileName = secure_filename(assessment_file.filename)
            print(sourceFileName)
            # cwd = os.getcwd()+'/'
            # print(cwd)
            # if 'temp' not in os.listdir(cwd):
            #     os.mkdir(cwd + 'temp')
            # assessment_file.save(os.path.join(cwd + 'temp', sourceFileName))

            # with open(cwd + 'temp/'+ sourceFileName, 'rb') as f:
                # data_file = {
                #     "common_file":(sourceFileName, 'rb')
                # }
            print("BASE_DIR : ",BASE_DIR)
            if 'temp' not in os.listdir(BASE_DIR):
                os.mkdir(str(BASE_DIR) + '/' + 'temp')
            assessment_file.save(os.path.join(str(BASE_DIR) +'/' + 'temp', sourceFileName))

            file_stats = os.stat(str(BASE_DIR) + '/' + 'temp/'+ sourceFileName)
            # print(file_stats)
            file_size=f'{round(file_stats.st_size / (1024 * 1024),2)} MB'
            print(file_size)
            print(f'{file_stats.st_size / (1024)} KB')
            print(f'{file_stats.st_size / (1024 * 1024)} MB')

            with open(str(BASE_DIR) + '/' + 'temp/'+ sourceFileName, 'rb') as f:    
                data_file = {
                    "common_file":(sourceFileName, f)
                }
                print(data_file)
                file_uploader_api=base_url+file_upload_api
                file_upload_submit = requests.post(file_uploader_api,files=data_file,)
                                    
                file_upload_response=json.loads(file_upload_submit.text)
                print(file_upload_response)
                
                print(file_upload_submit.status_code)
                # ""  Fetching File Path From Response and Passing it to Analysis info API  ""
                analysis_path=file_upload_response['common_file']
                print(analysis_path)
                print(base_url+analysis_text_api)
                data={
                    "appointment_id":appointment_id,
                    "doctor_id":user_id,
                    "analysis_path":str(analysis_path),
                    "file_size":file_size,
                    "file_name":sourceFileName,
                    "operation_flag":"file"
                }
                api_data=json.dumps(data)
                print(api_data)
                assessment_submit=requests.post(base_url+analysis_text_api,data=api_data,headers=headers)
                print(assessment_submit.status_code)
                assessment_response=json.loads(assessment_submit.text)
                print(assessment_response)
                if assessment_response['response_code']==200:
                    flash("Upload success","success")
                else:
                    flash("Something went wrong..","error")
            if file_upload_response['common_file']:
                    # delete the  file from the temporary directory
                    os.remove(os.path.join(str(BASE_DIR) +'/' + 'temp', sourceFileName))
            # print("upload assessment")
            # file_headers={
            #     'files' : 'multipart/form-data'
            # }
            # print("error 1")
            # assessment_file=request.files['customFile']
            # print("error2")
            # print(assessment_file)
            # filename=secure_filename(assessment_file.filename)
            # print("error3")
            # print(filename)
            # files={
            #     'common_file' : open(filename,'rb')
            # }
            # print(files)
            # data={
            #     'appointment_id': appointment_id,
            #     'file_flag':'analysis_info'
            # }
            # api_data=json.dumps(data)
            # file_upload_submit=requests.post(base_url+file_upload_api, files=files, data=api_data, headers=file_headers)
            # file_upload_response=json.loads(file_upload_submit.text)
            # print(file_upload_response)
            # print(file_upload_submit.status_code)

        # if request.form['form_type'] == 'download_assessment': 
        #     print("download")
        #     count=len(attachments)
        #     print("attachments count",count)
        #     analysis_id=request.form['analysis_id']
        #     for one_file in attachments:
        #         url=one_file['analysis_info']    
        #         print(one_file)

        return redirect(url_for("order_details",appointment_id=appointment_id, active_tab=active_tab))
    print(appointment_details)
    print(session)
    return render_template("order_details.html",appointment_details=appointment_details,follow_ups=follow_ups,
    followup_reminder=followup_reminder,observations=observations,active_tab=active_tab,ndays=ndays)

@app.route("/reschedule/<int:appointment_id>/<string:appointment_date>/<string:appointment_time_slot_id>/<string:rescheduled_date>",methods=['GET','POST'])
def reschedule_order(appointment_id, appointment_date, appointment_time_slot_id, rescheduled_date):
    print(session)
    headers={   
        "Content-Type":"application/json"
        }
    if rescheduled_date != 'none':
        flash("You have already rescheduled this appointment once and cannot be rescheduled again.")
        return redirect(url_for('orders_list'))
    
    try:
        appointment_datetime_str = f"{appointment_date} {appointment_time_slot_id}"
        appointment_datetime = datetime.strptime(appointment_datetime_str, "%Y-%m-%d %I:%M%p")
        
        current_datetime = datetime.now()

        time_difference = appointment_datetime - current_datetime

        if time_difference > timedelta(hours=24):
            pass
        else:
            data={
            "appointment_id":appointment_id,
            }
            api_data=json.dumps(data)
            reschedule_check_request=requests.post(base_url+reschedule_check,data=api_data,headers=headers)
            reschedule_check_response=json.loads(reschedule_check_request.text)
            if reschedule_check_response['response_code'] == 200:
                pass
            else:
                flash(" This appointment cannot be rescheduled. You have to reschedule your appointment at least 24 hours prior to your appointment time.")
                return redirect(url_for('orders_list'))
    
    except ValueError as e:
        print( f"Invalid date or time format: {e}")

    try:
        if 'doctor_flag' in session:
            doctor_flag=session['doctor_flag']
            print(doctor_flag)
        else:
            return redirect(url_for('login_phone'))
        if 'user_id' in session:
            user_id=session['user_id']
            print(user_id)
        else:
            return redirect(url_for('login_phone'))
        
        if 'country' in session:
            location=session['country']
        else:
            return redirect(url_for('login_phone'))

        session['appointment_id']=appointment_id

        
        
        # Appointment details api call
        data={
            "appointment_id":appointment_id,
            "user_id":"",
            "file_flag":"",
            "doctor_id":""
        }
        api_data=json.dumps(data)
        appointment_detail=requests.post(base_url+appointment_detail_api,data=api_data,headers=headers)
        appointment_detail_response=json.loads(appointment_detail.text)
        's'
        print("detail api :",appointment_detail_response)
        appointment_details=appointment_detail_response['data']
        # print(appointment_details)
        user_id=appointment_details['user_id']
        # category_id=appointment_details['category_id']
        type_booking=str(appointment_details['type_booking'])
        print("type_booking",type_booking)
        preferred = True
        # Checking booking type
        if str(type_booking) == "regular" or type_booking=="followup":
            time_flag=1
            print("snr doc")
            data={
                # "specialization":specialist,
                "language_pref":"",
                "gender":"",
                "doctor_flag":"senior",
                "specialization":"",
                "appointment_id":appointment_id,
                "location":location,
                "regular":'regular'
                # "appointment_date":date
            }
            api_data=json.dumps(data)
            # senior doctor time slot api
            senior_time=requests.post(base_url+snr_doc_time_api,data=api_data,headers=headers)
            print("senior time slot",senior_time.status_code)
            time_response=json.loads(senior_time.text)
            print(time_response)
            if time_response['response_code'] == 200:
                print("snr timeslot")
                timeslots=time_response['slots']
               
        elif type_booking == "new":
            
            print("new")
            if appointment_details['escalated_date']:
                time_flag=1
                print("escalated")
                # if escalated senior doctor timeslot is called
                data={
                # "specialization":specialist,
                "language_pref":"",
                "gender":"",
                "doctor_flag":"senior",
                "location":location,
                "appointment_id":appointment_id,
                "senior_doctor_id":appointment_detail_response['data']['senior_doctor']
                }
                api_data=json.dumps(data)
                print(api_data)
                # senior doctor time slot api
                senior_time=requests.post(base_url+specialization_time_slot_reschedule,data=api_data,headers=headers)
                print("senior time slot",senior_time.status_code)
                time_response=json.loads(senior_time.text)
                print('1341 ',time_response['preferred'],'\n')
                preferred = time_response['preferred']
                if time_response['response_code'] == 200:
                    timeslots=time_response['slots']
               
            else:
                time_flag=2
                print("jr doc")
                # if order not escalated junior doctor timeslot api is called
                payload={
                    "language":"",
                    "gender":"",
                    "doctor":"junior",
                    "appointment_date":"",
                    "location":location,
                    "appointment_id":appointment_id
                    # "specialization":""
                }
                api_data=json.dumps(payload)
                jr_doc_time=requests.post(base_url+time_slot_api2, data=api_data, headers=headers)
                print(jr_doc_time.status_code)
                jr_time=json.loads(jr_doc_time.text)
                print(jr_time)
                timeslots = jr_time['slots']
        print("flag",time_flag)   
        print("time slots :",timeslots)     

        if request.method == "POST":
            print('POST')
            print(session)
            try:
                
                reschedule_time=request.form.get('time')
                reschedule_date=request.form.get('app_date')
                reschedule_data={
                    "appointment_id":appointment_id,
                    "appointment_date":reschedule_date,
                    "appointment_time":reschedule_time,
                    "appointment_status":7,
                    "user_id": user_id,
                    "doctor_flag":doctor_flag,
                    "doctor_id":""
                }
                reschedule_data_json=json.dumps(reschedule_data)
                print(reschedule_data_json)
                reschedule_submit=requests.post(base_url+reschedule_api, data=reschedule_data_json, headers=headers)
                'ss'
                reschedule_submit_response=json.loads(reschedule_submit.text)
                print(reschedule_submit_response)
                print(reschedule_submit.status_code)
                if reschedule_submit_response['response_code'] == 200:
                    flash("Appointment rescheduled","success")
                else:
                    flash("Something went wrong.. Try again later","error")
                return redirect(url_for('orders_list'))
            except Exception as e:
                print('Exception inside post',e)
                flash("Something went wrong.. Try again","error")
                return render_template("reschedule.html")
        return render_template("reschedule.html",appointment_details=appointment_details,timeslots=timeslots,time_flag=time_flag,preferred=preferred)
    except Exception as e:
        print('Exception outside post',e)
        flash("Something went wrong..","error")
        return render_template("reschedule.html",)



@app.route("/orders_list/order_detail/<actions>/<int:appointment_id>", methods=['GET','POST'])
# actions: accept=1,reject=3,escalate=2, 
# reschedule by doctor = 4, reschedule by customer = 5
# appointment closed = 6
def action_button(actions,appointment_id):
    # appointent_status_api="api/doctor/appointment_status_update"
    headers={
            "Content-Type":"application/json"
        }
    print(appointment_id)
    print(actions)
    payload={
        'appointment_id':appointment_id,
        'appointment_status':actions
    }
    api_data=json.dumps(payload)

    action=requests.post(base_url+appointent_status_api,data=api_data,headers=headers)
    print(action)
    action_button_response=json.loads(action.text)
    print('goasidjfoiasdf')

    print(action.status_code)
    print(action_button_response)
    return redirect(url_for("order_details",appointment_id=appointment_id))

@app.route("/prescription_pdf/<int:appointment_id>/<int:prescription_id>",methods=['GET','POST'])
def prescription_pdf(appointment_id,prescription_id):
    print(prescription_id)
    # if 'user_id' in session:
    #     doctor_id=session['user_id']
    #     print("doc id",doctor_id)
    # else:
    #     return redirect(url_for('login'))
    
    # if 'doctor_flag' in session:
    #     doctor_flag=session['doctor_flag']
    #     print("doc flag",doctor_flag)

    headers={
            "Content-type":"application/json"
    }
    print(appointment_id)
    payload={
        "appointment_id":appointment_id,
        "user_id":"",
        "file_flag":"",
        "doctor_id":""
    }
    api_data=json.dumps(payload)
    print(api_data)
    appointment_detail=requests.post(base_url+appointment_detail_api, data=api_data, headers=headers)
    appointment_detail_response=json.loads(appointment_detail.text)
    appointment_details=appointment_detail_response['data']
    print("detail api :",appointment_detail.status_code)
    user_id=appointment_details['user_id']
    print(user_id)
    category_id=appointment_details['category_id']
    follow_ups = appointment_details['followup']
    observations=appointment_details['observations']
    prescript_text=appointment_details["prescript_text"]
    for precription in prescript_text:
        if precription['id'] == prescription_id:
            precription ={
            "doctor_id":precription['doctor_id'],
            "uploaded_time":precription['uploaded_time'],
            "uploaded_date":precription['uploaded_date'],
            "prescriptions_text":precription['prescriptions_text'],
            "tests_to_be_done" : precription['tests_to_be_done'],
            "medicines" :precription['medicines'],
            "doctor_name" : precription['doctor_name'],
            }
    return render_template("prescription_pdf.html", appointment_details=appointment_details,prescript_text=prescript_text,prescription=precription)

@app.route("/follow_up_remarks",methods=['GET','POST'])
def follow_up_remarks():
    if request.method == 'POST':
        remarks=request.form['remarks']
        if 'remarks'in session:
            session.pop('remarks',None)
            session['remarks']=remarks
        else:
            session['remarks']=remarks
    return render_template("follow_up_remarks.html")

@app.route("/follow_up/<int:appointment_id>", methods=['GET','POST'])
def follow_up(appointment_id):
    # if 'user_id' in session:
    #     user_id=session['user_id']
    #     print(user_id)
    print(session)
    if 'country' in session:
        if session['country'] == 'United States':
            country = 'USA'
        else:
            country = session['country']
        print('country')
        if (country == 'IN') or (country == 'IND'):
            location_id = 1
        else:
            location_id = 2
    else:
        location_id = 2

    session['loc_id']=location_id

    headers={
        "Content-Type":"application/json"
        }
    
    #category list api call
    category_req=requests.post(base_url+category_api,headers=headers)
    print("category api:",category_req.status_code)
    category_resp=json.loads(category_req.text)
    print(category_resp)
    categories=category_resp['data']

    data={
        "appointment_id":appointment_id,
        "user_id":"",
        "file_flag":""
    }
    api_data=json.dumps(data)
    appointment_detail=requests.post(base_url+appointment_detail_api,data=api_data,headers=headers)
    appointment_detail_response=json.loads(appointment_detail.text)
    print("follow up",appointment_detail.status_code)
    appointment_details=appointment_detail_response['data']
    user_id=appointment_details['user_id']
    print(user_id)
    category_id=appointment_details['category_id']
    for category in categories:
        print("categories")
        if int(category_id) == category['id']:
            print(category_id,category['id'])
            category_title=category['title']
            print(category_title)
            session['category_title']=category_title
    
    data={
        # "specialization":specialist,
        "appointment_id":appointment_id,
        "language_pref":"",
        "gender":"",
        "doctor":"senior",
        "location":country
        # "appointment_date":date
    }
    api_data=json.dumps(data)
    print(api_data)
    # senior doctor Time Slot api call
    senior_time=requests.post(base_url+snr_doc_time_api,data=api_data,headers=headers)
    print("senior time slot",senior_time.status_code)
    time_response=json.loads(senior_time.text)
    print("Senior time slots :",time_response)
    if time_response['response_code'] == 200:
        timeslots=time_response['slots']

    if request.method=='POST':
        paid_appointment=request.form['form_type']
        session['paid_appointment']=paid_appointment
        appointment_date=request.form['app_date']
        appointment_time=request.form['time']
        # remarks=request.form['remarks']
        payload={
                            "new_user":0,
                            "user_id":user_id,
                            "appointment_date":appointment_date,
                            "appointment_time":appointment_time,
                            "followup_id":appointment_id,
                            "category_id":category_id,
                            "type_booking":"followup",
                            "doctor_flag":0,
                            "doctor_id":"",
                            "appointment_status":8,
                            "remarks":"",
                            "followup_created_by":"user",
                            "followup_created_doctor_id":user_id,
                            "specialization":"",
                            # "followup_doctor":""
                }
        session['follow_up_data']=payload
        print(payload)
        # api_data=json.dumps(payload)
        # follow_up_submit=requests.post(base_url+follow_up_api, data=api_data, headers=headers)
        # follow_up_response=json.loads(follow_up_submit.text)
        # print(follow_up_submit.status_code)
        # print(follow_up_response)
        return redirect(url_for('follow_up_preview'))
    return render_template('follow_up.html',appointment_details=appointment_details,timeslots=timeslots)

@app.route("/follow_up_preview",methods=['GET','POST'])
def follow_up_preview():
    headers={
        "Content-Type":"application/json"
        }

    if 'category_title' in session:
        category_title = session['category_title']
    if 'loc_id' in session:
        location_id = session['loc_id']
    # payload={
    #         "invoice_id":11
    #     }
    # api_data=json.dumps(payload)
    # invoice_request=requests.post(base_url+invoice_detail_api,data=api_data,headers=headers)
    # invoice_response=json.loads(invoice_request.text)
    # print("invoice detail",invoice_request.status_code)
    # invoice_details=invoice_response['data']
    # print(invoice_details)
    
    if 'follow_up_data' in session:
        follow_up_data=session['follow_up_data']
        print("preview",follow_up_data)
        # payload={
        # "location_id":1
        # } 
        user_id=follow_up_data['user_id'] 
        appointment_id=follow_up_data['followup_id']

        data={
        "appointment_id":appointment_id,
        "user_id":"",
        "file_flag":"",
        "doctor_id":""
        }
        api_data1=json.dumps(data)
        print(api_data1)
        appointment_detail=requests.post(base_url+appointment_detail_api,data=api_data1,headers=headers)
        appointment_detail_response=json.loads(appointment_detail.text)
        print("detail api :",appointment_detail.status_code)
        appointment_details=appointment_detail_response['data']
        if request.method == 'POST':
            coupon = request.form['coupon']
        else:
            coupon = ""
        payload={
                    "user_id":user_id,
                    "appointment_id":appointment_id,
                    "specialization":"",
                    "coupon_code":"",
                    "location_id":str(location_id)
                }
        api_data=json.dumps(payload)
        payments_request=requests.post(base_url+payments_api,data=api_data,headers=headers)
        payment_response=json.loads(payments_request.text)
        print(payment_response)
        print("payment api",payments_request.status_code)
        payment=payment_response['payment']
        temp_data_id = payment_response['temp_data_id']
        session['temp_data_id']= temp_data_id
        # if request.method=='POST':
        #     print("post")
        #     api_data=json.dumps(follow_up_data)
        #     follow_up_submit=requests.post(base_url+follow_up_api, data=api_data, headers=headers)
        #     follow_up_response=json.loads(follow_up_submit.text)
        #     print("follow up",follow_up_submit.status_code)
        #     print(follow_up_response)
        #     new_appointment_id=follow_up_response["followup_appointment_id"]
        #     print("new id:",new_appointment_id)
        #     return redirect(url_for('pay_confirm',appointment_id=new_appointment_id))
            # return render_template('follow_up_preview.html')

    return render_template('follow_up_preview.html',follow_up_data=follow_up_data,payment=payment,appointment_details=appointment_details)

@app.route("/customer_profile", methods=['GET','POST'])
def customer_profile():
    try:
        if 'user_id' in session:
            user_id=session['user_id']
            print(user_id)
        else:
            return redirect(url_for('login'))
        headers = {
                "Content-Type":"application/json"
            }
        payload={
            "user_id":user_id
        }
        api_data=json.dumps(payload)
        print(api_data)
        customer_profile_request=requests.post(base_url+customer_profile_api, data=api_data, headers=headers)
        print(customer_profile_request.status_code)
        customer_profile_response=json.loads(customer_profile_request.text)
        print(customer_profile_request.status_code)
        profile1=customer_profile_response['data1']
        profile2=customer_profile_response['data2']
        customer_first_name = profile1['first_name']
        session['customer_first_name'] = customer_first_name
        customer_last_name = profile1['last_name']
        session['customer_last_name'] = customer_last_name
        profile_pic=profile2['profile_pic']
        session['profile_pic'] = profile_pic
        # customer_email = profile1['email']
        # session['customer_email'] = customer_email
        print(customer_first_name, customer_last_name)

        if request.method == 'POST': 
            print("edit_customer_info")
            photo_file = request.files["photo_file"]     
            if photo_file.filename == '':
                photo_file_path=''
                print("no photo file")
            else:
                photo_file = request.files["photo_file"]
                print("photo file present")
                sourceFileName = secure_filename(photo_file.filename)
                print(sourceFileName)
                # cwd = os.getcwd()+'/'
                # print(cwd)
                # if 'temp' not in os.listdir(cwd):
                #     os.mkdir(cwd + 'temp')
                # photo_file.save(os.path.join(cwd + 'temp', sourceFileName))

                # with open(cwd + 'temp/'+ sourceFileName, 'rb') as f:
                print("BASE_DIR : ",BASE_DIR)
                if 'temp' not in os.listdir(BASE_DIR):
                    os.mkdir(str(BASE_DIR) + '/' + 'temp')
                photo_file.save(os.path.join(str(BASE_DIR) +'/' + 'temp', sourceFileName))

                with open(str(BASE_DIR) + '/' + 'temp/'+ sourceFileName, 'rb') as f:
                    # data_file = {
                    #     "common_file":(sourceFileName, 'rb')
                    # }
                    data_file = {
                        "common_file":(sourceFileName, f)
                    }
                    print(data_file)
                    file_uploader_api=base_url+file_upload_api
                    file_upload_submit = requests.post(file_uploader_api,files=data_file,)
                    print(file_upload_submit.status_code)                    
                    file_upload_response=json.loads(file_upload_submit.text)
                    print(file_upload_response)
                    print(file_upload_submit.status_code)
                    photo_file_path=file_upload_response['common_file']
                    if file_upload_response['common_file']:
                        flash(f"{sourceFileName} uploaded","success")
                        # delete the photo file from the temporary directory
                        os.remove(os.path.join(str(BASE_DIR) +'/' + 'temp', sourceFileName))
                    else:
                        flash("Something went wrong","error")

            first_name=request.form['first_name']
            last_name=request.form['last_name']
            date_of_birth=request.form['date_of_birth']
            phone_number=request.form['phone_number']
            email_address=request.form['email_address']
            gender=request.form['gender']

            data={
                "user_id":user_id,
                "user_fname":first_name,
                "user_lname":last_name,
                "mobile_num":phone_number,
                "dob":date_of_birth,
                "gender":gender,
                "user_mail":email_address,
                "profile_pic":photo_file_path,
                "operation_flag":"edit"
            }
            json_data=json.dumps(data)
            print(json_data)
            customer_edit_submit=requests.post(base_url+customer_edit_api, data=json_data, headers=headers)
            print(customer_edit_submit.status_code)
            customer_edit_submit_response=json.loads(customer_edit_submit.text)
            print("customer profile edit response:",customer_edit_submit.status_code)
            print(customer_edit_submit_response)
            # updating customer details in session
            customer_first_name = profile1['first_name']
            session['customer_first_name'] = customer_first_name
            customer_last_name = profile1['last_name']
            session['customer_last_name'] = customer_last_name
            profile_pic=profile2['profile_pic']
            session['profile_pic'] = profile_pic
            # customer_email = profile1['email']
            # session['customer_email'] = customer_email
            print(customer_first_name, customer_last_name)
            if customer_edit_submit_response['response_code'] == 200:
                flash("profile updated","success")
                return redirect(url_for('customer_profile'))
            else:
                flash("Sorry .. something went wrong","error")
                return redirect(url_for('customer_profile'))
            return redirect(url_for('customer_profile'))
        return render_template("customer_profile.html",profile1=profile1,profile2=profile2)
    except Exception as e:
        print(e)
        flash("No file selected","error")
    return render_template('customer_profile.html',profile1=profile1,profile2=profile2)

@app.route("/invoices")
def invoices():
    try:
        if 'user_id' in session:
            user_id=session['user_id']
            print(user_id)
        headers={
        "Content-Type":"application/json"
        }
        payload1={
            "user_id":user_id,
            "status": "1"
        }
        api_data1=json.dumps(payload1)
        print(api_data1)
        invoices_request=requests.post(base_url+invoice_list_api,data=api_data1,headers=headers)
        invoice_response=json.loads(invoices_request.text)
        print("invoice list:",invoices_request.status_code)
        paid_invoices=invoice_response['data']
        payload2={
            "user_id":user_id,
            "status": "2"
        }
        api_data2=json.dumps(payload2)
        print(api_data2)
        invoices_request=requests.post(base_url+invoice_list_api,data=api_data2,headers=headers)
        invoice_response=json.loads(invoices_request.text)
        print("invoice list:",invoices_request.status_code)
        unpaid_invoices=invoice_response['data']
        return render_template('invoices.html',paid_invoices=paid_invoices,unpaid_invoices=unpaid_invoices)

    except Exception as e:
        print(e)
    return render_template('invoices.html')

@app.route("/invoice_details/<int:invoice_id>", methods=['GET','POST'])
def invoice_details(invoice_id):
    try:
        headers={
        "Content-Type":"application/json"
        }
        payload={
            "invoice_id":invoice_id
        }
        api_data=json.dumps(payload)
        invoice_request=requests.post(base_url+invoice_detail_api,data=api_data,headers=headers)
        invoice_response=json.loads(invoice_request.text)
        print("invoice detail",invoice_request.status_code)
        invoice_details=invoice_response['data']
        print(invoice_details)
        paid_appointment="unpaid_invoice"
        session['paid_appointment']= paid_appointment
        session['invoice_data']=invoice_details
        # if request.method == 'POST':
        #     print("post")
        #     payload={
        #         "appointment_id":appointment_id,
        #         "location_id":1
        #     }
        #     api_data=json.dumps(payload)
        #     print(api_data)
        #     pay_confirm_request=requests.post(base_url+customer_payments_api,data=api_data,headers=headers)
        #     pay_confirm_response=json.loads(pay_confirm_request.text)
        #     print("payment confirm :", pay_confirm_request.status_code)
        #     print(pay_confirm_response)
        #     return redirect(url_for('pay_confirm'))
        return render_template('invoice_details.html',invoice_details=invoice_details)

    except Exception as e:
        print(e)
    return render_template('invoice_details.html')

@app.route("/invoice_preview",methods=['GET','POST'])
def invoice_preview():
    print("invoice preview")

    if 'country' in session:
        country = session['country']
        print('country')
        if (country == 'IN') or (country == 'IND'):
            location_id = 1
        else:
            location_id = 2
    else:
        location_id = 2

    session['loc_id']=location_id

    headers={
        "Content-Type":"application/json"
        }
  
    if 'invoice_data' in session:
        invoice_data=session['invoice_data']
        print("preview",invoice_data)
        user_id=invoice_data['user_id']
        appointment_id = invoice_data['appointment_id']
    # if 'new_appointment_specialization' in session:
    #     new_appointment_specialization=session['new_appointment_specialization']
    if request.method == 'POST':
        coupon = request.form['coupon']
    else:
        coupon = ""
        #paymemts api call
        # payload={
        # "location_id":1
        # }  
    payload={
                    "user_id":user_id,
                    "appointment_id":appointment_id,
                    "specialization":"",
                    "coupon_code":"",
                    "location_id":str(location_id)
                }
    api_data=json.dumps(payload)
    print(api_data)
    payments_request=requests.post(base_url+payments_api,data=api_data,headers=headers)
    payment_response=json.loads(payments_request.text)   
    print("payments api",payments_request.status_code)
    print(payment_response)
    payment=payment_response['payment']
    temp_data_id = payment_response['temp_data_id']
    session['temp_data_id']= temp_data_id
        # if request.method=='POST':
        #     print("post")
        #     api_data=json.dumps(new_data)
        #     new_appointment_request=requests.post(base_url+follow_up_api, data=api_data, headers=headers)
        #     new_appointment_response=json.loads(new_appointment_request.text)
        #     print(new_appointment_request.status_code)
        #     print(new_appointment_response)
        #     new_appointment_id=new_appointment_response["appointment_id"]
        #     print("new id:",new_appointment_id)
        #     return redirect(url_for('pay_confirm',appointment_id=new_appointment_id))
            # return render_template('follow_up_preview.html')

    return render_template('unpaid_invoice_preview.html',invoice_data=invoice_data,payment=payment)

@app.route("/payment_confirm/<int:appointment_id>")
def pay_confirm(appointment_id):
    try:
        print("pay confirm")
        headers={
            "Content-Type":"application/json"
            }
            # change this appointment id
        # if 'appointment_id' in session:
        #     appointment_id=session['appointment_id']
        #     print(appointment_id)
        payload={
            
            "location_id":1,
            "appointment_id":appointment_id
        }
        api_data=json.dumps(payload)
        print(api_data)
        pay_confirm_request=requests.post(base_url+customer_payments_api,data=api_data,headers=headers)
        pay_confirm_response=json.loads(pay_confirm_request.text)
        print("payment confirm :", pay_confirm_request.status_code)
        print(pay_confirm_response)
        return render_template("payment_confirmation.html")
    except Exception as e:
        print(e)
    return render_template("payment_confirmation.html")

@app.route("/follow_up_disclaimer/<int:appointment_id>" , methods=['GET','POST'])
def disclaimer(appointment_id):
    print('appointment_id',appointment_id)
    if request.method == 'POST':
        print('post')
        #in new appointment creation appointment id will be passed as 0000
        if appointment_id == 0000 :
            return redirect(url_for('new_appointment'))
        else :
            return redirect(url_for('follow_up',appointment_id=appointment_id))
    return render_template('disclaimer_page.html')

@app.route("/new_appointment",methods=['GET','POST'])
def new_appointment():
    try:
        if 'user_id' in session:
            user_id=session['user_id']
            print(user_id)
        else:
            return redirect(url_for('login'))
        headers = {
            "Content-Type":"application/json"
        }
        # customer list api call
        payload={
            "operation_flag":"view"
        }
        api_data=json.dumps(payload)
        customer_list_request=requests.post(base_url+customer_listing_api, data=api_data, headers=headers)
        's'
        customer_list_response=json.loads(customer_list_request.text)
        print("customer list",customer_list_request.status_code)
        customers=customer_list_response['data']
        # doctor list api call
        doctor_listing=requests.post(base_url+doctor_listing_api, headers=headers)
        doctor_list_response=json.loads(doctor_listing.text)
        print("doctor list",doctor_listing.status_code)
        doctors = doctor_list_response['data']
        # language api call
        language_api_request=requests.get(base_url+language_api,headers=headers)
        print("language",language_api_request.status_code)
        language_api_response=json.loads(language_api_request.text)
        languages=language_api_response['data']
        #specializations list api call
        specialization_request=requests.get(base_url+specialization_list_api, headers=headers)
        specialization_response=json.loads(specialization_request.text)
        print("specialization",specialization_request.status_code)
        specializations=specialization_response['data']
        print(specializations)
        #category list api call
        category_req=requests.post(base_url+category_api,headers=headers)
        print("category api:",category_req.status_code)
        category_resp=json.loads(category_req.text)
        print(category_resp)
        categories=category_resp['data']
        
        # new appointment creation with follow up api
        if request.method == 'POST':
            print("post")
            paid_appointment=request.form['form_type']
            session['paid_appointment']=paid_appointment
            # customer_id=request.form['customer_id']
            category_id=request.form['category_id']
            specialization=request.form['specialization']
            session['new_appointment_specialization']=specialization
            appointment_date=request.form['date']
            appointment_time=request.form['time']
            doctor_gender=request.form['doc_gender']
            language=request.form['language']
            # senior_doctor_id=request.form['doctor']
            # remarks=request.form['remarks']
            for category in categories:
                print("categories")
                if int(category_id) == category['id']:
                    print(category_id,category['id'])
                    category_title=category['title']
                    print(category_title)
                    session['category_title']=category_title

            payload={
                "new_user":0,
                "user_id":user_id,
                "appointment_date":appointment_date,
                "appointment_time":appointment_time,
                "followup_id":"",
                "category_id":category_id,
                "type_booking":"regular",
                "gender_pref":doctor_gender,
                "language_pref":language,
                # "doctor_id":senior_doctor_id,
                "doctor_flag":0,
                "remarks":"",
                "appointment_status":12
            }
            session['new_data']=payload
            print(payload)
            
            # api_data=json.dumps(payload)
            # print(api_data)
            # new_appointment_request=requests.post(base_url+follow_up_api, data=api_data, headers=headers)
            # new_appointment_response=json.loads(new_appointment_request.text)
            # print(new_appointment_request.status_code)
            # print(new_appointment_response)
            return redirect(url_for('new_appointment_preview'))
        return render_template("new_appointment.html",customers=customers,doctors=doctors,languages=languages,
        specializations=specializations,categories=categories)
    except Exception as e:
        print(e)
    return render_template("new_appointment.html")

@app.route("/primary_concern", methods=['GET','POST'])
def select_category():
    print("category")
    try:
        if 'user_id' in session:
            user_id = session['user_id']
        else:
            return redirect(url_for('login_phone'))
        if 'paid_appointment' in session:
            session.pop('paid_appointment',None)
        headers = {
                "Content-Type":"application/json"
            }
        # category api call
        category_req=requests.post(base_url+category_api,headers=headers)
        print("category api:",category_req.status_code)
        category_resp=json.loads(category_req.text)
        print(category_resp)
        
        categories=category_resp['data']
        if request.method == 'POST':
            paid_appointment=request.form['form_type']
            session['paid_appointment']=paid_appointment
            category_id = request.form['category']
            session_type = request.form['session_type']
            print(category_id, session_type)
            if 'category_title' in session:
                session.pop('category_title',None)
            for category in categories:
                print("categories")
                if int(category_id) == category['id']:
                    print(category_id,category['id'])
                    category_title=category['title']
                    print(category_title)
                    session['category_title']=category_title

            # category_title = request.form['category_title']
            print("category",category_id, category_title)
            session['category_id']=category_id
            session['session_type']=session_type
            return redirect(url_for('select_spec',c=category_id, pc=category_title))
        return render_template("select_category.html",categories=categories)
    except Exception as e:
        print(e)
        return render_template("select_category.html",categories=categories)

@app.route("/select_specialist", methods=['GET','POST'])
def select_spec():
    category_id=request.args.get('c')
    category_title=request.args.get('pc')

    # session.pop('loc_id',None)

    headers = {
            "Content-Type":"application/json"
        }
    print('session:',session)
    if 'country' in session:
        country = session['country']
        country_req = requests.post(base_url+get_location_api,headers=headers, data = json.dumps({'location':session['country']}))
        print('country')
        country_resp = json.loads(country_req.text)
        location_id = country_resp['location_id']
    else:
        location_id = 2

    session['loc_id']=location_id

    # plans list api call
    # data ={
    #     "location_id":str(location_id),
    #     "session_type":session['session_type']
    # }
    # api_data=json.dumps(data)
    # print(api_data)
    # plans_req=requests.get(base_url+plans_api,data=api_data, headers=headers)
    # plans_resp=json.loads(plans_req.text)
    # print("Plans API Status Code:", plans_req.status_code)
    # plans=plans_resp['data']

    #specializations list api call
    specialization_request=requests.get(base_url+specialization_list_api, headers=headers)
    specialization_response=json.loads(specialization_request.text)
    print("specialization",specialization_request.status_code)
    specializations=specialization_response['data']
    print(specializations)
    
    if request.method == 'POST':
     
        # specialization
        specialization = request.form['specialization']
        print("specialization",specialization)
        
        return redirect(url_for('select_gender_lang',c=category_id,pc=category_title,s=specialization))
    return render_template("select_spec.html",plans=specializations)

@app.route("/select_gender_lang", methods=['GET','POST'])
def select_gender_lang():
    specialist=request.args.get('s')
    # category_id=request.args.get('c')
    # category_title=request.args.get('pc')
    if 'category_id' in session:
        category_id = session['category_id']
    if 'category_title' in session:
        category_title = session['category_title']
    print(specialist)
    headers = {
            "Content-Type":"application/json"
        }
    # language api call
    language_api_request=requests.get(base_url+language_api,headers=headers)
    print("language",language_api_request.status_code)
    language_api_response=json.loads(language_api_request.text)
    languages=language_api_response['data']
    if request.method == 'POST':
        gender=request.form['doc_gender']
        language=request.form['language']
        print(gender, language)
        # date=request.form['date']
        return redirect(url_for('select_time',c=category_id,pc=category_title,s=specialist,g=gender,l=language,))
    # return render_template("new_app_date_gender.html")
    return render_template("select_doc_gender.html",languages=languages)

from datetime import datetime, timedelta

@app.route("/select_time", methods=['GET','POST'])
def select_time():
    print('select timeeeeee')
    specialist = request.args.get('s')
    gender = request.args.get('g')
    language = request.args.get('l')
    # date = request.args.get('d')
    category_id=request.args.get('c')
    category_title=request.args.get('pc')
    print('2237 ',session)

    if 'user_id' in session:
        user_id=session['user_id']
        print(user_id)

    if 'new_appointment_specialization' in session:
        session.pop('new_appointment_specialization',None)
        session['new_appointment_specialization']=specialist
        print("spec",session['new_appointment_specialization'])
    else:
        session['new_appointment_specialization']=specialist
        print("new_appointment_specialization",specialist)

    if 'category_title' in session:
        session.pop('category_title',None)
        session['category_title']=category_title
        print("category",session['category_title'])
    else:
        session['category_title']=category_title
        print("category",session['category_title'])

    if 'country' in session:
        location=session['country']
    else:
        return redirect(url_for('login_phone'))

    headers = {
            "Content-Type":"application/json"
        }
    # data={
    #     "specialization":"psychologist",
    #     "language":"english",
    #     "gender":"male",
    #     "doctor":"senior",
    #     "appointment_date":"2023-02-15"
    # }

    # Senior Timeslot
    data={
        "specialization":specialist,
        "language_pref":language,
        "gender":gender,
        "doctor_flag":"senior",
        "appointment_id":"",
        "location":location
        # "appointment_date":date
    }
    api_data=json.dumps(data)
    print(api_data)
    # senior doctor Time Slot api call
    senior_time=requests.post(base_url+snr_doc_time_api,data=api_data,headers=headers)
    print("senior time slot",senior_time.status_code)
    time_response=json.loads(senior_time.text)
    print("Senior time slots :",time_response['no_timeslots'])
    duration =  time_response['Message'].split(' ')[-2]

    if time_response['response_code'] == 200:
        timeslots=time_response['slots']
        if request.method == 'POST':
            print('post')
            print(request.form)
            selected_time = request.form.get('time')
            selected_date = request.form.get('selected_date')
            
            print('Selected Time:', selected_time)
            print('Selected Date:', selected_date)
            payload={
                "new_user":0,
                "user_id":user_id,
                "appointment_date":selected_date,
                "appointment_time":selected_time,
                "followup_id":"",
                "category_id":category_id,
                "type_booking":"regular",
                "gender_pref":gender,
                "language_pref":language,
                # "doctor_id":senior_doctor_id,
                "doctor_flag":0,
                "remarks":"",
                "appointment_status":12,
                "specialization": specialist,
                "session_type":session['session_type']
            }
            if 'new_data' in session:
                session.pop('new_data',None)
                session['new_data']=payload
                print("payload",session['new_data'])
            else:
                session['new_data']=payload
                print("payload",session['new_data'])
            return redirect(url_for('new_appointment_preview',invoice_id=0))
        print('******************#####################*****************')
        print(timeslots)
        print(time_response['Message'])
        print( time_response['Message'].split(' ')[-2])
        print( time_response['no_timeslots'])

        return render_template("select_time.html",timeslots=timeslots, time_response=time_response,dr_response = time_response['no_timeslots'])
    elif time_response['response_code'] == 400:
        time_slots= None
    else:
        flash("Something went wrong.. Try again","error")
    
    return render_template("select_time.html")

@app.route("/new_appointment_preview/<int:invoice_id>",methods=['GET','POST'])
def new_appointment_preview(invoice_id):
    print("new appointment preview")
    print(invoice_id)
    print(session)
    headers={
        "Content-Type":"application/json"
        }
    escalated_one_res = None
    if invoice_id != 0:
        session['appointment_id'] = invoice_id
        try:
            escalated_one = requests.post(base_url+get_escalated,data=json.dumps({'appointment_id':invoice_id}),headers=headers)
            print("escalated_one api:",escalated_one.status_code)
            escalated_one_res=json.loads(escalated_one.text)
            print(escalated_one_res)
            new_data = {
                'appointment_date': escalated_one_res['data']['appointment_date'],
                'appointment_status': escalated_one_res['data']['appointment_status'],
                'appointment_time' : escalated_one_res['data'].get('time_slot') or escalated_one_res['data'].get('escalated_time_slot'),
                'category_id': escalated_one_res['data']['category_id'],
                'doctor_flag':2,
                'followup_id':'',
                'gender_pref': escalated_one_res['data']['gender_pref'],
                'language_pref': escalated_one_res['data']['language_pref'],
                'new_user':0,
                'remarks':'',
                'specialization': escalated_one_res['data']['specialization'],
                'type_booking':'regular',
                'user_id': escalated_one_res['data']['user_id'],
                'session_type':escalated_one_res['data']['session_type']
            }
            session['new_data'] = new_data
            session['loc_id'] = escalated_one_res['data']['loc_id']
            session['paid_appointment'] = 'escalated_payment'
        except Exception as e:
            print(e)
    #category list api call
    category_req=requests.post(base_url+category_api,headers=headers)
    print("category api:",category_req.status_code)
    category_resp=json.loads(category_req.text)
    print(category_resp)
    categories=category_resp['data']

    for category in categories:
        if (escalated_one_res is not None):
            if category['id'] == escalated_one_res['data']['category_id']:
                session['category_title'] = category['title']

    if 'category_title' in session:
        category_title = session['category_title']
        print(category_title)

    if 'new_appointment_specialization' in session:
            new_appointment_specialization=session['new_appointment_specialization']
            print(new_appointment_specialization)
    elif escalated_one_res:
        new_appointment_specialization=escalated_one_res['data']['specialization']
        print('ss')
    else:
        # flash("Something went wrong","error")
        return redirect(url_for('new_appointment'))
    if 'new_data' in session:
        new_data=session['new_data']
        print("new appointment")
        print("preview",new_data)
        user_id=new_data['user_id']
    payment = ''
    if 'loc_id' in session:
        location_id = session['loc_id']
        
        if request.method == 'POST':
            print("post")
            coupon = request.form['coupon']
        else:
            print("no coupon")
            coupon = ""
            #paymemts api call
            # payload={
            # "location_id":1
            # }  
        if invoice_id != 0:
            payload={
                    "user_id":user_id,
                    "appointment_id": invoice_id,
                    "specialization":new_appointment_specialization,
                    "coupon_code":"",
                    "location_id":str(location_id)
                }
        else:
            
            payload={
                    "user_id":user_id,
                    "appointment_id": '',
                    "specialization":new_appointment_specialization,
                    "coupon_code":"",
                    "location_id":str(location_id),
                    "session_type":session['session_type'],
                    "date":session['new_data']['appointment_date'],
                    "time":session['new_data']['appointment_time'],
                    "gender_pref": session['new_data']['gender_pref'],
                    "language_pref":session['new_data']['language_pref'],
                }
        api_data=json.dumps(payload)
        print('api_data',api_data)
        payments_request=requests.post(base_url+payments_api,data=api_data,headers=headers)
        
        payment_response=json.loads(payments_request.text)   
        print("payments apiiiiiiiiiiii",payments_request.status_code)
        print(payment_response)
        payment=payment_response['payment']
        print(payment)
        session_type=payment_response['session_type']
        new_data['senior_doctor'] = payment_response['doctor_id']
        new_data['doctor_user_id'] = payment_response['doctor_user_id']
        if 'session_type' in session and not session_type:
            new_data['session_type'] = session['session_type']
        new_data['duration'] = payment_response['duration']
        temp_data_id = payment_response['temp_data_id']
        print('temp_data_id: ',temp_data_id)
        session['appointment_flag'] = 'appointment'
        session['temp_data_id']= temp_data_id
        if 'customer_email' in session:
            new_data['email'] = session['customer_email']
        if 'customer_first_name' in session and 'customer_last_name' in session:
            new_data['name'] = session['customer_first_name']+' '+session['customer_last_name']
        if 'loc_id ' in session:
            new_data['loc_id'] = session['loc_id']

        print(session)

    return render_template('new_appointment_preview.html',new_data=new_data,categories=categories,payment=payment,appointment_flag='not_first_appointment')

@app.route("/discussion/<int:appointment_id>", methods=['GET','POST'])
def discussion(appointment_id):
    try:
        if 'user_id' in session:
            user_id=session['user_id']
            print(user_id)
        else:
            return redirect(url_for('login'))
        headers={
        "Content-Type":"application/json"
        }
        payload={
            "appointment_id":appointment_id
        }
        api_data=json.dumps(payload)
        discussion_list_request=requests.post(base_url+discussion_list_api, data=api_data, headers=headers)
        discussion_list_response=json.loads(discussion_list_request.text)
        print("discussion list", discussion_list_request.status_code)
        discussion_list=discussion_list_response['data']
        # print(discussion_list)
        limit = discussion_list_response['discussion_count']
        print(limit)
        # create discussion api call
        if request.method == 'POST':
            if limit != 3:
                discuss_text=request.form['discuss_text']
                create_payload={
                        "appointment_id":appointment_id,
                        "content":discuss_text,
                        "is_query":1,
                        "is_reply":0,
                        "doctor_id":""
                    }
                create_api_data=json.dumps(create_payload)
                print("create discussion payload",create_api_data)
                create_discussion_request=requests.post(base_url+create_discussion_api, data=create_api_data, headers=headers)
                create_discussion_response=json.loads(create_discussion_request.text)
                print("create discussion", create_discussion_request.status_code)
                print(create_discussion_request.text)
                return redirect(url_for('discussion',appointment_id=appointment_id))
            else :
                flash("You have reached discussion limit","info")
        return render_template("discussion.html",discussion_list=discussion_list)
    except Exception as e:
        print(e)
    return render_template("discussion.html")

@app.route("/change_password/<string:encrypted_user_id>",methods=['GET','POST'])
def change_password(encrypted_user_id):
    headers={
        "Content-Type":"application/json"
        }
    if request.method == 'POST':
        new_password=request.form['new_password']
        payload={
                "user_id":encrypted_user_id,
                "password": new_password
            }
        api_data=json.dumps(payload)
        print(api_data)
        change_password_submit = requests.post(base_url+change_password_api, data=api_data, headers=headers)
        print("change password",change_password_submit.status_code)
        change_password_resp=json.loads(change_password_submit.text)
        print(change_password_resp)
        flash("Password changed","success")
        return redirect(url_for('login'))
    return render_template("change_password.html")

@app.route("/forgot_password",methods=['GET','POST'])
def forgot_password():
    headers={
        "Content-Type":"application/json"
        }
    if request.method == 'POST':
        email=request.form['email']
        payload={
            "email":email
        }
        api_data = json.dumps(payload)
        print(api_data)
        forgot_password_request=requests.post(base_url+forgot_password_api, data=api_data, headers=headers)
        forgot_password_response=json.loads(forgot_password_request.text)
        print("forgot password",forgot_password_request.status_code)
        print(forgot_password_response)
        return render_template("forgot_password_success.html")
    return render_template("forgot_password.html")

@app.route("/add_rating/<string:encrypted_appointment_id>", methods=['GET','POST'])
def add_rating(encrypted_appointment_id):
    headers={
        "Content-Type":"application/json"
        }
    payload={
        "encrypted_appointment_id":encrypted_appointment_id,
        "user_id":"",
        "file_flag":"",
        
    }
    api_data=json.dumps(payload)
    print(api_data)
    appointment_detail=requests.post(base_url+appointment_detail_api, data=api_data, headers=headers)
    appointment_detail_response=json.loads(appointment_detail.text)
    appointment_details=appointment_detail_response['data']
    print("detail api :",appointment_detail.status_code)
    user_id=appointment_details['user_id']
    senior_doctor_id=appointment_details['senior_doctor']
    print(user_id)
    # calling add ratings api
    if request.method == 'POST':

        app_rating=request.form['rate']
        customer_rating=request.form['customer_rate']
        rating_comments=request.form['comments']

        rating_payload={
            "encrypted_appointment_id": encrypted_appointment_id,
            "doctor_id":senior_doctor_id,
            "user_id": user_id,
            "rating_comments": rating_comments,
            "rating": customer_rating,
            "app_rating": app_rating,
            "added_by": "customer"
        }
        rating_data=json.dumps(rating_payload)
        print(rating_data)
        rating_submit=requests.post(base_url+add_rating_api,data=rating_data,headers=headers)
        submit_response=json.loads(rating_submit.text)
        print("add rating", rating_submit.status_code)
        print(submit_response)
        # flash("Thank you for rating" , "success")
        return render_template("thank_you.html")

    return render_template("add_rating.html",appointment_details=appointment_details)

last_execution_times = {}
import json, requests, time
RATE_LIMIT_PERIOD = 10

def is_rate_limited(user_id):

    current_time = time.time()
    
    if user_id in last_execution_times:
        last_time = last_execution_times[user_id]
        if current_time - last_time < RATE_LIMIT_PERIOD:
            return True
    
    # Update the last execution time
    last_execution_times[user_id] = current_time
    return False

@app.route("/payment_success")
def payment_success():

    if is_rate_limited(session['user_id']):
        return render_template("payment_success_new.html")

    try:
        print("appointment creation")
        print(session)
        try:
            payment_gateway = request.args.get('payment_gateway')
        except:
            payment_gateway = ""
        headers={
        "Content-Type":"application/json"
        }
        if 'paid_appointment' in session:
            paid_appointment=session['paid_appointment']
            print(paid_appointment)
        else:
            return redirect(url_for('orders_list'))
        if paid_appointment == 'new_appointment':
            print('new_appointment')
            if 'new_data' in session:
                new_data=session['new_data']
                print("preview",new_data)
                user_id=new_data['user_id']
                new_data['payment_gateway'] = payment_gateway
                print("post")
                new_data['followup'] = False
                api_data=json.dumps(new_data)
                print('api_data',api_data)
                new_appointment_request=requests.post(base_url+follow_up_api, data=api_data, headers=headers)
                's'
                new_appointment_response=json.loads(new_appointment_request.text)
                print(new_appointment_request.status_code)
                print(new_appointment_response)
                new_appointment_id=new_appointment_response["appointment_id"]
                print("new id:",new_appointment_id)
                session.pop('paid_appointment',None)
                session.pop('new_data',None)
                session.pop('temp_data_id',None)
                session.pop('category_title',None)
                session.pop('new_appointment_specialization',None)
                flash("New appointment created","success")
                return redirect(url_for('appointment_finished'))   

        elif paid_appointment == 'followup_appointment':
            print("follow up appointment")
            if 'follow_up_data' in session:
                follow_up_data=session['follow_up_data']
                print("preview",follow_up_data)
                print("post")
                follow_up_data['payment_gateway'] = payment_gateway
                api_data=json.dumps(follow_up_data)
                follow_up_submit=requests.post(base_url+follow_up_api, data=api_data, headers=headers)
                follow_up_response=json.loads(follow_up_submit.text)
                print("follow up",follow_up_submit.status_code)
                print(follow_up_response)
                new_appointment_id=follow_up_response["followup_appointment_id"]
                print("new id:",new_appointment_id)
                session.pop('paid_appointment',None)
                session.pop('follow_up_data',None)
                session.pop('temp_data_id',None)
                session.pop('category_title',None)
                session.pop('category_id',None)
                flash("Follow up appointment created","success")
                return redirect(url_for('appointment_finished'))   

        elif paid_appointment == 'unpaid_invoice':
            print('unpaid invoice')
            if 'invoice_data' in session:
                invoice_data=session['invoice_data']
                print("preview",invoice_data)
                session.pop('paid_appointment',None)
                session.pop('invoice_data',None)
                session.pop('temp_data_id',None)
                session.pop('category_title',None)
                flash("Payment complete","success")
                return redirect(url_for('appointment_finished'))   

        elif paid_appointment == 'escalated_payment':
            if 'new_data' in session:
                session['new_data']['type_booking'] = 'referred'
                new_data=session['new_data']

                print("preview",new_data)
                user_id=new_data['user_id']
                new_data['appointment_id'] = session['appointment_id']
                print("post")
                new_data['payment_gateway'] = payment_gateway
                api_data=json.dumps(new_data)
                new_appointment_request=requests.post(base_url+follow_up_api, data=api_data, headers=headers)
                's'
                new_appointment_response=json.loads(new_appointment_request.text)
                print(new_appointment_request.status_code)
                print(new_appointment_response)
                new_appointment_id=new_appointment_response["appointment_id"]
                print("new id:",new_appointment_id)
                session.pop('paid_appointment',None)
                session.pop('new_data',None)
                session.pop('temp_data_id',None)
                session.pop('category_title',None)
                session.pop('new_appointment_specialization',None)
                flash("New appointment created","success")
                return redirect(url_for('appointment_finished'))   
      
            print('2611',session)
        return redirect(url_for('appointment_finished'))         
    except Exception as e:
        print(e)
    return redirect(url_for('appointment_finished'))   
 
@app.route('/appointment_finished')
def appointment_finished():
    return render_template("payment_success_new.html")        

@app.route("/payment_failure")
def payment_failed():
    session.pop('paid_appointment',None)
    session.pop('follow_up_data',None)
    session.pop('new_data',None)
    session.pop('temp_data_id',None)
    flash("Something went wrong","error")
    return render_template("payment_failed.html")

@app.route("/consultation_disclaimer/<string:meeting_link>")
def consultation_disclaimer(meeting_link):
    print("meeting link:", meeting_link)
    return render_template("consultation_disclaimer.html",meeting_link=meeting_link)

@app.route('/invalid')
def show_error():
    if session['err'] is not None:
        err=session['err']
    return render_template('show_error.html',err=err)
# if __name__ == '__main__':
#     app.run(debug = True)

if __name__ == '__main__':
    app.run(port=8002,debug = True)