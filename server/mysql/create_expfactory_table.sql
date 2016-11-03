CREATE TABLE `concerto`.`expfactory` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `test_time` TIMESTAMP,
  `subject` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `experiment` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `json` longtext COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
