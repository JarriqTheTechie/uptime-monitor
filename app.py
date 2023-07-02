from flask import Flask, render_template, request, session

from packages.experimental.hubi_admin.hubi_ext import HubiAdmin

app = Flask(__name__)
# app.config['EXPLAIN_TEMPLATE_LOADING'] = True
HubiAdmin(app)



@app.before_request
def before_request():
    session['username'] = 'jrolle'
    session['fullname'] = 'Jarriq Rolle'
    pass


if __name__ == '__main__':
    app.run()
