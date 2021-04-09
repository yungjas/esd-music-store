-- phpMyAdmin SQL Dump
-- version 4.9.7
-- https://www.phpmyadmin.net/
--
-- Host: localhost:8889
-- Generation Time: Mar 29, 2021 at 04:43 AM
-- Server version: 5.7.32
-- PHP Version: 7.4.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `cdalbums`
--

-- --------------------------------------------------------

--
-- Table structure for table `cdalbums`
--

CREATE DATABASE IF NOT EXISTS `inventory` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `inventory`;

CREATE TABLE `inventory` (
  `item_name` varchar(64) NOT NULL,
  `artist` varchar(64) NULL,
  `item_id` varchar(64) NOT NULL,
  `item_price` decimal(10,2) NOT NULL,
  `item_quantity` int(11) NOT NULL,
  `item_category` varchar(64) NOT NULL,
  `item_status` varchar(64) NOT NULL,
  `item_desc` varchar(255) NOT NULL,
  PRIMARY KEY (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `cdalbums`
--

INSERT INTO `inventory` (`item_name`, `artist`, `item_id`, `item_price`, `item_quantity`, `item_category`, `item_status`, `item_desc`) VALUES
('ASTROWORLD', 'Travis Scott', '190758883625', '8.99', 0, 'Rap & HipHop', 'Out of Stock', 'Hip Hop album incorporating trap and hip hop'),
('IGOR', 'Tyler, The Creator', '190759652022', '9.99', 0, 'Rap & HipHop', 'Out of Stock', 'Hip Hop album incorporating trap and hip hop'),
('Fuzzybrain', 'Dayglow', '194397445391', '13.99', 0, 'Indie', 'Out of Stock', 'An indie album with soothing sounds'),
('Please Be Mine', 'Molly Burch', '194397460985', '13.99', 7, 'Rock & Pop', 'In Stock', 'Feeling like a rockstar? Than grab this album today!'),
('Rubber Soul', 'The Beatles', '194397463451', '14.99', 1, 'Rock & Pop', 'In Stock', 'Enjoy some classic rock with a Beatles album!'),
('Dark Side Of The Moon', 'Pink Floyd', '194397464528', '19.99', 7, 'Rock & Pop', 'In Stock', 'Feeling like a rockstar? Than grab this album today!'),
('The Beautiful & The Damned', 'G-Eazy', '194397466573', '10.99', 10, 'Rap & Hip-Hop', 'In Stock', 'Hip Hop album incorporating trap and hip hop'),
('Fearless', 'Wolfalice', '194397468649', '9.99', 11, 'Rock & Pop', 'In Stock', 'Be fearless and buy this album today!'),
('When You See Yourself', 'Kings of Leon', '194397468724', '12.99', 10, 'Rock & Pop', 'In Stock', 'Feeling like a rockstar? Than grab this album today!'),
('Wish You Were Here', 'Pink Floyed', '194397468829', '15.99', 14, 'Rock & Pop', 'In Stock', 'Feeling like a rockstar? Than grab this album today!'),
('Cry', 'Cigarettes After Sex', '194397476523', '7.99', 20, 'Rock & Pop', 'In Stock', 'Cry is the second studio album by American ambient pop band Cigarettes After Sex, released through Partisan Records on October 25, 2019'),
('Mindful Moments', 'Charlotte Hawkins', '5414939834152', '13.99', 20, 'Classical', 'In Stock', 'Kick back and relax and enjoy some classical music!'),
('Classical Chillout', 'Various Performers', '5414939934165', '27.99', 14, 'Classical', 'In Stock', 'Kick back and relax and enjoy some classical music!'),
('Citizen Of Glass', 'Agnes Obel', '5414939944338', '24.99', 24, 'Rock & Pop', 'In Stock', 'Feeling like a rockstar? Than grab this album today!'),
('X', 'She Past Away', '744861008976', '20.99', 12, 'Rock & Pop', 'In Stock', 'Feeling like a rockstar? Than grab this album today!'),
('The Greatest', 'Cat Power', '744861074304', '8.99', 24, 'Rock & Pop', 'In Stock', 'Feeling like a rockstar? Than grab this album today!'),
('The Dirt and the Stars', 'Mary Chapin Carpenter', '744861078341', '12.99', 13, 'Country', 'In Stock', 'Enjoy some good old country music!'),
('Yamaha Electric Guitar', Null, '744861078355', '200.99', 30, 'Instrument', 'In Stock', 'Learn a new instrument today!'),
('Yamaha Acoustic Guitar', Null, '744861078366', '100.99', 20, 'Instrument', 'In Stock', 'Learn a new instrument today!'),
('Johnny Cash and the Philharmonic Orchestra', 'Johnny Cash', '744861452648', '19.99', 24, 'Country', 'In Stock', 'Enjoy some good old country music!'),
('Now That\'s What I Call Country', 'Various Artists', '744868364517', '9.99', 24, 'Country', 'In Stock', 'Enjoy some good old country music!');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `cdalbums`
--
