import pyodbc
import confluent_kafka as ck
import json
import redis
 
def kafka_consumer():
    conf= {"bootstrap.servers":"localhost:9092","group.id":"RedisKeys"}
    return ck.Consumer(conf)

def redis_connect():
    return redis.Redis(host='localhost', port= 6379,decode_responses=True)

def redis_set(r,rKey,rValue):
    r.delete(rKey)
    r.set(rKey,rValue)

    # # Delete all keys in the current database (FLUSHDB)
    # r.flushdb()

def mainConsumer():

    # Initiate Kafka Consumer
    topic_name = 'mssql-to-redis'
    kConsumer = kafka_consumer()
    kConsumer.subscribe([topic_name])

    # Initialize Redis
    rConnect = redis_connect()

    while True:
        msg = kConsumer.poll(0.10)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == ck.KafkaError._PARTITION_EOF:
                continue
            else:
                print(f'Error while consuming: {msg.error()}')
        else:
            #Parse the received message
            value = json.loads(msg.value().decode('utf-8')) #Convert to dictionary
            kvPair = [(k,v)  for k, v in value.items()]
            redisKey =  kvPair[0][0]
            redisValue =  kvPair[0][1]

            # Update Redis Key 
            redis_set(rConnect,redisKey,redisValue)

            # print(f'{redisKey}, -, {redisValue}') # For Testing
            print(rConnect.get(redisKey))


if __name__ == "__main__":
    mainConsumer()
