-- Person table
CREATE TABLE IF NOT EXISTS Room (
    room_no INT PRIMARY KEY,
    person_name VARCHAR(255) NOT NULL,
);

CREATE TABLE IF NOT EXISTS Observation (
    observation_id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT,
    bpm INT,
    bpm_avg INT,
    temperature FLOAT,
    time_observed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(255),
    FOREIGN KEY (person_id) REFERENCES Person(person_id)
);

INSERT INTO observation (room_id, pulse, temperature_C, status)
VALUES (1, 75, 23.5, 'normal');