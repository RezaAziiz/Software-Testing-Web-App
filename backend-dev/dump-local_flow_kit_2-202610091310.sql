-- MySQL dump 10.13  Distrib 9.4.0, for Win64 (x86_64)
--
-- Host: localhost    Database: local_flow_kit_2
-- ------------------------------------------------------
-- Server version	9.4.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ms_cfg_edge`
--

DROP TABLE IF EXISTS `ms_cfg_edge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ms_cfg_edge` (
  `ms_id_edge` varchar(255) NOT NULL,
  `ms_id_modul` varchar(255) DEFAULT NULL,
  `ms_id_start_node` varchar(255) DEFAULT NULL,
  `ms_id_finish_node` varchar(255) DEFAULT NULL,
  `ms_label` varchar(255) DEFAULT NULL,
  `createdby` varchar(255) DEFAULT '1',
  `created` datetime DEFAULT CURRENT_TIMESTAMP,
  `updatedby` varchar(255) DEFAULT '1',
  `updated` datetime DEFAULT CURRENT_TIMESTAMP,
  `ms_branch_type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ms_id_edge`),
  KEY `ix_ms_cfg_edge_ms_id_edge` (`ms_id_edge`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ms_cfg_node`
--

DROP TABLE IF EXISTS `ms_cfg_node`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ms_cfg_node` (
  `ms_id_node` varchar(255) NOT NULL,
  `ms_id_modul` varchar(255) DEFAULT NULL,
  `ms_line_number` int DEFAULT NULL,
  `ms_source_code` text,
  `createdby` varchar(255) DEFAULT '1',
  `created` datetime DEFAULT CURRENT_TIMESTAMP,
  `updatedby` varchar(255) DEFAULT '1',
  `updated` datetime DEFAULT CURRENT_TIMESTAMP,
  `ms_execution_order` int DEFAULT NULL,
  `ms_line_start` int DEFAULT NULL,
  `ms_line_end` int DEFAULT NULL,
  `ms_ast_node_type` varchar(100) DEFAULT NULL,
  `ms_node_type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ms_id_node`),
  KEY `ix_ms_cfg_node_ms_id_node` (`ms_id_node`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ms_class`
--

DROP TABLE IF EXISTS `ms_class`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ms_class` (
  `ms_class_id` varchar(255) NOT NULL,
  `ms_class_grade` varchar(10) DEFAULT NULL,
  `ms_class_major` varchar(100) DEFAULT NULL,
  `ms_class_class` varchar(10) DEFAULT NULL,
  `ms_class_teacher` varchar(100) DEFAULT NULL,
  `ms_class_description` varchar(255) DEFAULT NULL,
  `ms_class_total_hour` varchar(10) DEFAULT NULL,
  `createdby` varchar(255) DEFAULT NULL,
  `created` date DEFAULT NULL,
  `updatedby` varchar(255) DEFAULT NULL,
  `updated` date DEFAULT NULL,
  PRIMARY KEY (`ms_class_id`),
  KEY `ix_ms_class_ms_class_id` (`ms_class_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ms_modul_parameter`
--

DROP TABLE IF EXISTS `ms_modul_parameter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ms_modul_parameter` (
  `ms_id_parameter` varchar(255) NOT NULL,
  `ms_id_modul` varchar(255) DEFAULT NULL,
  `ms_nama_parameter` varchar(255) DEFAULT NULL,
  `ms_tipe_data` varchar(50) DEFAULT NULL,
  `ms_rules` text,
  `no_urut` int DEFAULT NULL,
  `createdby` varchar(255) DEFAULT '1',
  `created` datetime DEFAULT CURRENT_TIMESTAMP,
  `updatedby` varchar(255) DEFAULT '1',
  `updated` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ms_id_parameter`),
  KEY `ix_ms_modul_parameter_ms_id_parameter` (`ms_id_parameter`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ms_modul_program`
--

DROP TABLE IF EXISTS `ms_modul_program`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ms_modul_program` (
  `ms_id_modul` varchar(255) NOT NULL,
  `ms_jenis_modul` enum('F','P') DEFAULT 'F',
  `ms_nama_modul` varchar(50) DEFAULT NULL,
  `ms_deskripsi_modul` text,
  `ms_source_code` varchar(255) DEFAULT NULL,
  `ms_class_name` varchar(255) DEFAULT NULL,
  `ms_function_name` varchar(255) DEFAULT NULL,
  `ms_return_type` varchar(255) DEFAULT NULL,
  `ms_jml_parameter` int DEFAULT NULL,
  `ms_tingkat_kesulitan` varchar(255) DEFAULT NULL,
  `ms_cc` int DEFAULT NULL,
  `createdby` varchar(255) DEFAULT '1',
  `created` datetime DEFAULT CURRENT_TIMESTAMP,
  `updatedby` varchar(255) DEFAULT '1',
  `updated` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ms_id_modul`),
  KEY `ix_ms_modul_program_ms_id_modul` (`ms_id_modul`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ms_student`
--

DROP TABLE IF EXISTS `ms_student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ms_student` (
  `ms_student_id` varchar(255) NOT NULL,
  `isactive` enum('Y','N') DEFAULT 'Y',
  `ms_student_nim` varchar(20) DEFAULT NULL,
  `ms_student_name` varchar(255) DEFAULT NULL,
  `ms_student_kelas` varchar(255) DEFAULT NULL,
  `ms_student_prodi` varchar(255) DEFAULT NULL,
  `ms_student_password` varchar(255) DEFAULT NULL,
  `ms_student_current_token` varchar(512) DEFAULT NULL,
  `ms_student_token` varchar(5) DEFAULT NULL,
  `createdby` varchar(255) DEFAULT '1',
  `created` datetime DEFAULT CURRENT_TIMESTAMP,
  `updatedby` varchar(255) DEFAULT '1',
  `updated` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ms_student_id`),
  KEY `ix_ms_student_ms_student_id` (`ms_student_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ms_system`
--

DROP TABLE IF EXISTS `ms_system`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ms_system` (
  `ms_system_category` varchar(100) NOT NULL,
  `ms_system_sub_category` varchar(100) NOT NULL,
  `ms_system_cd` varchar(100) NOT NULL,
  `ms_system_value` varchar(255) DEFAULT NULL,
  `ms_system_description` varchar(255) DEFAULT NULL,
  `isactive` enum('Y','N') DEFAULT 'Y',
  `createdby` varchar(255) DEFAULT '1',
  `created` datetime DEFAULT CURRENT_TIMESTAMP,
  `updatedby` varchar(255) DEFAULT '1',
  `updated` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ms_system_category`,`ms_system_sub_category`,`ms_system_cd`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ms_teacher`
--

DROP TABLE IF EXISTS `ms_teacher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ms_teacher` (
  `ms_teacher_id` varchar(255) NOT NULL,
  `ms_teacher_kode_dosen` varchar(20) DEFAULT NULL,
  `ms_teacher_name` varchar(255) DEFAULT NULL,
  `isactive` enum('Y','N') DEFAULT 'Y',
  `ms_teacher_password` varchar(255) DEFAULT NULL,
  `ms_teacher_current_token` varchar(512) DEFAULT NULL,
  `ms_teacher_token` varchar(5) DEFAULT NULL,
  `createdby` varchar(255) DEFAULT '1',
  `created` datetime DEFAULT CURRENT_TIMESTAMP,
  `updatedby` varchar(255) DEFAULT '1',
  `updated` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ms_teacher_id`),
  KEY `ix_ms_teacher_ms_teacher_id` (`ms_teacher_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ms_topik_modul`
--

DROP TABLE IF EXISTS `ms_topik_modul`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ms_topik_modul` (
  `ms_id_topik_modul` varchar(255) NOT NULL,
  `ms_id_topik` varchar(255) DEFAULT NULL,
  `ms_id_modul` varchar(255) DEFAULT NULL,
  `ms_no` int DEFAULT NULL,
  `createdby` varchar(255) DEFAULT '1',
  `created` datetime DEFAULT CURRENT_TIMESTAMP,
  `updatedby` varchar(255) DEFAULT '1',
  `updated` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ms_id_topik_modul`),
  KEY `ix_ms_topik_modul_ms_id_topik_modul` (`ms_id_topik_modul`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ms_topik_pengujian`
--

DROP TABLE IF EXISTS `ms_topik_pengujian`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ms_topik_pengujian` (
  `ms_id_topik` varchar(255) NOT NULL,
  `status` enum('D','P') DEFAULT 'D',
  `ms_kode_enroll` varchar(20) DEFAULT NULL,
  `ms_nama_topik` varchar(255) DEFAULT NULL,
  `ms_deskripsi_topik` varchar(255) DEFAULT NULL,
  `createdby` varchar(255) DEFAULT '1',
  `created` datetime DEFAULT CURRENT_TIMESTAMP,
  `updatedby` varchar(255) DEFAULT '1',
  `updated` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ms_id_topik`),
  KEY `ix_ms_topik_pengujian_ms_id_topik` (`ms_id_topik`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tr_cfg_edge`
--

DROP TABLE IF EXISTS `tr_cfg_edge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tr_cfg_edge` (
  `tr_id_edge` varchar(255) NOT NULL,
  `tr_id_topik_modul` varchar(255) NOT NULL,
  `tr_id_student` varchar(255) NOT NULL,
  `tr_status` enum('Y','N') NOT NULL DEFAULT 'N',
  `createdby` varchar(255) NOT NULL DEFAULT '1',
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updatedby` varchar(255) NOT NULL DEFAULT '1',
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`tr_id_edge`,`tr_id_topik_modul`,`tr_id_student`),
  KEY `ix_tr_cfg_edge_tr_id_student` (`tr_id_student`),
  KEY `ix_tr_cfg_edge_tr_id_topik_modul` (`tr_id_topik_modul`),
  KEY `ix_tr_cfg_edge_tr_id_edge` (`tr_id_edge`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tr_cfg_node`
--

DROP TABLE IF EXISTS `tr_cfg_node`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tr_cfg_node` (
  `tr_id_node` varchar(255) NOT NULL,
  `tr_id_topik_modul` varchar(255) NOT NULL,
  `tr_id_student` varchar(255) NOT NULL,
  `tr_status` enum('Y','N','S') NOT NULL DEFAULT 'N',
  `createdby` varchar(255) NOT NULL DEFAULT '1',
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updatedby` varchar(255) NOT NULL DEFAULT '1',
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`tr_id_node`,`tr_id_topik_modul`,`tr_id_student`),
  KEY `ix_tr_cfg_node_tr_id_student` (`tr_id_student`),
  KEY `ix_tr_cfg_node_tr_id_node` (`tr_id_node`),
  KEY `ix_tr_cfg_node_tr_id_topik_modul` (`tr_id_topik_modul`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tr_penyelesaian_modul`
--

DROP TABLE IF EXISTS `tr_penyelesaian_modul`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tr_penyelesaian_modul` (
  `tr_id_topik_modul` varchar(255) NOT NULL,
  `tr_student_id` varchar(255) NOT NULL,
  `tr_nilai` float DEFAULT NULL,
  `tr_tgl_mulai` datetime NOT NULL,
  `tr_tgl_selesai` datetime DEFAULT NULL,
  `tr_persentase_coverage` float DEFAULT NULL,
  `tr_result_report` text,
  `tr_coverage_report` text,
  `tr_tgl_eksekusi` datetime DEFAULT NULL,
  `tr_status_eksekusi` enum('Y','N') NOT NULL DEFAULT 'N',
  `tr_status_penyelesaian` enum('Y','N') NOT NULL DEFAULT 'N',
  `createdby` varchar(255) NOT NULL DEFAULT '1',
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updatedby` varchar(255) NOT NULL DEFAULT '1',
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`tr_id_topik_modul`,`tr_student_id`),
  KEY `ix_tr_penyelesaian_modul_tr_id_topik_modul` (`tr_id_topik_modul`),
  KEY `ix_tr_penyelesaian_modul_tr_student_id` (`tr_student_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tr_test_case_modul`
--

DROP TABLE IF EXISTS `tr_test_case_modul`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tr_test_case_modul` (
  `tr_id_test_case` varchar(255) NOT NULL,
  `tr_id_topik_modul` varchar(255) NOT NULL,
  `tr_student_id` varchar(255) NOT NULL,
  `tr_no` int DEFAULT NULL,
  `tr_object_pengujian` text NOT NULL,
  `tr_data_test_input` text,
  `tr_expected_result` text,
  `tr_test_result` enum('P','F') DEFAULT NULL,
  `createdby` varchar(255) NOT NULL DEFAULT '1',
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updatedby` varchar(255) NOT NULL DEFAULT '1',
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`tr_id_test_case`),
  KEY `ix_tr_test_case_modul_tr_id_test_case` (`tr_id_test_case`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'local_flow_kit_2'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-09 13:10:23
