"""
Author: T.T. Ouzounellis Kavlakonis
Date: 20th of January

Description: Flask App offering an intuitive UI for data input
"""

# using python 3
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
import alexa_service

app = Flask(__name__)
# Flask-WTF requires an enryption key - the string can be anything
app.config['SECRET_KEY'] = 'some?bamboozle#string-foobar'
# Flask-Bootstrap requires this line
Bootstrap(app)
# this turns file-serving to static, using Bootstrap files installed in env
# instead of using a CDN
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

# with Flask-WTF, each web form is represented by a class
# "NameForm" can change; "(FlaskForm)" cannot
# see the route for "/" and "index.html" to see how this is used
class urlForm(FlaskForm):
    url = StringField('Which URL do you want to summarize?', validators=[Required()])
    submit = SubmitField('Submit')

# define functions to be used by the routes (just one here)

# all Flask routes below

# two decorators using the same function
@app.route('/', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    # 'form' is the variable name used in this template: index.html
    form = urlForm()
    message = ""
    if form.validate_on_submit():
        url = form.url.data
        print(url)
        url = str(url)
        print(type(url))
        form.url.data = ""
        message = "Your URL was submitted! You can now activate the \
        Privacy Expert skill by saying \"Alexa, open Privacy Expert\""
        #make a call to the azure_qna backend to update the QnA Maker Knowledge Based according to questions generated from the URL.
        alexa_service.alexa_service(url)

    # notice that we don't need to pass name or names to the template
    return render_template('index.html', form=form, message=message)


# keep this as is
if __name__ == '__main__':
    app.run(debug=True)
