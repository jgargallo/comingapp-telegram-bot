CREATE TABLE `chat` (
  `id` bigint(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `event` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `chat_id` bigint(20) NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_event_chat` (`chat_id`),
  CONSTRAINT `FK_event_chat` FOREIGN KEY (`chat_id`) REFERENCES `chat` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `attendant` (
  `id` bigint(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `event_attendant` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `event_id` bigint(20) NOT NULL,
  `attendant_id` bigint(20) NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT '0' COMMENT '0/NO, 1/YES, 2/MAYBE',
  `last_updated` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_event_attendant_event` (`event_id`),
  CONSTRAINT `FK_event_attendant_event` FOREIGN KEY (`event_id`) REFERENCES `event` (`id`),
  KEY `FK_event_attendant_att` (`attendant_id`),
  CONSTRAINT `FK_event_attendant_att` FOREIGN KEY (`attendant_id`) REFERENCES `attendant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

