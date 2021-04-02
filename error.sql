SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

CREATE DATABASE IF NOT EXISTS `error` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `error`;

CREATE TABLE `error` (
  `error_id` int(11) NOT NULL AUTO_INCREMENT,
  `error_category` varchar(64) NULL,
  `error_desc` varchar(255) NOT NULL,
  PRIMARY KEY (`error_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;