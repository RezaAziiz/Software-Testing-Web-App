import os
import pytest
from infrastructure.parsers.jacoco_parser import JaCoCoParser

class TestJaCoCoParser:
    def test_parse_line_execution_status_not_found(self):
        """
        Test Case Name: Parsing Status Eksekusi Baris - File Tidak Ditemukan
        Precondition: Path file XML coverage line yang diberikan tidak eksis di direktori.
        Step to Execute: 
            1. Inisialisasi JaCoCoParser.
            2. Panggil parse_line_execution_status() dengan string "non_existent_file.xml".
        Test Data: "non_existent_file.xml"
        Expected Result: Method mengembalikan list kosong [].
        """
        parser = JaCoCoParser()
        result = parser.parse_line_execution_status("non_existent_file.xml")
        assert result == []

    def test_parse_line_execution_status_success(self, tmp_path):
        """
        Test Case Name: Parsing Status Eksekusi Baris - Sukses
        Precondition: File XML coverage line valid tersedia dengan atribut `ci` dan `mb`.
        Step to Execute: 
            1. Buat file dummy XML menggunakan tmp_path.
            2. Inisialisasi JaCoCoParser.
            3. Panggil parse_line_execution_status() menggunakan path file dummy tersebut.
        Test Data:
            - XML berisi baris 1 (ci=0, mb=0), baris 2 (ci=2, mb=1), baris 3 (ci=5, mb=0).
        Expected Result: Method mengembalikan 3 elemen dengan status baris 1 'N', baris 2 'S', baris 3 'Y'.
        """
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<report name="test"><package name="com.example"><class name="com.example.Main">
<method name="testMethod" desc="()V" line="1"><line nr="1" mi="0" ci="0" mb="0" cb="0"/><line nr="2" mi="0" ci="2" mb="1" cb="1"/><line nr="3" mi="0" ci="5" mb="0" cb="2"/></method>
</class></package></report>"""
        xml_file = tmp_path / "coverage.xml"
        xml_file.write_text(xml_content)
        
        parser = JaCoCoParser()
        result = parser.parse_line_execution_status(str(xml_file))
        
        assert len(result) == 3
        assert result[0] == {"line_number": 1, "status": "N"}
        assert result[1] == {"line_number": 2, "status": "S"}
        assert result[2] == {"line_number": 3, "status": "Y"}

    def test_parse_line_execution_status_exception(self, tmp_path):
        """
        Test Case Name: Parsing Status Eksekusi Baris - Format XML Salah (Exception)
        Precondition: File XML tersedia namun isinya terkorupsi / tidak valid.
        Step to Execute: 
            1. Buat file dummy XML dengan tag yang tidak ditutup.
            2. Inisialisasi JaCoCoParser.
            3. Panggil parse_line_execution_status().
        Test Data: XML = "<invalid><unclosed>"
        Expected Result: Method menangkap Exception dan mengembalikan list kosong [].
        """
        xml_file = tmp_path / "invalid.xml"
        xml_file.write_text("<invalid><unclosed>")
        
        parser = JaCoCoParser()
        result = parser.parse_line_execution_status(str(xml_file))
        assert result == []

    def test_parse_method_coverage_not_found(self):
        """
        Test Case Name: Parsing Coverage Method - File Tidak Ditemukan
        Precondition: Path file XML coverage method yang diberikan tidak eksis.
        Step to Execute: 
            1. Inisialisasi JaCoCoParser.
            2. Panggil parse_method_coverage() dengan nama method dan file fiktif.
        Test Data: File "non_existent_file.xml", Method = "method"
        Expected Result: Mengembalikan float 0.0.
        """
        parser = JaCoCoParser()
        result = parser.parse_method_coverage("non_existent_file.xml", "method")
        assert result == 0.0

    def test_parse_method_coverage_success(self, tmp_path):
        """
        Test Case Name: Parsing Coverage Method - Sukses
        Precondition: File XML coverage tersedia berisi perhitungan INSTRUCTION, BRANCH, dll untuk suatu method.
        Step to Execute: 
            1. Buat dummy XML yang valid.
            2. Inisialisasi JaCoCoParser.
            3. Panggil parse_method_coverage() untuk "testMethod".
        Test Data: XML dengan "testMethod" memiliki INSTRUCTION covered=8, missed=2 dan BRANCH covered=3, missed=1.
        Expected Result: Menghitung (11 / 14) * 100 = 78.57, lalu mengembalikan 78.57.
        """
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<report name="test"><package name="com.example"><class name="com.example.Main">
<method name="testMethod" desc="()V" line="1"><counter type="INSTRUCTION" missed="2" covered="8"/><counter type="BRANCH" missed="1" covered="3"/><counter type="METHOD" missed="0" covered="1"/></method>
<method name="otherMethod" desc="()V" line="10"><counter type="INSTRUCTION" missed="5" covered="0"/></method>
</class></package></report>"""
        xml_file = tmp_path / "coverage.xml"
        xml_file.write_text(xml_content)
        
        parser = JaCoCoParser()
        result = parser.parse_method_coverage(str(xml_file), "testMethod")
        
        # total_node = 2+8 + 1+3 = 14
        # total_covered = 8 + 3 = 11
        # coverage = 11 / 14 * 100 = 78.57
        assert result == 78.57
        
    def test_parse_method_coverage_zero(self, tmp_path):
        """
        Test Case Name: Parsing Coverage Method - 0 Nodes
        Precondition: Method yang dicari ada di XML, tetapi tidak memiliki counter instruction atau branch di dalamnya.
        Step to Execute: 
            1. Buat XML valid tetapi method-nya kosong tanpa counter tags.
            2. Panggil parse_method_coverage().
        Test Data: "testMethod" = <method></method> kosong.
        Expected Result: Menghindari division by zero dan mengembalikan 0.0.
        """
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<report name="test"><package name="com.example"><class name="com.example.Main">
<method name="testMethod" desc="()V" line="1"></method>
</class></package></report>"""
        xml_file = tmp_path / "coverage_empty.xml"
        xml_file.write_text(xml_content)
        
        parser = JaCoCoParser()
        result = parser.parse_method_coverage(str(xml_file), "testMethod")
        assert result == 0.0

    def test_parse_method_coverage_exception(self, tmp_path):
        """
        Test Case Name: Parsing Coverage Method - Format XML Salah (Exception)
        Precondition: File XML tersedia namun isinya invalid/tidak sesuai standar XML.
        Step to Execute: 
            1. Buat file dummy invalid.
            2. Panggil parse_method_coverage().
        Test Data: XML = "<invalid><unclosed>"
        Expected Result: Exception tertangani dan method mengembalikan 0.0.
        """
        xml_file = tmp_path / "invalid2.xml"
        xml_file.write_text("<invalid><unclosed>")
        
        parser = JaCoCoParser()
        result = parser.parse_method_coverage(str(xml_file), "testMethod")
        assert result == 0.0

    def test_parse_line_execution_status_no_line_tags(self, tmp_path):
        """
        Test Case Name: Parsing Status Eksekusi Baris - XML Valid Namun Tidak Memiliki Tag <line>
        Precondition: XML valid namun method kosong (tidak ada eksekusi baris di dalamnya).
        Step to Execute: 
            1. Buat dummy XML valid yang elemen <method> nya kosong (tanpa child <line>).
            2. Panggil parse_line_execution_status().
        Test Data: XML valid dengan tag <method></method> kosong.
        Expected Result: Method mengembalikan list kosong [].
        """
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<report name="test"><package name="com.example"><class name="com.example.Main">
<method name="testMethod" desc="()V" line="1"></method>
</class></package></report>"""
        xml_file = tmp_path / "coverage_no_lines.xml"
        xml_file.write_text(xml_content)
        
        parser = JaCoCoParser()
        result = parser.parse_line_execution_status(str(xml_file))
        assert result == []

    def test_parse_line_execution_status_missing_attributes(self, tmp_path):
        """
        Test Case Name: Parsing Status Eksekusi Baris - Atribut Tag <line> Hilang (Missing Attributes)
        Precondition: Tag <line> ada namun tidak memiliki atribut krusial seperti 'ci' atau 'nr'.
        Step to Execute: 
            1. Buat dummy XML valid dengan tag <line> yang hanya berisi atribut sebagian.
            2. Panggil parse_line_execution_status().
        Test Data: <line nr="1" /> tanpa atribut ci dan mb.
        Expected Result: ValueError tertangkap oleh blok except, mengembalikan list kosong [].
        """
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<report name="test"><package name="com.example"><class name="com.example.Main">
<method name="testMethod" desc="()V" line="1"><line nr="1" /></method>
</class></package></report>"""
        xml_file = tmp_path / "coverage_missing_attr.xml"
        xml_file.write_text(xml_content)
        
        parser = JaCoCoParser()
        result = parser.parse_line_execution_status(str(xml_file))
        assert result == []

