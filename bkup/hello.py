from tailormade import app

#@app.route('/tailormade/d')
#def hello_world():
#    return 'Hello World!'

def index():
    if request.method == 'OPTIONS':
        # custom options handling here
        a=1
    return 'Hello World!'
index.provide_automatic_options = False
index.methods = ['GET', 'OPTIONS']

app.add_url_rule('/', index)

