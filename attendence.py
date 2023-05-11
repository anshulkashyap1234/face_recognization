import sqlite3
from datetime import datetime
def create_database():
    try:
        con=sqlite3.connect(database="school.sqlite")
        cur=con.cursor()
        table1="create table attendence(name text ,date text,primary key(name,date))"
    
        
        cur.execute(table1)
        con.commit()
        con.close()  
        return ("Table created")
    except:
        return ("something went wrong in db,might be tabl(s) already exists")


def verify_user(name):
    try:
        # if email and password are null
        if(name==""):
             return None
        else:
            #fetch userinfo by using email and password
            con=sqlite3.connect(database="school.sqlite")
            cur=con.cursor()
            cur.execute("select * from attendence where name=?",(name,))
            tup=cur.fetchall()
            con.close()
            return tup

    except:
        return None

# sign up user
def add_student(name):
            try:
                #check user fill all values or not
                if name=="":
                    return False
                else:
                    # check if email not exist in database 
                    date=datetime.today()
                    
                    con=sqlite3.connect(database="school.sqlite")
                    
                
                    cur=con.cursor()
                    cur.execute("insert into attendence(name,date) values(?,?)",(name,date.date()))
                    con.commit()
                    con.close()

                    
                        #call user_info for user information
                    return True
            except:
                 return False



def attendence_sheet():
            con=sqlite3.connect(database="school.sqlite")
            cur=con.cursor()
            cur.execute("select * from attendence")
            txn=cur.fetchall()
            con.close()
            return txn