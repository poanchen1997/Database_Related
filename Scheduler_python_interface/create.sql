CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

-- add part start
CREATE TABLE Patients (
    Username varchar(255), 
    Salt BINARY(16), 
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Appointments (
    id INT PRIMARY KEY, 
    Username_c VARCHAR(255), -- caregiver name
    Username_p VARCHAR(255), -- patient name
    Name VARCHAR(255), -- vaccine name
    date date,  -- appointments date
    FOREIGN KEY (Username_c) REFERENCES Caregivers(Username), 
    FOREIGN KEY (Username_p) REFERENCES Patients(Username), 
    FOREIGN KEY (Name) REFERENCES Vaccines(Name)
);
-- add part end
