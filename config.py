# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 16:59:28 2020

@author: skuruba
"""

validation_list = ['rowcount', 'columncount', 'nullcount']

sqlit_dict = {'rowcount': 'preprocess', 'columncount': 'preprocess', 'nullcount': 'postprocess'}
sqlitedb_file = r'C:\Users\rsiripud\PycharmProjects\flaskIdea\IdeaQAdb.db'
input_path = r'C:\\Users\\rsiripud\\Downloads\\TeraJDBC__indep_indep.16.20.00.13\\'


installs = ['python.exe -m pip install jaydebeapi',
'python.exe -m pip install pandas',
'python.exe -m pip install xlwt',
'python.exe -m pip install pyodbc',
'python -m pip install flask-bootstrap',
'python -m pip install flask-wtf',
'python -m pip install flask-sqlalchemy',
'python -m pip install flask-login',
'python -m pip install email_validator']


