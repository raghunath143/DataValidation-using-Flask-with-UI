
import sqlite3

from sqlite3 import Error

try:
    conn = sqlite3.connect("IdeaQAdb.db", check_same_thread=False)

    sql_create_QA_Connection_table = """CREATE TABLE IF NOT EXISTS QAConnection
                 (Connection_ID integer PRIMARY KEY AUTOINCREMENT, 
                 Connection_Name text NOT NULL, 
                 Server text NOT NULL, Username text NOT NULL, 
                 Password text NOT NULL, Database text NOT NULL, 
                 Connection_Desc text);"""

    c = conn.cursor()
    c.execute(sql_create_QA_Connection_table)
    conn.commit()

    #    print(c.fetchall())

    sql_create_QA_login_table = """CREATE TABLE IF NOT EXISTS QA_login (
                                       User_ID integer PRIMARY KEY AUTOINCREMENT,
                                       Username text NOT NULL,
                                       Password text NOT NULL,
                                       Email text NOT NULL,
                                       Active boolean NOT NULL,
                                       Access_Type text
                                       );"""
    c1 = conn.cursor()
    c1.execute(sql_create_QA_login_table)
    conn.commit()

    sql_create_QA_Testcase_table = """ CREATE TABLE IF NOT EXISTS QA_Testcase 
                          (Testcase_ID integer PRIMARY KEY AUTOINCREMENT,
                            Testcase_Group text NOT NULL,
                            Testcase_Desc text,
                             Selected_Testcases text NOT NULL);"""

    c2 = conn.cursor()
    c2.execute(sql_create_QA_Testcase_table)
    conn.commit()

    sql_create_QA_TestGroup_table = """CREATE TABLE IF NOT EXISTS QA_testcasegroup(
                                       testcasegroup_ID integer PRIMARY KEY AUTOINCREMENT,
                                       testcase_ID integer NOT NULL,
                                       testcasegroup_Name text,
                                       testcasegroup_Description text,
                                       FOREIGN KEY (testcase_ID) REFERENCES QA_Testcase(testcase_ID)                                  
                                       );"""
    c3 = conn.cursor()
    c3.execute(sql_create_QA_TestGroup_table)

    conn.commit()

    sql_create_QA_Result_table = """CREATE TABLE IF NOT EXISTS QA_Results (Execution_ID integer PRIMARY KEY, 
                Source_Name text NOT NULL, Target_Name text NOT NULL, 
                Testcase_Group text NOT NULL, Testcase_Name text NOT NULL,
                Validation_Status text NOT NULL, Report text);"""
    c4 = conn.cursor()
    c4.execute(sql_create_QA_Result_table)

    conn.commit()

    sql_create_QA_user_table = """ CREATE TABLE IF NOT EXISTS user (
                                       id integer PRIMARY KEY AUTOINCREMENT,
                                       username varchar(255),
                                       email varchar(255),
                                       password varchar(255));"""

    c5 = conn.cursor()

    c5.execute(sql_create_QA_user_table)

    conn.commit()

    conn.close()

except Error as e:
    print(e)





