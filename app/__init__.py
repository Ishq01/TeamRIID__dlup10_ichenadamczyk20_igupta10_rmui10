# run app.py but without debug mode
import app
app.app.debug = True
app.app.run(host='0.0.0.0')