import oauth2

client_id       ="788164556802-jiv01d9fg17i3emc1ieeivoas749t5cb.apps.googleusercontent.com"

client_secret   ="MwXOV-oCRmOJy3NBLQFSW5fj"

refresh_token   ="1/aVsjsx2vF5Vir0-vljHUTw6iNyDqGHXN9QLvbdXd_gw"

response        = oauth2.RefreshToken(client_id,client_secret,refresh_token)

print "New Access Token :", response['access_token']

print "Expires in :", response['expires_in']

