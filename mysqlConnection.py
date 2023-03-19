import mysql.connector

class DatabaseConnection():

    def __init__(self, username : str, password : str, database : str, host : str="localhost", port = 3306):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password

    def connection(self):
        self.db = mysql.connector.connect(
            host=self.host,
            user=self.username,
            port=self.port,
            password=self.password,
            database=self.database,
            charset='utf8mb4',
        )

        if self.db.is_connected():
            print("You're connected to database!")
        else:
            print("Error Connection!")
        self.cursor = self.db.cursor(buffered=True)

    def close_connection(self):
        self.cursor.close()
        self.db.close()
        if not self.db.is_connected():
            print("MySQL connection is closed")
        else:
            print("Connection is not closed Successfully!")