DROP TABLE IF EXISTS Ripe;
DROP TABLE IF EXISTS Unripe;
DROP TABLE IF EXISTS Twilight_zone;
DROP TABLE IF EXISTS Batch_info;
DROP TABLE IF EXISTS Customers;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Shippings;


-- Create tables
PRAGMA foreign_keys = ON;

CREATE TABLE Batch_info (
    batch_number INTEGER PRIMARY KEY,
    tomato INTEGER NOT NULL
);

CREATE TABLE Ripe (
    batch_number INTEGER PRIMARY KEY,
    tomato INTEGER NOT NULL,
    FOREIGN KEY (batch_number) REFERENCES Batch_info(batch_number)
);

CREATE TABLE Unripe (
    batch_number INTEGER PRIMARY KEY,
    tomato INTEGER NOT NULL,
    FOREIGN KEY (batch_number) REFERENCES Batch_info(batch_number)
);

CREATE TABLE Twilight_zone (
    batch_number INTEGER PRIMARY KEY,
    tomato INTEGER NOT NULL,
    FOREIGN KEY (batch_number) REFERENCES Batch_info(batch_number)
);

-- Insert sample data into Batch_info
INSERT INTO Batch_info (batch_number, tomato) VALUES
    (1, 15),
    (2, 15),
    (3, 15),
    (4, 15),
    (5,0);

-- Insert sample data into Ripe, Unripe, and Twilight_zone
-- Splitting the 15 tomatoes differently for each batch

-- Batch 1: 5 ripe, 7 unripe, 3 twilight zone
INSERT INTO Ripe (batch_number, tomato) VALUES (1, 5);
INSERT INTO Unripe (batch_number, tomato) VALUES (1, 7);
INSERT INTO Twilight_zone (batch_number, tomato) VALUES (1, 3);

-- Batch 2: 6 ripe, 4 unripe, 5 twilight zone
INSERT INTO Ripe (batch_number, tomato) VALUES (2, 6);
INSERT INTO Unripe (batch_number, tomato) VALUES (2, 4);
INSERT INTO Twilight_zone (batch_number, tomato) VALUES (2, 5);

-- Batch 3: 8 ripe, 3 unripe, 4 twilight zone
INSERT INTO Ripe (batch_number, tomato) VALUES (3, 8);
INSERT INTO Unripe (batch_number, tomato) VALUES (3, 3);
INSERT INTO Twilight_zone (batch_number, tomato) VALUES (3, 4);

-- Batch 4: 7 ripe, 6 unripe, 2 twilight zone
INSERT INTO Ripe (batch_number, tomato) VALUES (4, 7);
INSERT INTO Unripe (batch_number, tomato) VALUES (4, 6);
INSERT INTO Twilight_zone (batch_number, tomato) VALUES (4, 2);

INSERT INTO Ripe (batch_number, tomato) VALUES (5, 0);
INSERT INTO Unripe (batch_number, tomato) VALUES (5, 0);
INSERT INTO Twilight_zone (batch_number, tomato) VALUES (5, 0);

SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM Batch_info) 
        THEN (
            SELECT batch_number || ', ' || tomato
            FROM Batch_info 
            WHERE batch_number = (SELECT MAX(batch_number) FROM Batch_info)
            LIMIT 1
        )
        ELSE 'No data available'
    END AS result;

-- Update the total tomato count in Batch_info for batch number 4
UPDATE Batch_info
SET tomato = tomato + 3
WHERE batch_number = 4;

-- Add 1 tomato to the Ripe table for batch number 4
UPDATE Ripe
SET tomato = tomato + 1
WHERE batch_number = 4;

-- Add 1 tomato to the Unripe table for batch number 4
UPDATE Unripe
SET tomato = tomato + 1
WHERE batch_number = 4;

-- Add 1 tomato to the Twilight Zone table for batch number 4
UPDATE Twilight_zone
SET tomato = tomato + 1
WHERE batch_number = 4;
