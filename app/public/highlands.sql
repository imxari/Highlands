CREATE TABLE `users` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`username` VARCHAR(75) NOT NULL,
	`password` VARCHAR(75) NOT NULL,
	`firstname` VARCHAR(75) NOT NULL,
	`lastname` VARCHAR(75) NOT NULL,
	`email` VARCHAR(75) NOT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
;
