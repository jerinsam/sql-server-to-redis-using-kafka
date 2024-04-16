
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

conf= {"bootstrap.servers":"localhost:9092"}

####### Produce ##########
p = ck.Producer(conf)

p.produce('mssql-to-redis', "Test Message from Python:JERIN")

p.flush() #Wait  for message delivery
