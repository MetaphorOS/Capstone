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


-- INSERT INTO Batch_info (batch_number, tomato) VALUES
--     (1, 15),
--     (2, 15),
--     (3, 15),
--     (4, 15);

-- -- Batch 1: 5 ripe, 7 unripe, 3 twilight zone
-- INSERT INTO Ripe (batch_number, tomato) VALUES (1, 5);
-- INSERT INTO Unripe (batch_number, tomato) VALUES (1, 7);
-- INSERT INTO Twilight_zone (batch_number, tomato) VALUES (1, 3);

-- -- Batch 2: 6 ripe, 4 unripe, 5 twilight zone
-- INSERT INTO Ripe (batch_number, tomato) VALUES (2, 6);
-- INSERT INTO Unripe (batch_number, tomato) VALUES (2, 4);
-- INSERT INTO Twilight_zone (batch_number, tomato) VALUES (2, 5);

-- -- Batch 3: 8 ripe, 3 unripe, 4 twilight zone
-- INSERT INTO Ripe (batch_number, tomato) VALUES (3, 8);
-- INSERT INTO Unripe (batch_number, tomato) VALUES (3, 3);
-- INSERT INTO Twilight_zone (batch_number, tomato) VALUES (3, 4);

-- -- Batch 4: 7 ripe, 6 unripe, 2 twilight zone
-- INSERT INTO Ripe (batch_number, tomato) VALUES (4, 7);
-- INSERT INTO Unripe (batch_number, tomato) VALUES (4, 6);
-- INSERT INTO Twilight_zone (batch_number, tomato) VALUES (4, 2);