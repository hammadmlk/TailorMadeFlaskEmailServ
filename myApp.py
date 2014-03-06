#from __future__ import unicode_literals

from flask import Flask, url_for, render_template, request, make_response, redirect
from flask.ext.login import (LoginManager, current_user, login_required,
                             login_user, logout_user, UserMixin, AnonymousUserMixin)                             
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
#from flask_sqlalchemy import SQLAlchemy
from modules.oauth2 import GeneratePermissionUrl
from modules.oauth2 import AuthorizeTokens

from imapclient.imapclient import IMAPClient
from email.parser import Parser

import datetime
import sys
import json
import requests
import oauth2
import imaplib
import email

app = Flask(__name__)
app.config.from_pyfile('settings.py')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

###
###

class Email(db.Model):
    mailbox = db.Column(db.String(250), primary_key=True, nullable=False)
    msgid = db.Column(db.BigInteger, primary_key=True)
    threadid = db.Column(db.BigInteger)    
    subject = db.Column(db.String(250))
    date = db.Column(db.DateTime)
    inreplyto = db.Column(db.String(250))
    #EmailAddrs = db.relationship('EmailAddr', backref='email', lazy='dynamic')
    
    def __init__(self, mailbox, msgid, threadid, subject, date, inreplyto):
        self.mailbox = mailbox
        self.msgid = msgid
        self.threadid = threadid
        self.subject = subject
        self.date = date
        self.inreplyto = inreplyto
        #self.emailAddrs
        
    def __repr__(self):
        return '   MAILBOX: %s,  MSG-ID: %d,  THREAD-ID: %d,  Subject: %s  Date:%s \n' % (self.mailbox, self.msgid, self.threadid, self.subject, str(self.date))
    
class EmailAddr(db.Model):
    mailbox = db.Column(db.String(250), primary_key=True)
    msgid = db.Column(db.BigInteger, db.ForeignKey('email.msgid'), primary_key=True)
    type = db.Column(db.String(50), primary_key=True)
    emailaddress = db.Column(db.String(250), primary_key=True)
    
    def __init__(self, mailbox, msgid, type, emailaddress):
        self.mailbox = mailbox
        self.msgid = msgid
        self.type = type
        self.emailaddress = emailaddress
        
    def __repr__(self):
        return '   MAILBOX: %s, MSG-ID: %d,   TYPE: %s,   EMAIL-ADDRESS: %s \n' % (self.mailbox, self.msgid, self.type, self.emailaddress)

db.create_all()        


def addEmailAddrToDd(db, mailbox, msgid, type, emailAddrList ):
    for e in emailAddrList:
        ea = EmailAddr(mailbox, msgid, type, e)       
        try:
            db.session.add(ea)
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            #print "Duplicate Ignored\n"

####
####

class User(UserMixin):
    """User Session management Class
    """
    def __init__(self, email, id, fname="", lname="", accesstoken="", refreshtoken="", active=True):
        self.email = email
        self.id = id
        self.active = active
        self.fname = fname
        self.lname = lname
        self.accesstoken = accesstoken
        self.refreshtoken = refreshtoken

    def access_token(self):
        return self.accesstoken

    def refresh_token(self):
        return self.refreshtoken

    def is_active(self):
        return self.active

    def myemail(self):
        return self.email

    def get_userid(self):
        return self.id

    def get_fname(self):
        return self.fname

    def get_lname(self):
        return self.lname
    
    def printx(self):
        #print self.email, self.id, self.accesstoken, self.refreshtoken
        return
    

"""
USER_STORE is the store of all the users. Ideally it should be in Database
"""
USERS = {
    1: User("anurag@grexit.com", 1, "Anurag", "Maher", "", "", True)
}

"""
USER_NAMES maintains a dictionary of all the users with their email address
"""
USER_NAMES = dict((u.email, u) for u in USERS.itervalues())

latestID = 1

def newID():
    global latestID
    latestID+=1
    return latestID

    
    
    
def ParseAddressStructure(addressStructure):
    emails = [];
    if addressStructure != None:
        for emailAddr in addressStructure:
            #             mailboxName  + '@'+ hostName
            if emailAddr[2] ==None or emailAddr[3] == None:
                #print "ERROR XC33 - server returned None in mailbox name or host name, which is not excepted"
                emails.append("UNKNOWN")
            else:
                emails.append(emailAddr[2] +"@"+ emailAddr[3])
    return emails
    
    
    
@app.route('/')
def index():
    return render_template('index.html')
	
@app.route('/auth', methods=['GET'])
def authorize():
    if request.method == 'GET':
        auth_code = request.args.get('code','')
        tokens = oauthAPI.getTokens(auth_code)
        resp = make_response(render_template('authorize.html', tokens=tokens))
        #resp.set_cookie('refresh_token', tokens['refresh_token'])
        return resp
    return "Error 0X1"

@app.route('/setcookie', methods=['GET'])
def setcookie():
    resp = make_response(render_template('hello.html', name=request.cookies.get('biscuit')))
    resp.set_cookie('biscuit', request.args.get('biscuit',''))
    return resp


@app.route('/getcookie')
def getcookie():
    return render_template('hello.html', name= request.cookies.get('biscuit'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    #if request.method == "GET" and request.args.get('email', ''):
        #print "Generating Permission URL For: " + request.args.get('email', '')
    url = GeneratePermissionUrl(app.config['GOOGLE_CLIENT_ID'], 'emailFake', redirect_uri=app.config['REDIRECT_URI'], google_account_base_url=app.config['GOOGLE_ACCOUNTS_BASE_URL'])
    #print "Permission URL: ", url
    return redirect(url)
    #return "No Email Provided"
		

@app.route("/oauth2callback", methods=["GET", "POST"])
def oauth2callback():
    if request.method == "GET":
        authorizationcode = request.args.get('code', '')
        #useremail = request.args.get('state', '')
        response = AuthorizeTokens(app.config['GOOGLE_CLIENT_ID'],
                                   app.config['GOOGLE_CLIENT_SECRET'],
                                   authorizationcode,
                                   redirect_uri=app.config['REDIRECT_URI'],
                                   google_account_base_url=app.config['GOOGLE_ACCOUNTS_BASE_URL'])
        #print "--"
        #print "--"
        #print response
        #print "--"
        #print "--"
        accesstoken = response["access_token"]
        refreshtoken = response["refresh_token"]
		
        r = requests.get('https://www.googleapis.com/oauth2/v1/userinfo?access_token=' + accesstoken)
        #print "json file: " + r.text
        j = json.loads(r.text)
        #if useremail != j["email"]:
        #    return "Initiated e-mail does not match with the authenticated email"
        options = {}
        options["email"] = j.get("email")
        options["firstname"] = j.get("given_name")
        options["lastname"] = j.get("family_name")
        options["accesstoken"] = accesstoken
        options["refreshtoken"] = refreshtoken
        userid = newID()
		
        u = User(options.get("email"), userid, options.get("firstname"), options.get("lastname"), accesstoken, refreshtoken)
        USERS[userid] = u
        loginit = login_user(u, remember="yes")
        if loginit == True:
            resp = make_response(redirect('/imap'))
            resp.set_cookie('ak', accesstoken)
            resp.set_cookie('email', options.get("email"))
            return resp
            #return "Authentication Tokens Saved Successfully"
        return "Some Problem happened"		
		

@app.route('/tokens')
def tokens():
    for user in USERS:
        USERS[user].printx()
        #print " "
    return "DONE"


@app.route('/summary', methods=["GET"])
def summary():
    mailbox_name = str(request.cookies.get('email'))
    stri = ""
    startDate = datetime.date(2014, 02, 06)

    #### Total
    stri+= '\n\n||TOTAL EMAILS IN DB'
    stri+= '\n  '+ str(Email.query.count())
    
    stri+= '\n\n||Total Emails from ' + mailbox_name + ':'
    stri+= '\n  '+ str(Email.query.filter_by(mailbox=mailbox_name).count())
    ###
    
    #### By day of month
    stri += "\n\n||Showing by Day of Month (1-31)\n  Day \tnum"
    sDate = startDate
    eDate = sDate + datetime.timedelta(days=1)
    for i in range(30):
        dayCount = Email.query.filter_by(mailbox=mailbox_name).filter(Email.date >= sDate).filter(Email.date < eDate).order_by(Email.date).count()
        sDate = eDate
        eDate = sDate + datetime.timedelta(days=1)
        stri += "\n  " + str(sDate.day) + '\t' + str(dayCount)        
    ####
    
    #### By day of week
    stri += "\n\n||Showing by Day of Week. Mon=0, w1=1st week of Month, sum=row total\n  Day \t(sum) \tw1 \tw2 \tw3 \tw4 \tw5"    
    
    weekdayCount = [[0 for x in range(5)] for y in range(7)]
    #print weekdayCount
    
    for e in Email.query.filter_by(mailbox=mailbox_name).all():
        #print e.date.weekday(), '-', e.date.day/7        
        weekdayCount[e.date.weekday()][e.date.day/7] += 1
        #print weekdayCount
    
    for i in range(7):
        stri += "\n  " + str(i)
        for j in range(5):
            if (j == 0):
                sum = reduce(lambda x, y: x + y, weekdayCount[i])
                stri+= '\t' + str(sum)
            stri += '\t' + str(weekdayCount[i][j])
    ####
    
    #### By hour of day
    stri += "\n\n||By Hour of Day. \n  Hour \t(Sum) \tday1 \tday2 \tday3 \tday4 \tday5 \tday6 ... ..."       
    hourdayCount = [[0 for x in range(31)] for y in range(24)]
    
    for e in Email.query.filter_by(mailbox=mailbox_name).all():
        #print e.date.day, '-', e.date.hour        
        hourdayCount[e.date.hour][e.date.day] += 1
    
    for h in range(24):
        stri += "\n  " + str(h)
        for d in range(31):
            if (d == 0):
                sum = reduce(lambda x, y: x + y, hourdayCount[h]) #/ len(hourdayCount[h])
                stri+= '\t' + str(sum)
            stri += '\t' + str(hourdayCount[h][d])
    ####


    return '<pre>'+stri+'</pre>'
    
    
@app.route('/sql', methods=["GET"])
def sql():
    mailbox_name = str(request.cookies.get('email'))
    
    #emails = Email.query.filter_by(mailbox=mailbox_name)#.all()
    #emailaddrs = EmailAddr.query.filter_by(mailbox=mailbox_name)#.all()
    
    sentEmails = db.session.query(Email, EmailAddr).filter(Email.msgid==EmailAddr.msgid).\
                         filter(EmailAddr.type=='from').filter(EmailAddr.emailaddress==mailbox_name)#.all()
    
    receivedEmails = db.session.query(Email, EmailAddr).filter(Email.msgid==EmailAddr.msgid).\
                         filter(EmailAddr.type=='to').filter(EmailAddr.emailaddress==mailbox_name)#.all()
    
    return '<pre>'+str("\n\n==== SENT EMAILS "+str(sentEmails.count())+" : ===== \n\n")+str(sentEmails.all())+'</pre>'+\
            '<pre>'+str("\n\n==== RECEIVED EMAILS "+str(receivedEmails.count())+" : ===== \n\n")+str(receivedEmails.all())+'</pre>'
    
    
    #return '<pre>'+str(emails)+'</pre>'+'<pre>'+str(emailaddrs)+'</pre>'

@app.route('/imap', methods=['GET'])
def imapPage():

    folder = request.args.get('folder','')
    if (folder == ''):
        folder="All Mail"
    
    email = request.cookies.get('email')
    accesskey = request.cookies.get('ak')
    
    if email != "" and accesskey != "":
                
        server = IMAPClient('imap.gmail.com', use_uid=True, ssl=True)
        
        server.oauth2_login(email, accesskey)
        
        #PRINT FOLDERS
        #folders = server.list_folders()
        #for folderx in folders:
        #    print folderx
        
        
        select_info = server.select_folder('[Gmail]/'+folder, readonly=True) 
        #print select_info
        
        #messages = server.search(['SINCE 05-Feb-2014 NOT FROM \"facebook\"'])
        messages = server.search(['SINCE 06-Feb-2014'])
        
        #print "-"
        #print messages
        #print "-"
                    
        response = server.fetch(messages, ['X-GM-MSGID', 'X-GM-THRID', 'FLAGS', 'INTERNALDATE', 'ENVELOPE'])
        for msgid, data in response.iteritems():
            
            #print "==========="
            #print data['FLAGS']
            #print data['INTERNALDATE']
            #print data['ENVELOPE']
            #print data['BODY[HEADER]']
            
            '''
            The fields of the envelope structure are in the following order: date, subject, from, sender, reply-to, to, cc, bcc, in-reply-to, and message-id.  
            The date, subject, in-reply-to, and message-id fields are strings.  
            The from, sender, reply-to, to, cc, and bcc fields are parenthesized lists of address structures.
            '''
            ##
            #Making proper data structure for Envelope
            ##
            env = {}
            env['date']= data['ENVELOPE'][0]
            env['subject']= data['ENVELOPE'][1]
            env['in-reply-to']= data['ENVELOPE'][8]
            env['message-id']= data['ENVELOPE'][9]
            
            env['from']= ParseAddressStructure(data['ENVELOPE'][2])
            env['sender']= ParseAddressStructure(data['ENVELOPE'][3])
            env['reply-to']= ParseAddressStructure(data['ENVELOPE'][4])
            env['to']= ParseAddressStructure(data['ENVELOPE'][5])
            env['cc']= ParseAddressStructure(data['ENVELOPE'][6])
            env['bcc']= ParseAddressStructure(data['ENVELOPE'][7])
            
            em = Email(email, data['X-GM-MSGID'],data['X-GM-THRID'],env['subject'], data['INTERNALDATE'], env['in-reply-to'])
            
            try:
                db.session.add(em)
                db.session.flush()
            except IntegrityError:
                db.session.rollback()
                #print "Duplicate Ignored\n"
            
            addEmailAddrToDd(db, email, data['X-GM-MSGID'], 'from', env['from'] )
            addEmailAddrToDd(db, email, data['X-GM-MSGID'], 'sender', env['sender'] )
            addEmailAddrToDd(db, email, data['X-GM-MSGID'], 'reply-to', env['reply-to'] )
            addEmailAddrToDd(db, email, data['X-GM-MSGID'], 'to', env['to'] )
            addEmailAddrToDd(db, email, data['X-GM-MSGID'], 'cc', env['cc'] )
            addEmailAddrToDd(db, email, data['X-GM-MSGID'], 'bcc', env['bcc'] )
            
            
            #  Or for parsing headers in a string, use:
            #headers = Parser().parsestr(data['BODY[HEADER]'])                
            #  Now the header items can be accessed as a dictionary:
            #print 'To: %s' % headers['to']
            #print 'From: %s' % headers['from']
            #print 'Subject: %s' % headers['Subject'] 
            #print 'Date: %s' % headers['date']
            #print "+++++++"
            
        db.session.commit()
    
    
    if (folder=="All Mail"):
        return redirect('/imap?folder=Trash')
    if (folder=="Trash"):
        return redirect('/summary')
    return 'Error SW32 - check GET parameters'
    
    
        


	
@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id

with app.test_request_context():
    url_for('index')
    url_for('hello')
    url_for('show_post', post_id=12)
    url_for('static', filename='style.css')
    #print url_for('index')
    #print url_for('hello')
    #print url_for('show_post', post_id=12)
    #print url_for('static', filename='style.css')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')


