import pandas as pd
import pyodbc 
import os
import glob
conn1 = pyodbc.connect('Driver={SQL Server};' 
                      'Server=192.168.0.117;'
                      'Database=AJWorldWide;'
                      'UID=ajview;'
                      'PWD=aj$%^World@123;'
                      'Trusted_Connection=no;'
                      )

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=192.168.0.117;'
                      'Database=BI;'
                      'UID=BI;'
                      'PWD=BI$%^app;'
                      'Trusted_Connection=no;'
                      )