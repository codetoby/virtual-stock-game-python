CREATE TABLE `portfolio` (
        `id` INT, cash INT default 5000,
        PRIMARY KEY (`id`)
);
CREATE TABLE `users` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        `email` TEXT,
        `password` TEXT,
        `admin` BIT
);
CREATE TABLE `history` (
        `id` INT,
        `orderType` TEXT,
        `ticker` TEXT,
        `shares` INT,
        `date` DATE, 
        `price` INT);
CREATE TABLE `stocks` (
        `id` INT,
        `ticker` TEXT,
        `price` INT,
        `shares` INT,
        `date` DATE
);
