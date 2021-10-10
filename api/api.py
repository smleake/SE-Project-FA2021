import keys
import json
from flask import Flask, request, session, json, make_response, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import pymysql
import mysql
from datetime import datetime, timedelta
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = keys.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://' + keys.mysql_user + ':' + keys.mysql_password + '@' + keys.mysql_host
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

def token_required(func):
  @wraps(func)
  def decorated(*args, **kwargs):
    token = request.values.get('token')
    if not token:
      return jsonify({'Alert!': 'Token is missing!'}), 403
    try:
      payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
    except:
      return jsonify({'Alert!': 'Invalid Token!'}), 403
    return func(*args, **kwargs)

  return decorated

class Usercredentials(db.Model):
  username = db.Column(db.String(20), primary_key=True)
  password = db.Column(db.String(128))
  information = relationship("Userinfo", backref = "Usercredentials", passive_deletes = True, uselist=False)

class Userinfo(db.Model):
  usercredentials_username = db.Column(db.String(20), db.ForeignKey('usercredentials.username', ondelete = "CASCADE"), primary_key = True)
  name = db.Column(db.String(45))
  phonenumber = db.Column(db.String(12))
  email = db.Column(db.String(45))
  points = db.Column(db.Integer)
  billingaddressid = db.Column(db.Integer, db.ForeignKey('address.addressid', ondelete = "CASCADE"))
  mailingaddressid = db.Column(db.Integer, db.ForeignKey('address.addressid', ondelete = "CASCADE"))
  paymentmethod = db.Column(db.String(6))

class Address(db.Model):
  addressid = db.Column(db.Integer, primary_key=True)
  city = db.Column(db.String(20))
  state = db.Column(db.String(2))
  address = db.Column(db.String(50))
  zipcode = db.Column(db.Integer)
  billing = relationship("Userinfo", backref = "Address", foreign_keys="Userinfo.billingaddressid", passive_deletes = True, uselist=False)
  mailing = relationship("Userinfo", backref = "Address2", foreign_keys="Userinfo.mailingaddressid", passive_deletes = True, uselist=False)

def areAddressEqual(mailing, billing):
  if mailing == billing:
    return True
  else:
    return False

@app.route('/', methods=['GET'])
def index():
  return "This returns something."

@app.route('/api/register', methods=['GET', 'POST'])
def register_endpoint():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']

    hashed_password = generate_password_hash(password, method='sha256')

    user = Usercredentials.query.filter_by(username=username).first()

    if user:
       return make_response('Username taken!', 403)

    newUser = Usercredentials(username = username, password = hashed_password)

    db.session.merge(newUser)
    db.session.commit()
    
    token = jwt.encode({
      'username': request.form['username'],
      'expiration': str(datetime.utcnow() + timedelta(minutes=30)),
    }, app.config['SECRET_KEY'])

    return {'token': token}

@app.route('/api/login', methods=['GET', 'POST'])
def login_endpoint():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']

    user = Usercredentials.query.filter_by(username=username).first()

    if not user:
      return make_response('Unable to verify', 403, {'WWW-Authenticate': 'Basic realm: "Authentication failed!"'})
    
    if check_password_hash(user.password, password):
      token = jwt.encode({
      'username': request.form['username'],
      'expiration': str(datetime.utcnow() + timedelta(minutes=30)),
      }, app.config['SECRET_KEY'])

      return {'token': token}

    return make_response('Unable to verify', 403, {'WWW-Authenticate': 'Basic realm: "Authentication failed!"'})

@app.route('/test')
def test_endpoint():
      checkBillingAddress = Userinfo.query.filter((Userinfo.billingaddressid == 35) | (Userinfo.mailingaddressid == 35))
      print(checkBillingAddress.count())
      return ''

@app.route('/api/profile', methods=['GET', 'POST'])
def profile_endpoint():

  if request.method == 'POST':
    username = request.values.get('username')
    name = request.form['name']
    phonenumber = request.form['phonenumber']
    email = request.form['email']

    billingAddress = json.loads(request.form['billingAddress'])
    mailingAddress = json.loads(request.form['mailingAddress'])

    print(billingAddress)
    print(mailingAddress)

    isAddressEqual = areAddressEqual(billingAddress, mailingAddress)
    print(isAddressEqual)

    user = Userinfo.query.filter_by(usercredentials_username = username).first()
    billingAddressID = None
    mailingAddressID = None

    if isAddressEqual: #checks if addresses are equal
      userAddress = Address.query.filter_by(city = billingAddress['city'], state = billingAddress['state'], address = billingAddress['address'], zipcode = billingAddress['zip']).first() #looks for address in DB
      if userAddress: #if found stores ID of address
        billingAddressID = userAddress.addressid
        mailingAddressID = userAddress.addressid
      else: #if not found adds address to id and stores value
        newAddress = Address(city = billingAddress['city'], state = billingAddress['state'], address = billingAddress['address'], zipcode = billingAddress['zip'])
        db.session.merge(newAddress)
        db.session.commit()
        newAddress = Address.query.filter_by(city = billingAddress['city'], state = billingAddress['state'], address = billingAddress['address'], zipcode = billingAddress['zip']).first()
        billingAddressID = newAddress.addressid
        mailingAddressID = newAddress.addressid
    else: #if not equal
      userMailingAddress = Address.query.filter_by(city = mailingAddress['city'], state = mailingAddress['state'], address = mailingAddress['address'], zipcode = mailingAddress['zip']).first() #looks for address in DB
      userBillingAddress = Address.query.filter_by(city = billingAddress['city'], state = billingAddress['state'], address = billingAddress['address'], zipcode = billingAddress['zip']).first() #looks for address in DB
      if userBillingAddress: #if found
        billingAddressID = userBillingAddress.addressid #Store value of the id
      else:
        newBillingAddress = Address(city = billingAddress['city'], state = billingAddress['state'], address = billingAddress['address'], zipcode = billingAddress['zip']) #adds to db
        db.session.merge(newBillingAddress)
        db.session.commit()
        newBillingAddress = Address.query.filter_by(city = billingAddress['city'], state = billingAddress['state'], address = billingAddress['address'], zipcode = billingAddress['zip']).first()
        print(newBillingAddress)
        billingAddressID = newBillingAddress.addressid #store value to id

      if userMailingAddress:
        mailingAddressID = userMailingAddress.addressid
      else:
        newMailingAddress =  Address(city = mailingAddress['city'], state = mailingAddress['state'], address = mailingAddress['address'], zipcode = mailingAddress['zip'])
        db.session.merge(newMailingAddress)
        db.session.commit()
        newMailingAddress = Address.query.filter_by(city = mailingAddress['city'], state = mailingAddress['state'], address = mailingAddress['address'], zipcode = mailingAddress['zip']).first()
        mailingAddressID = newMailingAddress.addressid
        print(mailingAddressID)

    #Updates current user
    if user:
      user.name = name
      user.phonenumber = phonenumber
      user.email = email

      oldBillingAddressID = user.billingaddressid
      oldMailingAddressID = user.mailingaddressid

      user.billingaddressid = billingAddressID
      user.mailingaddressid = mailingAddressID

      db.session.commit()

      #check if address is still being used
      checkBillingAddress = Userinfo.query.filter((Userinfo.billingaddressid == oldBillingAddressID) | (Userinfo.mailingaddressid == oldBillingAddressID))
      checkMailingAddress = Userinfo.query.filter((Userinfo.billingaddressid == oldMailingAddressID) | (Userinfo.mailingaddressid == oldMailingAddressID))

      print(checkBillingAddress.count())
      print(checkMailingAddress.count())

      if checkBillingAddress.count() == 0:
        Address.query.filter_by(addressid = oldBillingAddressID).delete()
        print("Deleting not used Address")
        db.session.commit()
      if checkMailingAddress.count() == 0:
        Address.query.filter_by(addressid = oldMailingAddressID).delete()
        print("Deleting not used Address")
        db.session.commit()

      print("updating")
    else: #Creates new user 
      newProfile = Userinfo(usercredentials_username = username, name = name, phonenumber = phonenumber, email = email, billingaddressid = billingAddressID, mailingaddressid = mailingAddressID)
      db.session.merge(newProfile)
      db.session.commit()

    return "Your data is submitted"

  if request.method == 'GET':
    username = request.values.get('username')
    user = Userinfo.query.filter_by(usercredentials_username = username).first()

    if user: 
        billingAddressQuery = Address.query.filter_by(addressid = user.billingaddressid).first()
        mailingAddressQuery = Address.query.filter_by(addressid = user.mailingaddressid).first()

        bAddress = {
          "address": billingAddressQuery.address,
          "city": billingAddressQuery.city,
          "state": billingAddressQuery.state,
          "zip": billingAddressQuery.zipcode
        }
        mAddress = {
          "address": mailingAddressQuery.address,
          "city": mailingAddressQuery.city,
          "state": mailingAddressQuery.state,
          "zip": mailingAddressQuery.zipcode
        }

        dataToReturn = {
            "name": user.name,
            "phonenumber": user.phonenumber,
            "email": user.email,
            "billingAddress": bAddress,
            "mailingAddress": mAddress
        }

        print(dataToReturn)

        return json.dumps(dataToReturn)
    else:
        return jsonify({'Alert!': 'Error somewhere!'}), 400

@app.route('/api/reserve', methods=['GET', 'POST'])
def reserve_endpoint():

  if request.method == 'GET':
    username = request.values.get('username')
    user = Userinfo.query.filter_by(usercredentials_username = username).first()

    if user: 
        dataToReturn = {
            "name": user.name,
            "phonenumber": user.phonenumber,
            "email": user.email
        }

        print(dataToReturn)

        return json.dumps(dataToReturn)
    else:
        return jsonify({'Alert!': 'Error somewhere!'}), 400
