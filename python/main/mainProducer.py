import pyodbc
import confluent_kafka as ck
import json

def sql_server_connection(pServer, pDb, pUserNm, pPwd, pQuery):

    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={pServer};DATABASE={pDb};UID={pUserNm};PWD={pPwd};encrypt=no;'

    conn = pyodbc.connect(connectionString)

    cursor = conn.cursor()
    cursor.execute(pQuery)

    records = cursor.fetchall()
    
    cursor.close()
    return records

def kafka_producer():
    conf= {"bootstrap.servers":"localhost:9092"}
    return ck.Producer(conf)

def main():

    SERVER = '10.10.14.100'
    DATABASE = 'TRYIT'
    USERNAME = 'js'
    PASSWORD = 'js'
    SQL_QUERY = 'Select RedisKey, RedisValue from TestCache' 
    sqlOutput = sql_server_connection (SERVER, DATABASE, USERNAME, PASSWORD, SQL_QUERY) 
    
    # Initiate Kafka Producer
    topic_name = 'mssql-to-redis'
    kProducer = kafka_producer()

    for r in sqlOutput:   
        
        Redis_Key = r.RedisKey
        Redis_Value = r.RedisValue

        dictRedis = {Redis_Key : Redis_Value}

        # Serialize dictionary to JSON
        json_data = json.dumps(dictRedis)
        
        # print(json_data) ## Used for Testing
        # print(type(json_data))
        
        # Produce message to Kafka topic
        kProducer.produce(topic_name, value=json_data.encode('utf-8'))

        # Wait for message to be delivered
        kProducer.flush()

if __name__ == "__main__":
    main()