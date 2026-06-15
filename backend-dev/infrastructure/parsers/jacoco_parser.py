import os
import logging
from xml.dom import minidom
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class JaCoCoParser:
    """Murni menangani parsing file XML hasil code coverage dari JaCoCo."""

    def parse_method_coverage(self, xml_path: str, method_name: str) -> float:
        """
        Mengekstrak persentase coverage khusus untuk satu method tertentu.
        
        Returns:
            float: Persentase coverage (0.0 - 100.0)
        """
        if not os.path.exists(xml_path):
            logger.warning(f"Coverage result XML not found: {xml_path}")
            return 0.0
            
        try:
            data_coverage_test = minidom.parse(xml_path)
            tag_methods = data_coverage_test.getElementsByTagName('method')
            
            total_node = 0
            total_covered = 0
            
            for method in tag_methods:
                name_case = method.getAttribute("name")
                if name_case == method_name: 
                    child_nodes = method.childNodes
                    for child in child_nodes:
                        type_name = child.getAttribute("type")
                        # Abaikan deklarasi method itu sendiri, hitung instruksi/branch di dalamnya
                        if type_name != "METHOD":
                            total_node += int(child.getAttribute("missed"))
                            total_node += int(child.getAttribute("covered"))
                            total_covered += int(child.getAttribute("covered"))
            
            if total_node == 0:
                return 0.0
                
            coverage_percent = round((total_covered / total_node) * 100, 2)
            return coverage_percent
            
        except Exception as e:
            logger.error(f"Error parsing JaCoCo Coverage XML {xml_path}: {str(e)}")
            return 0.0

    def parse_line_execution_status(self, xml_path: str) -> List[Dict[str, Any]]:
        """
        Mengekstrak status eksekusi (Fully, Partially, Not Executed) per baris kode.
        
        Returns:
            List[dict]: Daftar baris dan statusnya [{'line_number': 10, 'status': 'Y'/'N'/'S'}]
        """
        if not os.path.exists(xml_path):
            logger.warning(f"Coverage line XML not found: {xml_path}")
            return []
            
        try:
            data_coverage_test = minidom.parse(xml_path)
            tag_lines = data_coverage_test.getElementsByTagName('line')
            
            line_statuses = []
            
            for line in tag_lines:
                line_number = int(line.getAttribute('nr'))
                ci = int(line.getAttribute('ci')) # Covered Instructions
                mb = int(line.getAttribute('mb')) # Missed Branches
                
                # Tentukan status eksekusi untuk baris ini
                if ci == 0:               
                    # Tidak ada instruksi yang ter-cover sama sekali
                    status_executed = 'N'
                elif mb > 0:              
                    # Ada branch miss (sebagian ter-cover)
                    status_executed = 'S'
                else:                     
                    # Fully executed
                    status_executed = 'Y'
                    
                line_statuses.append({
                    "line_number": line_number,
                    "status": status_executed
                })
                
            return line_statuses
            
        except Exception as e:
            logger.error(f"Error parsing JaCoCo Line Status XML {xml_path}: {str(e)}")
            return []