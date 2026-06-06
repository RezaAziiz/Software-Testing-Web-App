import os
import json
from typing import List, Dict, Any

class TestCodeGenerator:
    
    def generate_junit_class(
        self, 
        class_name: str, 
        function_name: str, 
        return_type: str, 
        test_cases: List[Dict[str, Any]], 
        output_path: str
    ) -> str:
        filename = f"{class_name}Test.java"
        target_file = os.path.join(output_path, filename)
        
        with open(target_file, 'w') as file:
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
                file.write(f'\t\t{return_type} actual = objectTest.{function_name}(')
                
                # Generate parameters
                for i, param in enumerate(data_test):
                    p_type = param.get('param_type')
                    p_value = param.get('param_value')
                    
                    if p_type == 'String': 
                        if p_value == "{}":
                            file.write('""')
                        elif p_value == "{null}":
                            file.write('null')
                        else:    
                            file.write(f'"{p_value}"')
                    elif p_type == 'char':
                        file.write(f"'{p_value}'")
                    elif p_type == 'float':
                        file.write(f"{p_value}f")
                    else:
                        file.write(str(p_value))
                    
                    # Add separator if not last parameter
                    if i + 1 < len(data_test):
                        file.write(', ')
                
                file.write(');\n')
                
                # Generate assertions
                expected = test_case['tr_expected_result']
                file.write('\t\tAssert.assertEquals(')
                
                if return_type == 'String': 
                    file.write(f'"{expected}"')
                elif return_type == 'char':
                    file.write(f"'{expected}'")
                else:
                    file.write(str(expected))
                    
                # Handling for double/float needs delta in assert
                if return_type in ['float', 'double']: 
                    file.write(', actual, 0.0f);\n')
                else:
                    file.write(', actual);\n')

                file.write('\t}\n\n')   
                
            file.write('}\n')
            
        return target_file