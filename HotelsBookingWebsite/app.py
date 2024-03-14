from pymongo import MongoClient
from bson.objectid import ObjectId
from secrets import token_urlsafe
from passlib.hash import pbkdf2_sha256
from datetime import datetime,date,timedelta
from  flask import (
    Flask,
    session,
    render_template,
    request,
    abort,
    flash,
    redirect,
    url_for,
)

def create_app():
    app = Flask(__name__, template_folder ="Templates",static_folder="static" )
    app.secret_key  ="ZQfCf2u2Hd1HTWnL0GUGqyCo7rlgbtOngdh9DffUMQM"
    client = MongoClient("mongodb+srv://hisham3214:Hisho76403405@351project.khomprh.mongodb.net/test")
    app.db = client.HotelBookings
    users={}
    

    @app.get("/")
    def home():
        return render_template ("home.html") 
    
    @app.route("/history", methods=["GET","POST"])
    def history():
        name=session["username"]
        dic=app.db.users.find_one({'username' : name})
        prr=dic["PRR"]
        crr=dic["CRR"]
        listprr=[] 
        listcrr=[]
        for i in prr.keys():#list of dictionaries of all rooms ever booked
            room=app.db.Rooms.find_one({'_id' : ObjectId(prr[i])})
            room["dat"]=i#date when room was booked
            listprr.append(room)
        print("This is the list of dics of prev booked rooms listprr")
        print(listprr)
        for i in crr.keys():#list of dictionaries of rooms currently booked
            room=app.db.Rooms.find_one({'_id' : ObjectId(crr[i])})
            room["dat"]=i
            listcrr.append(room) 
        print("This is listcrr")
        print(listcrr)
        if request.method == "POST":
            datecanceled = request.form['cancel_reservation']
            print("This is cancelled date"+datecanceled)
            roomID=prr[datecanceled]
            print("This is the room Id"+roomID)
            del prr[datecanceled]
            print("This is the del prr")
            print(prr)
            del crr[datecanceled]
            print(name)
            
            app.db.users.update_one(
                {"username" : name},                                             #search
                {'$set' : {'CRR' : crr}}                     #update
            )
            app.db.users.update_one(
                {"username" : name},                                             #search
                {'$set' : {"PRR" : prr}}                     #update
            )
            roomm=app.db.Rooms.find_one({'_id' : ObjectId(roomID)})
            newdate=roomm['date']
            newdate[datecanceled] = "False"
            app.db.Rooms.update_one(
                {'_id' : ObjectId(roomID)},
                {'$set' : {'date':newdate}}
            )
   

        return render_template("history.html",pbr=listprr,cbr=listcrr)
    
    @app.route("/invoice")
    def invoice():
        return render_template("invoice.html")

    @app.route("/room")
    def room():
        return render_template("room.html")

    @app.route("/book", methods=["GET","POST"])
    def book():
        if request.method == "POST":
            if request.form['submit_button'] == "findbtn":
                fromm = request.form.get("from")
                to = request.form.get("to")
                numberofpeople = request.form.get("numberofbeds")
                
                error_room_unavailable = "This room is not available on the selected date"
                error_invalid_input = "Please enter a valid date and number of people"
                dt1 = datetime.strptime(fromm,"%Y-%m-%d")
                session["dt1"]=dt1
                dt2 = datetime.strptime(to, "%Y-%m-%d")
                session["dt2"]=dt2
                cd= (date.today()).strftime("%Y-%m-%d")
                dtc=datetime.strptime(cd,"%Y-%m-%d")
                dater=[]
                
                #function to give all dates in a range----------------------
                #dater.clear()
                def daterange(date1, date2):
                    for n in range(int ((date2 - date1).days)+1):
                        yield date1 + timedelta(n)

                for dt in daterange(dt1, dt2):
                    dater.append((dt.strftime("%Y-%m-%d")))
                numofdays=len(dater)
                session["numofdays"]=numofdays
                #------------------------------------------------------------
                def filterrr(L,nbOfPpl):
                    findD={}
                    for date in L:
                        findD["date."+date]="False"
                    findD["sleeps"]=nbOfPpl
                    return findD
                Filter=filterrr(dater,numberofpeople)#things to search for from func
                #print(Filter)

                
                if(dt2>dt1) and (dt1>dtc) and int(numberofpeople)>0:#check input
                    rooms = app.db.Rooms.find(Filter)#search for rooms with these dates available and put in list of dics
                    roomz=[]
                    for room in rooms:
                        roomz.append(room)
                    
                    session["dates"]=dater
                    return render_template("RoomSearch.html",rooms=roomz)#send list to RoomSearch page and redirect there

                else:
                    return render_template("RoomSearch.html", error_invalid_input=error_invalid_input)
            else:
                if not session.get("username"):
                    render_template("login.html")
                else:
                    room_id = request.form['submit_button'] #for every room id
                    print("This is the room ID")
                    print(room_id)
                    room_dic={}#room dictionary
                    ListOfDates=session['dates']#list containing dates to be reserved
                    print("This is the list of dates")
                    print(ListOfDates)
                    room_dic=app.db.Rooms.find_one({'_id' : ObjectId(room_id)})
                    roomtyype=room_dic["roomtype"]
                    roompricee=room_dic["price"]
                    print(room_dic)
                    dic=room_dic["date"]#dictionary of dates of the room
                    for i in ListOfDates:#setting dates in dic to true to indicate that they are reserved 
                        dic[i]="true"
                    print("This is the updated dates")
                    print(dic)
                    app.db.Rooms.update_one(
                        {'_id' : ObjectId(room_id)},                           #search
                        {'$set' : {'date' : dic}}                    #update
                    )
                    un=session["username"]#get username from session info
                    print("This is username")
                    print(un)
                    userdic=app.db.users.find_one({'username' : un})#get user data
                    fullname=userdic["name"]
                    print("This is the userdic")
                    print(userdic)
                    y=userdic["CRR"]#CRR OF USER
                    x=userdic["PRR"]##PRR of user
                    print("This is x the PRR of the user")
                    print(x)
                    prc=room_dic["price"]
                    for i in ListOfDates:#updating PRR in x
                        x[i]= room_id
                    for i in ListOfDates:
                        y[i]= room_id
                    print("This is the updated x")
                    print(x)
                    app.db.users.update_one(
                        {'username' : un},                        #search for user in db
                        {'$set' : {'CRR' : y}}
                    )
                    app.db.users.update_one(
                        {'username' : un},                        #search for user in db
                        {'$set' : {'PRR' : x}}                    #updatin PRR in users db

                    )
                    today_date=datetime.now()
                    
                    total=session["numofdays"]*(int(roompricee))
                   
                    #reserve these dates
                    #render_template("sl.html")
                    return render_template("invoice.html",date_today=today_date,username=un,fullname=fullname,Room_type=roomtyype,roomprice=roompricee,date_from=session["dt1"],date_to=session["dt2"],total=total)
                    #should do something here

            
            
        return render_template("book.html")
    
    @app.route("/RoomSearch", methods=["GET","POST"])
    def RoomSearch(rooms):
        
        if request.method == "POST":#If book is PRESSED
            if not session.get("username"):
                render_template("login.html")
            else:
                room_id = request.form['submit_button'] #for every room id
                print("This is the room ID")
                print(room_id)
                room_dic={}#room dictionary
                ListOfDates=session['dates']#list containing dates to be reserved
                print("This is the list of dates")
                print(ListOfDates)
                room_dic=app.db.Rooms.find_one({'_id' : ObjectId(room_id)})
                print(room_dic)
                dic=room_dic["date"]#dictionary of dates of the room
                for i in ListOfDates:#setting dates in dic to true to indicate that they are reserved 
                    dic[i]="true"
                print("This is the updated dates")
                print(dic)
                app.db.Rooms.update_one(
                    {'_id' : ObjectId(room_id)},                           #search
                    {'$set' : {'date' : dic}}                    #update
                )
                un=session["username"]#get username from session info
                print("This is username")
                print(un)
                userdic=app.db.users.find_one({'username' : un})#get user data
                print("This is the userdic")
                print(userdic)
                x=userdic["PRR"]##PRR of user
                print("This is x the PRR of the user")
                print(x)
                prc=room_dic["price"]
                for i in ListOfDates:#updating PRR in x
                    x[i]={"room_id":room_id,"price":prc}
                print("This is the updated x")
                print(x)

                app.db.users.update_one(
                    {'username' : un},                        #search for user in db
                    {'$set' : {'PRR' : x}}                    #updatin PRR in users db

                )
                print("Booked")

                    #reserve these dates
                flash("succefuly booked")
                message="succefuly booked"
                    
        return render_template("RoomSearch.html",username=session.get("username"),message=message)


    #@app.get("/protected_home")
    #def protected_home():
    #    if not session.get("username"):
    #        abort(401)
    #   return render_template ("protected_home.html")

    @app.route("/login", methods=["GET","POST"])
    def login():
        if request.method == "POST":
             
            userName = request.form.get("UserName")
            password = request.form.get("password")
            error_statment = "Incorrect Credentials"
            user = app.db.users.find_one({'username':userName})
            if user["username"] == userName:
                if pbkdf2_sha256.verify(password, user["password"]):
                    session["username"]=userName
                    userdic=app.db.users.find_one({'username' : userName})
                    """
                    y=userdic["CRR"]                                               
                    for date in y:
                        dte = datetime.strptime(date,"%Y-%m-%d")
                        cd= (date.today()).strftime("%Y-%m-%d")
                        dtc=datetime.strptime(cd,"%Y-%m-%d")
                        if dtc>dte:
                            del y[date]
                    app.db.users.update_one(
                        {'username' : userName},                      
                        {'$set' : {'CRR' : y}}
                    )
                    """
                    return redirect(url_for("book"))
            else:
                return render_template("login.html",error_statment = error_statment)

        return render_template("login.html")

    @app.route("/sign-up", methods=["GET","POST"])
    def signup():
        if request.method == "POST":
            FullName = request.form.get("FullName")
            UserName = request.form.get("UserName")
            Email = request.form.get("Email")
            PhoneNumber = request.form.get("PhoneNumber")
            Password = request.form.get("Password")
            PasswordConfirm = request.form.get("PasswordConfirm")
            
            error_statment_phone_number = "Please Enter Valid Lebanese Phone number"
            error_statment_password_mismatch = "Passwords do not match."
            error_statment_username_used = "This username is already taken!"
            error_statment_password_weak = "Please Enter a stronger password including at least: 1 lowercase charecter, 1 upper case, 1 number, and 1 special charecter. Should Be longer than 8 chars"

            def passcheck(password):
                l, u, p, d = 0, 0, 0, 0
                capitalalphabets="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                smallalphabets="abcdefghijklmnopqrstuvwxyz"
                specialchar="$@_#%!?/+=-*&;%^()`~{[}];:<>,."
                digits="0123456789"

                for i in password:

                    if (i in smallalphabets):   l+=1           
                    if (i in capitalalphabets): u+=1         
                    if (i in digits):   d+=1   
                    if(i in specialchar):   p+=1

                if ((l<1) or (u<1) or (d<1) or (p<1) or (len(password)<8)==True):   return False
                else:   return True
                
            if Password!=PasswordConfirm:
                return render_template("sign-up.html",
                    error_statment_password_mismatch=error_statment_password_mismatch,
                    FullName=FullName,
                    UserName=UserName,
                    Email=Email,
                    PhoneNumber=PhoneNumber,
                    Password=Password)

            elif not passcheck(Password):
                return render_template("sign-up.html",
                    error_statment_password_weak=error_statment_password_weak,
                    FullName=FullName,
                    UserName=UserName,
                    Email=Email,
                    PhoneNumber=PhoneNumber,
                    Password=Password)

            elif len(PhoneNumber)!=8:
                return render_template("sign-up.html",
                        error_statment_phone_number=error_statment_phone_number,
                        FullName=FullName,
                        UserName=UserName,
                        Email=Email,
                        Password=Password)
                        
            elif app.db.users.find_one({'username':UserName}):
                return render_template("sign-up.html",
                    error_statment_username_used=error_statment_username_used,
                    FullName=FullName,
                    PhoneNumber=PhoneNumber,
                    Email=Email,
                    Password=Password)

            else:
                users={
                    "name" : FullName,
                    "username": UserName,
                    "email": Email,
                    "phonenumber" : PhoneNumber,
                    #"password" : Password,
                    "password" : pbkdf2_sha256.hash(Password),#(Hashing the password for more security and when we want to authenticate user we hash the password they sent and compare it not the otherway around)
                    "CRR":{},#Currently reserved rooms saved as (room#:date) in dic
                    "PRR":{}#Past Reserved Rooms saved similary but if we reserved the same room already we just add this date to it
                    }
                app.db.users.insert_one(users)
               
                return redirect(url_for("login"))
        
                #session["Email"] = Email if we want to user to get signed in automatically creates cookie

        return render_template("sign-up.html")

    @app.route("/profile", methods=["GET","POST"])
    def profile():
        uname=session["username"]
        dic=app.db.users.find_one({'username' : uname})
        email = dic["email"]
        number=dic["phonenumber"]
        oldpass=dic["password"]
        message=""
        if request.method=="POST":
            if request.form['update'] == "creds":
                newMail=request.form.get("newmail")
                newNumber=request.form.get("newnumber")
                app.db.users.update_one(
	                {'username' : session["username"]},                      
	                {'$set' : {'phonenumber' : newNumber}}
                )
                app.db.users.update_one(
	                {'username' : session["username"]},                      
	                {'$set' : {'email' : newMail}}
                )
                flash("Information Succefuly Updated")
                message="Information Succefuly Updated"
            else:
                oldpassfromuser=request.form.get("oldpassword")
                newpassfromuser=pbkdf2_sha256.hash(request.form.get("newpassword"))
                if pbkdf2_sha256.verify(oldpassfromuser, oldpass):
                    app.db.users.update_one(
	                    {'username' : session["username"]},                      
	                    {'$set' : {'password' : newpassfromuser}}
                    )
                    flash ("You have succefuly chaged your password")
                    message="You have succefuly chaged your password"
                else:
                    flash("Old Password is not correct")
                    message="Old Password is not correct"

        return render_template("profile.html",uname=uname,number=number,email=email,message=message)

    
    return app

