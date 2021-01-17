#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask import Flask, render_template, request, Response, flash, redirect, url_for
import json
import dateutil.parser
import babel
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
from datetime import timedelta
import _datetime
from datetime import datetime as dt
import numpy as np



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

@app.template_filter()
def format_datetime(value, format='medium'):
    if format == 'full':
        format="EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="EE dd.MM.y HH:mm"
    return babel.dates.format_datetime(value, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  city_states = {}
  city_statesQueries =  db.session.query(venue).with_entities(venue.city,venue.venue_state).group_by(venue.city,venue.venue_state).all()
  for city_state in city_statesQueries:
    x = city_state.venue_state + '_' + city_state.city
    city_states[x] = {
      "city": city_state.city,
      "state": city_state.venue_state,
      "venues": []
    }
  print(city_states)
  venues = venue.query.all()
  for eachvenue in venues:
    num_upcoming_shows = 0
    shows =  db.session.query(show).filter(eachvenue.id == show.venue_id,(show.start_time)<dt.now()).all()
    num_upcoming_shows= len(shows)
    y = eachvenue.venue_state+'_'+eachvenue.city
    city_states[y]['venues'].append({
      "id": eachvenue.id,
      "name": eachvenue.venue_name,
      "num_upcoming_shows": num_upcoming_shows
    })

  print(city_states)
  data = []

  for index in city_states:
    print(index)
    cityStateJson = city_states[index];
    data.append(cityStateJson)
  print(data)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    # search_term
    if request.method == 'POST':
      search_term = request.form.get('search_term')
      search = "%{}%".format(search_term)
      print(search)
      venues=  venue.query.filter(venue.venue_name.ilike(search))
      print(venues)
      response = {
        "data":[],
        "count":0
      }
      for eachvenue in venues:
        response['data'].append({
          "id": eachvenue.id,
          "name": eachvenue.venue_name
        })
      count = len(response['data'])
      response['count']= count

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venueData = db.session.query(venue).filter(venue.id == venue_id).all()
  for venues in venueData:
      venues = venues

  past_shows = db.session.query(show, artist , venue).with_entities(
            artist.id.label('artist_id'),
            artist.artist_name,
            artist.image_link.label('artist_image_link'),
            show.start_time
            ).join(artist,
                   artist.id == show.artist_id).join(
            venue, show.venue_id == venue.id).filter(venue.id==venue_id,(show.start_time)<dt.now()).all()
  past_shows_count = len(past_shows)

  upcoming_shows =  db.session.query(show, artist , venue).with_entities(
            artist.id.label('artist_id'),
            artist.artist_name,
            venue.image_link.label('artist_image_link'),
            show.start_time
            ).join(artist,
                   artist.id == show.artist_id).join(
            venue, show.venue_id == venue.id).filter(venue.id==venue_id,(show.start_time)>dt.now()).all()

  upcoming_shows_count = len(upcoming_shows)
  return render_template('pages/show_venue.html', venueData=venues,past_shows=past_shows,past_shows_count=past_shows_count,upcoming_shows_count=upcoming_shows_count,upcoming_shows=upcoming_shows)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # TODO: on unsuccessful db insert, flash an error instead.

  if request.method == 'POST':
    venue_name = request.form.get('name')
    city = request.form.get('city')
    venue_state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    genres = request.form.getlist('genres')
    delim = ','
    genres = delim.join(map(str, genres))
    facebook_link = request.form.get('facebook_link')
    seeking_artist = request.form.get('seeking_artist')
    website = request.form.get('website')
    seeking_description = request.form.get('seeking_description')
  try:
    create_venue_submission = venue(
      venue_name=venue_name,
      city=city,
      venue_state=venue_state,
      address=address,
      phone=phone,
      image_link=image_link,
      genres=genres,
      facebook_link=facebook_link,
      seeking_artist=seeking_artist,
      website=website,
      seeking_description=seeking_description
    )
    db.session.add(create_venue_submission)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(artist).with_entities(artist.id,artist.artist_name.label('name')).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  if request.method == 'POST':
      search_term = request.form.get('search_term')
      search = "%{}%".format(search_term)
      artists=  artist.query.filter(artist.artist_name.ilike(search))
      print(artists)
      response = {
        "data":[],
        "count":0
      }
      for eachartist in artists:
        response['data'].append({
          "id": eachartist.id,
          "name": eachartist.artist_name
        })
      count = len(response['data'])
      response['count']= count
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the venues table, using artist_id
  artistData = db.session.query(artist).filter(artist.id == artist_id).all()
  for artists in artistData:
      artists = artists

  past_shows = db.session.query(show, venue, artist).with_entities(
            venue.id.label('venue_id'),
            venue.venue_name,
            venue.image_link.label('venue_image_link'),
            show.start_time
            ).join(venue,
                   venue.id == show.venue_id).join(
            artist, show.artist_id == artist.id).filter(artist.id==artist_id,(show.start_time)<dt.now()).all()
  past_shows_count = len(past_shows)

  upcoming_shows =  db.session.query(show, venue, artist).with_entities(
            venue.id.label('venue_id'),
            venue.venue_name,
            venue.image_link.label('venue_image_link'),
            show.start_time
            ).join(venue,
                   venue.id == show.venue_id).join(
            artist, show.artist_id == artist.id).filter(artist.id==artist_id,(show.start_time)>dt.now()).all()

  upcoming_shows_count = len(upcoming_shows)

  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artistData=artists, past_shows=past_shows ,past_shows_count=past_shows_count,upcoming_shows=upcoming_shows,upcoming_shows_count=upcoming_shows_count)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  if request.method == 'POST':
    artist_name = request.form.get('name')
    city = request.form.get('city')
    venue_state = request.form.get('state')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    genres = request.form.getlist('genres')
    delim = ','
    genres = delim.join(map(str, genres))
    facebook_link = request.form.get('facebook_link')
    seeking_venue = request.form.get('seeking_venue')
    website = request.form.get('website')
    seeking_description = request.form.get('seeking_description')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  try:
    create_artist_submission = artist(
      artist_name=artist_name,
      city=city,
      venue_state=venue_state,
      phone=phone,
      image_link=image_link,
      genres=genres,
      facebook_link=facebook_link,
      seeking_venue = seeking_venue,
      website = website,
      seeking_description = seeking_description
    )
    db.session.add(create_artist_submission)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
     flash('An error occurred. Artist ' +request.form['name']  + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = db.session.query(show, venue, artist).with_entities(
            venue.id.label('venue_id'),
            venue.venue_name,
            artist.id.label('artist_id'),
            artist.artist_name,
            artist.image_link,
            show.start_time
            ).join(venue,
                   venue.id == show.venue_id).join(
            artist, show.artist_id == artist.id).all()

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  if request.method == 'POST':
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')

  try:
    create_show_submission = show(
      artist_id=artist_id,
      venue_id=venue_id,
      start_time=start_time
    )
    db.session.add(create_show_submission)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()


  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#
# Start app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=1010, debug=True, threaded=True)