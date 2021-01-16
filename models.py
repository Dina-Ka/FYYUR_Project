# Imports
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime
# from datetime import datetime, timedelt
from sqlalchemy.types import TypeDecorator, TIMESTAMP
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:scholarshipFWDudicity@localhost:5432/scholarshipFWDudicity"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    venue_name = db.Column(db.String(255))
    city = db.Column(db.String(120))
    venue_state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    seeking_artist = db.Column(db.String(120))
    website = db.Column(db.String(255))
    seeking_description = db.Column(db.String(255))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String)
    city = db.Column(db.String(120))
    venue_state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue =  db.Column(db.String(120))
    website =  db.Column(db.String(255))
    seeking_description = db.Column(db.String(255))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.String(255),db.ForeignKey('artist.id'))
    venue_id = db.Column(db.String(255),db.ForeignKey('venue.id'))
    start_time =db.Column(db.DateTime, default=datetime.datetime.utcnow)
    venue = relationship("venue")
    artist = relationship("artist")

