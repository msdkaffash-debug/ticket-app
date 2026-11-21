import hashlib
import datetime
import turso_serverless

from database import get_db

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    abort,
    send_file
)

from functools import wraps
from io import BytesIO

app=Flask(__name__)
print("### NEW APP VERSION 2026-11-14 ###")
app.secret_key = "a34d@dk_-#s0jsu.Wb.!"

def check_user(func):
    @wraps(func)
    def wrapper(username, *args, **kwargs):

        if 'username' not in session:
            return redirect(url_for('login'))

        if username != session['username']:
            abort(403)

        return func(username, *args, **kwargs)

    return wrapper
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/user/<username>")
@check_user
def user(username):
    username=username
    error = request.args.get('error')
    try:
        conn=get_db()
        cur=conn.cursor()
        
        cur.execute("SELECT * FROM tickets")
        all_tickets=cur.fetchall()

        cur.execute("SELECT * FROM tickets WHERE username=?",(username,))
        user_tickets=cur.fetchall()

        cur.execute("SELECT * FROM tickets WHERE receiver=?",(username,))
        expert_tickets=cur.fetchall()

        cur.execute("SELECT * FROM tickets WHERE username=? AND status!=?",(username,'بسته شده'))
        open_tickets=cur.fetchall()
        open_tickets=list(open_tickets)
        
        cur.execute("SELECT * FROM tickets WHERE username=? AND status=?",(username,'بسته شده'))
        close_tickets=cur.fetchall()
        close_tickets=list(close_tickets)

        cur.execute("SELECT * FROM tickets WHERE receiver=? AND status!=?",(username,'بسته شده'))
        expert_open_tickets=cur.fetchall()
        expert_open_tickets=list(expert_open_tickets)
        

        cur.execute("SELECT * FROM tickets WHERE receiver=? AND status=?",(username,'بسته شده'))
        expert_close_tickets=cur.fetchall()
        expert_close_tickets=list(expert_close_tickets)
        
        cur.execute("SELECT * FROM all_users WHERE role=?",('expert',))
        expert_list=cur.fetchall()
        expert_list=list(expert_list)

        cur.execute("SELECT * FROM all_users WHERE username=?",(username,))
        user_info=cur.fetchone()
        user_info=list(user_info)
        if user_info[4]!='login':
            return render_template("login.html", error='لطفا ابتدا وارد حساب کاربری شوید')
        user_namefamily=user_info[1]
        user_info[3]="?"
        # user_namefamily=user_info[1]
        user_role=user_info[9]
    finally:
        conn.close()
    
    # return [user_info]
    if user_role=='user':
        return render_template("user.html",user_namefamily=user_namefamily,user_role=user_role, user_info=user_info, user_tickets=user_tickets, close_tickets=close_tickets, open_tickets=open_tickets,error=error)
    elif user_role=='admin':
        return render_template("admin.html",user_namefamily=user_namefamily,user_role=user_role, user_info=user_info, user_tickets=all_tickets, close_tickets=close_tickets, open_tickets=open_tickets, expert_close_tickets=expert_close_tickets, expert_open_tickets=expert_open_tickets,expert_list=expert_list,error=error)        
    elif user_role=='expert':
        return render_template("expert.html",user_namefamily=user_namefamily,user_role=user_role, user_info=user_info, user_tickets=expert_tickets, expert_close_tickets=expert_close_tickets, expert_open_tickets=expert_open_tickets,error=error)       

@app.route("/login_check", methods=['POST'])
def login_check():
    if request.method=='POST':
        username=request.form.get('pusername')
        password=request.form.get('ppass')

        conn=get_db()
        cur=conn.cursor()

        cur.execute("SELECT * FROM all_users WHERE username=?",(username,))
        user_info=cur.fetchone()
        if not user_info:
            return render_template("login.html", error="نام کاربری یا رمز عبور اشتباه است")
        role=user_info[9]

        if user_info[3]==hashlib.sha256(password.encode()).hexdigest():
            # return "password is OK"
            
            session.clear()
            session['username'] = username

            cur.execute("UPDATE all_users SET status=? WHERE username=?",('login',username))
            conn.commit()
            conn.close()
            return redirect(url_for('user', username=username))
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
            return render_template("login.html", error="نام کاربری یا رمز عبور اشتباه است")


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
                return render_template("signup.html", error="رمز عبور با تکرار رمز عبور مطابقت ندارد")
            password=hashlib.sha256(password.encode()).hexdigest()
            conn=get_db()
            cur=conn.cursor()
            
            cur.execute("INSERT INTO all_users(namefamily, username, password,tel, email, role, status) VALUES (?,?,?,?,?,?,?)",(name,username,password,tel,email,role,status))
            conn.commit()
            cur.execute("SELECT * FROM all_users")
            allrows=cur.fetchall()
            return render_template("login.html", error="ثبت نام با موفقیت انجام شد")
        except Exception as e:
                    conn.rollback()
                    return render_template("login.html", error=f"خطای پایگاه داده: {e}")
        finally:
            conn.close()


@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/user/<username>/add_ticket", methods=['POST'])
@check_user
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

            now=datetime.datetime.today() + datetime.timedelta(hours=3, minutes=30)
            date=str(now.month)+"/"+str(now.day)+"/"+str(now.year)
            time=str(now.hour)+":"+str(now.minute)+":"+str(now.second)
            info=""
            status="ارسال شده"
            
            conn=get_db()
            
            cur=conn.cursor()
            cur.execute("SELECT username FROM all_users WHERE namefamily=?",(receiver,))
            receiver_username=cur.fetchone()[0]
            

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
            return redirect(url_for('user', username=username, error='تیکت با موفقیت ارسال شد'))

            # cur.execute("SELECT * FROM tickets")
            # allrows=cur.fetchall()
        except Exception as e:
            conn.rollback()
            return render_template("login.html", error=f"خطای پایگاه داده: {e}")
        finally:
            conn.close()


@app.route("/user/<username>/add_expert", methods=['POST'])
@check_user
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

            now=datetime.datetime.today() + datetime.timedelta(hours=3, minutes=30)
            date=str(now.month)+"/"+str(now.day)+"/"+str(now.year)
            time=str(now.hour)+":"+str(now.minute)+":"+str(now.second)

            # status="فعال"
            
            conn=get_db()
            cur=conn.cursor()

            cur.execute("SELECT username FROM all_users WHERE username=?",(user,))
            theuser=cur.fetchone()
            
            if (theuser):
                return render_template("login.html", error='نام کاربری تکراری است')

            cur.execute("SELECT role FROM all_users WHERE username=?",(username,))
            theuser=cur.fetchone()
            if theuser[0]=='admin':
                cur.execute("INSERT INTO all_users(namefamily, username, password,tel, email, role, status) VALUES (?,?,?,?,?,?,?)",(name,user,password,tel,email,role,status))
                conn.commit()
                return redirect(url_for('user', username=username, error='یوزر (کارشناس) جدید با موفقیت ایجاد شد'))
            else:
                return render_template("create_expert.html", error='فقط مدیر کل مجاز به افزودن کارشناس است')

        finally:
            conn.close()
        # return render_template("create_expert.html", error='یوزر (کارشناس) جدید با موفقیت ایجاد شد')


@app.route("/user/<username>/<expert_username>/edit_expert_page")
@check_user
def edit_expert_page(username,expert_username):
    username=username
    expert_username=expert_username
    try:
        conn=get_db()
        cur=conn.cursor()
        cur.execute("SELECT * FROM all_users WHERE username=? AND status=?",(username,'login'))
        users=cur.fetchone()
        if (users):
            cur.execute("SELECT namefamily, username, tel, email, status, role FROM all_users WHERE username=?",(expert_username,))
            expertinfo=cur.fetchone()

            conn.close()
            return render_template("edit_expert.html",username=username,expert_username=expert_username,expertinfo=expertinfo)
        else:
            return render_template("login.html", error='لطفا ابتدا وارد حساب کاربری شوید')
    finally:
        conn.close()

@app.route("/user/<username>/edit_expert", methods=['POST'])
@check_user
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

            now=datetime.datetime.today() + datetime.timedelta(hours=3, minutes=30)
            date=str(now.month)+"/"+str(now.day)+"/"+str(now.year)
            time=str(now.hour)+":"+str(now.minute)+":"+str(now.second)
            
            conn=get_db()
            cur=conn.cursor()


            # cur.execute("SELECT username FROM all_users WHERE username='{user}'")
            # theuser=cur.fetchone()
            
            # if (theuser):
            #     return '<h2>نام کاربری تکراری است</h2>'
            
            cur.execute("SELECT password FROM all_users WHERE username=?",(user,))
            thepass=cur.fetchone()
            
            if len(password)>0:
                password=hashlib.sha256(password.encode()).hexdigest()
            else:
                password=thepass[0]
            
            cur.execute("SELECT role FROM all_users WHERE username=?",(username,))
            theuser=cur.fetchone()
            
            if theuser[0]=='admin':
                cur.execute("UPDATE all_users SET namefamily=?, password=?, tel=?, email=?, status=?, role=? WHERE username=?",(name,password,tel,email,status,role,user))
                conn.commit()
                return redirect(url_for('user', username=username, error='کاربر با موفقیت ویرایش شد'))
                
            else:
                return redirect(url_for('user', username=username, error='فقط مدیر کل مجاز به ویرایش کارشناس است'))

        finally:
            conn.close()


@app.route("/user/<username>/delete_expert/<expertusername>")
@check_user
def delete_expert(username,expertusername):
    username=username
    expertusername=expertusername
    # username='1'
    try:
        conn=get_db()
        cur=conn.cursor()
        cur.execute("SELECT role FROM all_users WHERE username=?",(username,))
        theuser=cur.fetchone()
                
        if theuser[0]=='admin':
            cur.execute("DELETE FROM all_users WHERE username=?",(expertusername,))
            conn.commit()
            # cur.execute("UPDATE tickets SET receiver='{username}' WHERE receiver='{expertusername}'")
            # conn.commit()
            return redirect(url_for('user', username=username, error='کاربر با موفقیت حذف شد'))

        else:
            return redirect(url_for('user', username=username, error='فقط مدیرکل مجاز به حذف کاربر می باشد'))   

    finally:
        conn.close()


@app.route("/user/<username>/edit_user", methods=['POST'])
@check_user
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
            now=datetime.datetime.today() + datetime.timedelta(hours=3, minutes=30)
            date=str(now.month)+"/"+str(now.day)+"/"+str(now.year)
            time=str(now.hour)+":"+str(now.minute)+":"+str(now.second)
            
            if username!=user:
                return "خطای امنیتی!"

            conn=get_db()
            cur=conn.cursor()

            
            cur.execute("SELECT password FROM all_users WHERE username=?",(user,))
            thepass=cur.fetchone()
            
            if len(password)>0:
                password=hashlib.sha256(password.encode()).hexdigest()
            else:
                password=thepass[0]
        
            cur.execute("UPDATE all_users SET namefamily=?, password=?, tel=?, email=? WHERE username=?",(name,password,tel,email,user))
            conn.commit()
            return redirect(url_for('user', username=username, error='کاربر با موفقیت ویرایش شد'))
        finally:
            conn.close()


@app.route("/user/<username>/create_ticket")
@check_user
def create_ticket(username):
    username=username
    try:
        conn=get_db()
        cur=conn.cursor()

        cur.execute("SELECT namefamily FROM all_users WHERE role=?",('expert',))
        experts_name=cur.fetchall()

        cur.execute("SELECT * FROM all_users WHERE username=? AND status=?",(username,'login'))
        users=cur.fetchone()
        if (users):
            conn.close()
            return render_template("create_ticket.html",username=username,experts_name=experts_name)
        else:
            return render_template("login.html", error='لطفا ابتدا وارد حساب کاربری شوید')
    finally:
        conn.close()


@app.route("/user/<username>/add_expert")
@check_user
def create_expert(username):
    username=username
    try:
        conn=get_db()
        cur=conn.cursor()
        cur.execute("SELECT role FROM all_users WHERE username=?",(username,))
        user_role=cur.fetchone()
        if user_role[0]=='admin':
            conn.close()
            return render_template("create_expert.html",username=username)
        else:
            return "Your're not allowed to add expert. you're not admin!"
    finally:
        conn.close()


@app.route("/user/<username>/tickets/<ticketID>")
@check_user
def show_ticket(username,ticketID):
    username=username
    ticketID=ticketID
    conn=get_db()
    cur=conn.cursor()

    cur.execute("SELECT * FROM all_users WHERE username=?",(username,))
    the_user=cur.fetchone()
    user_role=the_user[9]

    if user_role=='expert':
        cur.execute(f"SELECT * FROM tickets WHERE receiver=? AND ID=?",(username,ticketID))
        ticket=cur.fetchone()
        if not ticket:
            return redirect(url_for('user', username=username, error='دسترسی غیرمجاز!'))
            
        cur.execute("SELECT * FROM tickets WHERE receiver=?",(username,))
        user_tickets=cur.fetchall()
        # user_tickets=list(user_tickets)

        
        cur.execute("SELECT * FROM tickets WHERE receiver=? AND status!=?",(username,'بسته شده'))
        open_tickets=cur.fetchall()
        open_tickets=list(open_tickets)
        
        cur.execute("SELECT * FROM tickets WHERE receiver=? AND status=?",(username,'بسته شده'))
        close_tickets=cur.fetchall()
        close_tickets=list(close_tickets)
    

        cur.execute("SELECT * FROM tickets WHERE receiver=? AND ID=?",(username,ticketID))
        ticket=cur.fetchone()
        if ticket:
            ticket=list(ticket)
            if len(ticket)>0:
                code=int(ticket[1])
            cur.execute("UPDATE tickets SET status=? WHERE receiver=? AND ID=?",('در انتظار پاسخ',username,ticketID))
            conn.commit()
            cur.execute("SELECT * FROM tickets WHERE receiver=? AND ID=?",(username,ticketID))
            ticket=cur.fetchone()
        else:
            return redirect(url_for('user', username=username))

        cur.execute("SELECT file FROM tickets WHERE code=?",(code,))
        data = cur.fetchall()
        
        cur.execute("SELECT receiver FROM tickets WHERE code=?",(code,))
        receiver_username=cur.fetchone()
        cur.execute("SELECT namefamily FROM all_users WHERE username=?",(receiver_username[0],))
        receiver_namefamily=cur.fetchone()[0]
        # data=list(data)
        
        for d in data[0]:
            if d is None:
                data=[]
        # return str(len(data))
        # if (data):
        #     with open(f'file', 'wb') as file:
        #         file.write(data)
        

        cur.execute("SELECT message,info,file,date,time FROM tickets WHERE receiver=? AND code=?",(username,code))
        ticketmsg=cur.fetchall()
        ticketmsg=list(ticketmsg)


        cur.execute("SELECT namefamily,username FROM all_users  WHERE role IN (?,?) AND username !=?",('expert', 'admin',username))
        expert_list=cur.fetchall()
        
        cur.execute("SELECT * FROM all_users WHERE username=?",(username,))
        user_info=cur.fetchone()
        user_info=list(user_info)
        if user_info[4]!='login':
            return render_template("login.html", error='لطفا ابتدا وارد حساب کاربری شوید')
        user_namefamily=user_info[1]
        user_info[3]="?"
        # user_namefamily=user_info[1]
        # user_role=user_info[9]


        conn.close()
        return render_template("showticket_expert.html",user_namefamily=user_namefamily,user_role=user_role, user_info=user_info, user_tickets=user_tickets, close_tickets=close_tickets, open_tickets=open_tickets,ticketID=ticketID,ticket=ticket,ticketmsg=ticketmsg,username=username,code=code,data=data,receiver_namefamily=receiver_namefamily,expert_list=expert_list)

    
    elif user_role=='admin':
        cur.execute("SELECT * FROM tickets")
        user_tickets=cur.fetchall()
        # user_tickets=list(user_tickets)

        
        cur.execute("SELECT * FROM tickets WHERE username=? AND status!=?",(username,'بسته شده'))
        open_tickets=cur.fetchall()
        open_tickets=list(open_tickets)
        
        cur.execute("SELECT * FROM tickets WHERE username=? AND status=?",(username,'بسته شده'))
        close_tickets=cur.fetchall()
        close_tickets=list(close_tickets)
        
        cur.execute("SELECT * FROM tickets WHERE receiver=? AND status!=?",(username,'بسته شده'))
        expert_open_tickets=cur.fetchall()
        expert_open_tickets=list(expert_open_tickets)
        

        cur.execute("SELECT * FROM tickets WHERE receiver=? AND status=?",(username,'بسته شده'))
        expert_close_tickets=cur.fetchall()
        expert_close_tickets=list(expert_close_tickets)

        cur.execute("SELECT * FROM tickets WHERE ID=?",(ticketID,))
        ticket=cur.fetchone()
        ticket=list(ticket)
        if len(ticket)>0:
            code=int(ticket[1])
        cur.execute("SELECT file FROM tickets WHERE code=?",(code,))
        data = cur.fetchall()
        
        cur.execute("SELECT receiver FROM tickets WHERE code=?",(code,))
        receiver_username=cur.fetchone()
        cur.execute("SELECT namefamily FROM all_users WHERE username=?",(receiver_username[0],))
        receiver_namefamily=cur.fetchone()[0]
        # data=list(data)
        
        for d in data[0]:
            if d is None:
                data=[]
        # return str(len(data))
        # if (data):
        #     with open(f'file', 'wb') as file:
        #         file.write(data)
        

        cur.execute("SELECT message,info,file,date,time FROM tickets WHERE code=?",(code,))
        ticketmsg=cur.fetchall()
        ticketmsg=list(ticketmsg)
        # return ticketmsg


        cur.execute("SELECT * FROM all_users WHERE role=?",('expert',))
        expert_list=cur.fetchall()
        expert_list=list(expert_list)

        cur.execute("SELECT * FROM all_users WHERE username=?",(username,))
        user_info=cur.fetchone()
        user_info=list(user_info)
        if user_info[4]!='login':
            return render_template("login.html", error='لطفا ابتدا وارد حساب کاربری شوید')
        user_namefamily=user_info[1]
        user_info[3]="?"
        # user_namefamily=user_info[1]
        # user_role=user_info[9]

        conn.close()
        return render_template("showticket_admin.html",user_namefamily=user_namefamily,user_role=user_role, user_info=user_info, user_tickets=user_tickets, close_tickets=close_tickets, open_tickets=open_tickets,ticketID=ticketID,ticket=ticket,ticketmsg=ticketmsg,username=username,code=code,data=data,expert_list=expert_list,expert_close_tickets=expert_close_tickets,expert_open_tickets=expert_open_tickets,receiver_namefamily=receiver_namefamily)    
        
    elif user_role=='user':
        cur.execute(f"SELECT * FROM tickets WHERE username=? AND ID=?",(username,ticketID))
        ticket=cur.fetchone()
        if not ticket:
            return redirect(url_for('user', username=username, error='دسترسی غیرمجاز!'))
            
        cur.execute("SELECT * FROM tickets WHERE username=?",(username,))
        user_tickets=cur.fetchall()
        
        cur.execute("SELECT * FROM tickets WHERE username=? AND status!=?",(username,'بسته شده'))
        open_tickets=cur.fetchall()
        open_tickets=list(open_tickets)
        
        cur.execute("SELECT * FROM tickets WHERE username=? AND status=?",(username,'بسته شده'))
        close_tickets=cur.fetchall()
        close_tickets=list(close_tickets)
        # print(type(username))
        cur.execute("SELECT * FROM tickets WHERE ID=?",(ticketID,))
        ticket=cur.fetchone()
        ticket=list(ticket)
        if len(ticket)>0:
            code=int(ticket[1])
        cur.execute("SELECT file FROM tickets WHERE code=?",(code,))
        data = cur.fetchall()
        
        cur.execute("SELECT receiver FROM tickets WHERE code=?",(code,))
        receiver_username=cur.fetchone()
        cur.execute("SELECT namefamily FROM all_users WHERE username=?",(receiver_username[0],))
        receiver_namefamily=cur.fetchone()[0]
        
        for d in data[0]:
            if d is None:
                data=[]
        

        cur.execute("SELECT message,info,file,date,time FROM tickets WHERE code=?",(code,))
        ticketmsg=cur.fetchall()
        ticketmsg=list(ticketmsg)


        cur.execute("SELECT * FROM all_users WHERE username=?",(username,))
        user_info=cur.fetchone()
        user_info=list(user_info)
        if user_info[4]!='login':
            return render_template("login.html", error='لطفا ابتدا وارد حساب کاربری شوید')
        user_namefamily=user_info[1]
        user_info[3]="?"
        # user_namefamily=user_info[1]
        # user_role=user_info[9]

        conn.close()
        return render_template("showticket_user.html",user_namefamily=user_namefamily,user_role=user_role, user_info=user_info, user_tickets=user_tickets, close_tickets=close_tickets, open_tickets=open_tickets,ticketID=ticketID,ticket=ticket,ticketmsg=ticketmsg,username=username,code=code,data=data,receiver_namefamily=receiver_namefamily)
        




@app.route("/logout_all")
def logout_all():
    try:
        conn=get_db()
        cur=conn.cursor()

        cur.execute("UPDATE all_users SET status=?",('logout',))
        conn.commit()
        return render_template("login.html", error='با موفقیت از حساب کاربری خارج شدید')
    finally:
        conn.close()

@app.route("/user/<username>/logout")
@check_user
def logout(username):
    username=username
    try:
        conn=get_db()
        cur=conn.cursor()
        cur.execute("UPDATE all_users SET status=? WHERE username=?",('logout',username))
        conn.commit()
        return render_template("login.html", error='با موفقیت از حساب کاربری خارج شدید')
    finally:
        conn.close()


@app.route("/user/<username>/edit_account")
@check_user
def edit_account(username):
    username=username
    try:
        conn=get_db()
        cur=conn.cursor()
        cur.execute("SELECT namefamily,username,tel,email,status,role FROM all_users WHERE username=?",(username,))
        edit_info=cur.fetchone()
        conn.commit()
        return render_template("edit_account.html", edit_info=edit_info, username=username)
    finally:
        conn.close()

@app.route("/showdb_allusers")
def showdbusers():
    try:
        conn=get_db()
        cur=conn.cursor()
        cur.execute("SELECT * FROM all_users")
        alldballusers=cur.fetchall()
        return alldballusers
    finally:
        conn.close()

@app.route("/user/<username>/tickets/<code>/close_ticket")
@check_user
def close_ticket(username,code):
    username=username
    code=int(code)
    try:
        conn=get_db()
        cur=conn.cursor()

        cur.execute("UPDATE tickets SET status=? WHERE code=?",('بسته شده',code))
        conn.commit()
        return redirect(url_for('user', username=username, error='تیکت با موفقیت بسته شد'))
        
    finally:
        conn.close()
        # return 'The ticket was successfully closed.'

@app.route("/user/<username>/response_ticket", methods=['POST'])
@check_user
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
            
            now=datetime.datetime.today() + datetime.timedelta(hours=3, minutes=30)
            date=str(now.month)+"/"+str(now.day)+"/"+str(now.year)
            time=str(now.hour)+":"+str(now.minute)+":"+str(now.second)
            # info=""
            status="پاسخ داده شده"

            conn2=get_db()
            
            cur=conn2.cursor()
            cur.execute("INSERT INTO tickets(code, username, receiver, title, message, file, date, time, info, status) VALUES (?,?,?,?,?,?,?,?,?,?)",(code,username,receiver,title,message,file,date,time,info,status))
            conn2.commit()
            
            cur.execute("SELECT * FROM tickets")
            allrows=cur.fetchall()
            return redirect(url_for('user', username=username, error='پاسخ تیکت با موفقیت ارسال شد'))
        except Exception as e:
            conn2.rollback()
            return "DB ERROR:", e
        finally:
            conn2.close()
            # return f"<h2>A response for the ticket is added.<br>All Table recorde:<br></h2>{allrows}<br>{date}<br>{time}"


@app.route("/user/<username>/erja_ticket", methods=['POST'])
@check_user
def erja_ticket(username):
    username=username
    # username='1'
    if request.method=='POST':
        try:
        
            code=request.form.get('pcode')
            new_receiver=request.form.get('pnew_receiver')
            
            now=datetime.datetime.today() + datetime.timedelta(hours=3, minutes=30)
            date=str(now.month)+"/"+str(now.day)+"/"+str(now.year)
            time=str(now.hour)+":"+str(now.minute)+":"+str(now.second)
            # info=""
            # status="response"

            conn2=get_db()

            cur=conn2.cursor()
            
            cur.execute("UPDATE tickets SET receiver=? WHERE code=?",(new_receiver,code))
            conn2.commit()
            return redirect(url_for('user', username=username, error='ارجاع صورت گرفت'))
            
        except Exception as e:
            conn2.rollback()
            return "DB ERROR:", e
        finally:
            conn2.close()
            # return f"<h2>ارجاع صورت گرفت</h2><br>{date}<br>{time}"
            

@app.route("/user/<username>/tickets/<code>/download_data/<int:file_number>")
@check_user
def download_data(username, code, file_number):

    conn = None

    try:
        conn =get_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT file FROM tickets WHERE code = ? AND username = ?",
            (code, username)
        )

        datas = cur.fetchall()

        files = [data[0] for data in datas if data[0] is not None]

        if file_number < 1 or file_number > len(files):
            return "File not found", 404

        file_data = files[file_number - 1]

        return send_file(
            BytesIO(file_data),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=f'file{file_number}.jpg'
        )

    except Exception as e:
        app.logger.exception("Download error")
        return f"Download error: {str(e)}", 500

    finally:
        if conn:
            conn.close()    



if (__name__=="__main__"):
    app.run(debug=True)
