from flask import Flask, render_template, flash, request, send_file
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from scrape import *
import subprocess
 
# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
 
class ReusableForm(Form):
    url = TextField('URL:', validators=[validators.DataRequired()])
    tagged_threshold = TextField('Tagged Threshold:', validators=[validators.DataRequired()])
    followers_threshold = TextField('Followers Threshold:', validators=[validators.DataRequired()])
    following_threshold = TextField('Following Threshold:', validators=[validators.DataRequired()])
    posts_threshold = TextField('Posts Threshold:', validators=[validators.DataRequired()])
 
@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)
    if request.method == 'POST':
        url = request.form['url']
        tagged_threshold = request.form['tagged_threshold']
        followers_threshold = request.form['followers_threshold']
        following_threshold = request.form['following_threshold']
        posts_threshold = request.form['posts_threshold']
 
        if form.validate():
            # Save the comment here.
            flash("url = "+url+"\ntagged_threshold = "+tagged_threshold+"\nfollowers_threshold = "+
            followers_threshold+"\nfollowing_threshold = "+following_threshold+"\nposts_threshold = "+posts_threshold)
            find_winner(str(url), int(tagged_threshold), int(followers_threshold), int(following_threshold), int(posts_threshold))
            time.sleep(2)
            return send_file('results.csv',
                            mimetype='text/csv',
                            attachment_filename='results.csv',
                            as_attachment=True)
        else:
            flash('All the form fields are required. ')
 
    return render_template('hello.html', form=form)

 
if __name__ == "__main__":
    app.run()