-- Create User table
CREATE TABLE User (
    userID INTEGER PRIMARY KEY AUTOINCREMENT,
    password TEXT NOT NULL,
    dateCreated TEXT NOT NULL,
    lastLogin TEXT
);

-- Create Category table
CREATE TABLE Category (
    categoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER NOT NULL,
    name TEXT NOT NULL,
    colour TEXT,
    icon TEXT,
    FOREIGN KEY (userID) REFERENCES User(userID) ON DELETE CASCADE
);

-- Create Transactions table
CREATE TABLE Transactions (
    transactionID INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER NOT NULL,
    categoryID INTEGER,
    type TEXT NOT NULL,
    details TEXT,
    particulars TEXT,
    code TEXT,
    reference TEXT,
    amount REAL NOT NULL,
    date TEXT NOT NULL,
    foreignCurrencyAmount REAL,
    conversionCharge REAL,
    FOREIGN KEY (userID) REFERENCES User(userID) ON DELETE CASCADE,
    FOREIGN KEY (categoryID) REFERENCES Category(categoryID) ON DELETE SET NULL
);
