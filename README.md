# EasyEats

A backend Python application for a UberEats type application that uses a microservices architecture that uses docker, python, and APIs. Overall purpose of the application is to receive data from post requests, process and store that data in a database and displays the processed data on the dashboard. Each microservice has their own unique functionalities:

Receiver: Receives the data from POST requests and sends that data to the Kafka client
Storage: Receives data between 2 timestamps from the Kafka client and queries it to the MySQL database

Processor: Receives data from the MySQL database, processes it, and stores them in it's sqlite database

audit log: Gets the most recent data from the Kafka client and returns it. 

Health Check: Sends get requests on all of the services. Marks the services as running if they return 200, otherwise marks them as Down. Stores this data in it's own sqlite database.

Dashboard: Gets data from the endpoints of the audit_log, processing, and health check services and displays them on a page


