import pyodbc
import confluent_kafka as ck
import json
import time

def sql_server_select(pServer, pDb, pUserNm, pPwd, pQuery):

    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={pServer};DATABASE={pDb};UID={pUserNm};PWD={pPwd};encrypt=no;'

    conn = pyodbc.connect(connectionString)

    cursor = conn.cursor()
    cursor.execute(pQuery)

    records = cursor.fetchall()
    
    cursor.close()
    return records

def sql_server_update(pServer, pDb, pUserNm, pPwd, pQuery):

    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={pServer};DATABASE={pDb};UID={pUserNm};PWD={pPwd};encrypt=no;'

    conn = pyodbc.connect(connectionString)

    cursor = conn.cursor()
    cursor.execute(pQuery)

    conn.commit() #Importent to commit else connection will be closed without commit and wont udpate the data.
    cursor.close()

def kafka_producer():
    conf= {"bootstrap.servers":"localhost:9092"}
    return ck.Producer(conf)

def mainProducer (nextBatchDateTime):

    SERVER = '10.10.14.100'
    DATABASE = 'TRYIT'
    USERNAME = 'js'
    PASSWORD = 'js'
    SQL_QUERY = "Select RedisKey, RedisValue, max(CreatedDate) over() MaxCreatedDate from TestCache where createdDate > DATEADD(MS, 1 ,CAST('" + str(nextBatchDateTime) + "' as DATETIME2))"

    # print(SQL_QUERY) #For Testing

    sqlOutput = sql_server_select (SERVER, DATABASE, USERNAME, PASSWORD, SQL_QUERY) 
    
    # Initiate Kafka Producer
    topic_name = 'mssql-to-redis'
    kProducer = kafka_producer()

    for r in sqlOutput:   
        
        Redis_Key = r.RedisKey
        Redis_Value = r.RedisValue
        # This will be same for all the rows, Window function is used to get the max date in the returned list of rows
        nextBatchDateTime = r.MaxCreatedDate 

        # create dict for Redis Key Values
        dictRedis = {Redis_Key : Redis_Value}

        # Serialize dictionary to JSON
        json_data = json.dumps(dictRedis)
        
        # print(json_data) ## Used for Testing
        # print(type(json_data))
        
        # Stream message to Kafka topic
        kProducer.produce(topic_name, value=json_data.encode('utf-8'))

        # Wait for message to be delivered
        kProducer.flush()

    return nextBatchDateTime

if __name__ == "__main__":
    
    #I nitial Data Batch Counter
    dataBatchNum = 1

    # Get data of streamed till ; Will be used as watermark so that when producer reruns then it needs to start from last processed date
    SERVER = '10.10.14.100'
    DATABASE = 'TRYIT'
    USERNAME = 'js'
    PASSWORD = 'js'
    SQL_QUERY_STREAMED_TILL_INITIAL  = "Select ProcessedTillDate from dbo.CacheProcessedDate"
    sqlOutputStreamedTill = sql_server_select(SERVER, DATABASE, USERNAME, PASSWORD, SQL_QUERY_STREAMED_TILL_INITIAL)
    
    for pt in sqlOutputStreamedTill:
        batchStartDate = pt.ProcessedTillDate

    # Start Sending Data Rows in Batches to Kafka Topic
    
    while True:
        print(f'Data Batch - {dataBatchNum} Stream Started')
        bst = mainProducer(batchStartDate)
        print(f'Data Batch - {dataBatchNum} Stream Completed')

        batchStartDate = bst
        
        # Update Data Batch Counter
        dataBatchNum = dataBatchNum + 1

        # Update Date Time -  Data streamed till Datetime
        SERVER = '10.10.14.100'
        DATABASE = 'TRYIT'
        USERNAME = 'js'
        PASSWORD = 'js'
        SQL_QUERY_STREAMED_TILL = "Update dbo.CacheProcessedDate set ProcessedTillDate = CAST('" + str(batchStartDate) + "' as DATETIME2)"
        # print(SQL_QUERY_STREAMED_TILL)
        sqlOutput = sql_server_update (SERVER, DATABASE, USERNAME, PASSWORD, SQL_QUERY_STREAMED_TILL)

        time.sleep(60)