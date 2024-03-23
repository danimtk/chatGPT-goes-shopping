import sqlite3 as sqt
import re

class ExperimentDao:

    def  __init__(self, llm):

        self.llm = llm

        self.databasePath = 'data/database/database.db'

        self.conn = sqt.connect(self.databasePath)

        self.cursor = self.conn.cursor()


    def databaseName(self, llm):

        return llm.replace('.', '')

 
    def selectInstance(self, table, column_names):

        sql = "SELECT {} FROM {} WHERE status ='0'".format(', '.join(column_names), table)

        self.cursor.execute(sql)

        data = self.cursor.fetchall()

        list_of_dicts = [dict(zip(column_names, row)) for row in data]
        
        return list_of_dicts


    def selectJudgedInstances(self, table, column_names):

        sql = "SELECT {} FROM {} WHERE status ='1'".format(', '.join(column_names), table)

        self.cursor.execute(sql)

        data = self.cursor.fetchall()

        list_of_dicts = [dict(zip(column_names, row)) for row in data]
        
        return list_of_dicts


    def updateInstance(self, table, uniqid, content, finish_reason, prompt_tokens, completion_tokens, total_tokens, elapsed_time):

        content = re.sub(r'"', "'", content)


        sql = "UPDATE {} SET status = '1', content = \"{}\", finish_reason = '{}', prompt_tokens = {}, completion_tokens = {}, total_tokens = {}, elapsed_time = {} WHERE uniqueID = '{}'".format(table, content, finish_reason, prompt_tokens, completion_tokens, total_tokens, elapsed_time, uniqid)

        self.cursor.execute(sql)
                        
        self.conn.commit()

        return True

    

    def closeConnection(self):

        self.cursor.close()