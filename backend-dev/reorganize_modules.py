"""
Script untuk mereorganisasi file Java di folder modules/
dari struktur flat menjadi subfolder per ms_id_modul.

Sebelum: modules/HitungPengurangan.java
Sesudah: modules/{ms_id_modul}/HitungPengurangan.java
"""

import os
import shutil
import pymysql

# Database config (sesuai .env)
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'local_flow_kit'
}

MODULES_DIR = os.path.join(os.path.dirname(__file__), 'modules')

def main():
    # Connect to database
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    
    # Get all modules with source code info
    cursor.execute("SELECT ms_id_modul, ms_nama_modul, ms_source_code, ms_class_name FROM ms_modul_program")
    modules = cursor.fetchall()
    
    print(f"{'='*80}")
    print(f"  REORGANISASI FILE MODULES")
    print(f"{'='*80}")
    print(f"\nDitemukan {len(modules)} modul di database.\n")
    
    # Show current flat files
    flat_files = [f for f in os.listdir(MODULES_DIR) if f.endswith('.java')]
    print(f"File Java flat di modules/: {len(flat_files)}")
    for f in flat_files:
        print(f"  📄 {f}")
    print()
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for modul in modules:
        id_modul = modul['ms_id_modul']
        nama = modul['ms_nama_modul']
        source_code = modul['ms_source_code']
        class_name = modul['ms_class_name']
        
        print(f"{'─'*60}")
        print(f"Modul: {nama}")
        print(f"  ID:          {id_modul}")
        print(f"  Source Code: {source_code}")
        print(f"  Class Name:  {class_name}")
        
        if source_code is None:
            print(f"  ⚠️  SKIP: ms_source_code = NULL")
            skip_count += 1
            continue
        
        # Check if subfolder already exists
        subfolder = os.path.join(MODULES_DIR, id_modul)
        target_file = os.path.join(subfolder, source_code)
        
        if os.path.exists(target_file):
            print(f"  ✅ SUDAH ADA: {id_modul}/{source_code}")
            skip_count += 1
            continue
        
        # Check if flat file exists
        source_file = os.path.join(MODULES_DIR, source_code)
        if not os.path.exists(source_file):
            # Try with class name + .java
            alt_source = os.path.join(MODULES_DIR, class_name + '.java')
            if os.path.exists(alt_source):
                source_file = alt_source
                print(f"  ℹ️  File ditemukan dengan nama alternatif: {class_name}.java")
            else:
                print(f"  ❌ ERROR: File '{source_code}' tidak ditemukan di modules/")
                error_count += 1
                continue
        
        # Create subfolder and copy file
        os.makedirs(subfolder, exist_ok=True)
        shutil.copy2(source_file, target_file)
        print(f"  ✅ BERHASIL: {source_code} → {id_modul}/{source_code}")
        success_count += 1
    
    cursor.close()
    connection.close()
    
    print(f"\n{'='*80}")
    print(f"  RINGKASAN")
    print(f"{'='*80}")
    print(f"  ✅ Berhasil dipindahkan: {success_count}")
    print(f"  ⏭️  Dilewati (sudah ada/NULL): {skip_count}")
    print(f"  ❌ Error (file tidak ditemukan): {error_count}")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
