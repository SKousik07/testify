from flask import Flask,jsonify,request
import pymongo
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import json
from bson.objectid import ObjectId
##########################################################

app=Flask(__name__)
client = pymongo.MongoClient("mongodb+srv://flaskadmin:flaskpwd@cluster0.pb8ro.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = client.users
bcrypt = Bcrypt(app)
CORS(app)
##########################################################

@app.route("/login",methods=["POST"])
def login():
    req=request.json
    res=db.auth.find_one({"email": req["email"] })
    
    if res:
        if bcrypt.check_password_hash(res['password'], req['password']):

            return {"result" : "success",
                "data": {"id": str(res["_id"]),"email": res['email'],"completed_tests":res["completed_tests"]}},201
        else:

            return {"result" : "Password did not match",
                "data": f"{request.json}"},200

    else:
        return {"result" : "No user found",
              "data": f"{request.json}"},200



@app.route("/signup",methods=["POST"])
def signup():
    req=request.json
    res=db.auth.find_one({"email": req["email"] })
    if res:
        return {"result" : "User already present",
              "data": f"{request.json}"},201
    else:
        res1=db.auth.insert_one({"email": req["email"], 
                                "password": bcrypt.generate_password_hash(req['password'])})
        # print(res1)
        return {"result" : "success",
               "data": {"id": f"{res1.inserted_id}", "email": req["email"]  },
              "insertedID": f"{res1.inserted_id}"},200

######################################################################

@app.route("/courses",methods=["GET"])
def getCourses():
    dbres=list(db.courses.find())
   
    for i in dbres:
        i["_id"]=str(i["_id"])
    return {"data": dbres }

@app.route("/tests/<name>",methods=["GET"])    ##################what to do??????????????/
def getTests(name):
    dbres=list(db.courses.find({"name": name}))
    for i in dbres:
        i["_id"]=str(i["_id"])
    
    return {"data": dbres}
        
@app.route("/submit/<name>",methods=["POST"])
def submitTest(name):
    test=request.json
    m=0
    for i in test['questions']:
        if i['answer']==i['selected']:
            m+=1
    test['score']=m
    dbres1=list(db.auth.find({ 'completed_tests.name': test['name']}))
    if dbres1:
        x=db.auth.find_one_and_update({ 'email': name}, {'$pull': { 'completed_tests': { 'name': test['name'] }}})
        # print("**************")
        # print(x)
        # print("**************")

    dbres=db.auth.find_one_and_update({ 'email': name}, {'$push': {'completed_tests': test}})
   
    # print(dbres)
    return {"msg":"success"},200

@app.route("/comp/<name>",methods=["GET"])
def comp(name):
    res=list(db.auth.find({'email': name}))
    print(res)
        
    return {"data":{"completed_tests": res[0]["completed_tests"]}}



if __name__ == "__main__":
    app.run(debug=True)