DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  firstname VARCHAR(100) NOT NULL,
  lastname VARCHAR(100) NOT NULL,
  username VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL,
  password VARCHAR(32) NOT NULL,
  old_password VARCHAR(32) NULL,
  date_of_birth DATE NULL,
  registration_date_time DATETIME NULL,
  last_login_date_time DATETIME NULL
);

INSERT INTO users
(firstname, lastname, username, email, password, old_password, date_of_birth, registration_date_time, last_login_date_time)
VALUES
('', '', '', '', '', '', date(''), datetime(), datetime());

DROP TABLE IF EXISTS gender;

CREATE TABLE gender (
  female VARCHAR(6),
  male VARCHAR(4)
);

INSERT INTO gender
(female, male)
VALUES
('female', 'male');
