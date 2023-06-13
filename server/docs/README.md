### API framework - fastapi

I have used [fastapi](https://fastapi.tiangolo.com/) for this project which is a modern, fast (high-performance), web framework for building APIs with Python. The reasons behind this choice is as follows:

* *Type Safety and Data Validation*: It integrates with [pydantic](https://docs.pydantic.dev/latest/), which provides robust data validation and serialization capabilities based on Python type hints. This ensures that incoming requests and outgoing responses are properly validated, reducing the risk of data corruption or errors. Type safety also improves code maintainability by catching potential issues during development.

* *Asynchronous Support*: It has built-in support for asynchronous programming which is essential for event-driven applications. It allows for handling long-running operations efficiently and enables the API to respond quickly to multiple requests, making it suitable for applications that require real-time updates, event-driven behavior, or heavy asynchronous processing.

* *Performance*: It comes with asynchronous capabilities making it highly scalable and efficient in handling high loads. It allows for concurrent processing of requests, reducing response times and ensuring optimal performance even under heavy traffic. This is crucial for this write-intensive project as it needs to handle multiple requests simultaneously without causing delays or timeouts as well as reducing the probability for data-loss.


### Databases - PostgreSQL, Redis, InfluxDB

I chose to use three kinds of databases for different use cases in this project, namely, PostgreSQL to handle user data, Redis key-value store for caching, and InfluxDB for storing audit events.

* *PostgreSQL*: I used a PostgreSQL database to manage users and their access keys for managing access of the API.

* *Redis*: I used redis in front of my PostgreSQL database as a cache to improve performance of common database queries as well as reducing the load on the database itself. I also used redis to create unique keys with short TTL (time to live) to create temporary URLs for verification (done without a mailing system).

* *InfluxDB*: The key decision here was to choose the database required for storing the audit log. For this, I narrowed down the options to three: [elasticsearch](https://www.elastic.co/), [InfluxDB](https://www.influxdata.com/), and [MongoDB](https://www.mongodb.com/), and eventually, I decided to opt for the second option.

The decision to choose InfluxDB as the database for the audit log service was based on several key factors and requirements.

First and foremost, an audit log plays a critical role in capturing and storing detailed information about, for example, user actions, system events, and changes for security, compliance, and troubleshooting purposes. Therefore, it was essential to select a database that could effectively handle the unique characteristics and demands of an audit log.

One of the primary reasons for choosing InfluxDB was its suitability for `time-series data storage`. The audit log data follows a **chronological order**, making it well-aligned with InfluxDB's design as a `purpose-built time-series database`. This enables efficient storage and retrieval of audit log entries based on timestamps.

Another crucial requirement was the ability to handle `high-volume data ingestion` and `high write throughputs`. InfluxDB excels in this aspect, offering robust write performance to accommodate the continuous influx of audit log entries without impacting the overall system performance. Its **optimized write capabilities** ensure that audit log data is rapidly recorded and securely stored.

Scalability was also a vital consideration. As the audit log grows over time, InfluxDB's horizontal scalability allows for seamless expansion of storage and processing capabilities. This ensures that the audit log service can handle increasing data volumes without compromising performance or reliability.

InfluxDB's support for `tagging and filtering data` was another advantage. This feature enables easy querying and analysis of audit log entries based on various attributes, providing flexibility in extracting valuable insights from the audit data.

In summary, InfluxDB emerged as the optimal choice for the audit log service due to its efficient *time-series data storage, high write performance, and compatibility with the specific requirements*. By leveraging InfluxDB, the audit log service can reliably capture, store, and analyze audit data, meeting the security, compliance, and troubleshooting needs of the system. While all of this can be achieved by using either of elasticsearch or MongoDB, I opted to use InfluxDB, a specialized time-series database, based on the importance of time-series analysis on audit log records.


### Task Queue - (Celery + Redis)

The decision to use [Celery](https://docs.celeryq.dev/en/stable/) with [Redis](https://redis.io/) as the broker and backend for handling data writes in the API was driven by the need to address performance and scalability concerns in a write-intensive application.

In a high-traffic environment, directly writing data to the database from the API can lead to performance issues and potential bottlenecks. By implementing a queue-based approach with Celery and Redis, we can decouple the data writing process from the API, allowing for better scalability and responsiveness.

By utilizing a task queue, incoming data requests can be quickly added to the queue, ensuring a swift response to the API caller. This asynchronous processing enables the API to handle a large volume of requests without becoming overwhelmed or experiencing significant delays and provides a *near real-time* performance.

Celery, as a distributed task queue system, provides the necessary infrastructure to manage the task execution and distribution across multiple workers. Redis, serving as the message broker and backend, efficiently handles the communication between the API and Celery workers.

The use of Celery and Redis also enhances fault tolerance and resilience. If a worker fails or experiences issues during data processing, tasks can be automatically retried or reassigned to other available workers. This ensures that data writes are resilient to potential failures and can recover gracefully.

Furthermore, this design decision allows for easy horizontal scalability. By adding more Celery workers as needed, the system can handle increasing write loads without affecting the overall performance of the API. This flexibility ensures that the application can scale effectively as the user base grows or during periods of peak traffic.

Redis is an in-memory data structure store known for its exceptional performance and low-latency communication. While [RabbitMQ](https://www.rabbitmq.com/) is a robust message broker with advanced features such as message routing, exchange types, and guaranteed message delivery, in scenarios where high throughput and minimal message delivery latency are crucial, Redis provides an advantage over RabbitMQ. The decision to choose Redis as the message broker was primarily driven by the specific requirements of the write-intensive application, the need for high performance and low-latency communication, simplicity in setup and configuration, persistence options, scalability, and the strong community support surrounding Redis.

In summary, by leveraging Celery with Redis as the task queue and backend, we can significantly improve the performance and scalability of the API when dealing with high volumes of write-intensive data. This design decision enables asynchronous data processing, fault tolerance, and horizontal scalability, ensuring a responsive and efficient system for handling data writes.


### Other considerations

In the design of this project, several factors were taken into consideration to ensure efficient resource utilization and optimal performance. Due to the limited hardware resources available on the development machine and other reasons, I opted not to use [Kubernetes](https://kubernetes.io/), [Kafka](https://kafka.apache.org/), and [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/).

* *Kubernetes and Hardware Limitations*: Kubernetes is a powerful container orchestration platform that offers scalability, resilience, and automated management of containers. However, it requires additional resources to set up and operate effectively. Considering the hardware limitations, it was decided not to utilize Kubernetes in the development environment to avoid straining the available resources.

* *Kafka and Message Broker Selection*: Kafka is a highly scalable and fault-tolerant distributed messaging platform. While Kafka offers advanced message queuing capabilities, it also introduces additional resource requirements. Considering the hardware limitations and the goal of conserving system resources, the decision was made not to use Kafka as the message broker.

* *Telegraf vs. Celery Worker*: Telegraf is a flexible data ingestion tool commonly used for monitoring and data collection purposes, especially designed for data ingestion to InfluxDB. However, in this project, an alternative approach was adopted. A dedicated Celery worker was built to offload processing tasks from the API and reduce the potential strain on the resources used by the REST API. By leveraging a Celery worker, the application achieves a more efficient distribution of processing tasks, allowing the API to focus on handling incoming requests while delegating data processing and ingestion to the worker.


### Limitations

In the design of the project, the selection of InfluxDB as the data storage solution was made based on its time-series database capabilities and its suitability for handling high-volume data ingestion. However, during the implementation phase, certain limitations and incomplete implementations of the available client library for InfluxDB in Python, [influxdb-client](https://github.com/influxdata/influxdb-client-python), were encountered. This led to constraints in implementing certain features and leveraging the full potential of the technology stack.

One specific limitation was the lack of support for different API tokens per user with necessary bucket access. This limitation prevented the implementation of fine-grained access control and restricted the ability to provide each user with specific access privileges to their designated data buckets. This could be particularly valuable in a business setting where monetization strategies could be built around different levels of access and data usage.

Another constraint was the inability to implement retention policies on data buckets. Retention policies allow for the automatic removal or archiving of data after a certain time period, which can be crucial for data management and storage optimization. The absence of this feature limited the ability to effectively manage data retention and potentially impacted the overall scalability and efficiency of the system.

Additionally, the incomplete implementation of asynchronous drivers for InfluxDB in Python hindered the ability to fully leverage the asynchronous capabilities of FastAPI, which operates on an ASGI web server. Asynchronous programming can significantly enhance performance and scalability, enabling concurrent execution of tasks and efficient resource utilization. However, the limitations in the available async drivers for InfluxDB restricted the extent to which the project could harness the benefits of asynchronous programming and potentially affected the overall responsiveness and throughput of the system.

Given these limitations and incomplete implementations in the client library, it was necessary to make trade-offs and find workarounds to address the specific requirements and objectives of the project. Alternative approaches or additional tools may have been considered to overcome these limitations, such as implementing custom authorization mechanisms or exploring other time-series databases with more robust Python client libraries. However, considering the project's scope, timeline, and resource constraints, it was decided to work within the limitations of the existing InfluxDB client library and find suitable compromises to ensure a functional and performant system.
