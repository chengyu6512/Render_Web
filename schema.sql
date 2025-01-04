-- schema.sql
CREATE TABLE room (
    room_number VARCHAR(10) PRIMARY KEY,
    room_type VARCHAR(50),
    price_per_night DECIMAL(10, 2),
    max_guests INT
);

CREATE TABLE guest (
    guest_id SERIAL PRIMARY KEY,
    guest_name VARCHAR(255) NOT NULL,
    contact_info VARCHAR(255)
);

CREATE TABLE booking (
    booking_id SERIAL PRIMARY KEY,
    guest_id INT REFERENCES guest(guest_id),
    room_number VARCHAR(10) REFERENCES room(room_number),
    check_in_date DATE,
    check_out_date DATE,
    total_price DECIMAL(10, 2),
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);