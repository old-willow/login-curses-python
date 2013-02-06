# Create table  users for database login_register
# date: Sep 22, 2011.
# Author: Kolozsi Robert


USE login_register;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id int(5) UNSIGNED NOT NULL AUTO_INCREMENT,
  gender ENUM("male", "female") DEFAULT NULL,
  firstname VARCHAR(100) NOT NULL,
  lastname VARCHAR(100) NOT NULL,
  username VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL,
  password VARCHAR(32) NOT NULL,
  old_password VARCHAR(32) NOT NULL,
  date_of_birth DATE NULL,
  registration_date_time DATETIME NOT NULL,
  last_login_date_time DATETIME NOT NULL,
  PRIMARY KEY (id)
)
TYPE = myIsam
DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

INSERT INTO users
(gender, firstname, lastname, username, email, password, old_password, date_of_birth, registration_date_time, last_login_date_time)
VALUES
('', '', '', '', '', MD5(''), MD5(''), '', NOW(), NOW());
