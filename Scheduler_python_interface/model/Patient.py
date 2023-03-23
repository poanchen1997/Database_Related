import pymssql
from db.ConnectionManager import ConnectionManager
from util.Util import Util
import sys
sys.path.append("../util/*")
sys.path.append("../db/*")


class Patient:
    def __init__(self, username, password=None, salt=None, hash=None):
        self.username = username
        self.password = password
        self.salt = salt
        self.hash = hash

    def get_username(self):
        return self.username

    def get_salt(self):
        return self.salt

    def get_hash(self):
        return self.hash

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_patient = "INSERT INTO Patients VALUES (%s, %s, %s)"
        try:
            cursor.execute(add_patient, (self.username, self.salt, self.hash))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()

    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_patient_details = "SELECT Salt, Hash FROM Patients WHERE Username = %s"
        try:
            cursor.execute(get_patient_details, self.username)
            for row in cursor:
                curr_salt = row['Salt']
                curr_hash = row['Hash']
                calculated_hash = Util.generate_hash(self.password, curr_salt)
                if not curr_hash == calculated_hash:
                    # print("Incorrect password")
                    cm.close_connection()
                    return None
                else:
                    self.salt = curr_salt
                    self.hash = calculated_hash
                    cm.close_connection()
                    return self
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()
        return None

    # check availability with parameter date d
    def check_availability(self, d):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        search_availability = "SELECT DISTINCT Username FROM Caregivers WHERE Username not in (SELECT DISTINCT Username FROM Availabilities WHERE Time != %s)"
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(search_availability, d)
            caregiver_available = []
            for row in cursor:
                caregiver_available.append(row['Username'])
            return caregiver_available
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()
