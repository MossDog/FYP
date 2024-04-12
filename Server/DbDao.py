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


    def add_room(self, room_no, age):
        self.connect()
        query = "INSERT INTO Room (room_no, age) VALUES (%s, %s)"
        data = (room_no, age)
        self.cursor.execute(query, data)
        self.conn.commit()
        self.disconnect()

    def get_room_by_no(self, room_no):
        self.connect()
        query = "SELECT * FROM Room WHERE room_no = %s"
        self.cursor.execute(query, (room_no,))
        room = self.cursor.fetchone()
        self.disconnect()
        return room

    def add_observation(self, room_no, bpm, temp, fall, status):
        self.connect()
        query = "INSERT INTO Observation (room_no, bpm, temperature, fall, status) VALUES (%s, %s, %s, %s, %s)"
        data = (room_no, bpm, temp, fall, status)
        self.cursor.execute(query, data)
        self.conn.commit()
        self.disconnect()