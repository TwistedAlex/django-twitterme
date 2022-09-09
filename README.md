# django-twitterme

Tech Stack: Python, Django REST Framework, MySQL, HBase, Redis, Memcached, RabbitMQ, Amazon S3/EC2
•	Built push model to fanout news feeds
•	Leveraged Redis and Memcached to reduce DB queries for tables which has lot reads and lot writes
•	Used Key-value store HBase to split DB queries for tables which has less reads and lot writes
•	Utilized denormalization to store the number of comments & likes to reduce DB queries
•	Adapted Message Queue to deliver asynchronized tasks to reduce response time
•	The whole project resulted in 10000 lines of code changes, cost over 3 months
