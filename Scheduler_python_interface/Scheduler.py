from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    """
    TODO: Part 1
    """
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]

    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    patient = Patient(username, salt=salt, hash=hash)

    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user", username)


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def find_all_vaccine_available():
    # return all the available vaccines in dictionary form
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    search_vaccines = "SELECT * FROM Vaccines WHERE Doses > 0"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(search_vaccines)
        vaccine_available = {}
        for row in cursor:
            vaccine_available[row['Name']] = row['Doses']
        return vaccine_available
    except pymssql.Error:
        raise
    finally:
        cm.close_connection()


def vaccine_still_in_stock(v_name):
    # return how many available dose for "v_name"
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    search_vaccines = "SELECT * FROM Vaccines WHERE Name = %s"
    try:
        cursor.execute(search_vaccines, v_name)
        vaccine_exist = None
        for row in cursor:
            vaccine_exist = row['Doses']
        if vaccine_exist == None or vaccine_exist == 0:
            return 0
        return vaccine_exist
    except pymssql.Error:
        raise
    finally:
        cm.close_connection()


def check_appointment_id():
    # return the biggest appointment id right now
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    check_biggest_id = "SELECT MAX(id) from Appointments"
    try:
        cursor.execute(check_biggest_id)
        row = cursor.fetchone()
        if row[0] == None:
            return 0
        return row[0]
    except pymssql.Error:
        raise
    finally:
        cm.close_connection()


def login_patient(tokens):
    """
    TODO: Part 1
    """
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
    # check 1: check there at least one type of user is logined
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
        # there is no possibility to have both caregiver and patient login at the same time,
        # because there is a check when you login as each position.
    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    try:
        d = datetime.datetime(year, month, day)
        if current_caregiver is None:
            res = current_patient.check_availability(d)
        else:
            res = current_caregiver.check_availability(d)
    except pymssql.Error as e:
        print("search Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when searching availability")
        print("Error:", e)
        return

    # print all the caregiver name if successfully search
    print(f"For {month}/{day}/{year}, we have the following caregivers:")
    for c in res:
        print(c, end=" ")
    print()
    print()  # for makeing it more pretty
    all_valid_vaccine = find_all_vaccine_available()
    print("And now we have the following vaccines available:")
    for a, b in all_valid_vaccine.items():
        print(f"{b} dose(s) of vaccine {a}", end=" ")
    print()


def reserve(tokens):
    """
    TODO: Part 2
    """
    # reserve <date> <vaccine>
    # check 1: if there is no person login or the person who login is caregiver
    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return
    elif current_patient is None:
        print("Please login as a patient!")
        return

    # check 2: if the tokens is not having date or vaccines
    if len(tokens) != 3:
        print("Please try again! -- tokens length issue.")
        return

    date = tokens[1]
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    try:
        d = datetime.datetime(year, month, day)
        available_caregiver = current_patient.check_availability(d)

        # if there are no available caregiver
        if len(available_caregiver) == 0:
            print("No Caregiver is available!")
            return
        # if the "vaccine" is out of stock
        if vaccine_still_in_stock(tokens[2]) == 0:
            print(f"The vaccine {tokens[2]} is now run out of stock!")
            return

        available_caregiver = sorted(available_caregiver)
        next_appointment_id = check_appointment_id() + 1
        upload_appointment_and_availability(
            next_appointment_id, available_caregiver[0], current_patient.username, tokens[2], d)
        print(
            f"Appointment ID: {next_appointment_id}, Caregiver username: {available_caregiver[0]}")

    except pymssql.Error as e:
        print("Reserved Appointment Failed")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when reserving appointment")
        print("Error:", e)
        return
    print("Appointment Reserved!")


def upload_appointment_and_availability(id, caregiver, patient, vaccine_name, d):
    # upload the appointment to the database
    # upload the availability in order not to duplicated reserved
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    # decrease "vaccine" for 1 to correctly store the new number of doses.
    curr_available_dose = vaccine_still_in_stock(vaccine_name)
    vaccine = Vaccine(vaccine_name, curr_available_dose)
    vaccine.decrease_available_doses(1)

    # upload Availability and Appointments
    # add the tuple in Availabilities
    add_availability = "INSERT INTO Availabilities VALUES (%s, %s)"
    # add the tuple in Appointments
    add_appointment = "INSERT INTO Appointments VALUES (%d, %s, %s, %s, %s)"
    try:
        cursor.execute(add_availability, (d, caregiver))
        cursor.execute(add_appointment,
                       (id, caregiver, patient, vaccine_name, d))
        conn.commit()
    except pymssql.Error:
        print("Error when uploading appointment and availability.")
        raise
    finally:
        cm.close_connection()


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    # cancel <appointment_id>

    # check 1: if the token length is not correct
    if len(tokens) != 2:
        print("Please check the operation commend!")
        return
    # check 2: check the appointment id is now existing
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    check_id = "SELECT * FROM Appointments WHERE id = %s"
    try:
        cursor.execute(check_id, tokens[1])
        test_id = None
        for row in cursor:
            test_id = row['id']
        if (test_id == None):
            print("The appointment has been canceled or not been reserved.")
    except pymssql.Error:
        print("Error when checking 2")
        raise

    # check 3: check you're the one in the appointment, i.e. only caregiver and patient in the appointment able to cancel the appointment
    if not current_caregiver and not current_patient:
        print("Please login first!")
        return

    try:
        cursor.execute(check_id, tokens[1])
        relative_caregiver, relative_patient = None, None
        for row in cursor:
            relative_caregiver = row['Username_c']
            relative_patient = row['Username_p']
        if (not current_patient and current_caregiver.username != relative_caregiver) or (not current_caregiver and current_patient.username != relative_patient):
            print("You don't have the permission to change the appointment!")
            print("Please login as the relative caregiver or patient.")
            return
    except pymssql.Error:
        print("Error when checking 3")
        raise

    # before removing those tuple, first record them
    appointment_detail = []  # id, username_c, username_p, vaccine_name, date
    try:
        cursor.execute(check_id, tokens[1])
        for row in cursor:
            appointment_detail.append(row['id'])
            appointment_detail.append(row['Username_c'])
            appointment_detail.append(row['Username_p'])
            appointment_detail.append(row['Name'])
            appointment_detail.append(row['date'])
    except pymssql.Error:
        print("Error when recording the appointment detail")
        raise
    # remove the appointment
    remove_appointment = "DELETE FROM Appointments WHERE id = %s"
    try:
        cursor.execute(remove_appointment, tokens[1])
        conn.commit()
    except pymssql.Error:
        print("Error when removing the appointment")
        raise
    # free the caregiver (availability)
    remove_availability = "DELETE FROM Availabilities WHERE Time = %s AND Username = %s"
    try:
        cursor.execute(remove_availability,
                       (appointment_detail[4], appointment_detail[1]))
        conn.commit()
    except pymssql.Error:
        print("Error when free the caregiver")
        raise
    # available dose plus 1 (vaccine)
    search_available_vaccine = "SELECT * FROM Vaccines WHERE Name = %s"
    try:
        cursor.execute(search_available_vaccine, appointment_detail[3])
        vaccine_exist = None
        for row in cursor:
            vaccine_exist = row['Doses']
        if vaccine_exist == None:
            print("No such vaccine!!")
    except pymssql.Error:
        print("Error when checking the information of the vaccine")
        raise
    finally:
        cm.close_connection()

    current_v = Vaccine(appointment_detail[3], vaccine_exist)
    current_v.increase_available_doses(1)
    # after do the above, show the person's whole schedule
    print(f"After removing appointment {tokens[1]}, ")
    show_appointments(["show_appointments"])


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    '''
    TODO: Part 2
    '''
    # check 1: you add words that no needed
    if len(tokens) != 1:
        print("Please adjust the comment without any arguments!")
        return
    # check 2: not login
    if not current_caregiver and not current_patient:
        print("Please login first!")
        return
    elif not current_patient:  # login as an caregiver
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        search_commend = "SELECT id, Name, date, Username_p FROM Appointments WHERE Username_c = %s ORDER BY id"
        try:
            cursor.execute(search_commend, current_caregiver.username)
            print(
                f"{current_caregiver.username} now have the following appointments:\n")
            print("appointment_ID | vaccine_name | date | patient_name")
            for row in cursor:
                print(row['id'], row['Name'], row['date'], row['Username_p'])

        except pymssql.Error:
            raise
        finally:
            cm.close_connection()
    elif not current_caregiver:  # login as an patient
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        search_commend = "SELECT id, Name, date, Username_c FROM Appointments WHERE Username_p = %s ORDER BY id"
        try:
            cursor.execute(search_commend, current_patient.username)
            print(
                f"{current_patient.username} now has the following appointments:\n")
            print("appointment_ID | vaccine_name | date | caregiver_name")
            for row in cursor:
                print(row['id'], row['Name'], row['date'], row['Username_c'])

        except pymssql.Error:
            raise
        finally:
            cm.close_connection()
    else:
        print("Please try again!")


def logout(tokens):
    """
    TODO: Part 2
    """
    # logout  -> no other argument
    global current_caregiver, current_patient
    if len(tokens) != 1:
        print("Please try again!")
        return
    try:
        if current_caregiver is None and current_patient is None:
            print("Please login first!")
        else:
            current_caregiver = None
            current_patient = None
            print("Successfully logged out!")
    except Exception as e:
        print("Please try again!")
        print("Error:", e)


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    # //TODO: implement create_patient (Part 1)
    print("> create_patient <username> <password>")
    print("> create_caregiver <username> <password>")
    # // TODO: implement login_patient (Part 1)
    print("> login_patient <username> <password>")
    print("> login_caregiver <username> <password>")
    # // TODO: implement search_caregiver_schedule (Part 2)
    print("> search_caregiver_schedule <date>")
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    # // TODO: implement cancel (extra credit)
    print("> cancel <appointment_id>")
    print("> add_doses <vaccine> <number>")
    # // TODO: implement show_appointments (Part 2)
    print("> show_appointments")
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    '''
    test part start
    '''

    '''
    test part end
    '''
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        # tokens would be a list
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
