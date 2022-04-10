# To run, modify last 2 environment variables in .flaskenv
import requests
import sys
import json
from dotenv import load_dotenv
from os import environ
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment

class SearchForm(FlaskForm):
    keyword = StringField('Keyword', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    submit = SubmitField('Search')

# force loading of environment variables
load_dotenv('.flaskenv')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'csc330 spring 2022'
bootstrap = Bootstrap(app)
moment = Moment(app)

# Read values from .flaskenv
API_KEY = environ.get('API_KEY')
API_HOST = environ.get('API_HOST')
API_URL = environ.get('API_URL')
EMAIL = environ.get('EMAIL')

# Place holder for job result data
class JobInfo:
    def __JobInfo__(title, URI, location):
        self.title = title
        self.URI = URI
        self.location = location


@app.route('/search', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def search():
    headers =   {'Host': API_HOST,
                'User-Agent': EMAIL,
                'Authorization-Key': API_KEY}
    form = SearchForm()
    if form.validate_on_submit():
        city = form.city.data + '%20' + form.state.data
        keyword = form.keyword.data
        full_URL = f'{API_URL}?LocationName={city}&Keyword={keyword}&ResultsPerPage=50'
        response = requests.get(full_URL, headers = headers)

        if response.status_code == 200:
            print('Success!', file = sys.stdout)
        elif response.status_code == 404:
            print('Not found.', file=sys.stdout)

        # Extract title, location and URI from API and package as a list of
        # objects (job_results)
        response_json = response.json()
        job_results = []
        for item in response_json['SearchResult']['SearchResultItems']:
            job = JobInfo()
            job.URI = item['MatchedObjectDescriptor']['PositionURI']
            job.title = item['MatchedObjectDescriptor']['PositionTitle']
            job.location = item['MatchedObjectDescriptor']['PositionLocationDisplay']
            job_results.append(job)

        # display search results as an HTML table
        return render_template('show_results.html', job_results=job_results)
    else:
        return render_template('search.html', form=form)
