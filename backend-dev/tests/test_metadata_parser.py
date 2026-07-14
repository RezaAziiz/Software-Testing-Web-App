import pytest
from unittest.mock import MagicMock
from services.modul_service import ModulService

class TestModulServiceMetadataParser:
    
    def setup_method(self):
        # Setup ModulService with mocked dependencies
        self.modul_repo = MagicMock()
        self.cfg_service = MagicMock()
        self.file_manager = MagicMock()
        self.gradle_executor = MagicMock()
        self.service = ModulService(
            modul_repo=self.modul_repo,
            cfg_service=self.cfg_service,
            file_manager=self.file_manager,
            gradle_executor=self.gradle_executor
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

    def test_parse_metadata_success_multiple_methods_and_types(self):
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
        result = self.service.parse_metadata(java_code)
        
        assert result["class_name"] == "Helper"
        assert len(result["methods"]) == 2
        
        greet_method = result["methods"][0]
        assert greet_method["method_name"] == "greet"
        assert greet_method["return_type"] == "String"
        assert len(greet_method["parameters"]) == 2
        assert greet_method["parameters"][0] == {"param_name": "prefix", "param_type": "String"}
        assert greet_method["parameters"][1] == {"param_name": "initial", "param_type": "char"}
        
        calc_method = result["methods"][1]
        assert calc_method["method_name"] == "calculate"
        assert calc_method["return_type"] == "double"
        assert len(calc_method["parameters"]) == 2
        assert calc_method["parameters"][0] == {"param_name": "multiplier", "param_type": "float"}
        assert calc_method["parameters"][1] == {"param_name": "active", "param_type": "boolean"}

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
