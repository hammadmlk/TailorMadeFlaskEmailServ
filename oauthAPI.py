##############
## oAuth2 API for GMail Authentication
##############
import oauth2

## Keys
client_id= "788164556802-77032h0shl056j1jkdpv58irspq6kavj.apps.googleusercontent.com"
client_secret="-g2U1yx5rnajiQub9y5CJPc8"
redirect_uri='http://moodrhythm.com:5000/auth'

## PermissionURL
def permissionURL():
    return oauth2.GeneratePermissionUrl(client_id, redirect_uri);

## Get Tokens
def getTokens(auth_code):
    response = oauth2.AuthorizeTokens(client_id,client_secret,auth_code, redirect_uri)
    #print "Refresh Token :", response['refresh_token']
    #print "Access Token :",response['access_token']
    #print "Expires in :",response['expires_in']
    #print authTokens['refresh_token']
    #print authTokens['access_token']
    #print authTokens['expires_in']
    return

## refresh Tokens
def refreshToken(refresh_token):
    return oauth2.RefreshToken(client_id,client_secret,refresh_token)
    #print refreshedToken['access_token']

##############
## END
##############
