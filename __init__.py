from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm
from sqlalchemy.sql.functions import current_timestamp
from wtforms import StringField, RadioField, SelectField, IntegerField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func
from datetime import datetime
import os
import math

# TODO:
## Write migration to store elapsed time as int
## Write migration to store temperature as int
## Allow settings for temp as celsius
## convenience function for elapsed time int to label

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\athon\\Documents\\roastly\\roastly.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)

def convert_elapsed_time(elapsed_time):
    minute, second = elapsed_time.split(":")
    minute = int(minute)
    second = int(second)
    return (minute * 60) + second

# MODELS
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

    def __str__(self):
        return self.name

class RoastLevel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ordering = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __str__(self):
        return self.name

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

# FORMS
class BeanForm(FlaskForm):
    bean_name = StringField('Bean Name:')

    origin_choices = [(origin.id, origin.name) for origin in Origin.query.all()]
    origin_id = SelectField('Origin:', choices=origin_choices)

    processing_method = [(method.id, method.name) for method in ProcessingMethod.query.all()]
    processing_method_id = RadioField('Processing Method:', choices=processing_method)

class StartRoastForm(FlaskForm):
    bean_id = QuerySelectField(query_factory=lambda: Bean.query)
    starting_weight = IntegerField("Starting Weight (g):", default=140)

class EndRoastForm(FlaskForm):
    roast_level = QuerySelectField(query_factory=lambda: RoastLevel.query)
    ending_weight = IntegerField("Ending Weight (g):", default=120)

# ROUTES
@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("home.html")

@app.route("/bean", methods=['GET'])
def bean():
    beans = Bean.query\
            .join(Origin)\
            .join(ProcessingMethod)\
            .join(Roast)\
            .filter(Roast.ending_weight > -1)\
            .with_entities(
                Bean.id,
                Bean.name,
                Origin.name.label('origin'),
                ProcessingMethod.name.label('method'),
                func.count(Bean.name).label('count_roasts')
            )\
            .group_by(Bean.id)\
            .all()
    
    return render_template("bean.html", beans=beans)

@app.route("/bean/new/", methods=['GET', 'POST'])
def new_bean():
    if request.method == 'GET':
        form = BeanForm()
        return render_template("new_bean.html", form=form)
    else:
        name = request.form.get('bean_name')
        origin_id = request.form.get('origin_id')
        processing_method_id = request.form.get('processing_method_id')
        bean = Bean(
            name = name,
            slug = name.lower().strip().replace(" ", "_"),
            origin_id = origin_id,
            processing_method_id = processing_method_id
        )
        db.session.add(bean)
        db.session.commit()
        return render_template("home.html")

@app.route("/bean/delete/<bean_id>", methods=['GET'])
def delete_bean(bean_id):
    if request.method == 'GET':
        bean = Bean.query.filter_by(id=bean_id).first()
        db.session.delete(bean)
        db.session.commit()
        return redirect('/bean')

@app.route("/roast")
def roast():
    roasts = Roast.query\
        .join(Bean)\
        .join(RoastLevel)\
        .add_columns(
            Roast.id, Roast.created_at, Bean.name.label('bean_name'),
            RoastLevel.name.label("roast_level"), Roast.duration,
            Roast.starting_weight, Roast.ending_weight).all()

    return render_template("roast.html", roasts=roasts)

@app.route("/roast/new", methods=['GET', 'POST'])
def new_roast():
    if request.method == 'GET':
        form = StartRoastForm()
        return render_template("new_roast.html", form=form)
    else:
        roast = Roast(
            user_id = 1,
            bean_id = request.form['bean_id'],
            starting_weight = int(request.form['starting_weight'])
        )
        db.session.add(roast)
        db.session.commit()
        db.session.flush()
        return redirect(f"/roast/diary/{roast.id}")

@app.route("/roast/delete/<roast_id>", methods=['GET'])
def delete_roast(roast_id):
    roast = Roast.query.filter_by(id=roast_id).first()
    db.session.delete(roast)
    db.session.commit()
    return redirect('/roast')

@app.route("/roast/diary/<roast_id>", methods=['GET'])
def roast_diary(roast_id):
    return render_template(f"roast_diary.html")

@app.route("/roast/<roast_id>", methods=['GET'])
def get_roast(roast_id):
    events = RoastEvent.query.filter_by(roast_id=roast_id).order_by(RoastEvent.elapsed_time).all()
    max_time = convert_elapsed_time(events[-1].elapsed_time)
    labels = []
    for second in range(max_time + 1):
        minutes = math.floor(second / 60)
        seconds = second % 60
        second_formatted = f"{minutes}:{seconds}"
        labels.append(second_formatted)
    roast_events = {
        "labels": labels,
        "temperature": [],
        "power": [],
        "fan": []
    }
    last_timestamp = 0
    for event in events:
        ts = convert_elapsed_time(event.elapsed_time)
        if ts == last_timestamp and len(roast_events['temperature']) != 0:
            roast_events['temperature'].pop()
            roast_events['power'].pop()
            roast_events['fan'].pop()
        else:
            diff = ts - last_timestamp
            for x in range(diff):
                roast_events['temperature'].append(event.temperature[:-2])
                roast_events['power'].append(event.power)
                roast_events['fan'].append(event.fan)
        last_timestamp = ts

    return render_template(f"roast_stats.html", roast=roast_events)

@app.route("/roast/finish/<roast_id>", methods=['GET', 'POST'])
def finish_roast(roast_id):
    if request.method == 'GET':
        form = EndRoastForm()
        return render_template("end_roast.html", form=form, roast_id=roast_id)
    else:
        roast_level_id = request.form['roast_level']
        ending_weight = request.form['ending_weight']
        roast = Roast.query.filter_by(id=roast_id).first()
        roast_event = RoastEvent.query\
            .filter_by(roast_id=roast_id)\
            .order_by(RoastEvent.created_at.desc())\
            .first()
        duration_str = roast_event.elapsed_time
        duration_list = duration_str.split(":")
        duration = int(duration_list[0]) * 60 + int(duration_list[1])
        roast.roast_level_id = roast_level_id
        roast.ending_weight = ending_weight
        roast.duration = duration
        db.session.commit()
        return redirect(f"/roast")

@app.route("/roast/diary/api/log_event/")
def log_event():
    roast_id = request.args.get('roast_id')
    elapsed_time = request.args.get('timerLabel')
    temperature = request.args.get('temperatureLabel')
    fan = request.args.get('fanLabel')
    power = request.args.get('powerLabel')
    event = RoastEvent(
        roast_id = roast_id,
        elapsed_time = elapsed_time,
        temperature = temperature,
        fan = fan,
        power = power
    )
    db.session.add(event)
    db.session.commit()
    return request.args

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)