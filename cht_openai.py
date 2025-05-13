import openai
import pymysql
import os
from openai import OpenAI
class SQLChatbot:
    print('Initializing Chatbot...')

    def __init__(self, db_handler):
        self.db_handler = db_handler  # MySQL Database Connection
        self.client = OpenAI(api_key="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")

    def generate_sql(self, user_input):
        """Use GPT-3.5 to generate SQL queries dynamically."""
        prompt = f"""
        You are a SQL expert. Based on the given MySQL database schema, generate an SQL query for the following user request:

        Tables:
        1. users (id, user_id, username, email, phone_no, user_password, status)
        2. work_time (id, user_id, date, login_time, break_time, screen_time, logout_time)
        3. app_usage (id, user_id, app_name, url, duration, date)

        User Input: "{user_input}"

        Generate a valid MySQL query:
        """
        try:
            response = self.client.chat.completions.create(  # ✅ Uses correct API method
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert SQL query generator."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def execute_query(self, sql):
        """Run SQL query and return results."""
        try:
            cursor = self.db_handler.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            if result:
                return "\n".join([str(row) for row in result])
            return "No data found."
        except Exception as e:
            return f"SQL Error: {str(e)}"

    def get_response(self, user_query):
        """Process user query and return chatbot response."""
        sql_query = self.generate_sql(user_query)
        if "SELECT" in sql_query:
            return self.execute_query(sql_query)
        return sql_query
