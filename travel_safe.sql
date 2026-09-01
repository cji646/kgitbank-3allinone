/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.5.29-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: travel_safe
-- ------------------------------------------------------
-- Server version	10.5.29-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `countries`
--

DROP TABLE IF EXISTS `countries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `countries` (
  `country_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `country_name` varchar(100) NOT NULL,
  `continent` varchar(50) DEFAULT NULL,
  `safety_level` varchar(20) DEFAULT NULL,
  `emergency_number` varchar(30) DEFAULT NULL,
  `precautions` text DEFAULT NULL,
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`country_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `countries`
--

LOCK TABLES `countries` WRITE;
/*!40000 ALTER TABLE `countries` DISABLE KEYS */;
INSERT INTO `countries` VALUES (1,'대한민국','아시아','안전','112 / 119','여행 중 소지품 관리에 주의하고, 응급 상황 발생 시 긴급전화 112 또는 119로 신고하세요.','2026-09-01 15:33:24');
/*!40000 ALTER TABLE `countries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `password` varchar(255) NOT NULL,
  `name` varchar(50) NOT NULL,
  `email` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `role` enum('user','admin') NOT NULL DEFAULT 'user',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'1234','이름','test@email.com','2026-08-27 14:47:15','2026-08-27 14:47:15','user'),(2,'1234','박유진','naver@naver.com','2026-08-27 14:50:03','2026-08-27 14:50:03','admin'),(3,'scrypt:32768:8:1$Pm4ehrXxQb4aCfXT$93bcaa71d5f9abb5c0eaf90ef1f37152fa29878054b4f7aafac9c8a37263c90f318d124c9f10733c0bf53347953e160276ad7c9065b9de726eb3ff5cab36ce87','홍길동','test@test.com','2026-08-28 10:50:30','2026-08-28 10:50:30','user'),(4,'scrypt:32768:8:1$ZQvanhIKBbcRdMkK$60472449ff1c87f34f9569b6c1ffc1ddc6ea88d9ec164e320066d870cc6569726079798fe62a630e54cac375972443dc5438317cb42dd488becbff94219114f5','gana','test111@test.com','2026-08-28 10:57:10','2026-08-28 10:57:10','user'),(5,'scrypt:32768:8:1$CwdioK6Wxa1srUNm$42a20560d2b9b2e8b965401d2c25e9fcd2c25a7eaa642d5a56232f25efcd040b9b0963816c53f9a7245f02024be40220be926a32bc1cb0cf810419d2eaaff1c5','hi','test122@test.com','2026-08-28 10:58:24','2026-08-28 10:58:24','user'),(6,'scrypt:32768:8:1$Jq46b8ENORfh8dMk$fdeabfa297932e3610975d630adce94f64a0e067ab62d9a8277824b3b538c6f7349861faf679ab19b541bed7112449c8974f12ca598b34857e3732cebe719576','hddi','test123@test.com','2026-08-28 11:00:12','2026-08-28 11:00:12','user'),(7,'scrypt:32768:8:1$uQods6sH4RdCJuZJ$d9538c2b568d28b1af3ca81a730e1be819b5e0a7781fe47319ec9f01eacf27ad320f239f4d771ceb14931d46fe75e9df919a034b8abc2288c52170e5a414412b','3조 조원','happy@test.com','2026-08-28 11:07:18','2026-08-28 11:07:18','user'),(8,'scrypt:32768:8:1$LA13HVp73ubyAI9z$be3e86a9b11dba9d826cbc453e40d49256e137a9c37038d00ed93378f225d40adb96436fedfd36856eeb6498e294b4e1e7de90a1545278a09ad4cdfb26a7417a','집가고싶다','iwannahome@test.com','2026-08-28 11:08:40','2026-08-28 11:08:40','user'),(9,'scrypt:32768:8:1$x2lhPlu8mFuMZhOe$2235cd9044758a322eee69df9526344f441545d729e29e7c5adf2fd543364067f2f03aec023d6af70f810ce317c9c52f55a0886c432532cbdd805a7a46197d3c','가나다','test222@test.com','2026-08-28 11:16:38','2026-08-28 11:16:38','user'),(10,'scrypt:32768:8:1$0KGuX1p4zIYDlcWd$000745991c12ffd2214a85487e3cac03d8a96fb2de01f77e8e36210c7de7704b02b4ed49e62a5a31e232a56e027f9ad51ee24a88027c0919fe8b0ea1c791959c','가나다','test223@test.com','2026-08-28 11:17:05','2026-08-28 11:17:05','user'),(11,'scrypt:32768:8:1$XpNEvSy71dTgXkjz$3e44c5edf10e82181b3c8001376074f6e04dc95e0118e9affd73968af8b581b82e58ed83cd9a5f1b1245c38d7e2defc64ad535b222b3b224f95224bf25f0c1e3','김만수','testttttt@test.com','2026-08-28 11:48:22','2026-08-28 11:48:22','user');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-01 15:34:58
