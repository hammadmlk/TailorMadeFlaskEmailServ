import oauth2

client_id="788164556802-jiv01d9fg17i3emc1ieeivoas749t5cb.apps.googleusercontent.com"

client_secret="MwXOV-oCRmOJy3NBLQFSW5fj"


client_id= "788164556802-77032h0shl056j1jkdpv58irspq6kavj.apps.googleusercontent.com"
client_secret="-g2U1yx5rnajiQub9y5CJPc8"
redirect_uri='http://moodrhythm.com:5000/auth'



print 'To authorize token, visit this url and follow the directions:'

print ' %s' % oauth2.GeneratePermissionUrl(client_id, redirect_uri)

authorization_code = raw_input('Enter verification code: ')

response = oauth2.AuthorizeTokens(client_id,client_secret,authorization_code, redirect_uri)
print "Refresh Toke :",response['refresh_token']
print "Access Token :",response['access_token']
print "Expires in :",response['expires_in']

