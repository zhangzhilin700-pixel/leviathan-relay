import mysql.connector
from datetime import datetime
import time

class LeviathanDBManager:
    def __init__(self, host="localhost", user="root", password="password", database="sensor_data"):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database
        }
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor()
            return True
        except mysql.connector.Error as err:
            print(f"資料庫連線錯誤: {err}")
            return False

    def insert_sensor_data(self, sensor_id, temperature, humidity):
        if not self.connection:
            if not self.connect():
                return False
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = "INSERT INTO sensor_data (sensor_id, timestamp, temperature, humidity) VALUES (%s, %s, %s, %s)"
        try:
            self.cursor.execute(query, (sensor_id, timestamp, temperature, humidity))
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            print(f"資料插入錯誤: {err}")
            return False

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
