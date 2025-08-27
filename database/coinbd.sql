-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1:3306
-- Tiempo de generación: 27-08-2025 a las 04:41:33
-- Versión del servidor: 9.1.0
-- Versión de PHP: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `coinbd`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `accounts`
--

DROP TABLE IF EXISTS `accounts`;
CREATE TABLE IF NOT EXISTS `accounts` (
  `account_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `balance` decimal(12,2) NOT NULL DEFAULT '0.00',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`account_id`),
  KEY `idx_accounts_user_id` (`user_id`)
) ;

--
-- Volcado de datos para la tabla `accounts`
--

INSERT INTO `accounts` (`account_id`, `user_id`, `balance`, `created_at`, `status`) VALUES
(2, 7, 150.75, '2025-08-25 16:59:43', 1),
(3, 12, 80.00, '2025-08-25 17:03:28', 1),
(4, 6, 30.00, '2025-08-25 18:05:14', 1),
(5, 6, 300.90, '2025-08-25 18:07:57', 1),
(6, 14, 150.00, '2025-08-26 21:00:41', 1),
(7, 15, 1420.00, '2025-08-26 21:05:39', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `answers`
--

DROP TABLE IF EXISTS `answers`;
CREATE TABLE IF NOT EXISTS `answers` (
  `answer_id` int NOT NULL AUTO_INCREMENT,
  `question_id` int NOT NULL,
  `answer_text` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_correct` tinyint(1) NOT NULL DEFAULT '0',
  `status` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`answer_id`),
  KEY `fk_question_answer` (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `attendance`
--

DROP TABLE IF EXISTS `attendance`;
CREATE TABLE IF NOT EXISTS `attendance` (
  `attendance_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `date` date NOT NULL,
  `status` varchar(50) NOT NULL,
  `coins_awarded` int DEFAULT NULL,
  `created_by_admin_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`attendance_id`),
  KEY `user_id` (`user_id`),
  KEY `created_by_admin_id` (`created_by_admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `courses`
--

DROP TABLE IF EXISTS `courses`;
CREATE TABLE IF NOT EXISTS `courses` (
  `course_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `status` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `loans`
--

DROP TABLE IF EXISTS `loans`;
CREATE TABLE IF NOT EXISTS `loans` (
  `loan_id` int NOT NULL AUTO_INCREMENT,
  `lender_account_id` int DEFAULT NULL,
  `borrower_account_id` int NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `interest_rate` decimal(5,2) NOT NULL,
  `due_date` timestamp NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `reason` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`loan_id`),
  KEY `lender_account_id` (`lender_account_id`),
  KEY `borrower_account_id` (`borrower_account_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3;

--
-- Volcado de datos para la tabla `loans`
--

INSERT INTO `loans` (`loan_id`, `lender_account_id`, `borrower_account_id`, `amount`, `interest_rate`, `due_date`, `status`, `created_at`, `reason`) VALUES
(2, 7, 6, 100.00, 0.00, '0000-00-00 00:00:00', 'approved', '2025-08-26 23:23:54', 'Necesito dinero para un proyecto escolar'),
(3, NULL, 6, 100.00, 8.00, '2025-09-26 00:56:24', 'rejected', '2025-08-27 00:56:24', 'Necesito dinero para un proyecto escolar'),
(4, 7, 3, 130.00, 8.00, '2025-09-26 01:05:24', 'partially_paid', '2025-07-27 01:05:24', 'Necesito dinero mano');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `loan_payments`
--

DROP TABLE IF EXISTS `loan_payments`;
CREATE TABLE IF NOT EXISTS `loan_payments` (
  `payment_id` int NOT NULL AUTO_INCREMENT,
  `loan_id` int NOT NULL,
  `amount_paid` decimal(12,2) NOT NULL,
  `payment_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`payment_id`),
  KEY `fk_loan_payments` (`loan_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `loan_payments`
--

INSERT INTO `loan_payments` (`payment_id`, `loan_id`, `amount_paid`, `payment_date`, `status`) VALUES
(1, 4, 50.00, '2025-08-27 01:32:33', 'completed');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `loan_rejections`
--

DROP TABLE IF EXISTS `loan_rejections`;
CREATE TABLE IF NOT EXISTS `loan_rejections` (
  `rejection_id` int NOT NULL AUTO_INCREMENT,
  `loan_id` int NOT NULL,
  `rejected_by_user_id` int NOT NULL,
  `reason` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `rejected_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`rejection_id`),
  KEY `fk_rejected_loan` (`loan_id`),
  KEY `fk_rejected_by_user` (`rejected_by_user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `loan_rejections`
--

INSERT INTO `loan_rejections` (`rejection_id`, `loan_id`, `rejected_by_user_id`, `reason`, `rejected_at`) VALUES
(1, 3, 15, 'El solicitante ya tiene un préstamo activo o parcialmente pagado.', '2025-08-27 00:57:13');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `questions`
--

DROP TABLE IF EXISTS `questions`;
CREATE TABLE IF NOT EXISTS `questions` (
  `question_id` int NOT NULL AUTO_INCREMENT,
  `video_id` int NOT NULL,
  `question_text` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`question_id`),
  KEY `fk_video_question` (`video_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `redemptions`
--

DROP TABLE IF EXISTS `redemptions`;
CREATE TABLE IF NOT EXISTS `redemptions` (
  `redemption_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `item_id` int NOT NULL,
  `redemption_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  PRIMARY KEY (`redemption_id`),
  KEY `fk_redemption_user` (`user_id`),
  KEY `fk_redemption_item` (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `redemption_codes`
--

DROP TABLE IF EXISTS `redemption_codes`;
CREATE TABLE IF NOT EXISTS `redemption_codes` (
  `code_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `amount` decimal(12,2) NOT NULL,
  `is_redeemed` tinyint(1) NOT NULL DEFAULT '0',
  `redeemed_at` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`code_id`),
  KEY `fk_redeemer` (`user_id`)
) ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `rewards_catalog`
--

DROP TABLE IF EXISTS `rewards_catalog`;
CREATE TABLE IF NOT EXISTS `rewards_catalog` (
  `item_id` int NOT NULL AUTO_INCREMENT,
  `item_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cost` decimal(12,2) NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `status` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

DROP TABLE IF EXISTS `roles`;
CREATE TABLE IF NOT EXISTS `roles` (
  `role_id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `status` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`role_id`),
  UNIQUE KEY `role_name` (`role_name`)
) ;

--
-- Volcado de datos para la tabla `roles`
--

INSERT INTO `roles` (`role_id`, `role_name`, `description`, `status`) VALUES
(1, 'super_admin', 'Acceso completo al sistema, incluyendo la gestión de usuarios, contenido y finanzas.', 1),
(2, 'intermediario', 'Gestión de contenido educativo, asignación de tareas y monitoreo del progreso de los estudiantes.', 1),
(3, 'estudiante', 'Participa en el contenido educativo, gana recompensas y gestiona su cuenta virtual.', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `student_tasks`
--

DROP TABLE IF EXISTS `student_tasks`;
CREATE TABLE IF NOT EXISTS `student_tasks` (
  `student_task_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `task_id` int NOT NULL,
  `completion_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_paid` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`student_task_id`),
  UNIQUE KEY `unique_student_task` (`user_id`,`task_id`),
  KEY `fk_user_task` (`user_id`),
  KEY `fk_task_student` (`task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tasks`
--

DROP TABLE IF EXISTS `tasks`;
CREATE TABLE IF NOT EXISTS `tasks` (
  `task_id` int NOT NULL AUTO_INCREMENT,
  `created_by_admin_id` int NOT NULL,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `reward_amount` decimal(12,2) NOT NULL,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'open',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`task_id`),
  KEY `fk_admin_task` (`created_by_admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `transactions`
--

DROP TABLE IF EXISTS `transactions`;
CREATE TABLE IF NOT EXISTS `transactions` (
  `transaction_id` int NOT NULL AUTO_INCREMENT,
  `from_account_id` int DEFAULT NULL,
  `to_account_id` int NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `transaction_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `event_id` int DEFAULT NULL,
  `event_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`transaction_id`),
  KEY `idx_transactions_from_account` (`from_account_id`),
  KEY `idx_transactions_to_account` (`to_account_id`),
  KEY `idx_transactions_created_at` (`created_at`)
) ;

--
-- Volcado de datos para la tabla `transactions`
--

INSERT INTO `transactions` (`transaction_id`, `from_account_id`, `to_account_id`, `amount`, `transaction_type`, `status`, `notes`, `created_at`, `event_id`, `event_type`) VALUES
(1, 3, 2, 150.75, 'injection', 'completed', 'Inyección de capital por admin', '2025-08-25 17:03:40', NULL, NULL),
(2, 7, 6, 50.00, 'transfer', 'completed', 'Transferencia entre usuarios', '2025-08-26 22:31:09', NULL, NULL),
(3, 7, 6, 100.00, 'loan_approved', 'completed', 'Préstamo aprobado', '2025-08-26 23:40:50', NULL, NULL),
(4, 7, 3, 130.00, 'loan_approved', 'completed', 'Préstamo aprobado', '2025-08-27 01:06:27', NULL, NULL),
(8, NULL, 7, 1000.00, 'coin_created', 'completed', 'create de monedas por superadministrador', '2025-08-27 03:01:12', NULL, NULL),
(9, 7, 4, 30.00, 'transfer', 'completed', 'Regalo para un amigo', '2025-08-27 03:06:40', NULL, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone_number` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `phone_number` (`phone_number`),
  KEY `fk_role` (`role_id`),
  KEY `idx_users_email` (`email`),
  KEY `idx_users_phone` (`phone_number`),
  KEY `idx_users_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `users`
--

INSERT INTO `users` (`user_id`, `username`, `email`, `password_hash`, `phone_number`, `role_id`, `created_at`, `status`) VALUES
(5, 'usuario_de_prueba', 'prueba@ejemplo.com', '$2b$12$A4m54L2o.Zkr/SoZAwAruOdxNjcxKMoW5jHqSaN1EjXj/6N19sJjS', NULL, 3, '2025-08-24 02:10:57', 1),
(6, 'rodri', 'rodri@gmail.com', '$2b$12$9PqgCphcz3tg5Ol0Qjns9et9/myahst64vKcZW9g4xP8c/mHAz/R2', NULL, 3, '2025-08-24 02:12:32', 1),
(7, 'aaaari', 'rzzzz@gmail.com', '$2b$12$4ERbblfEQv.P8LB.Gw.oqeiFRh.889YmYMINgixKucuYGKVwQCaIO', NULL, 2, '2025-08-24 03:22:07', 1),
(10, 'aaghgjri', 'rzz@gmail.com', '$2b$12$Ori6xmu7LYowOdgvkOF15OuYn2ee/DKpOekF5C3QqT.WfEcCKyqbW', '9987654567', 3, '2025-08-24 03:40:02', 1),
(12, 'ander', 'denis@gmail.com', '$2b$12$j8YV/MzeVERlaQi1LiIsYeVPx8u0z8KLrkhEtKI0XLH9HLfBYuS5i', '998877665', 3, '2025-08-24 04:25:03', 1),
(14, 'alexis', 'alexis@gmail.com', '$2b$12$LkhySGnLheEA58Fx8KnYm.FVxrJoSzy7xH.0HSuwwspbV4.UPpOzu', '923456789', 3, '2025-08-26 21:00:41', 1),
(15, 'nico', 'nicolas@gmail.com', '$2b$12$jwbfHz.f6eGXJJ9pVNeRRe7WO7wfEPLXYeQslWLrJSkaJCQv.HxEm', '989999991', 1, '2025-08-26 21:05:39', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_profiles`
--

DROP TABLE IF EXISTS `user_profiles`;
CREATE TABLE IF NOT EXISTS `user_profiles` (
  `user_profile_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `first_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `profile_picture_url` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`user_profile_id`),
  UNIQUE KEY `user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `user_profiles`
--

INSERT INTO `user_profiles` (`user_profile_id`, `user_id`, `first_name`, `last_name`, `birth_date`, `profile_picture_url`, `status`) VALUES
(1, 14, NULL, NULL, NULL, NULL, 1),
(2, 15, 'nicolas', 'novillo', NULL, NULL, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_progress`
--

DROP TABLE IF EXISTS `user_progress`;
CREATE TABLE IF NOT EXISTS `user_progress` (
  `progress_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `video_id` int NOT NULL,
  `is_completed` tinyint(1) NOT NULL DEFAULT '0',
  `score` int DEFAULT NULL,
  `completion_date` datetime DEFAULT NULL,
  `status` tinyint(1) DEFAULT '1',
  `answer_id` int DEFAULT NULL,
  PRIMARY KEY (`progress_id`),
  UNIQUE KEY `unique_progress` (`user_id`,`video_id`),
  KEY `fk_video_progress` (`video_id`),
  KEY `idx_user_progress_user_id` (`user_id`),
  KEY `fk_user_answer` (`answer_id`)
) ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `videos`
--

DROP TABLE IF EXISTS `videos`;
CREATE TABLE IF NOT EXISTS `videos` (
  `video_id` int NOT NULL AUTO_INCREMENT,
  `course_id` int NOT NULL,
  `youtube_url` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `duration_seconds` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`video_id`),
  KEY `fk_course` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `video_rewards`
--

DROP TABLE IF EXISTS `video_rewards`;
CREATE TABLE IF NOT EXISTS `video_rewards` (
  `reward_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `video_id` int NOT NULL,
  `amount_earned` decimal(12,2) NOT NULL,
  `claimed` tinyint(1) NOT NULL DEFAULT '0',
  `claimed_at` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`reward_id`),
  UNIQUE KEY `unique_reward` (`user_id`,`video_id`),
  KEY `fk_video_reward` (`video_id`),
  KEY `idx_rewards_user_id` (`user_id`)
) ;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `accounts`
--
ALTER TABLE `accounts`
  ADD CONSTRAINT `fk_account_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Filtros para la tabla `answers`
--
ALTER TABLE `answers`
  ADD CONSTRAINT `fk_question_answer` FOREIGN KEY (`question_id`) REFERENCES `questions` (`question_id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `attendance`
--
ALTER TABLE `attendance`
  ADD CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `attendance_ibfk_2` FOREIGN KEY (`created_by_admin_id`) REFERENCES `users` (`user_id`);

--
-- Filtros para la tabla `loans`
--
ALTER TABLE `loans`
  ADD CONSTRAINT `loans_ibfk_1` FOREIGN KEY (`lender_account_id`) REFERENCES `accounts` (`account_id`),
  ADD CONSTRAINT `loans_ibfk_2` FOREIGN KEY (`borrower_account_id`) REFERENCES `accounts` (`account_id`);

--
-- Filtros para la tabla `loan_payments`
--
ALTER TABLE `loan_payments`
  ADD CONSTRAINT `fk_loan_payments` FOREIGN KEY (`loan_id`) REFERENCES `loans` (`loan_id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `loan_rejections`
--
ALTER TABLE `loan_rejections`
  ADD CONSTRAINT `fk_rejected_by_user` FOREIGN KEY (`rejected_by_user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `fk_rejected_loan` FOREIGN KEY (`loan_id`) REFERENCES `loans` (`loan_id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `questions`
--
ALTER TABLE `questions`
  ADD CONSTRAINT `fk_video_question` FOREIGN KEY (`video_id`) REFERENCES `videos` (`video_id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `redemptions`
--
ALTER TABLE `redemptions`
  ADD CONSTRAINT `fk_redemption_item` FOREIGN KEY (`item_id`) REFERENCES `rewards_catalog` (`item_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_redemption_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `redemption_codes`
--
ALTER TABLE `redemption_codes`
  ADD CONSTRAINT `fk_redeemer` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL;

--
-- Filtros para la tabla `student_tasks`
--
ALTER TABLE `student_tasks`
  ADD CONSTRAINT `fk_task_student` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`task_id`),
  ADD CONSTRAINT `fk_user_task` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Filtros para la tabla `tasks`
--
ALTER TABLE `tasks`
  ADD CONSTRAINT `fk_admin_task` FOREIGN KEY (`created_by_admin_id`) REFERENCES `users` (`user_id`);

--
-- Filtros para la tabla `transactions`
--
ALTER TABLE `transactions`
  ADD CONSTRAINT `fk_from_account` FOREIGN KEY (`from_account_id`) REFERENCES `accounts` (`account_id`),
  ADD CONSTRAINT `fk_to_account` FOREIGN KEY (`to_account_id`) REFERENCES `accounts` (`account_id`);

--
-- Filtros para la tabla `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `fk_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`);

--
-- Filtros para la tabla `user_profiles`
--
ALTER TABLE `user_profiles`
  ADD CONSTRAINT `fk_user_profile` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `user_progress`
--
ALTER TABLE `user_progress`
  ADD CONSTRAINT `fk_user_answer` FOREIGN KEY (`answer_id`) REFERENCES `answers` (`answer_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_user_progress` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_video_progress` FOREIGN KEY (`video_id`) REFERENCES `videos` (`video_id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `videos`
--
ALTER TABLE `videos`
  ADD CONSTRAINT `fk_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `video_rewards`
--
ALTER TABLE `video_rewards`
  ADD CONSTRAINT `fk_user_reward` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_video_reward` FOREIGN KEY (`video_id`) REFERENCES `videos` (`video_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
