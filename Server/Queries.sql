INSERT INTO Room (room_no, age)
VALUES (1, 20), (2,21), (3,20), (4, 34);

INSERT INTO Observation (room_no, bpm, temperature, fall, status)
VALUES (1, 80, 22, FALSE, 'Normal'), (2, 80, 22, FALSE, 'Normal'), (3, 80, 22, FALSE, 'Normal');


SELECT * FROM Room;
SELECT * FROM Observation;