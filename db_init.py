from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SelectField, IntegerField
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\athon\\Documents\\roastly\\roastly.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Origin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)

class ProcessingMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)

class Bean(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    origin_id = db.Column(db.Integer, db.ForeignKey('origin.id'), nullable=False)
    processing_method_id = db.Column(db.Integer, db.ForeignKey('processing_method.id'), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return self.display_name

class RoastLevel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ordering = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)

class Roast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bean_id = db.Column(db.Integer, db.ForeignKey('bean.id'), nullable=False)
    starting_weight = db.Column(db.Integer, default=140, nullable=False)
    ending_weight = db.Column(db.Integer, default=-1, nullable=False)
    roast_level_id = db.Column(db.Integer, db.ForeignKey('roast_level.id'))
    duration = db.Column(db.Integer, default=-1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)

class RoastEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roast_id = db.Column(db.Integer, db.ForeignKey('roast.id'), nullable=False)
    elapsed_time = db.Column(db.Integer, nullable=False)
    temperature = db.Column(db.Integer, nullable=False)
    fan = db.Column(db.Integer, nullable=False)
    power = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

db.create_all()

# create user
admin = User(name='admin', password='admin')
db.session.add(admin)

# create origins
origins = [
    ('brazil', 'Brazil'), ('vietnam', 'Vietnam'), ('colombia', 'Colombia'), ('indonesia', 'Indonesia'), 
    ('ethiopia', 'Ethiopia'), ('honduras', 'Honduras'), ('india', 'India'), ('uganda', 'Uganda'), 
    ('mexico', 'Mexico'), ('guatemala', 'Guatemala'),  ('peru', 'Peru'), ('nicaragua', 'Nicaragua'), 
    ('china', 'China'), ('ivory_coast', 'Ivory Coast'), ('costa_rica', 'Costa Rica'), ('kenya', 'Kenya'), 
    ('papua_new_guinea', 'Papua New Guinea'), ('tanzania', 'Tanzania'), ('el_salvador', 'El Salvador'), ('ecuador', 'Ecuador'), 
    ('cameroon', 'Cameroon'), ('laos', 'Laos'), ('madagascar', 'Madagascar'), ('gabon', 'Gabon'), 
    ('thailand', 'Thailand'), ('venezuela', 'Venezuela'), ('dominican_republic', 'Dominican Republic'), 
    ('haiti', 'Haiti'), ('democratic_republic_of_the_congo', 'Democratic Republic of the Congo'), ('rwanda', 'Rwanda'), ('burundi', 'Burundi'), 
    ('philippines', 'Philippines'), ('togo', 'Togo'), ('guinea', 'Guinea'), ('yemen', 'Yemen'), ('cuba', 'Cuba'), 
    ('panama', 'Panama'), ('bolivia', 'Bolivia'), ('timor_leste', 'Timor Leste'), ('central_african_republic', 'Central African Republic'), 
    ('nigeria', 'Nigeria'), ('ghana', 'Ghana'), ('sierra_leone', 'Sierra Leone'), ('angola', 'Angola'), ('jamaica', 'Jamaica'), 
    ('paraguay', 'Paraguay'), ('malawi', 'Malawi'), ('trinidad_and_tobago', 'Trinidad and Tobago'), ('zimbabwe', 'Zimbabwe'), 
    ('liberia', 'Liberia'), ('zambia', 'Zambia')
]

for origin in origins:
    slug = origin[1].lower().replace(" ", "_")
    name = origin[1]
    o = Origin(name=name, slug=slug)
    db.session.add(o)

# create processing methods
processing_methods = ["Dried", "Washed", "Honey"]
for m in processing_methods:
    db.session.add(ProcessingMethod(name=m, slug=m.lower()))


# add roast levels
roast_levels = [
    (0, 'Cinnamon'), (1, 'Light'), (2, 'Medium'), (3, 'City Light'), (4, 'City'),
    (5, 'Full City'), (6, 'Vienna'), (7, 'French')
]

for r in roast_levels:
    db.session.add(RoastLevel(ordering=r[0], name=r[1]))

db.session.commit()