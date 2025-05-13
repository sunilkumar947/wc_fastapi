import google.generativeai as genai
import mysql.connector
from datetime import timedelta

class SQLChatbot:
    print('Initializing Chatbot...')
    
    def __init__(self, db_handler):
        print('inside Sqlchatbot  constructor ')
        self.db_handler = db_handler  # MySQL Database Connection
        genai.configure(api_key="AIzaSyBYmVoYj-bMy5UkneSzPMLF8jG2nPKYU1k")
        self.model = genai.GenerativeModel("gemini-1.5-pro")  

    def generate_sql(self, user_input):
        """Use Google Gemini to generate SQL queries dynamically."""
        prompt = f"""
        You are an expert in converting English questions to SQL query. Based on the given MySQL database schema, generate an SQL query for the following user request.
        IMPORTANT: Return ONLY the SQL query without any explanation, comments, or code formatting.
        DO NOT include markdown formatting like ```sql or ``` around your query.

        Tables:
        1. users (id, user_id, username, email, phone_no, user_password, status)
        2. work_time (id, user_id, date, login_time, break_time, screen_time, logout_time)
        3. app_usage (id, user_id, app_name, url, duration, date)
        4. screenshots (id,user_id, screenshot_path,timestamp)

        NOTES: 
        - When looking for a user's information, use a JOIN with the users table to match username
        - For "last" work time, sort by date DESC and use LIMIT 1
        - The date column in work_time contains the date of the work session
        - Always use user_id as the primary identifier for users instead of id.

        User Input: "{user_input}"

        Generate a valid MySQL query without any markdown or formatting:
        """

        try:
            response = self.model.generate_content(prompt)
            sql_query = response.text.strip() if hasattr(response, "text") else response.parts[0].text.strip()
            
            # Remove any markdown formatting if present
            if sql_query.startswith("```"):
                # Find the end of the code block and extract just the SQL
                sql_lines = sql_query.split("\n")
                clean_lines = []
                for line in sql_lines:
                    if line.startswith("```"):
                        continue
                    clean_lines.append(line)
                sql_query = "\n".join(clean_lines).strip()
            
            return sql_query
        except Exception as e:
            return f"Error: {str(e)}"

    def execute_query(self, sql):
        print('Inside execute query')
        """Run SQL query and return formatted results."""
        try:
            cursor = self.db_handler.connection.cursor()
            print(f"Executing SQL: {sql}")
            cursor.execute(sql)
            result = cursor.fetchall()
            print(f"Raw Result: {result}")
            cursor.close()
            
            if result:
                formatted_result = []
                for row in result:
                    formatted_row = []
                    for value in row:
                        if isinstance(value, timedelta):
                            # Convert timedelta to HH:MM:SS format
                            total_seconds = int(value.total_seconds())
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            formatted_row.append(f"{hours:02}:{minutes:02}:{seconds:02}")
                        else:
                            formatted_row.append(str(value))
                    formatted_result.append(" | ".join(formatted_row))

                return "\n".join(formatted_result)

            return "No data found."
        
        except mysql.connector.Error as e:
            return f"SQL Error: {str(e)}"

        except Exception as e:
            return f"SQL Error: {str(e)}"

    def get_response(self, user_query):
        print('inside get_response ')
        """Process user query and return chatbot response."""
        sql_query = self.generate_sql(user_query)
        if "SELECT" in sql_query:
            return self.execute_query(sql_query)
        return sql_query
