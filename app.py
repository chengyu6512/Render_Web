from flask import Flask, render_template, request, redirect, url_for  # 引入 Flask 所需的基本模組
from flask_wtf import FlaskForm  # 引入 Flask-WTF 以處理表單
from wtforms import StringField, SubmitField, DateField, SelectField, ValidationError  # 引入 WTForms 的表單字段
from wtforms.validators import DataRequired  # 引入 WTForms 的驗證器
from flask_sqlalchemy import SQLAlchemy  # 引入 SQLAlchemy，用於操作資料庫
from datetime import date  # 用於日期驗證
import os




app = Flask(__name__)  # 建立 Flask 應用程式實例
app.config['SECRET_KEY'] = 'YourSecretKey'  # 用於表單 CSRF 保護的密鑰
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 關閉 SQLAlchemy 的變更追蹤
# app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {  # 設定資料庫連接池
#     'pool_pre_ping': True,  # 確保連接池中的連接可用
#     'pool_recycle': 280  # 每隔 280 秒回收連接
# }

db = SQLAlchemy(app)  # 初始化資料庫

# Example room data (in a real application, this would come from a database)
rooms = [
    ('101', 'Single Room'),
    ('102', 'Double Room'),
    ('103', 'Deluxe Room')
]

# 定義資料庫模型
class Guest(db.Model):  # 訪客資料表
    guest_id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(255), nullable=False)
    contact_info = db.Column(db.String(255))

class Room(db.Model):  # 房間資料表
    room_number = db.Column(db.String(10), primary_key=True)
    # other room fields...
    
class Booking(db.Model):  # 訂房資料表
    booking_id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.guest_id'), nullable=False)
    room_number = db.Column(db.Integer, db.ForeignKey('room.room_number'), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    # other booking fields...

# 定義訂房表單
class BookingForm(FlaskForm):
    guest_name = StringField('Guest Name', validators=[DataRequired()])
    room_number = SelectField('Room Number', choices=rooms, validators=[DataRequired()])
    check_in_date = DateField('Check-In Date', format='%Y-%m-%d', validators=[DataRequired()])
    check_out_date = DateField('Check-Out Date', format='%Y-%m-%d', validators=[DataRequired()])
    contact_info = StringField('Contact Information', validators=[DataRequired()])
    submit = SubmitField('Book Now')

    # 驗證入住日期
    def validate_check_in_date(self, field):
        if field.data < date.today():  # 入住日期不能是過去日期
            raise ValidationError('Check-In Date cannot be in the past.')

    # 驗證退房日期
    def validate_check_out_date(self, field):
        if field.data <= self.check_in_date.data:  # 退房日期必須晚於入住日期
            raise ValidationError('Check-Out Date must be after Check-In Date.')


# 首頁路由
@app.route('/')
def index():
    # 查詢所有訂房資料並關聯訪客資訊
    bookings = db.session.query(Booking, Guest).join(Guest, Booking.guest_id == Guest.guest_id).all()
    # 整理數據供模板使用
    booking_data = [
        {
            'guest_name': booking.Guest.guest_name,
            'room_number': booking.Booking.room_number,
            'check_in_date': booking.Booking.check_in_date,
            'check_out_date': booking.Booking.check_out_date,
        }
        for booking in bookings
    ]
    return render_template('index.html', bookings=booking_data)  # 渲染首頁模板

# 訂房頁面路由
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    form = BookingForm()
    if form.validate_on_submit():  # 表單驗證成功
        # 新增訪客資料
        new_guest = Guest(guest_name=form.guest_name.data, contact_info=form.contact_info.data)
        db.session.add(new_guest)
        db.session.flush() # Flush to get the ID of the new guest

        # 新增訂房資料
        new_booking = Booking(
            guest_id = new_guest.guest_id,
            room_number = form.room_number.data,
            check_in_date = form.check_in_date.data,
            check_out_date = form.check_out_date.data
        )
        db.session.add(new_booking)
        db.session.commit()  # 提交變更

        for field in form:
            print(f"{field.name}: {field.data}")
        return redirect(url_for('index'))  # 重新導向首頁
    return render_template('booking.html', form=form)  # 渲染訂房頁面

# 清除所有訂房資料
@app.route('/clear_bookings', methods=['POST'])
def clear_bookings():
    try:
        # 刪除所有的 Booking 和 Guest 資料
        db.session.query(Booking).delete()
        db.session.query(Guest).delete()
        db.session.commit()  # 提交變更
        db.session.expunge_all()  # 清除會話緩存
        db.session.remove()  # 重置會話
    except Exception as e:
        db.session.rollback()  # 回滾變更
        print(f"Error clearing bookings: {e}")
    return redirect(url_for('index'))  # 重新導向首頁



if __name__ == '__main__':
    app.run(debug=True)  # 啟動 Flask 應用程式