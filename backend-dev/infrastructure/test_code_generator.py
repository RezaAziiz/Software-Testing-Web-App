import io
import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

class TestCodeGenerator:
    
    def parse_array_value(self, value: str) -> list[str]:
        if not value:
            return []
        value = value.strip()
        # Check if it looks like a JSON array
        if value.startswith('[') and value.endswith(']'):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except:
                pass
        # If it is inside curly braces {1, 2, 3}
        if value.startswith('{') and value.endswith('}'):
            value = value[1:-1].strip()
            if not value:
                return []
        
        # robust split by comma using csv reader to support quotes and escaping
        import csv
        try:
            reader = csv.reader([value], skipinitialspace=True)
            for row in reader:
                return row
        except:
            pass
        
        return [item.strip() for item in value.split(',') if item.strip()]

    def format_single_value(self, p_type: str, p_value: str) -> str:
        if p_type == 'String':
            if p_value == "{}":
                return '""'
            elif p_value == "{null}":
                return 'null'
            else:
                # Escape double quotes inside the string for Java code
                escaped = str(p_value).replace('"', '\\"')
                return f'"{escaped}"'
        elif p_type == 'char':
            # Remove any outer single quotes first to prevent double-wrapping
            val = str(p_value).strip("'")
            return f"'{val}'"
        elif p_type == 'float':
            return f"{p_value}f"
        elif p_type == 'double':
            return f"{p_value}d"
        elif p_type == 'boolean':
            return str(p_value).lower()
        else:
            return str(p_value)

    def format_value(self, p_type: str, p_value: str) -> str:
        if p_type.endswith('[]'):
            base_type = p_type[:-2]
            elements = self.parse_array_value(p_value)
            formatted_elements = [self.format_single_value(base_type, el) for el in elements]
            return f"new {base_type}[]{{{', '.join(formatted_elements)}}}"
        else:
            return self.format_single_value(p_type, p_value)

    def generate_junit_class(
        self, 
        class_name: str, 
        function_name: str, 
        return_type: str, 
        test_cases: list[dict[str, Any]],
        output_path: str
    ) -> str:
        filename = f"{class_name}Test.java"
        os.makedirs(output_path, exist_ok=True)
        target_file = os.path.join(output_path, filename)
        file = io.StringIO()

        try:
            file.write('import org.junit.Assert;\n')
            file.write('import org.junit.Test;\n\n')
            
            file.write(f'public class {class_name}Test {{\n')
            
            for test_case in test_cases:
                # Handle JSON string parsing gracefully
                data_test = test_case['tr_data_test_input']
                if isinstance(data_test, str):
                    data_test = json.loads(data_test)
                
                method_test_name = test_case['tr_object_pengujian'].replace(" ", "_")
                
                file.write('\t@Test\n')
                file.write(f'\tpublic void {method_test_name}() {{\n')
                file.write(f'\t\t{class_name} objectTest = new {class_name}();\n')
                
                # Assign actual value
                file.write(f'\t\t{return_type} actual = objectTest.{function_name}(')
                
                # Generate parameters
                for i, param in enumerate(data_test):
                    p_type = param.get('param_type')
                    p_value = param.get('param_value')
                    
                    formatted_val = self.format_value(p_type, p_value)
                    file.write(formatted_val)
                    
                    # Add separator if not last parameter
                    if i + 1 < len(data_test):
                        file.write(', ')
                
                file.write(');\n')
                
                # Generate assertions
                expected = test_case['tr_expected_result']
                
                if return_type.endswith('[]'):
                    # Use assertArrayEquals for arrays
                    formatted_expected = self.format_value(return_type, expected)
                    base_type = return_type[:-2]
                    if base_type in ['float', 'double']:
                        file.write(f'\t\tAssert.assertArrayEquals({formatted_expected}, actual, 0.0f);\n')
                    else:
                        file.write(f'\t\tAssert.assertArrayEquals({formatted_expected}, actual);\n')
                else:
                    # Use assertEquals for scalars
                    formatted_expected = self.format_value(return_type, expected)
                    if return_type in ['float', 'double']:
                        file.write(f'\t\tAssert.assertEquals({formatted_expected}, actual, 0.0f);\n')
                    else:
                        file.write(f'\t\tAssert.assertEquals({formatted_expected}, actual);\n')

                file.write('\t}\n\n')   
                
            file.write('}\n')
            generated_content = file.getvalue()
        finally:
            file.close()

        current_content = None
        existed = os.path.exists(target_file)
        mtime_before = os.stat(target_file).st_mtime_ns if existed else None
        if existed:
            with open(target_file, 'r') as current_file:
                current_content = current_file.read()

        rewritten = current_content != generated_content
        if rewritten:
            with open(target_file, 'w') as target:
                target.write(generated_content)

        logger.info(
            "[SOURCE PROFILE] Test source path=%s existed=%s content_unchanged=%s "
            "rewritten=%s mtime_before_ns=%s mtime_after_ns=%s",
            target_file,
            existed,
            existed and not rewritten,
            rewritten,
            mtime_before,
            os.stat(target_file).st_mtime_ns,
        )
        return target_file