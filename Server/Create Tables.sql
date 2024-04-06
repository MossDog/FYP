DROP TABLE IF EXISTS Observation;
DROP TABLE IF EXISTS Room;

CREATE TABLE IF NOT EXISTS Room (
    room_no INT PRIMARY KEY,
    age INT NOT NULL
);

CREATE TABLE IF NOT EXISTS Observation (
    observation_id INT AUTO_INCREMENT PRIMARY KEY,
    room_no INT,
    bpm INT,
    temperature FLOAT,
    fall BOOLEAN,
    time_observed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(255),
    FOREIGN KEY (room_no) REFERENCES Room(room_no)
);
