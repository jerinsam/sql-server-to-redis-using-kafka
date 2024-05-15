#### Problem Statement - 

There's a reporting application which populates charts based on filters applied by users. The underlying data resides in SQL Server and there are 2 major Fact tables with 5 Million and 3 Million respectively, with refresh frequency of weekly with full data load. These tables are used in the complex metric calculation queries (fully optimized queries) and reside in Stored Procedures. Whenever a user selects the filters, API calls these SPs and populates the data in the charts.

These calculations take 10-15 seconds to process the data and as per the standards data needs to be computed with in 5 seconds to keep users engaged on the App.

#### Solution - 
** Redis is an open source, in-memory, key-value store that stores data in RAM
To solve the above issue, Redis Cache has been implemented. Idea is, if a User select a specific filter and API will retrieve the desired output after executing the SP in 15 Seconds, that Output will be stored in JSON format in Redis Cache and also same Output will be used by UI to populate the chart. In this scenario, User will still be waiting for 15 seconds to view the chart with desired data (Initial wait issue). However, if next time, same filter criteria is selected by some other or same user then data will be retrieved in milliseconds.

To mitigate the initial wait issue, Pre-populating Redis cache with all the filter combination is the best option. To develop this solution, It's been decided to capture all the frequently used User Filters (which is used as Redis key) to a table and after the weekly data refresh, JSON output will be created for those Filter Criteria (by executing the SPs) and will be stored in a table. Once output for all the keys is populated, Redis keys will be updated with the latest JSON output. To process 1000 keys, DB takes 30 mins, which is acceptable in our use case and app will have downtime for that period. 

Now if any user selects new combination which does not exist in the Redis then again User will have to wait for 15 seconds and currently in DB there are ~200000 keys (combination of filters) and it’s not feasible to populate all the ~200k key at once as UI will be down for that long period.

Keeping all these issues in mind, Final Solution has following sections:
1. After Data Refresh, all the frequently used keys will be processed and loaded in Redis Cache.
2. Create all the filter combinations and identify the important keys based on Business use case.
3. Implement a SP which will continuously process the different filter combinations and store the JSON output in a table.
4. Implement a streaming solution which will push the new data available in the Table to Redis. 

This solution will not completely eliminate the Initial wait issue but will reduce a lot. 


#### Implementation - 
In this POC, We are looking into the Point 4, i.e. Streaming app to push the processed data to Redis.
The solution is created on following are the list of Services:
1. Kafka
2. SQL Server
3. Redis

**Refer**: install_and_config Folder to get the details of the installation. 
**Refer**: /python/main folder to go through the python code used to push the json output to Redis. 

2 Python scripts are created to implemet the solution:
1. Kafka Producer
2. Kafka Consumer

Database Table DDLs and Testing queries are also present in the /python/main folder

##### Description:
1. Kafka Producer : 
 

2. Kafka Consumer : In this script, following activities are performed - 

 - JSON received from producer will be converted to dictionary.
 - key and value will be extracted from the dictionary.
 - Extracted key from above will be used to update Redis value associated to the key.
