import os
import logging
from xml.dom import minidom
from typing import Dict, Any, Tuple, List

logger = logging.getLogger(__name__)

class JUnitResultParser:
    """Murni menangani parsing file XML hasil unit testing JUnit."""
    
    def parse(self, xml_path: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Membaca report JUnit dan mengembalikan status keseluruhan serta detail tiap test.
        
        Returns:
            Tuple[bool, List[dict]]: 
            - is_all_passed (True jika tidak ada yang fail)
            - detail_results (List berisi dict dengan nama test dan status P/F)
        """
        if not os.path.exists(xml_path):
            logger.warning(f"Test result XML not found: {xml_path}")
            return False, []

        try:
            data_result_test = minidom.parse(xml_path)
            tag_testcase = data_result_test.getElementsByTagName('testcase')
            
            is_failed_case = False
            detail_results = []
            
            for test_case in tag_testcase:
                child_nodes = test_case.childNodes
                name_case = test_case.getAttribute("name")
                
                # Jika tidak ada child node (seperti <failure> atau <error>), berarti Pass
                if len(child_nodes) == 0: 
                    result_test = 'P'
                else:
                    result_test = 'F'
                    is_failed_case = True
                
                # Standarisasi nama agar spasi / underscore konsisten
                formatted_name = name_case.replace("_", " ")
                
                detail_results.append({
                    "test_name": formatted_name,
                    "status": result_test
                })
                
            return (not is_failed_case), detail_results
            
        except Exception as e:
            logger.error(f"Error parsing JUnit XML {xml_path}: {str(e)}")
            return False, []