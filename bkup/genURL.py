import oauth2

client_id="788164556802-jiv01d9fg17i3emc1ieeivoas749t5cb.apps.googleusercontent.com"

client_secret="MwXOV-oCRmOJy3NBLQFSW5fj"

print 'To authorize token, visit this url and follow the directions:'

print ' %s' % oauth2.GeneratePermissionUrl(client_id)

authorization_code = raw_input('Enter verification code: ')

response = oauth2.AuthorizeTokens(client_id,client_secret,authorization_code)
print "Refresh Toke :",response['refresh_token']
print "Access Token :",response['access_token']
print "Expires in :",response['expires_in']

