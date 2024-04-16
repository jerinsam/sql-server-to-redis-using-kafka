import pyodbc

SERVER = '10.10.14.100'
DATABASE = 'TRYIT'
USERNAME = 'js'
PASSWORD = 'js'

connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};encrypt=no;'

conn = pyodbc.connect(connectionString)

SQL_QUERY = 'Select * from TestCache'

cursor = conn.cursor()
cursor.execute(SQL_QUERY)

records = cursor.fetchall()
 
for r in records:   
    Redis_Key = r.RedisKey
    Redis_Value = r.RedisValue
    print(f'{Redis_Key} \t {Redis_Value}')
cursor.close()