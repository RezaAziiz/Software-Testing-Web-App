System Requirment:
- Python 3.11.1
- Java 11
- gradle 4.4.1
- mysql 8

Set Mysql to connect with ip:
- open file /etc/mysql/mysql.conf.d/mysqld.conf
- bind-address set to 0.0.0.0

How to run :
- virtualenv env // create environment python for first setup
  or python3 -m virtualenv virtualenv_name  
- source env/bin/activate // activate virtual environment in linux
- D:/location_env/script/activate.bat // activate virtual environment in windows
- pip install -r requirements.txt
- uvicorn main:app --reload

if add new lib execute command:
- pip freeze > requirements.txt // get version of lib

Build app :
- pyinstaller main.py
- copy folder assets to /dist/main
- copy folder templates to /dist/main
- copy file firebase.json to /dist/main
- create file .env in folder /dist/main

run from dist :
- ./dist/main/main 

Create file migration alembic :
- alembic revision -m "create table pegawai"

Drop all table migration :
- alembic downgrade base

Create and run initial table :
- alembic upgrade head

run on server linux (on background) with dist file :
- ./main >output.log 2>&1 &

how to stop app in server (linux) with dist file :
check pid : lsof -i -P -n | grep LISTEN
stop process : kill [pid]

setup python as service:
https://websofttechs.com/tutorials/how-to-setup-python-script-autorun-in-ubuntu-18-04/
- copy file vms_backend.service to /etc/system/systemd/system folder
- reload service sudo systemctl daemon-reload
- enable service sudo systemctl enable test-py.service
- start service sudo systemctl start test-py.service
- log file in /var/log/syslog

copy from docker :
- docker cp {container_name}:{location_folder}/workspaces/python-3/vms-py-vue/backend/dist dist

JACOCO PLUGIN
- Java 11 -> install di linux: sudo apt-get install openjdk-11-jdk
- Gradle 4.4.1 -> install di linux: sudo apt-get install gradle

JACOCO PLUGIN
- Java 17 -> install di linux: sudo apt-get install openjdk-17-jdk
- Gradle 7.5.1 -> install di linux: sudo apt-get install gradle

SQL Alchemy -> 1.4.45

TROUBLESHOOT:
Error : python: error while loading shared libraries: libpython3.11m.so.1.0: cannot open shared object file: No such file or directory
Solution : 
- install python3.11-dev : apt-get install python3.11-dev
- export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/location_python_lib 
example : export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

Error : no module name 'websocket'
Solution : install websocket client : pip install websocket-client

Error : No module named 'firebase_admin'
Solution : install firebase-admin : pip install firebase_admin

Error :
Traceback (most recent call last):
  File "PyInstaller\loader\pyimod02_importers.py", line 22, in <module>
  File "pathlib.py", line 14, in <module>
  File "urllib\parse.py", line 40, in <module>
ModuleNotFoundError: No module named 'ipaddress'
Traceback (most recent call last):
  File "PyInstaller\loader\pyiboot01_bootstrap.py", line 17, in <module>
ModuleNotFoundError: No module named 'pyimod02_importers'
[3236] Failed to execute script 'pyiboot01_bootstrap' due to unhandled exception!
Solution : 
uninstall pyinstaller : pip uninstall pyinstaller (5.6)
install pyinstaller : pip install pyinstaller (6.6)

Error: Unsupported locale
Solution : sudo dpkg-reconfigure locales
- pilih locale id_ID.utf8