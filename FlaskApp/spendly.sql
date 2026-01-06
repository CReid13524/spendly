-- Create User table
CREATE TABLE IF NOT EXISTS User (
    userID INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NULL,
    googleEmail TEXT NULL,
    googleImage TEXT NULL,
    googleID TEXT NULL ,
    password TEXT  NULL,
    name TEXT NULL,
    dateCreated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lastLogin TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'active'
);

-- Create Category table
CREATE TABLE IF NOT EXISTS Category (
    categoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER NOT NULL,
    name TEXT NOT NULL,
    colour TEXT,
    icon TEXT,
    isHidden boolean default 0,
    isIncome boolean default 0,
    isDefault boolean default 1,
    status TEXT NOT NULL DEFAULT 'active',
    FOREIGN KEY (userID) REFERENCES User(userID) ON DELETE CASCADE
);

-- Create Transactions table
CREATE TABLE IF NOT EXISTS Transactions (
    transactionID INTEGER PRIMARY KEY AUTOINCREMENT,
    uploadID INTEGER NOT NULL,
    categoryID INTEGER,
    type TEXT NOT NULL,
    details TEXT,
    particulars TEXT,
    code TEXT,
    reference TEXT,
    amount REAL NOT NULL,
    date TEXT NOT NULL,
    title TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    FOREIGN KEY (uploadID) REFERENCES Upload(uploadID) ON DELETE CASCADE,
    FOREIGN KEY (categoryID) REFERENCES Category(categoryID) ON DELETE SET NULL
);

create TABLE IF NOT EXISTS Upload (
    uploadID INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER NOT NULL,
    date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userID) REFERENCES User(userID) ON DELETE CASCADE
); 