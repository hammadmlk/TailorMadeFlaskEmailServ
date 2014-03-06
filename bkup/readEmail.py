import oauth2
import imaplib
import email
import sys

emailid         = "hammadmlk@gmail.com"
client_id       ="788164556802-jiv01d9fg17i3emc1ieeivoas749t5cb.apps.googleusercontent.com"
client_secret   ="MwXOV-oCRmOJy3NBLQFSW5fj"
access_token   ="ya29.1.AADtN_UI8Z0TSGH71kZtu0LJnpEJXHX243ebziCiDf6gZ5hdwhW8IRzuYByrlcWWFlhd"

oAuth2String        = oauth2.GenerateOAuth2String(emailid,access_token,base64_encode=False) #before passing into IMAPLib access token needs to be converted into string
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.authenticate('XOAUTH2', lambda x: oAuth2String)

status, msgs = mail.select('[Gmail]/All Mail') # connect to inbox.

if status != 'OK':
    print 'warr gai'
    sys.exit()

print "---------   ", int(msgs[0])


#rest of the code to play with emails
#for more info please check the link on top

typ, data = mail.search(None, 'ALL')


outfile = open('subjects2.txt', 'w')

for num in data[0].split():
        typ, data = mail.fetch(num, '(RFC822.SIZE BODY[HEADER.FIELDS (SUBJECT)])')
        message = data[0][1].lstrip('Subject: ').strip() + ' '
        #print message
        outfile.write(message+'\n')

print "DONE!!!!!!!!!"
mail.logout()




