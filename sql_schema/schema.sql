/* Create the database */
CREATE DATABASE IF NOT EXISTS aus_cpi_wpi
  DEFAULT CHARACTER SET utf8
  DEFAULT COLLATE utf8_general_ci;

/* Switch to the database */
USE aus_cpi_wpi;

/* Drop existing tables */
DROP TABLE IF EXISTS cpi_values;
DROP TABLE IF EXISTS wpi_values;
DROP TABLE IF EXISTS time_periods;
DROP TABLE IF EXISTS categories;

/* Create the tables */
CREATE TABLE categories (
  api_id VARCHAR(10) NOT NULL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  sequence INT UNSIGNED NOT NULL,
  parent_api_id VARCHAR(10) NULL,

  UNIQUE KEY uk_api_id (api_id)
) ENGINE=InnoDB;

CREATE TABLE time_periods (
  api_id VARCHAR(10) NOT NULL PRIMARY KEY,
  name VARCHAR(10) NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,

  UNIQUE KEY uk_api_id (api_id)
) ENGINE=InnoDB;

CREATE TABLE cpi_values (
  category_api_id VARCHAR(10) NOT NULL,
  time_period_api_id VARCHAR(10) NOT NULL,
  value FLOAT NULL,

  PRIMARY KEY (category_api_id, time_period_api_id),
  INDEX idx_time_period_api_id (time_period_api_id),

  FOREIGN KEY (category_api_id) REFERENCES categories(api_id) ON DELETE CASCADE,
  FOREIGN KEY (time_period_api_id) REFERENCES time_periods(api_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE wpi_values (
  time_period_api_id VARCHAR(10) NOT NULL PRIMARY KEY,
  value FLOAT NULL,

  FOREIGN KEY (time_period_api_id) REFERENCES time_periods(api_id) ON DELETE CASCADE
) ENGINE=InnoDB;
