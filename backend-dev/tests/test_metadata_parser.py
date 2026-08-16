import pytest
from unittest.mock import MagicMock
from services.modul_service import ModulService

class TestModulServiceMetadataParser:
    
    def setup_method(self):
        # Setup ModulService with mocked dependencies
        self.modul_repo = MagicMock()
        self.modul_repo.find_by_class_name.return_value = None
        self.cfg_service = MagicMock()
        self.file_manager = MagicMock()
        self.service = ModulService(
            modul_repo=self.modul_repo,
            cfg_service=self.cfg_service,
            file_manager=self.file_manager
        )

    def test_parse_metadata_success_single_method(self):
        java_code = """
        public class SimpleCalculator {
            public int add(int x, int y) {
                return x + y;
            }
        }
        """
        result = self.service.parse_metadata(java_code)
        
        assert result["class_name"] == "SimpleCalculator"
        assert len(result["methods"]) == 1
        
        method = result["methods"][0]
        assert method["method_name"] == "add"
        assert method["return_type"] == "int"
        assert len(method["parameters"]) == 2
        
        assert method["parameters"][0]["param_name"] == "x"
        assert method["parameters"][0]["param_type"] == "int"
        
        assert method["parameters"][1]["param_name"] == "y"
        assert method["parameters"][1]["param_type"] == "int"

    def test_parse_metadata_rejects_multiple_methods(self):
        java_code = """
        class Helper {
            public String greet(String prefix, char initial) {
                return prefix + initial;
            }
            
            private double calculate(float multiplier, boolean active) {
                return 0.0;
            }
        }
        """
        with pytest.raises(ValueError) as exc_info:
            self.service.parse_metadata(java_code)
        assert "hanya mendukung 1 method" in str(exc_info.value)

    def test_parse_metadata_rejects_void_return_type(self):
        java_code = """
        public class Logger {
            public void logMessage(String msg) {}
        }
        """
        with pytest.raises(ValueError) as exc_info:
            self.service.parse_metadata(java_code)
        assert "bertipe 'void'" in str(exc_info.value)

    def test_parse_metadata_syntax_error(self):
        # Missing closing brace to trigger syntax error
        java_code = """
        public class Broken {
            public int add(int x, int y) {
                return x + @@@;
            }
        }
        """
        with pytest.raises(ValueError) as exc_info:
            self.service.parse_metadata(java_code)
        
        assert "Java source code has syntax errors" in str(exc_info.value)

    def test_parse_metadata_description_extraction(self):
        java_code = """
        /* Program: isVokal
         * Deskripsi: Memeriksa apakah suatu karakter merupakan huruf vokal atau bukan
         * Nama: Muhammad Saiful Islam/141524020
         * Tanggal/versi: 24 Oktober 2014/v.0
         */
        public class IsVokal {
            public boolean isVokal(char huruf) {
                return true;
            }
        }
        """
        result = self.service.parse_metadata(java_code)
        assert result["class_name"] == "IsVokal"
        assert result["description"] == "Memeriksa apakah suatu karakter merupakan huruf vokal atau bukan"

    def test_parse_metadata_multiline_description_extraction(self):
        java_code = """
        /**
         * Deskripsi :
         * Melakukan analisis terhadap kombinasi lima buah perulangan bersarang
         * berdasarkan nilai parameter limit. Parameter limit menentukan jumlah
         * iterasi pada setiap tingkat perulangan.
         * Nama: Muhammad Saiful Islam/141524020
         */
        public class NestedLoop {
            public int analyze(int limit) { return limit; }
        }
        """
        result = self.service.parse_metadata(java_code)
        assert result["class_name"] == "NestedLoop"

    def test_parse_metadata_rejects_comment_only_file(self):
        java_code = """
        /*
         * Ini hanya deskripsi modul saja.
         * Tidak ada kode class Java.
         */
        """
        with pytest.raises(ValueError) as exc_info:
            self.service.parse_metadata(java_code)
        assert "hanya berisi komentar" in str(exc_info.value)

    def test_parse_metadata_rejects_empty_method_body(self):
        java_code = """
        public class Hitung {
            public int hitungBiaya(int x) {
                // Method body kosong tanpa instruksi
            }
        }
        """
        with pytest.raises(ValueError) as exc_info:
            self.service.parse_metadata(java_code)
        assert "method body kosong" in str(exc_info.value)
