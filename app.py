from flask import Flask, render_template, request,Response,send_file
import cv2 
import time
import os
import pandas as pd
from sklearn.linear_model import LogisticRegression
import shutil
import attendence


app=Flask(__name__)
database=attendence.create_database()
print(database)

try:
    shutil.rmtree("face", ignore_errors=True)
    
except:
    pass


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/userpage')
def userpage():
    return render_template('userpage.html')


@app.route('/login',methods=['POST'])
def login():
    username=request.form['username']
    password=request.form['password']
    if username=="admin" and password=="admin":

        print(username,password)
        return render_template('userpage.html')
    else:
        return render_template('home.html',error='incorrect usernmae adn passo')




 # concat frame one by one and show result

@app.route('/video_page')
def video_page():
     
     return render_template('new.html')


@app.route('/recognize_page')
def recognize_page():
    df_target=pd.read_csv('target.csv')
    df_feature=pd.read_csv('feature.csv')
    y=df_target.values
    X=df_feature.values
    global model
    model=LogisticRegression()
    model.fit(X,y)
    return render_template('recognize.html')

@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    
    return Response(addvideo(), mimetype='multipart/x-mixed-replace; boundary=frame')
   

  
def addvideo():
    os.mkdir("face")
    vdo=cv2.VideoCapture(0)
    model=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    count=1
    t_end = time.time() + 20 * 1
    while time.time() < t_end:
        flag,img=vdo.read()
        if not flag:
            break
        else:
            gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            list_face=model.detectMultiScale(gray)
            
        
            for x,y,w,h in list_face:
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,255,255),2) 
                face=img[y:y+h,x:x+w]
                cv2.imwrite(f"face/{count}.png",face)
                count+=1
        
            ret, buffer = cv2.imencode('.png', img)
            img = buffer.tobytes()
        
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
   

@app.route('/add_user',methods=['POST'])
def add_user():
    try:
        name=request.form['name']

        X=[]
        y=[]
        img_names=os.listdir("face")
        for iname in img_names:
            img=cv2.imread(f"face/{iname}")
            img=cv2.resize(img,(100,100))
            gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            gray=gray.flatten()
            gray=gray/255
            X.append(gray)
            y.append(name)

        #now create dataframes   
        df_target=pd.DataFrame(y)
        df_feature=pd.DataFrame(X)
        df_target.to_csv("target.csv",mode='a',index=False,header=False)
        df_feature.to_csv("feature.csv",index=False,mode='a',header=False)
        attendence.add_student(name)
        return render_template('userpage.html')
    except:
        return "error"
    finally:
        shutil.rmtree("face", ignore_errors=True)



@app.route('/recognize')
def recognize():
    
    return Response(recognize_user(),mimetype='multipart/x-mixed-replace; boundary=frame')

def recognize_user():
    
    vdo=cv2.VideoCapture(0)
    model2=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    pr=[]
    while(True):
        flag,img=vdo.read()
        if(flag==False):
            break
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        list_face=model2.detectMultiScale(gray)
        
        for x,y,w,h in list_face:
            face=img[y:y+h,x:x+w]
            face=cv2.resize(face,(100,100))
            gray=cv2.cvtColor(face,cv2.COLOR_BGR2GRAY)
            gray=gray.flatten()
            gray=gray/255
            pred=model.predict([gray])
            
            n=pr.count(pred[0])
            if (n>30):
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,225,0),2) 
                cv2.putText(img,f"{pred[0]}",(x,y-10),cv2.FONT_HERSHEY_PLAIN,2.5,(0,225,0),2)
            
            elif(n==30):
                result=attendence.add_student(pred[0])
                print(result)
                



            else:
                cv2.rectangle(img,(x,y),(x+w,y+h),(225,225,255),2) 
               


            ret, buffer = cv2.imencode('.png', img)
            img1 = buffer.tobytes()
        
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + img1 + b'\r\n')
        pr.append(pred[0])
     
@app.route("/attendence_sheet")
def attendenc_sheet():
    sheet=attendence.attendence_sheet()
    return render_template("attendence_sheet.html",txn=sheet)


@app.route('/verify_user',methods=['POST'])
def verify_user():
    
        name=request.form['name']
        sheet=attendence.verify_user(name)
        if sheet:
            return render_template("attendence_sheet.html",txn=sheet)
        else:
            return render_template('home.html')
        

@app.route('/get_sheet')
def get_sheet():
    txn=attendence.attendence_sheet()
    d=[]
    for i in txn:
        d.append({"date":i[0],"transaction_type":i[1]})
            
    df=pd.DataFrame(d)

    df.to_excel("userinformation\\transfer.xlsx")
    p="userinformation\\transfer.xlsx"
    return send_file(p,as_attachment=True)

if __name__=='__main__':
    app.run(debug=True)