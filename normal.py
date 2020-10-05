# -*- coding: utf-8 -*-

"""

Created on Thu Sep 10 15:52:07 2020



@author: skuruba

"""

import pandas as pd

import datacompy

import os

from flask import Flask, request, render_template, jsonify, redirect, url_for

import requests

import jaydebeapi

import pyodbc

import sqlite3

from sqlite3 import Error

import config

import matplotlib.pyplot as plt

app = Flask(__name__)

validation_list = config.validation_list

sqlit_dict = config.sqlit_dict

sqlitedb_file = config.sqlitedb_file

input_path = config.input_path








@app.route('/querycompare', methods=['GET', 'POST'])
def comparision():
    def create_connection(db_file):

        """ create a database connection to the SQLite database

            specified by db_file

        :param db_file: database file

        :return: Connection object or None

        """

        conn = None

        try:

            conn = sqlite3.connect(db_file)

            return conn

        except Error as e:

            print(e)

        return conn

    def dataframe_summary(compare, sample_count=10):

        """Returns a string representation of a report.  The representation can

        then be printed or saved to a file.

        Parameters

        ----------

        sample_count : int, optional

            The number of sample records to return.  Defaults to 10.

        Returns

        -------

        str

            The report, formatted kinda nicely.

        """

        # Header

        report = render("header.txt")

        df_header = pd.DataFrame(

            {

                "DataFrame": [compare.df1_name, compare.df2_name],

                "Columns": [compare.df1.shape[1], compare.df2.shape[1]],

                "Rows": [compare.df1.shape[0], compare.df2.shape[0]],

            }

        )

        report += df_header[["DataFrame", "Columns", "Rows"]].to_string()

        report += "\n\n"

        return report

    def column_summary(compare, sample_count=10):

        # Column Summary

        report = render(

            "column_summary.txt",

            len(compare.intersect_columns()),

            len(compare.df1_unq_columns()),

            len(compare.df2_unq_columns()),

            compare.df1_name,

            compare.df2_name,

        )

        return report

    def row_summary(compare, sample_count=10):

        # Row Summary

        if compare.on_index:

            match_on = "index"

        else:

            match_on = ", ".join(compare.join_columns)

        report = render(

            "row_summary.txt",

            match_on,

            compare.abs_tol,

            compare.rel_tol,

            compare.intersect_rows.shape[0],

            compare.df1_unq_rows.shape[0],

            compare.df2_unq_rows.shape[0],

            compare.intersect_rows.shape[0] - compare.count_matching_rows(),

            compare.count_matching_rows(),

            compare.df1_name,

            compare.df2_name,

            "Yes" if compare._any_dupes else "No",

        )

        return report

    def column_matching(compare, sample_count=10):

        # Column Matching

        cnt_intersect = compare.intersect_rows.shape[0]

        report = render(

            "column_comparison.txt",

            len([col for col in compare.column_stats if col["unequal_cnt"] > 0]),

            len([col for col in compare.column_stats if col["unequal_cnt"] == 0]),

            sum([col["unequal_cnt"] for col in compare.column_stats]),

        )

        return report

    def column_unequal_values(compare, sample_count=10):

        report = render("column_unequal_values.txt")

        match_stats = []

        match_sample = []

        any_mismatch = False

        for column in compare.column_stats:

            if not column["all_match"]:

                any_mismatch = True

                match_stats.append(

                    {

                        "Column": column["column"],

                        "{} dtype".format(compare.df1_name): column["dtype1"],

                        "{} dtype".format(compare.df2_name): column["dtype2"],

                        "# Unequal": column["unequal_cnt"],

                        "Max Diff": column["max_diff"],

                        "# Null Diff": column["null_diff"],

                    }

                )

                if column["unequal_cnt"] > 0:
                    match_sample.append(

                        compare.sample_mismatch(column["column"], sample_count, for_display=True)

                    )

        if any_mismatch:
            report += "Columns with Unequal Values or Types\n"

            df_match_stats = pd.DataFrame(match_stats)

            df_match_stats.sort_values("Column", inplace=True)

            # Have to specify again for sorting

            report += df_match_stats[

                [

                    "Column",

                    "{} dtype".format(compare.df1_name),

                    "{} dtype".format(compare.df2_name),

                    "# Unequal",

                    "Max Diff",

                    "# Null Diff",

                ]

            ].to_string()

            report += "\n\n"

        return report

    def row_unequal_values(compare, sample_count=10):

        report = render("row_unequal_values.txt")

        match_stats = []

        match_sample = []

        any_mismatch = False

        for column in compare.column_stats:

            if not column["all_match"]:

                any_mismatch = True

                match_stats.append(

                    {

                        "Column": column["column"],

                        "{} dtype".format(compare.df1_name): column["dtype1"],

                        "{} dtype".format(compare.df2_name): column["dtype2"],

                        "# Unequal": column["unequal_cnt"],

                        "Max Diff": column["max_diff"],

                        "# Null Diff": column["null_diff"],

                    }

                )

                if column["unequal_cnt"] > 0:
                    match_sample.append(

                        compare.sample_mismatch(column["column"], sample_count, for_display=True)

                    )

        if any_mismatch:

            report += "Sample Rows with Unequal Values\n"

            for sample in match_sample:
                report += sample.to_string()

                report += "\n\n"

        return report

    def sample_df1_unique_rows(compare, sample_count=10):

        report = render("sample_df1_unique_rows.txt")

        if compare.df1_unq_rows.shape[0] > 0:
            report += "Sample Rows Only in {} (First 10 Columns)\n".format(compare.df1_name)

            columns = compare.df1_unq_rows.columns[:10]

            unq_count = min(sample_count, compare.df1_unq_rows.shape[0])

            report += compare.df1_unq_rows.sample(unq_count)[columns].to_string()

            report += "\n\n"

        return report

    def sample_df2_unique_rows(compare, sample_count=10):

        report = render("sample_df2_unique_rows.txt")

        if compare.df2_unq_rows.shape[0] > 0:
            report += "Sample Rows Only in {} (First 10 Columns)\n".format(compare.df2_name)

            columns = compare.df2_unq_rows.columns[:10]

            unq_count = min(sample_count, compare.df2_unq_rows.shape[0])

            report += compare.df2_unq_rows.sample(unq_count)[columns].to_string()

            report += "\n\n"

        return report

    def render(filename, *fields):

        """Renders out an individual template.  This basically just reads in a

        template file, and applies ``.format()`` on the fields.

        Parameters

        ----------

        filename : str

            The file that contains the template.  Will automagically prepend the

            templates directory before opening

        fields : list

            Fields to be rendered out in the template

        Returns

        -------

        str

            The fully rendered out file.

        """

        this_dir = os.path.dirname(os.path.realpath(__file__))

        with open(os.path.join(this_dir, "templates", filename)) as file_open:
            return file_open.read().format(*fields)

    def rowcount(Source_Table, Target_Table):

        if len(Source_Table) == len(Target_Table):

            return 'Sucess'

        else:

            return 'Fail'

    def columncounts(Source_Table, Target_Table):

        if len(Source_Table.columns) == len(Target_Table.columns):

            return 'Sucess'

        else:

            return 'Fail'

    def nullcounts(Source_Table, Target_Table):

        if Source_Table.isnull().sum().sum() == Target_Table.isnull().sum().sum():

            return 'Sucess'

        else:

            return 'Fail'

    def database_table(data, Connection_Name, Table_name):

        data = data[data.Connection_Name == Connection_Name]

        data_dict = data.to_dict()

        database_name = data_dict['Database'][data.index[0]]

        if database_name == 'ideasqldb':

            driver = '{ODBC Driver 17 for SQL Server}'

            server = data_dict['Server'][data.index[0]]

            username = data_dict['Username'][data.index[0]]

            password = data_dict['Password'][data.index[0]]

            conn = pyodbc.connect(
                'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database_name + ';UID=' + username + ';PWD=' + password)

            query = "select * from " + Table_name

            Table = pd.read_sql(query, conn)

            conn.close()



        elif database_name == 'TD_BIM_FR_TRNG_DB':

            driver = 'com.teradata.jdbc.TeraDriver'

            server = data_dict['Server'][data.index[0]]

            user = data_dict['Username'][data.index[0]]

            password = data_dict['Password'][data.index[0]]

            url = 'jdbc:teradata://' + server + '/' + database_name

            driver_args = [user, password]

            jars = input_path + 'terajdbc4.jar'

            conn = jaydebeapi.connect(driver, url, driver_args, jars)

            query = "select * from " + database_name + "." + Table_name

            Table = pd.read_sql(query, conn)

            conn.close()

        return Table

    def database_query(data, Connection_Name, query):

        data = data[data.Connection_Name == Connection_Name]

        data_dict = data.to_dict()

        database_name = data_dict['Database'][data.index[0]]

        if database_name == 'TD_BIM_FR_TRNG_DB':

            driver = 'com.teradata.jdbc.TeraDriver'

            server = data_dict['Server'][data.index[0]]

            user = data_dict['Username'][data.index[0]]

            password = data_dict['Password'][data.index[0]]

            url = 'jdbc:teradata://' + server + '/' + database_name

            driver_args = [user, password]

            jars = input_path + 'terajdbc4.jar'

            conn = jaydebeapi.connect(driver, url, driver_args, jars)

            Table = pd.read_sql(query, conn)

            conn.close()

        elif database_name == 'ideasqldb':

            driver = '{ODBC Driver 17 for SQL Server}'

            server = data_dict['Server'][data.index[0]]

            username = data_dict['Username'][data.index[0]]

            password = data_dict['Password'][data.index[0]]

            conn = pyodbc.connect(
                'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database_name + ';UID=' + username + ';PWD=' + password)

            Table = pd.read_sql(query, conn)

            conn.close()

        return Table

    if request.method == 'POST':

        conn = sqlite3.connect(sqlitedb_file)

        Source_Connection = request.form.get("SourceConnection")

        Source_Table_name = request.form["SourceTable"]

        Target_Connection = request.form.get("TargetConnection")

        Target_Table_name = request.form["TargetTable"]

        Source_query = request.form["source_query"]

        Target_query = request.form["target_query"]

        # Source_Connection = 'Teradata'

        # Source_Table_name = 'IDEA_T_TGT_BATCH_LOG'

        # Target_Connection = 'Azure'

        # Target_Table_name = 'IDEA_T_TGT_BATCH_LOG_COPY'

        # Source_query = 'select count(*) from IDEA_T_TGT_BATCH_LOG'

        # Target_query = 'select count(*) from IDEA_T_TGT_BATCH_LOG_COPY'

        query = "select * from QAConnection"

        data = pd.read_sql(query, conn)

        conn.close()

        if len(Source_query) > 5 and len(Target_query) > 5:

            data_ = data[data.Connection_Name == Source_Connection]

            data_dict = data_.to_dict()

            source_database_name = data_dict['Database'][data_.index[0]]

            q = Source_query.split("from ")

            Source_query_schema = q[0] + "from " + source_database_name + "." + q[1]

            source_data = database_query(data, Source_Connection, Source_query_schema)

            target_data = database_query(data, Target_Connection, Target_query)

            # target_data = database_table(data,Target_Connection, Target_Table_name)

            # source_data = database_table(data,Source_Connection, Source_Table_name)

            s = "<table style='border:1px solid red'><tr>"

            # for col in source_data.columns:

            #     s = s+"<td>"+col+"</td>"

            # s = s + "</tr>"

            for i, row in source_data.iterrows():

                s = s + "<tr>"

                for ele in row:
                    s = s + "<td>" + str(ele) + "</td>"

                s = s + "</tr>"

            s = s + "<tr></tr><tr></tr><tr></tr>"

            # for col in target_data.columns:

            #     s = s+"<td>"+col+"</td>"

            # s = s + "</tr>"

            for i, row in target_data.iterrows():

                s = s + "<tr>"

                for ele in row:
                    s = s + "<td>" + str(ele) + "</td>"

                s = s + "</tr>"

            return "<html><body>" + s + "</body></html>"



        else:

            Source_Table = database_table(data, Source_Connection, Source_Table_name)

            Target_Table = database_table(data, Target_Connection, Target_Table_name)

            # testcases = request.form.getlist('testcases')

            testcase_group = request.form.get("testcase_group")

            conn = sqlite3.connect(sqlitedb_file)

            query = "Select Selected_Testcases from QA_Testcase where Testcase_Group = '" + str(testcase_group) + "'"

            data = pd.read_sql(query, conn)

            conn.close()

            testcases = data['Selected_Testcases'].tolist()[0].split(", ")

            Join_Column = request.form['Joincolumn']

            compare = datacompy.Compare(Source_Table, Target_Table, join_columns=Join_Column)

            results = {}

            if 'dataframe_summary_1' in testcases:
                dataframe_summary = dataframe_summary(compare)

                results['dataframe_summary_1'] = dataframe_summary

            if 'ColumnSummary' in testcases:
                column_summary_ = column_summary(compare)

                results['ColumnSummary'] = column_summary_

            if 'row_summary_1' in testcases:
                row_summary = row_summary(compare)

                results['row_summary_1'] = row_summary

            if 'column_matching_1' in testcases:
                column_matching = column_matching(compare)

                results['column_matching_1'] = column_matching

            if 'sample_df2_unique_rows_1' in testcases:
                sample_df2_unique_rows = sample_df2_unique_rows(compare)

                results['sample_df2_unique_rows_1'] = sample_df2_unique_rows

            if 'sample_df1_unique_rows_1' in testcases:
                sample_df1_unique_rows = sample_df1_unique_rows(compare)

                results['sample_df1_unique_rows_1'] = sample_df1_unique_rows

            if 'row_unequal_values_1' in testcases:
                row_unequal_values = row_unequal_values(compare)

                results['row_unequal_values_1'] = row_unequal_values

            if 'column_unequal_values_1' in testcases:
                column_unequal_values = column_unequal_values(compare)

                results['column_unequal_values_1'] = column_unequal_values

            if 'rowcount' in testcases:
                rowcount = rowcount(Source_Table, Target_Table)

                results['rowcount'] = rowcount

            if 'columncount' in testcases:
                columncount = columncounts(Source_Table, Target_Table)

                results['columncount'] = columncount

            if 'nullcount' in testcases:
                nullcount = nullcounts(Source_Table, Target_Table)

                results['nullcount'] = nullcount

            conn = sqlite3.connect(sqlitedb_file)

            insert_query = """INSERT INTO QA_Results(Execution_ID, Source_Name, Target_Name, Testcase_Group, Testcase_Name, Validation_Status, Report)

                            VALUES ( NULL,?,?,?,?,?,?)"""

            cur = conn.cursor()

            for i, test_case in enumerate(testcases):

                if test_case in validation_list:

                    cur.execute(insert_query,
                                [Source_Connection, Target_Connection, testcase_group, test_case, results[test_case],
                                 ''])

                else:

                    cur.execute(insert_query, [Source_Connection, Target_Connection, testcase_group, test_case, '',
                                               results[test_case]])

            conn.commit()

            query = "select * from QA_Results"

            data = pd.read_sql(query, conn)

            cur.close()

            conn.close()

            validation_listcount = data['Validation_Status'].value_counts()

            plt.plot(validation_listcount)

            s = "<table style='border:1px solid red'><tr><td>Execution_ID</td><td>Source_Name</td><td>Target_Name</td><td>Testcase_Group</td><td>Testcase_Name</td><td>Validation_Status</td><td>Report</td></tr>"

            s = s + ""

            for i, row in data[-len(testcases):].iterrows():

                s = s + "<tr>"

                for ele in row:
                    s = s + "<td>" + str(ele) + "</td>"

                s = s + "</tr>"

            # for i,test_case in enumerate(testcases):

            #   print(results[test_case])

            return "<html><body>" + s + "</body></html>"

    con = sqlite3.connect(sqlitedb_file)

    query = "Select Connection_Name from QAConnection"

    data = pd.read_sql(query, con)

    c = data['Connection_Name'].tolist()

    query = "Select Testcase_Group from QA_Testcase"

    data = pd.read_sql(query, con)

    t = data['Testcase_Group'].tolist()

    con.close()

    return render_template('query_page.html',Databasename_src=c, Selected_Testcases=t)


if __name__ == "__main__":
    app.run(debug=True)