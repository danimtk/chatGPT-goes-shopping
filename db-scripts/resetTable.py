import pandas as pd
import sqlite3
# df = pd.read_csv(r'datasets\vtex_50_test.csv')


def resetTable(table_name):

    sql0 = "UPDATE {} SET status = 0, content = NULL, finish_reason = NULL, prompt_tokens = NULL, completion_tokens = NULL, total_tokens = NULL, elapsed_time = NULL ".format(table_name)

    cursor.execute(sql0)
                            
    conn.commit()



for db in ['gpt-35-turbo']:


    conn = sqlite3.connect(f"../data/database/database.db")
    cursor = conn.cursor()

    WANDS_TABLE_NAME = 'WANDS_2800_zero_shot_LLM_generated_gpt35'


    resetTable(WANDS_TABLE_NAME)

