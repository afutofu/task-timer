import sqlite3 as s3

class Database:
    def __init__(self, database):
        self.connection = s3.connect(database)
        self.cursor = self.connection.cursor()

        try:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS taskList(taskId INT PRIMARY KEY, taskName VARCHAR(20));")

            self.cursor.execute("CREATE TABLE IF NOT EXISTS log(taskId INT, logId INT, time INT, logDate TEXT);")

            self.connection.commit()
            print("Connection Successful")
        except:
            self.connection.rollback()

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def execute(self, query, command):
        try:
            self.cursor.execute(query)
            self.connection.commit()

        except Exception as e:
            if command == "select":
                print("Select Failed:", str(e))
            elif command == "insert":
                print("Insert Failed:", str(e))
            elif command == "update":
                print("Update Failed:", str(e))
            elif command == "delete":
                print("Delete Failed:", str(e))
            else:
                pass
            self.connection.rollback()

    def raw_execute(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            print(str(e))

    def select(self, table, columns, conditions=""):
        query = ""
        if conditions != "":
        	query = "SELECT %s FROM %s WHERE %s;" % (columns, table, conditions)
        else:
        	query = "SELECT %s FROM %s;" % (columns, table)
        self.execute(query, "select")

    def insert(self, table, columns, arguments):
        query = "INSERT INTO %s (%s) VALUES (%s);" % (table, columns, arguments)
        self.execute(query, "insert")

    def update(self, table, change, conditions=""):
        query = ""
        if conditions != "":
            query = "UPDATE %s SET %s WHERE %s" % (table, change, conditions)
        else:
            query = "UPDATE %s SET %s" % (table, change)
        self.execute(query, "update")

    def delete(self, table, conditions=""):
        query = ""
        if conditions != "":
            query = "DELETE FROM %s WHERE %s" % (table, conditions)
        else:
            query = "DELETE FROM %s" % (table)
        self.execute(query, "delete")

    def __del__(self):
        self.connection.close()

if __name__ == "__main__":

    db = Database("./tasktimer.db")

    db.raw_execute('SELECT DISTINCT logDate FROM log ORDER BY logId ASC LIMIT 31')
    res = db.fetchall()
    print(res)
