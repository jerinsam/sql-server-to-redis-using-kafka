
# # Create Kafka Topic
# cd ~/learn/kafka/bin
# ./kafka-topics.sh --create --bootstrap-server localhost:9092 --partitions 2 --topic mssql-to-redis

# # Test Topic : Add Producer
# ./kafka-console-producer.sh --bootstrap-server localhost:9092 --topic mssql-to-redis

# # Test Topic : Add Consumer
# ./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic mssql-to-redis --from-beginning

# # Check all created topics
# ./kafka-topics.sh --list --bootstrap-server localhost:9092


import confluent_kafka as ck

conf= {"bootstrap.servers":"localhost:9092","group.id":"RedisKeys"}
 

####### Consumer ########
c = ck.Consumer(conf)

c.subscribe(['mssql-to-redis'])


while True:
    msg = c.poll(0.10)

    if msg is None:
        continue
    if msg.error():
        if msg.error().code() == ck.KafkaError._PARTITION_EOF:
            continue
        else:
            print(f'Error while consuming: {msg.error()}')
    else:
    #Parse the received message
        value = msg.value().decode('utf-8')
        print(value)

