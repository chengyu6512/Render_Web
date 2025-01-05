from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm 
from wtforms import StringField, SubmitField, DateField, SelectField, IntegerField
from wtforms.validators import DataRequired, ValidationError

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask (__name__)
app. config['SECRET_KEY'] = 'loulin'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://my_hotel_47x0_user:u9OLqWszdCQIEOht2wrh9aH94rMckyv3@dpg-ctsfceq3esus73dpqgmg-a.oregon-postgres.render.com/my_hotel_47x0')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 關閉 SQLAlchemy 的變更追蹤

db = SQLAlchemy(app)


# Example room data (in a real application, this would come from a database)
rooms = [('101', 'Single Room'), ('102', 'SingleX Room'), ('103', 'Double Room'), ('201', 'Deluxe Room'), ('202', 'Super Deluxe'),('203', 'Executive Suite')]

class Guest(db.Model):
    guest_id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(255), nullable=False)
    contact_info = db.Column(db.String(255))
class Room(db.Model):
    room_number = db.Column(db.String(10), primary_key=True)
# other room fields...

class Booking(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.guest_id'), nullable=False)
    room_number = db.Column(db.Integer, db.ForeignKey('room.room_number'), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
# other booking fields...

class BookingForm (FlaskForm) :
    guest_name = StringField ( 'Your Name', validators= [DataRequired ()])
    room_number = SelectField ('Select A Room', choices=rooms, validators=[DataRequired ()])
    check_in_date = DateField ('Check-In Date', format='%Y-%m-%d', validators=[DataRequired ()])
    check_out_date = DateField('Check-Out Date',format='%Y-%m-%d', validators=[DataRequired()])
    contact_info = StringField('Contact Information', validators=[DataRequired()])
    submit = SubmitField('Book Now')

    def validate_check_out_date(self, field):
        if self.check_in_date.data and field.data <= self.check_in_date.data:
            raise ValidationError('Check-Out Date must be later than Check-In Date.')

class SearchForm(FlaskForm):
    booking_id = IntegerField('Booking ID', validators=[DataRequired()])
    submit = SubmitField('Search')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/room')
def room():
    return render_template('room.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/mybooking')
def mybooking():
    bookings = db.session.query(Booking, Guest, Room).join(Guest, Booking.guest_id == Guest.guest_id).join(Room, Booking.room_number == Room.room_number).all()
    return render_template('mybooking.html', bookings=bookings)

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    form = BookingForm()
    if form.validate_on_submit():
        new_guest = Guest(guest_name=form.guest_name.data, contact_info=form.contact_info.data)
        db.session.add(new_guest)
        db.session.flush()  # Flush to get the ID of the new guest
        new_booking = Booking(guest_id = new_guest.guest_id, room_number = form.room_number.data, check_in_date = form.check_in_date.data, check_out_date = form.check_out_date.data)
        db.session.add(new_booking)
        db.session.commit()
        return redirect(url_for('mybooking'))
    return render_template('booking.html', form = form)

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    booking_details = None
    if form.validate_on_submit():
        booking_id = form.booking_id.data
        booking_details = db.session.query(Booking, Guest, Room
        ).join(
            Guest, Booking.guest_id == Guest.guest_id
        ).join(
            Room, Booking.room_number == Room.room_number
        ).filter(Booking.booking_id == booking_id).first()
    return render_template('search.html', form=form, booking_details=booking_details)

if __name__ == '__main__':
    app.run(debug=True)