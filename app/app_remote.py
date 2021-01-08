# Runs the Flask app in app.py, but hosted on 0.0.0.0:5000 so that it can be accessible by other computers on the
# network, not just on the host.
import app
app.app.debug = False
app.app.run(host='0.0.0.0')
