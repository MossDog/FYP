INSERT INTO Room (room_no, age)
VALUES (1, 20), (2,21), (3,20), (4, 34);

INSERT INTO Observation (room_no, bpm, temperature, fall, status)
VALUES (2, 60, 22, FALSE, 'green');
INSERT INTO Observation (room_no, bpm, temperature, fall, status)
VALUES (3, 65, 22, FALSE, 'orange');
INSERT INTO Observation (room_no, bpm, temperature, fall, status)
VALUES (4, 70, 24, FALSE, 'red');
INSERT INTO Observation (room_no, bpm, temperature, fall, status)
VALUES (1, 60, 25, FALSE, 'Normal');
INSERT INTO Observation (room_no, bpm, temperature, fall, status)
VALUES (1, 75, 26, FALSE, 'Normal');
INSERT INTO Observation (room_no, bpm, temperature, fall, status)
VALUES (1, 63, 25, FALSE, 'Normal');
INSERT INTO Observation (room_no, bpm, temperature, fall, status)
VALUES (1, 53, 23, FALSE, 'Normal');
INSERT INTO Observation (room_no, bpm, temperature, fall, status)
VALUES (1, 49, 23, FALSE, 'Normal');
INSERT INTO Observation (room_no, bpm, temperature, fall, status)
VALUES (1, 70, 22, FALSE, 'Normal');
INSERT INTO Observation (room_no, bpm, temperature, fall, status)
VALUES (1, 63, 24, FALSE, 'Normal');
INSERT INTO Observation (room_no, bpm, temperature, fall, status)
VALUES (1, 40, 17, TRUE, 'red');


SELECT * FROM Room;
SELECT * FROM Observation;