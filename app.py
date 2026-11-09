import sqlite3,hashlib,datetime,turso_serverless,libsql
from flask import Flask,render_template,request,redirect,url_for

user_token=""
username="?"

# def convertToBinary(filename):
#     with open(filename,'rb') as file:
#         blobData=file.read()
#         file.close()
#         return blobData

# def hash(password):
#     return str(hashlib.sha256(password.encode()))

app=Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/user/<username>")
def user(username):
    username=username
    
    conn=sqlite3.connect('database12.db')
    cur=conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS tickets(ID INTEGER PRIMARY KEY AUTOINCREMENT, code INTEGER, username TEXT, receiver TEXT, title TEXT, message TEXT, file BLOB, date TEXT, time TEXT, info TEXT, status TEXT, a1 TEXT, a2 TEXT, a3 TEXT, a4 TEXT, a5 TEXT, a6 TEXT, a7 TEXT, a8 TEXT, a9 TEXT, a10 TEXT)")
    conn.commit()
    
    cur.execute(f"SELECT * FROM tickets")
    all_tickets=cur.fetchall()

    cur.execute(f"SELECT * FROM tickets WHERE username='{username}'")
    user_tickets=cur.fetchall()

    cur.execute(f"SELECT * FROM tickets WHERE receiver='{username}'")
    expert_tickets=cur.fetchall()

    cur.execute(f"SELECT * FROM tickets WHERE username='{username}' AND status='open'")
    open_tickets=cur.fetchall()
    open_tickets=list(open_tickets)
    
    cur.execute(f"SELECT * FROM tickets WHERE username='{username}' AND status='close'")
    close_tickets=cur.fetchall()
    close_tickets=list(close_tickets)

    cur.execute(f"SELECT * FROM tickets WHERE receiver='{username}' AND status='open'")
    expert_open_tickets=cur.fetchall()
    expert_open_tickets=list(expert_open_tickets)
    

    cur.execute(f"SELECT * FROM tickets WHERE receiver='{username}' AND status='close'")
    expert_close_tickets=cur.fetchall()
    expert_close_tickets=list(expert_close_tickets)
    
    cur.execute(f"SELECT * FROM all_users WHERE role='expert'")
    expert_list=cur.fetchall()
    expert_list=list(expert_list)

    cur.execute("CREATE TABLE IF NOT EXISTS all_users(ID INTEGER PRIMARY KEY AUTOINCREMENT, namefamily TEXT, username TEXT UNIQUE, password TEXT, status TEXT, access TEXT, token TEXT, tel TEXT, email TEXT, role TEXT, a1 TEXT, a2 TEXT, a3 TEXT, a4 TEXT, a5 TEXT, a6 TEXT, a7 TEXT, a8 TEXT, a9 TEXT, a10 TEXT)")
    conn.commit()
    cur.execute(f"SELECT * FROM all_users WHERE username='{username}'")
    user_info=cur.fetchone()
    user_info=list(user_info)
    if user_info[4]!='login':
        return f"First log in please. status={user_info[4]} , user={user_info[2]}"
    user_namefamily=user_info[1]
    user_info[3]="?"
    # user_namefamily=user_info[1]
    user_role=user_info[9]

    conn.close()
    
    # return [user_info]
    if user_role=='user':
        return render_template("user.html",user_namefamily=user_namefamily,user_role=user_role, user_info=user_info, user_tickets=user_tickets, close_tickets=close_tickets, open_tickets=open_tickets)
    
    elif user_role=='admin':
        return render_template("admin.html",user_namefamily=user_namefamily,user_role=user_role, user_info=user_info, user_tickets=all_tickets, close_tickets=close_tickets, open_tickets=open_tickets, expert_close_tickets=expert_close_tickets, expert_open_tickets=expert_open_tickets,expert_list=expert_list)        
    elif user_role=='expert':
        return render_template("expert.html",user_namefamily=user_namefamily,user_role=user_role, user_info=user_info, user_tickets=expert_tickets, expert_close_tickets=expert_close_tickets, expert_open_tickets=expert_open_tickets)       

@app.route("/login_check", methods=['POST'])
def login_check():
    if request.method=='POST':
        username=request.form.get('pusername')
        password=request.form.get('ppass')

        conn=sqlite3.connect('database12.db')
        cur=conn.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS all_users(ID INTEGER PRIMARY KEY AUTOINCREMENT, namefamily TEXT, username TEXT UNIQUE, password TEXT, status TEXT, access TEXT, token TEXT,tel TEXT, email TEXT, role TEXT, a1 TEXT, a2 TEXT, a3 TEXT, a4 TEXT, a5 TEXT, a6 TEXT, a7 TEXT, a8 TEXT, a9 TEXT, a10 TEXT)")
        conn.commit()
        cur.execute(f"SELECT * FROM all_users WHERE username='{username}'")
        user_info=cur.fetchone()
        role=user_info[9]

        if user_info[3]==hashlib.sha256(password.encode()).hexdigest():
            # return "password is OK"
            user_token="mytoken"
            cur.execute(f"UPDATE all_users SET status='login' WHERE username='{username}'")
            conn.commit()
            conn.close()
            # return render_template(f"user/{username}",username=username)
            return redirect(url_for('user', username=username))
            # return "ok"
            # if user_info[9]=='user':
            #     return render_template(f"user/{username}",username=username)
            # elif user_info[9]=='expert':
            #     return render_template(f"expert/{username}",username=username)
            # elif user_info[9]=='admin':
            #     return render_template(f"admin/{username}",username=username)
        else:
            return f"<h2>Password is incorrect!</h2><br>1->{hashlib.sha256(password.encode()).hexdigest()}<br>2->{user_info[3]}"


@app.route("/signup_check", methods=['POST'])
def signup_check():
    if request.method=='POST':
        try:
            name=request.form.get('pname')
            tel=request.form.get('ptel')
            email=request.form.get('pemail')
            username=request.form.get('pusername')
            role=request.form.get('prole')
            password=request.form.get('ppass')
            password2=request.form.get('ppass2')
            # role="user"
            status='logout'

            if password2!=password:
                return "passwords should be the same"
            password=hashlib.sha256(password.encode()).hexdigest()
            conn=sqlite3.connect('database12.db')
            cur=conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS all_users(ID INTEGER PRIMARY KEY AUTOINCREMENT, namefamily TEXT, username TEXT UNIQUE, password TEXT, status TEXT, access TEXT, token TEXT,tel TEXT, email TEXT, role TEXT, a1 TEXT, a2 TEXT, a3 TEXT, a4 TEXT, a5 TEXT, a6 TEXT, a7 TEXT, a8 TEXT, a9 TEXT, a10 TEXT)")
            conn.commit()
            cur.execute("INSERT INTO all_users(namefamily, username, password,tel, email, role, status) VALUES (?,?,?,?,?,?,?)",(name,username,password,tel,email,role,status))
            conn.commit()
            cur.execute("SELECT * FROM all_users")
            allrows=cur.fetchall()
            return f"<h2>{allrows}</h2>"
        except Exception as e:
                    conn.rollback()
                    return "DB ERROR:", e
        finally:
            conn.close()


@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/user/<username>/add_ticket", methods=['POST'])
def add_ticket(username):
    username=username
    # username='1'
    if request.method=='POST':
        try:
            title=request.form.get('ptitle')
            receiver=request.form.get('preceiver')
            message="متن تیکت: "+request.form.get('pmessage')
            # info=username+": "+request.form.get('pinfo')
            # file=convertToBinary(request.form.get('pfile'))
            receiver_username="?"


            file_obj = request.files.get('pfile')
            file = file_obj.read() if file_obj else None
            
            file_name=file_obj.filename if file_obj else ''

            now=datetime.datetime.today()
            date=str(now.month)+"/"+str(now.day)+"/"+str(now.year)
            time=str(now.hour)+":"+str(now.minute)+":"+str(now.second)
            info=""
            status="open"
            
            conn=sqlite3.connect('database12.db')
            
            cur=conn.cursor()
            cur.execute(f"SELECT username FROM all_users WHERE namefamily='{receiver}'")
            receiver_username=cur.fetchone()[0]
            

            cur.execute("CREATE TABLE IF NOT EXISTS tickets(ID INTEGER PRIMARY KEY AUTOINCREMENT, code INTEGER, username TEXT, receiver TEXT, title TEXT, message TEXT, file BLOB, date TEXT, time TEXT, info TEXT, status TEXT, a1 TEXT, a2 TEXT, a3 TEXT, a4 TEXT, a5 TEXT, a6 TEXT, a7 TEXT, a8 TEXT, a9 TEXT, a10 TEXT)")
            
            # conn.commit()
            #   سورت کردن  بر اساس کد تیکت و یافتن آخرین کدتیکت و اضافه کردن یک عدد به آن بعنوان کد تیکت جدید
            # code=کد تیکت جدید
            cur.execute("SELECT code FROM tickets ORDER BY code DESC")
           
            thelast=cur.fetchone()
            try:
                code=int(thelast[0])+1
            except:
                code=1001
            
            cur.execute("INSERT INTO tickets(code, username, receiver, title, message, file, date, time, info, status) VALUES (?,?,?,?,?,?,?,?,?,?)",(code,username,receiver_username,title,message,file,date,time,info,status))
            conn.commit()
            
            cur.execute("SELECT * FROM tickets")
            allrows=cur.fetchall()
        except Exception as e:
            conn.rollback()
            return "DB ERROR:", e
        finally:
            conn.close()
        return f"<h2>A new ticket is added.<br>All Table recorde:<br></h2>{allrows}<br>{date}<br>{time}"


@app.route("/user/<username>/add_expert", methods=['POST'])
def add_expert(username):
    username=username
    # username='1'
    if request.method=='POST':
        try:
            name=request.form.get('pname')
            user=request.form.get('puser')
            password=request.form.get('ppass')
            tel=request.form.get('ptel')
            email=request.form.get('pemail')
            status=request.form.get('pstatus')
            role=request.form.get('prole')

            now=datetime.datetime.today()
            date=str(now.month)+"/"+str(now.day)+"/"+str(now.year)
            time=str(now.hour)+":"+str(now.minute)+":"+str(now.second)

            # status="فعال"
            
            conn=sqlite3.connect('database12.db')
            cur=conn.cursor()

            cur.execute("CREATE TABLE IF NOT EXISTS all_users(ID INTEGER PRIMARY KEY AUTOINCREMENT, namefamily TEXT, username TEXT UNIQUE, password TEXT, status TEXT, access TEXT, token TEXT, tel TEXT, email TEXT, role TEXT, a1 TEXT, a2 TEXT, a3 TEXT, a4 TEXT, a5 TEXT, a6 TEXT, a7 TEXT, a8 TEXT, a9 TEXT, a10 TEXT)")
            conn.commit()

            cur.execute(f"SELECT username FROM all_users WHERE username='{user}'")
            theuser=cur.fetchone()
            
            if (theuser):
                return '<h2>نام کاربری تکراری است</h2>'

            cur.execute(f"SELECT role FROM all_users WHERE username='{username}'")
            theuser=cur.fetchone()
            if theuser[0]=='admin':
                cur.execute("INSERT INTO all_users(namefamily, username, password,tel, email, role, status) VALUES (?,?,?,?,?,?,?)",(name,user,password,tel,email,role,status))
                conn.commit()
            else:
                return "You're not admin and not allowed to add user"

        finally:
            conn.close()
        return f"<h2>A new user is added.<br><br>{date}<br>{time}"


@app.route("/user/<username>/<expert_username>/edit_expert_page")
def edit_expert_page(username,expert_username):
    username=username
    expert_username=expert_username
    try:
        conn=sqlite3.connect('database12.db')
        cur=conn.cursor()
        cur.execute(f"SELECT * FROM all_users WHERE username='{username}' AND status='login'")
        users=cur.fetchone()
        if (users):
            cur.execute(f"SELECT namefamily, username, tel, email, status, role FROM all_users WHERE username='{expert_username}'")
            expertinfo=cur.fetchone()

            conn.close()
            return render_template("edit_expert.html",username=username,expert_username=expert_username,expertinfo=expertinfo)
        else:
            return "First login please"
    finally:
        conn.close()

@app.route("/user/<username>/edit_expert", methods=['POST'])
def edit_expert(username):
    username=username
    # username='1'
    if request.method=='POST':
        try:
            name=request.form.get('pname')
            user=request.form.get('puser')
            password=request.form.get('ppass')
            tel=request.form.get('ptel')
            email=request.form.get('pemail')
            status=request.form.get('pstatus')
            role=request.form.get('prole')

            now=datetime.datetime.today()
            date=str(now.month)+"/"+str(now.day)+"/"+str(now.year)
            time=str(now.hour)+":"+str(now.minute)+":"+str(now.second)
            
            conn=sqlite3.connect('database12.db')
            cur=conn.cursor()

            cur.execute("CREATE TABLE IF NOT EXISTS all_users(ID INTEGER PRIMARY KEY AUTOINCREMENT, namefamily TEXT, username TEXT UNIQUE, password TEXT, status TEXT, access TEXT, token TEXT, tel TEXT, email TEXT, role TEXT, a1 TEXT, a2 TEXT, a3 TEXT, a4 TEXT, a5 TEXT, a6 TEXT, a7 TEXT, a8 TEXT, a9 TEXT, a10 TEXT)")
            conn.commit()

            # cur.execute(f"SELECT username FROM all_users WHERE username='{user}'")
            # theuser=cur.fetchone()
            
            # if (theuser):
            #     return '<h2>نام کاربری تکراری است</h2>'
            
            cur.execute(f"SELECT password FROM all_users WHERE username='{user}'")
            thepass=cur.fetchone()
            
            if len(password)>0:
                password=hashlib.sha256(password.encode()).hexdigest()
            else:
                password=thepass[0]
            
            cur.execute(f"SELECT role FROM all_users WHERE username='{username}'")
            theuser=cur.fetchone()
            
            if theuser[0]=='admin':
                cur.execute(f"UPDATE all_users SET namefamily='{name}', password='{password}', tel='{tel}', email='{email}', status='{status}', role='{role}' WHERE username='{user}'")
                conn.commit()
                
            else:
                return "You're not admin and not allowed to edit user"

        finally:
            conn.close()
        return f"<h2>The user was edited.<br><br>{date}<br>{time}"


@app.route("/user/<username>/delete_expert/<expertusername>")
def delete_expert(username,expertusername):
    username=username
    expertusername=expertusername
    # username='1'
    try:
        conn=sqlite3.connect('database12.db')
        cur=conn.cursor()
        cur.execute(f"SELECT role FROM all_users WHERE username='{username}'")
        theuser=cur.fetchone()
                
        if theuser[0]=='admin':
            # cur.execute(f"DELETE FROM all_users WHERE username='{expertusername}'")
            # conn.commit()
            cur.execute(f"UPDATE tickets SET receiver='{username}' WHERE receiver='{expertusername}'")
            conn.commit()

        else:
            return "You're not admin and not allowed to delete user"    

    finally:
        conn.close()
        return f"<h2>The user was deleted."


@app.route("/user/<username>/edit_user", methods=['POST'])
def edit_user(username):
    username=username
    # username='1'
    if request.method=='POST':
        try:
            name=request.form.get('pname')
            user=request.form.get('puser')
            password=request.form.get('ppass')
            tel=request.form.get('ptel')
            email=request.form.get('pemail')
            now=datetime.datetime.today()
            date=str(now.month)+"/"+str(now.day)+"/"+str(now.year)
            time=str(now.hour)+":"+str(now.minute)+":"+str(now.second)
            
            if username!=user:
                return "خطای امنیتی!"

            conn=sqlite3.connect('database12.db')
            cur=conn.cursor()

            cur.execute("CREATE TABLE IF NOT EXISTS all_users(ID INTEGER PRIMARY KEY AUTOINCREMENT, namefamily TEXT, username TEXT UNIQUE, password TEXT, status TEXT, access TEXT, token TEXT, tel TEXT, email TEXT, role TEXT, a1 TEXT, a2 TEXT, a3 TEXT, a4 TEXT, a5 TEXT, a6 TEXT, a7 TEXT, a8 TEXT, a9 TEXT, a10 TEXT)")
            conn.commit()
            
            cur.execute(f"SELECT password FROM all_users WHERE username='{user}'")
            thepass=cur.fetchone()
            
            if len(password)>0:
                password=hashlib.sha256(password.encode()).hexdigest()
            else:
                password=thepass[0]
        
            cur.execute(f"UPDATE all_users SET namefamily='{name}', password='{password}', tel='{tel}', email='{email}' WHERE username='{user}'")
            conn.commit()
        finally:
            conn.close()
        return f"<h2>This user was edited.<br><br>{date}<br>{time}"


@app.route("/user/<username>/create_ticket")
def create_ticket(username):
    username=username
    try:
        conn=sqlite3.connect('database12.db')
        cur=conn.cursor()

        cur.execute(f"SELECT namefamily FROM all_users WHERE role='expert'")
        experts_name=cur.fetchall()

        cur.execute(f"SELECT * FROM all_users WHERE username='{username}' AND status='login'")
        users=cur.fetchone()
        if (users):
            conn.close()
            return render_template("create_ticket.html",username=username,experts_name=experts_name)
        else:
            return "First login please"
    finally:
        conn.close()


@app.route("/user/<username>/add_expert")
def create_expert(username):
    username=username
    try:
        conn=sqlite3.connect('database12.db')
        cur=conn.cursor()
        cur.execute(f"SELECT role FROM all_users WHERE username='{username}'")
        user_role=cur.fetchone()
        if user_role[0]=='admin':
            conn.close()
            return render_template("create_expert.html",username=username)
        else:
            return "Your're not allowed to add expert. you're not admin!"
    finally:
        conn.close()


@app.route("/user/<username>/tickets/<ticketID>")
def show_ticket(username,ticketID):
    username=username
    ticketID=ticketID
    conn=sqlite3.connect('database12.db')
    cur=conn.cursor()

    cur.execute(f"SELECT * FROM all_users WHERE username='{username}'")
    the_user=cur.fetchone()
    user_role=the_user[9]

    if user_role=='expert':

        cur.execute(f"SELECT * FROM tickets WHERE receiver='{username}'")
        user_tickets=cur.fetchall()
        # user_tickets=list(user_tickets)

        
        cur.execute(f"SELECT * FROM tickets WHERE receiver='{username}' AND status='open'")
        open_tickets=cur.fetchall()
        open_tickets=list(open_tickets)
        
        cur.execute(f"SELECT * FROM tickets WHERE receiver='{username}' AND status='close'")
        close_tickets=cur.fetchall()
        close_tickets=list(close_tickets)
    

        cur.execute(f"SELECT * FROM tickets WHERE receiver='{username}' AND ID='{ticketID}'")
        ticket=cur.fetchone()
        if ticket:
            ticket=list(ticket)
            if len(ticket)>0:
                code=int(ticket[1])
        else:
            return redirect(url_for('user', username=username))

        cur.execute(f"SELECT file FROM tickets WHERE code='{code}'")
        data = cur.fetchall()
        
        cur.execute(f"SELECT receiver FROM tickets WHERE code='{code}'")
        receiver_username=cur.fetchone()
        cur.execute(f"SELECT namefamily FROM all_users WHERE username='{receiver_username[0]}'")
        receiver_namefamily=cur.fetchone()[0]
        # data=list(data)
        
        for d in data[0]:
            if d is None:
                data=[]
        # return str(len(data))
        # if (data):
        #     with open(f'file', 'wb') as file:
        #         file.write(data)
        

        cur.execute(f"SELECT message,info,file,date,time FROM tickets WHERE receiver='{username}' AND code='{code}'")
        ticketmsg=cur.fetchall()
        ticketmsg=list(ticketmsg)

        cur.execute("CREATE TABLE IF NOT EXISTS all_users(ID INTEGER PRIMARY KEY AUTOINCREMENT, namefamily TEXT, username TEXT UNIQUE, password TEXT, status TEXT, access TEXT, token TEXT, tel TEXT, email TEXT, role TEXT, a1 TEXT, a2 TEXT, a3 TEXT, a4 TEXT, a5 TEXT, a6 TEXT, a7 TEXT, a8 TEXT, a9 TEXT, a10 TEXT)")
        conn.commit()

        cur.execute(f"SELECT namefamily,username FROM all_users  WHERE role IN ('expert', 'admin') AND username !='{username}'")
        expert_list=cur.fetchall()
        print(expert_list)

        cur.execute(f"SELECT * FROM all_users WHERE username='{username}'")
        user_info=cur.fetchone()
        user_info=list(user_info)
        if user_info[4]!='login':
            return f"First log in please. status={user_info[4]} , user={user_info[2]}"
        user_namefamily=user_info[1]
        user_info[3]="?"
        # user_namefamily=user_info[1]
        # user_role=user_info[9]

        conn.close()
        return render_template("showticket_expert.html",user_namefamily=user_namefamily,user_role=user_role, user_info=user_info, user_tickets=user_tickets, close_tickets=close_tickets, open_tickets=open_tickets,ticketID=ticketID,ticket=ticket,ticketmsg=ticketmsg,username=username,code=code,data=data,receiver_namefamily=receiver_namefamily,expert_list=expert_list)
    
    
    elif user_role=='admin':
        cur.execute(f"SELECT * FROM tickets")
        user_tickets=cur.fetchall()
        # user_tickets=list(user_tickets)

        
        cur.execute(f"SELECT * FROM tickets WHERE username='{username}' AND status='open'")
        open_tickets=cur.fetchall()
        open_tickets=list(open_tickets)
        
        cur.execute(f"SELECT * FROM tickets WHERE username='{username}' AND status='close'")
        close_tickets=cur.fetchall()
        close_tickets=list(close_tickets)
        
        cur.execute(f"SELECT * FROM tickets WHERE receiver='{username}' AND status='open'")
        expert_open_tickets=cur.fetchall()
        expert_open_tickets=list(expert_open_tickets)
        

        cur.execute(f"SELECT * FROM tickets WHERE receiver='{username}' AND status='close'")
        expert_close_tickets=cur.fetchall()
        expert_close_tickets=list(expert_close_tickets)

        cur.execute(f"SELECT * FROM tickets WHERE ID='{ticketID}'")
        ticket=cur.fetchone()
        ticket=list(ticket)
        if len(ticket)>0:
            code=int(ticket[1])
        cur.execute(f"SELECT file FROM tickets WHERE code='{code}'")
        data = cur.fetchall()
        
        cur.execute(f"SELECT receiver FROM tickets WHERE code='{code}'")
        receiver_username=cur.fetchone()
        cur.execute(f"SELECT namefamily FROM all_users WHERE username='{receiver_username[0]}'")
        receiver_namefamily=cur.fetchone()[0]
        # data=list(data)
        
        for d in data[0]:
            if d is None:
                data=[]
        # return str(len(data))
        # if (data):
        #     with open(f'file', 'wb') as file:
        #         file.write(data)
        

        cur.execute(f"SELECT message,info,file,date,time FROM tickets WHERE code='{code}'")
        ticketmsg=cur.fetchall()
        ticketmsg=list(ticketmsg)
        # return ticketmsg

        cur.execute("CREATE TABLE IF NOT EXISTS all_users(ID INTEGER PRIMARY KEY AUTOINCREMENT, namefamily TEXT, username TEXT UNIQUE, password TEXT, status TEXT, access TEXT, token TEXT, tel TEXT, email TEXT, role TEXT, a1 TEXT, a2 TEXT, a3 TEXT, a4 TEXT, a5 TEXT, a6 TEXT, a7 TEXT, a8 TEXT, a9 TEXT, a10 TEXT)")
        conn.commit()

        cur.execute(f"SELECT * FROM all_users WHERE role='expert'")
        expert_list=cur.fetchall()
        expert_list=list(expert_list)

        cur.execute(f"SELECT * FROM all_users WHERE username='{username}'")
        user_info=cur.fetchone()
        user_info=list(user_info)
        if user_info[4]!='login':
            return f"First log in please. status={user_info[4]} , user={user_info[2]}"
        user_namefamily=user_info[1]
        user_info[3]="?"
        # user_namefamily=user_info[1]
        # user_role=user_info[9]

        conn.close()
        return render_template("showticket_admin.html",user_namefamily=user_namefamily,user_role=user_role, user_info=user_info, user_tickets=user_tickets, close_tickets=close_tickets, open_tickets=open_tickets,ticketID=ticketID,ticket=ticket,ticketmsg=ticketmsg,username=username,code=code,data=data,expert_list=expert_list,expert_close_tickets=expert_close_tickets,expert_open_tickets=expert_open_tickets,receiver_namefamily=receiver_namefamily)    
        
    elif user_role=='user':
        cur.execute(f"SELECT * FROM tickets WHERE username='{username}'")
        user_tickets=cur.fetchall()
        # user_tickets=list(user_tickets)
        
        cur.execute(f"SELECT * FROM tickets WHERE status='open'")
        open_tickets=cur.fetchall()
        open_tickets=list(open_tickets)
        
        cur.execute(f"SELECT * FROM tickets WHERE status='close'")
        close_tickets=cur.fetchall()
        close_tickets=list(close_tickets)
        
        cur.execute(f"SELECT * FROM tickets WHERE ID='{ticketID}'")
        ticket=cur.fetchone()
        ticket=list(ticket)
        if len(ticket)>0:
            code=int(ticket[1])
        cur.execute(f"SELECT file FROM tickets WHERE code='{code}'")
        data = cur.fetchall()
        
        cur.execute(f"SELECT receiver FROM tickets WHERE code='{code}'")
        receiver_username=cur.fetchone()
        cur.execute(f"SELECT namefamily FROM all_users WHERE username='{receiver_username[0]}'")
        receiver_namefamily=cur.fetchone()[0]
        
        for d in data[0]:
            if d is None:
                data=[]
        

        cur.execute(f"SELECT message,info,file,date,time FROM tickets WHERE code='{code}'")
        ticketmsg=cur.fetchall()
        ticketmsg=list(ticketmsg)

        cur.execute("CREATE TABLE IF NOT EXISTS all_users(ID INTEGER PRIMARY KEY AUTOINCREMENT, namefamily TEXT, username TEXT UNIQUE, password TEXT, status TEXT, access TEXT, token TEXT, tel TEXT, email TEXT, role TEXT, a1 TEXT, a2 TEXT, a3 TEXT, a4 TEXT, a5 TEXT, a6 TEXT, a7 TEXT, a8 TEXT, a9 TEXT, a10 TEXT)")
        conn.commit()

        cur.execute(f"SELECT * FROM all_users WHERE username='{username}'")
        user_info=cur.fetchone()
        user_info=list(user_info)
        if user_info[4]!='login':
            return f"First log in please. status={user_info[4]} , user={user_info[2]}"
        user_namefamily=user_info[1]
        user_info[3]="?"
        # user_namefamily=user_info[1]
        # user_role=user_info[9]

        conn.close()
        return render_template("showticket_user.html",user_namefamily=user_namefamily,user_role=user_role, user_info=user_info, user_tickets=user_tickets, close_tickets=close_tickets, open_tickets=open_tickets,ticketID=ticketID,ticket=ticket,ticketmsg=ticketmsg,username=username,code=code,data=data,receiver_namefamily=receiver_namefamily)
        




@app.route("/logout_all")
def logout_all():
    try:
        conn=sqlite3.connect('database12.db')
        cur=conn.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS all_users(ID INTEGER PRIMARY KEY AUTOINCREMENT, namefamily TEXT, username TEXT UNIQUE, password TEXT, status TEXT, access TEXT, token TEXT,tel TEXT, email TEXT, role TEXT, a1 TEXT, a2 TEXT, a3 TEXT, a4 TEXT, a5 TEXT, a6 TEXT, a7 TEXT, a8 TEXT, a9 TEXT, a10 TEXT)")
        conn.commit()
        cur.execute(f"UPDATE all_users SET status='logout' WHERE username='{username}'")
        conn.commit()
    finally:
        conn.close()
    return "loged out sucsessfully."

@app.route("/user/<username>/logout")
def logout(username):
    username=username
    try:
        conn=sqlite3.connect('database12.db')
        cur=conn.cursor()
        cur.execute(f"UPDATE all_users SET status='logout' WHERE username='{username}'")
        conn.commit()
    finally:
        conn.close()
        return render_template("login.html")


@app.route("/user/<username>/edit_account")
def edit_account(username):
    username=username
    try:
        conn=sqlite3.connect('database12.db')
        cur=conn.cursor()
        cur.execute(f"SELECT namefamily,username,tel,email,status,role FROM all_users WHERE username='{username}'")
        edit_info=cur.fetchone()
        conn.commit()
    finally:
        conn.close()
        return render_template("edit_account.html", edit_info=edit_info, username=username)

@app.route("/showdb_allusers")
def showdbusers():
    try:
        conn=sqlite3.connect('database12.db')
        cur=conn.cursor()
        cur.execute("SELECT * FROM all_users")
        alldballusers=cur.fetchall()
    finally:
        conn.close()
        return alldballusers

@app.route("/user/<username>/tickets/<code>/close_ticket")
def close_ticket(username,code):
    username=username
    code=int(code)
    try:
        conn=sqlite3.connect('database12.db')
        cur=conn.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS tickets(ID INTEGER PRIMARY KEY AUTOINCREMENT, code INTEGER, username TEXT, receiver TEXT, title TEXT, message TEXT, file BLOB, date TEXT, time TEXT, info TEXT, status TEXT, a1 TEXT, a2 TEXT, a3 TEXT, a4 TEXT, a5 TEXT, a6 TEXT, a7 TEXT, a8 TEXT, a9 TEXT, a10 TEXT)")
        cur.execute(f"UPDATE tickets SET status='close' WHERE code='{code}'")
        conn.commit()
        
    finally:
        conn.close()
        # return 'The ticket was successfully closed.'
        return redirect(url_for('user', username=username))

@app.route("/user/<username>/response_ticket", methods=['POST'])
def response_ticket(username):
    username=username
    # username='1'
    if request.method=='POST':
        try:
            
            code=request.form.get('pcode')
            namefamily=request.form.get('pname')
            receiver=request.form.get('preceiver')
            title=request.form.get('ptitle')
            role=request.form.get('prole')
            info=request.form.get('pinfo')
            if len(info)>0:
                info=f"{username} ({role}): "+request.form.get('pinfo')
            message=namefamily+"("+role+") : "+request.form.get('pmessage')
            
            file_obj = request.files.get('pfile')
            file = file_obj.read() if file_obj else None
            
            now=datetime.datetime.today()
            date=str(now.month)+"/"+str(now.day)+"/"+str(now.year)
            time=str(now.hour)+":"+str(now.minute)+":"+str(now.second)
            # info=""
            status="response"

            conn2=sqlite3.connect('database12.db')
            
            cur=conn2.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS tickets(ID INTEGER PRIMARY KEY AUTOINCREMENT, code INTEGER, username TEXT, receiver TEXT, title TEXT, message TEXT, file BLOB, date TEXT, time TEXT, info TEXT, status TEXT, a1 TEXT, a2 TEXT, a3 TEXT, a4 TEXT, a5 TEXT, a6 TEXT, a7 TEXT, a8 TEXT, a9 TEXT, a10 TEXT)")
            
            cur.execute("INSERT INTO tickets(code, username, receiver, title, message, file, date, time, info, status) VALUES (?,?,?,?,?,?,?,?,?,?)",(code,username,receiver,title,message,file,date,time,info,status))
            conn2.commit()
            
            cur.execute("SELECT * FROM tickets")
            allrows=cur.fetchall()
        except Exception as e:
            conn2.rollback()
            return "DB ERROR:", e
        finally:
            conn2.close()
            return f"<h2>A response for the ticket is added.<br>All Table recorde:<br></h2>{allrows}<br>{date}<br>{time}"


@app.route("/user/<username>/erja_ticket", methods=['POST'])
def erja_ticket(username):
    username=username
    # username='1'
    if request.method=='POST':
        try:
        
            code=request.form.get('pcode')
            new_receiver=request.form.get('pnew_receiver')
            print(new_receiver)
            
            now=datetime.datetime.today()
            date=str(now.month)+"/"+str(now.day)+"/"+str(now.year)
            time=str(now.hour)+":"+str(now.minute)+":"+str(now.second)
            # info=""
            # status="response"

            conn2=sqlite3.connect('database12.db')

            cur=conn2.cursor()
            
            cur.execute(f"UPDATE tickets SET receiver='{new_receiver}' WHERE code='{code}'")
            conn2.commit()
            
            
        except Exception as e:
            conn2.rollback()
            return "DB ERROR:", e
        finally:
            conn2.close()
            return f"<h2>ارجاع صورت گرفت</h2><br>{date}<br>{time}"



@app.route("/user/<username>/tickets/<code>/download_data/<int:file_number>")
def download_data(username,code,file_number):
    username=username
    code=code
    file_number=file_number
    try:
        conn=sqlite3.connect('database12.db')
        cur=conn.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS tickets(ID INTEGER PRIMARY KEY AUTOINCREMENT, code INTEGER, username TEXT, receiver TEXT, title TEXT, message TEXT, file BLOB, date TEXT, time TEXT, info TEXT, status TEXT, a1 TEXT, a2 TEXT, a3 TEXT, a4 TEXT, a5 TEXT, a6 TEXT, a7 TEXT, a8 TEXT, a9 TEXT, a10 TEXT)")
        conn.commit()

        cur.execute(f"SELECT file FROM tickets WHERE code={code}")
        datas = cur.fetchall()
        n=0
        # datas=list(datas)
        for data in datas:
            if data[0] is None:
                continue
            n=n+1
            if file_number==n:
                print(type(data))
                with open(f'file{n}.jpg', 'wb') as file:
                    file.write(data[0])
                    # return "The file was Downloaded"
    finally:
        conn.close()
        return str(n)

if (__name__=="__main__"):
    app.run(debug=True)
