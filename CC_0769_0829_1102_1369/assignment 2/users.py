from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api
import json
import os
import re
from constant import Area
from datetime import datetime
import requests
import ast
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

################################################
#Flask App
app = Flask(__name__)
basedir=os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
api=Api(app)

################################################

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, unique=True, nullable=False)
	password = db.Column(db.String, unique=False, nullable=False)

	def __init__(self,username,password):
		self.username=username
		self.password=password

class UserSchema(ma.Schema):
	class Meta:
		fields=('id','username','password')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

#################################################

class Rides(db.Model):
	rideId = db.Column(db.Integer, primary_key=True)
	created_by = db.Column(db.String, unique=False, nullable=False)
	timestamp = db.Column(db.String)
	source = db.Column(db.Integer, nullable=False)
	destination = db.Column(db.Integer, nullable=False)

	def __init__(self,created_by,timestamp,source,destination):
			self.created_by=created_by
			self.timestamp=timestamp
			#self.users=[users]

			self.source=source
			self.destination=destination

class RideSchema(ma.Schema):
	class Meta:
		fields=('rideId','created_by','timestamp','source','destination')

ride_schema = RideSchema()
rides_schema = RideSchema(many=True)

################################################

class Other_Users(db.Model):
	i = db.Column(db.Integer, primary_key=True)
	ID = db.Column(db.Integer, unique=False,nullable=False)
	user_names= db.Column(db.String, nullable=False)

	def __init__(self,ID,user_names):
		self.ID=ID
		self.user_names=user_names

class Other_UsersSchema(ma.Schema):
	class Meta:
		fields=('ID','user_names')

other_user_schema = Other_UsersSchema()
other_users_schema = Other_UsersSchema(many=True)

###############################################

db.create_all()
#API 1 : Remaining work : Validating password
#ADD USER
@app.route("/api/v1/users",methods=["PUT"])
def adduser():
	psd=re.compile("(^[abcdefABCDEF0123456789]{40}$)")
	userToAdd=request.get_json()["username"]
	pwd=request.get_json()["password"]

	if(request.method!="PUT"):
		return jsonify({}), 405

	if(not(psd.match(pwd))):
		return jsonify({}), 400 #if password is not valid

	d = dict()
	d['flag'] = 1 
	d['username'] = userToAdd
	d['password'] = pwd

	w=requests.post("http://127.0.0.1:8080/api/v1/db/read", json=d)

	e =ast.literal_eval(w.text)

	if(e):
		return jsonify({}), 400
	else:
		r=requests.post("http://127.0.0.1:8080/api/v1/db/write", json=d)
		return jsonify({}), 201


#API 2 
#DELETE USER
@app.route("/api/v1/users/<username>",methods=["DELETE"])
def delete_user(username):
	d = dict()
	d['flag'] = 1
	d['username'] = username

	w=requests.post("http://127.0.0.1:8080/api/v1/db/read", json=d)

	e =ast.literal_eval(w.text)

	if(e):
		d['flag'] = 2
		r=requests.post("http://127.0.0.1:8080/api/v1/db/write", json=d)
		return jsonify({}), 200
	else:
		return jsonify({}),400

#SHOW ALL USERS {FOR REFERENCE}
@app.route("/api/v1/users",methods=["GET"])
def show():
	all_users=User.query.all()
	re=users_schema.dump(all_users)
	#print(re)
	#re=[]
	if(not re):
		return (jsonify({}),204)
	if(request.method!="GET"):
		return (jsonify({}), 405)
	l=[]
	for i in re:
		for k in i.keys():
			if(k=="username"):
				l.append(i[k])
	#print("\n\n\n\n\n",l)

	return (jsonify(l),200)

#########################################################
#write API

@app.route("/api/v1/db/write",methods=["POST","DELETE"])
def writeToDB():
	flag = request.get_json()["flag"]
	if flag == 1:  #User add
		username = request.get_json()["username"]
		password = request.get_json()["password"]
		newUser=User(username,password)
		db.session.add(newUser)
		db.session.commit()
		return jsonify({})
	elif flag == 2 : #user delete
		username = request.get_json()["username"]
		User.query.filter_by(username=username).delete()
		Other_Users.query.filter_by(user_names=username).delete()
		Rides.query.filter_by(created_by=username).delete()
		db.session.commit()
		return jsonify({})
	elif flag == 3: #add ride
		hey=request.get_json()["created_by"]
		timestamp=request.get_json()["timestamp"]
		source=request.get_json()["source"]
		destination=request.get_json()["destination"]
		newRide=Rides(hey,timestamp,source,destination)
		db.session.add(newRide)
		db.session.commit()
		#return "hi"
		return jsonify({})
	elif flag == 4 : #delete ride
		rideId = request.get_json()["rideId"]
		Rides.query.filter_by(rideId=rideId).delete()
		Other_Users.query.filter_by(ID=rideId).delete()
		db.session.commit()
		print("Ride Deleted")
		return jsonify({})
	elif flag == 5 : #Add other user
		ID = request.get_json()["rideId"]
		username = request.get_json()["username"]
		new=Other_Users(ID,username)
		db.session.add(new)
		db.session.commit()
		return jsonify({})


###########################################################

#read API

@app.route("/api/v1/db/read",methods=["GET","PUT","POST","DELETE"])
def readFromDB():
	flag = request.get_json()["flag"]
	if flag == 1:  #check if username is present
		username = request.get_json()["username"]
		u=bool(User.query.filter_by(username = username).first())
		if(u):
			return "1"
		else:
			return "0"
	elif flag == 2: #check if createby is present in users db
		username = request.get_json()["created_by"]
		u=bool(User.query.filter_by(username = username).first())
		if(u):
			return "1"
		else:
			return "0"
	elif flag == 3: #check if ride is present
		rideId = request.get_json()["rideId"]
		u=bool(Rides.query.filter_by(rideId = rideId).first())
		if(u):
			return "1"
		else:
			return "0"
	elif flag == 4:
		rideId = request.get_json()["rideId"]
		ride = db.session.query(Rides.rideId, Rides.created_by, Rides.timestamp,Rides.source, Rides.destination).filter_by(rideId = rideId).all()
		return jsonify(ride)
	elif flag == 5:
		rideId = request.get_json()["rideId"]
		ursr= db.session.query(Other_Users.user_names).filter_by(ID = rideId).all()
		return jsonify(ursr)
	elif flag == 6:
		rideId = request.get_json()["rideId"]
		r=bool(Rides.query.filter_by(rideId = rideId).first())
		return jsonify({'val':r})	
	elif flag == 7: #source/destination - display ride details
		sourceok=request.get_json()['source']
		dest =request.get_json()['destination']
		now=datetime.utcnow()
		s1=now.strftime("%d-%m-%Y:%S-%M-%H")
		d1=datetime.strptime(s1, "%d-%m-%Y:%S-%M-%H")

		srcc = db.session.query(Rides).filter_by(source = sourceok, destination=dest).with_entities(Rides.rideId,Rides.created_by,Rides.timestamp).all()
		print("\n\n\n\n",srcc,"\n\n\n\n")
		temp = srcc.copy()
		for use in temp:
			s2=use.timestamp
			d2=datetime.strptime(s2,"%d-%m-%Y:%S-%M-%H")
			k=str(d2-d1)
			print("\n\n\n\n",k,"\n\n\n\n")
			user_data={}
			if(k[0]=="-"):
				srcc.remove(use)
		r_schema = RideSchema(many=True)
		print("\n\n\n\n",srcc,"\n\n\n\n")
		ress= r_schema.dump(srcc)       
		return jsonify(ress)

	elif flag == 8:
		rideId=request.get_json()['rideId']
		username=request.get_json()['username']
		r=bool(Rides.query.filter_by(rideId = rideId, created_by=username).first())
		if(r):
			return "0"
		else:
			return "1"
	elif flag ==9 :
		rideId=request.get_json()['rideId']
		username=request.get_json()['username']
		r=bool(Other_Users.query.filter_by(ID = rideId, user_names=username).first())
		if(r):
			return "0"
		else:
			return "1"

#CLEAR DB
@app.route("/api/v1/db/clear",methods=["POST"])
def clear_data():
	meta = db.metadata
	for table in reversed(meta.sorted_tables):
		db.session.execute(table.delete())
	db.session.commit()
	return jsonify({}),200

if __name__ == '__main__':
	app.debug=True
	app.run(host="0.0.0.0",port="8080")
		
