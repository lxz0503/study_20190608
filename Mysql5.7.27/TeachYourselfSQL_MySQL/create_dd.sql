-- -----------------------------------------
-- Sams Teach Yourself SQL in 10 Minutes
-- http://forta.com/books/0672336073/
-- Example table creation scripts for MySQL.
-- -----------------------------------------

use dd;  -- u must create this database in your workbench
-- ----------------------
-- Create Customers persons
-- ----------------------
CREATE TABLE Persons
(
  Id_P       int(10)      NOT NULL,
  LastName   varchar(50)  NOT NULL,
  FirstName  varchar(50)  NOT NULL,
  Address    varchar(50)  NOT NULL,
  City       varchar(50)  NOT NULL 
);

-- -----------------------
-- Create orders table
-- -----------------------
CREATE TABLE Orders
(
  Id_O     int(10)    NOT NULL,
  OrderNo  int(50)    NOT NULL,
  Id_P     int(10)    NOT NULL
);




-- -------------------
-- Define primary keys, should master this method,xiaozhan
-- -------------------
ALTER TABLE Persons ADD PRIMARY KEY (Id_P);
ALTER TABLE Orders ADD PRIMARY KEY (Id_O);   



-- -------------------
-- Define foreign keys
-- this means 2 tables have correlation through these same keys
-- for example, it both has Id_P in table Persons and Orders

-- -------------------
ALTER TABLE Orders ADD CONSTRAINT FK_Orders_Persons FOREIGN KEY (Id_P) REFERENCES Persons (Id_P);

