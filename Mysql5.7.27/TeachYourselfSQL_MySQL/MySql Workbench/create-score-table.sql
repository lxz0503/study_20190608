use test;
CREATE TABLE `scores` (
  `id` int(11) NOT NULL,
  `score` decimal(6,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8