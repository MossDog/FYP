import mysql.connector

class DbDao:

    def __init__(self) -> None:
        self.host = "localhost"
        self.username = "mossdog"
        self.password = "mossdog"
        self.database = "DB"
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.username,
            password=self.password,
            database=self.database
        )
        self.cursor = self.conn.cursor()

    def disconnect(self):
        if self.conn:
            self.conn.close()
        if self.cursor:
            self.cursor.close()

    def add_room(self, room_no, person_name, room_number):
        self.connect()
        query = "INSERT INTO Room (room_no, person_name) VALUES (%s, %s)"
        data = (person_name, room_number)
        self.cursor.execute(query, data)
        self.conn.commit()
        self.disconnect()

    def get_room_by_id(self, room_no):
        self.connect()
        query = "SELECT * FROM Room WHERE room_no = %s"
        self.cursor.execute(query, (room_no,))
        room = self.cursor.fetchone()
        self.disconnect()
        return room

    def add_observation(self, room_no, bpm, bpm_avg, temperature, status):
        self.connect()
        query = "INSERT INTO Observation (room_no, bpm, bpm_avg, temperature, status) VALUES (%s, %s, %s, %s, %s)"
        data = (room_no, bpm, bpm_avg, temperature, status)
        self.cursor.execute(query, data)
        self.conn.commit()
        self.disconnect()

    def get_observations_by_room_no(self, room_no):
        self.connect()
        query = "SELECT * FROM Observation WHERE room_no = %s"
        self.cursor.execute(query, (room_no,))
        observations = self.cursor.fetchall()
        self.disconnect()
        return observations
    
    def get_observations_by_room_and_time_range(self, room_no, start_time, end_time):
        self.connect()
        query = "SELECT * FROM Observation WHERE room_no = %s AND time_observed BETWEEN %s AND %s"
        self.cursor.execute(query, (room_no, start_time, end_time))
        observations = self.cursor.fetchall()
        self.disconnect()
        return observations