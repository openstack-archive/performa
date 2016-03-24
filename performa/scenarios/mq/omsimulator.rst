Oslo.messaging simulator report
-------------------------------

This report is result of `message_queue_performance`_ execution
with `Oslo.messaging Simulator`_


Test Case 1: RPC CALL Throughput Test
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Message processing
~~~~~~~~~~~~~~~~~~

Messages are collected at 3 points: ``sent`` - messages sent by the client,
``received`` - messages received by the server, ``round-trip`` - replies
received by the client. Also the number of lost messages is calculated.
Sizes of messages is based on the distribution of messages collected on
the 100-node cloud.

{{'''
    title: RPC CALL Message count
    axes:
      x: threads
      y: sent, msg
      y2: received, msg
      y3: round-trip, msg
      y4: lost, msg
    chart: line
    pipeline:
    - { $match: { task: omsimulator, mode: call }}
    - { $group: { _id: { threads: { $multiply: [ "$threads", "$host_count", "$processes" ] } },
                  sent: { $sum: "$client.count" },
                  received: { $sum: "$server.count" },
                  round_trip: { $sum: "$round_trip.count" },
                  lost: { $sum: { $subtract: ["$client.count", "$round_trip.count"] }}
                }}
    - { $project: { x: "$_id.threads",
                    y: "$sent",
                    y2: "$received",
                    y3: "$round_trip",
                    y4: "$lost"
                  }}
    - { $sort: { x: 1 }}
''' | chart_and_table
}}


The throughput, latency and RabbitMQ CPU utilization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The chart shows the throughput, latency and CPU utilization by RabbitMQ server
depending on number of concurrent threads.

{{'''
    title: RPC CALL throughput, latency and RabbitMQ CPU utilization depending on thread count
    axes:
      x: threads
      y: sent, msg/sec
      y2: received, msg/sec
      y3: round-trip, msg/sec
      y4: latency, ms
      y5: RabbitMQ CPU consumption, %
    chart: line
    pipeline:
    - $match: { task: omsimulator, mode: call }
    - $group:
        _id: { threads: { $multiply: [ "$threads", "$host_count", "$processes" ] } }
        msg_sent_per_sec: { $sum: { $divide: ["$client.count", "$client.duration"] }}
        msg_received_per_sec: { $sum: { $divide: ["$server.count", "$server.duration"] }}
        msg_round_trip_per_sec: { $sum: { $divide: ["$round_trip.count", "$round_trip.duration"] }}
        latency: { $avg: "$round_trip.latency" }
        rabbit_total_0: { $avg: "$rabbit_total_0" }
        rabbit_total_1: { $avg: "$rabbit_total_1" }
        rabbit_total_2: { $avg: "$rabbit_total_2" }
    - $project:
        x: "$_id.threads"
        y: "$msg_sent_per_sec"
        y2: "$msg_received_per_sec"
        y3: "$msg_round_trip_per_sec"
        y4: { $multiply: [ "$latency", 1000 ] }
        y5: { $multiply: [ { $sum: ["$rabbit_total_0", "$rabbit_total_1", "$rabbit_total_2"] }, 100 ] }
''' | chart_and_table
}}


Detailed RabbitMQ CPU consumption
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Thus chart shows statistics on RabbitMQ CPU consumption per nodes.

{{'''
    title: RabbitMQ nodes CPU consumption during RPC CALL load test
    axes:
      x: threads
      y0: Master total, %
      y1: Slave 1 total, %
      y2: Slave 2 total, %
      z0: Master sys, %
      z1: Slave 1 sys, %
      z2: Slave 2 sys, %
    chart: line
    pipeline:
    - $match: { task: omsimulator, mode: call }
    - $group:
        _id: { threads: { $multiply: [ "$threads", "$host_count", "$processes" ] } }
        rabbit_total_0: { $avg: "$rabbit_total_0" }
        rabbit_total_1: { $avg: "$rabbit_total_1" }
        rabbit_total_2: { $avg: "$rabbit_total_2" }
        rabbit_sys_0: { $avg: "$rabbit_sys_0" }
        rabbit_sys_1: { $avg: "$rabbit_sys_1" }
        rabbit_sys_2: { $avg: "$rabbit_sys_2" }
    - $project:
        x: "$_id.threads"
        y0: { $multiply: [ "$rabbit_total_0", 100 ] }
        y1: { $multiply: [ "$rabbit_total_1", 100 ] }
        y2: { $multiply: [ "$rabbit_total_2", 100 ] }
        z0: { $multiply: [ "$rabbit_sys_0", 100 ] }
        z1: { $multiply: [ "$rabbit_sys_1", 100 ] }
        z2: { $multiply: [ "$rabbit_sys_2", 100 ] }
''' | chart_and_table
}}

Detailed RabbitMQ resident memory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Thus chart shows statistics on RabbitMQ memory consumption (RSS) per nodes.

{{'''
    title: RabbitMQ nodes memory consumption during RPC CALL load test
    axes:
      x: threads
      y0: Master, Mb
      y1: Slave 1, Mb
      y2: Slave 2, Mb
    chart: line
    pipeline:
    - $match: { task: omsimulator, mode: call }
    - $group:
        _id: { threads: { $multiply: [ "$threads", "$host_count", "$processes" ] } }
        rabbit_0: { $avg: "$rabbit_resident_0" }
        rabbit_1: { $avg: "$rabbit_resident_1" }
        rabbit_2: { $avg: "$rabbit_resident_2" }
    - $project:
        x: "$_id.threads"
        y0: { $divide: [ "$rabbit_0", 1048576 ] }
        y1: { $divide: [ "$rabbit_1", 1048576 ] }
        y2: { $divide: [ "$rabbit_2", 1048576 ] }
''' | chart_and_table
}}


Test Case 2: RPC CAST Throughput Test
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Message processing
~~~~~~~~~~~~~~~~~~

Messages are collected at 2 points: ``sent`` - messages sent by the client
and ``received`` - messages received by the server. Also the number of lost
messages is calculated. Sizes of messages is based on the distribution of
messages collected on the 100-node cloud.

{{'''
    title: RPC CAST Message count
    axes:
      x: threads
      y: sent, msg
      y2: received, msg
      y3: lost, msg
    chart: line
    pipeline:
    - { $match: { task: omsimulator, mode: cast }}
    - { $group: { _id: { threads: { $multiply: [ "$threads", "$host_count", "$processes" ] } },
                  sent: { $sum: "$client.count" },
                  received: { $sum: "$server.count" },
                  lost: { $sum: { $subtract: ["$client.count", "$server.count"] }}
                }}
    - { $project: { x: "$_id.threads",
                    y: "$sent",
                    y2: "$received",
                    y3: "$lost"
                  }}
    - { $sort: { x: 1 }}
''' | chart_and_table
}}


The throughput, latency and RabbitMQ CPU utilization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The chart shows the throughput, latency and CPU utilization by RabbitMQ server
depending on number of concurrent threads.

{{'''
    title: RPC CAST throughput, latency and RabbitMQ CPU utilization depending on thread count
    axes:
      x: threads
      y: sent, msg/sec
      y2: received, msg/sec
      y3: latency, ms
      y4: RabbitMQ CPU consumption, %
    chart: line
    pipeline:
    - $match: { task: omsimulator, mode: cast }
    - $group:
        _id: { threads: { $multiply: [ "$threads", "$host_count", "$processes" ] } }
        msg_sent_per_sec: { $sum: { $divide: ["$client.count", "$client.duration"] }}
        msg_received_per_sec: { $sum: { $divide: ["$server.count", "$server.duration"] }}
        latency: { $avg: "$server.latency" }
        rabbit_total_0: { $avg: "$rabbit_total_0" }
        rabbit_total_1: { $avg: "$rabbit_total_1" }
        rabbit_total_2: { $avg: "$rabbit_total_2" }
    - $project:
        x: "$_id.threads"
        y: "$msg_sent_per_sec"
        y2: "$msg_received_per_sec"
        y3: { $multiply: [ "$latency", 1000 ] }
        y4: { $multiply: [ { $sum: ["$rabbit_total_0", "$rabbit_total_1", "$rabbit_total_2"] }, 100 ] }
''' | chart_and_table
}}

Detailed RabbitMQ CPU consumption
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Thus chart shows statistics on RabbitMQ CPU consumption per nodes.

{{'''
    title: RabbitMQ nodes CPU consumption during RPC CAST load test
    axes:
      x: threads
      y0: Master total, %
      y1: Slave 1 total, %
      y2: Slave 2 total, %
      z0: Master sys, %
      z1: Slave 1 sys, %
      z2: Slave 2 sys, %
    chart: line
    pipeline:
    - $match: { task: omsimulator, mode: cast }
    - $group:
        _id: { threads: { $multiply: [ "$threads", "$host_count", "$processes" ] } }
        rabbit_total_0: { $avg: "$rabbit_total_0" }
        rabbit_total_1: { $avg: "$rabbit_total_1" }
        rabbit_total_2: { $avg: "$rabbit_total_2" }
        rabbit_sys_0: { $avg: "$rabbit_sys_0" }
        rabbit_sys_1: { $avg: "$rabbit_sys_1" }
        rabbit_sys_2: { $avg: "$rabbit_sys_2" }
    - $project:
        x: "$_id.threads"
        y0: { $multiply: [ "$rabbit_total_0", 100 ] }
        y1: { $multiply: [ "$rabbit_total_1", 100 ] }
        y2: { $multiply: [ "$rabbit_total_2", 100 ] }
        z0: { $multiply: [ "$rabbit_sys_0", 100 ] }
        z1: { $multiply: [ "$rabbit_sys_1", 100 ] }
        z2: { $multiply: [ "$rabbit_sys_2", 100 ] }
''' | chart_and_table
}}

Detailed RabbitMQ resident memory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Thus chart shows statistics on RabbitMQ memory consumption (RSS) per nodes.

{{'''
    title: RabbitMQ nodes memory consumption during RPC CAST load test
    axes:
      x: threads
      y0: Master, Mb
      y1: Slave 1, Mb
      y2: Slave 2, Mb
    chart: line
    pipeline:
    - $match: { task: omsimulator, mode: cast }
    - $group:
        _id: { threads: { $multiply: [ "$threads", "$host_count", "$processes" ] } }
        rabbit_0: { $avg: "$rabbit_resident_0" }
        rabbit_1: { $avg: "$rabbit_resident_1" }
        rabbit_2: { $avg: "$rabbit_resident_2" }
    - $project:
        x: "$_id.threads"
        y0: { $divide: [ "$rabbit_0", 1048576 ] }
        y1: { $divide: [ "$rabbit_1", 1048576 ] }
        y2: { $divide: [ "$rabbit_2", 1048576 ] }
''' | chart_and_table
}}


Test Case 3: Notification Throughput Test
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Message processing
~~~~~~~~~~~~~~~~~~

Messages are collected at 2 points: ``sent`` - messages sent by the client
and ``received`` - messages received by the server. Also the number of lost
messages is calculated. Sizes of messages is based on the distribution of
messages collected on the 100-node cloud.

{{'''
    title: NOTIFY Message count
    axes:
      x: threads
      y: sent, msg
      y2: received, msg
      y3: lost, msg
    chart: line
    pipeline:
    - { $match: { task: omsimulator, mode: notify }}
    - { $group: { _id: { threads: { $multiply: [ "$threads", "$host_count", "$processes" ] } },
                  sent: { $sum: "$client.count" },
                  received: { $sum: "$server.count" },
                  lost: { $sum: { $subtract: ["$client.count", "$server.count"] }}
                }}
    - { $project: { x: "$_id.threads",
                    y: "$sent",
                    y2: "$received",
                    y3: "$lost"
                  }}
    - { $sort: { x: 1 }}
''' | chart_and_table
}}


The throughput, latency and RabbitMQ CPU utilization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The chart shows the throughput, latency and CPU utilization by RabbitMQ server
depending on number of concurrent threads.

{{'''
    title: NOTIFY throughput, latency and RabbitMQ CPU utilization depending on thread count
    axes:
      x: threads
      y: sent, msg/sec
      y2: received, msg/sec
      y3: latency, ms
      y4: RabbitMQ CPU consumption, %
    chart: line
    pipeline:
    - $match: { task: omsimulator, mode: notify }
    - $group:
        _id: { threads: { $multiply: [ "$threads", "$host_count", "$processes" ] } }
        msg_sent_per_sec: { $sum: { $divide: ["$client.count", "$client.duration"] }}
        msg_received_per_sec: { $sum: { $divide: ["$server.count", "$server.duration"] }}
        latency: { $avg: "$server.latency" }
        rabbit_total_0: { $avg: "$rabbit_total_0" }
        rabbit_total_1: { $avg: "$rabbit_total_1" }
        rabbit_total_2: { $avg: "$rabbit_total_2" }
    - $project:
        x: "$_id.threads"
        y: "$msg_sent_per_sec"
        y2: "$msg_received_per_sec"
        y3: { $multiply: [ "$latency", 1000 ] }
        y4: { $multiply: [ { $sum: ["$rabbit_total_0", "$rabbit_total_1", "$rabbit_total_2"] }, 100 ] }
''' | chart_and_table
}}

Detailed RabbitMQ CPU consumption
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Thus chart shows statistics on RabbitMQ CPU consumption per nodes.

{{'''
    title: RabbitMQ nodes CPU consumption during NOTIFY load test
    axes:
      x: threads
      y0: Master total, %
      y1: Slave 1 total, %
      y2: Slave 2 total, %
      z0: Master sys, %
      z1: Slave 1 sys, %
      z2: Slave 2 sys, %
    chart: line
    pipeline:
    - $match: { task: omsimulator, mode: notify }
    - $group:
        _id: { threads: { $multiply: [ "$threads", "$host_count", "$processes" ] } }
        rabbit_total_0: { $avg: "$rabbit_total_0" }
        rabbit_total_1: { $avg: "$rabbit_total_1" }
        rabbit_total_2: { $avg: "$rabbit_total_2" }
        rabbit_sys_0: { $avg: "$rabbit_sys_0" }
        rabbit_sys_1: { $avg: "$rabbit_sys_1" }
        rabbit_sys_2: { $avg: "$rabbit_sys_2" }
    - $project:
        x: "$_id.threads"
        y0: { $multiply: [ "$rabbit_total_0", 100 ] }
        y1: { $multiply: [ "$rabbit_total_1", 100 ] }
        y2: { $multiply: [ "$rabbit_total_2", 100 ] }
        z0: { $multiply: [ "$rabbit_sys_0", 100 ] }
        z1: { $multiply: [ "$rabbit_sys_1", 100 ] }
        z2: { $multiply: [ "$rabbit_sys_2", 100 ] }
''' | chart_and_table
}}

Detailed RabbitMQ resident memory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Thus chart shows statistics on RabbitMQ memory consumption (RSS) per nodes.

{{'''
    title: RabbitMQ nodes memory consumption during NOTIFY load test
    axes:
      x: threads
      y0: Master, Mb
      y1: Slave 1, Mb
      y2: Slave 2, Mb
    chart: line
    pipeline:
    - $match: { task: omsimulator, mode: notify }
    - $group:
        _id: { threads: { $multiply: [ "$threads", "$host_count", "$processes" ] } }
        rabbit_0: { $avg: "$rabbit_resident_0" }
        rabbit_1: { $avg: "$rabbit_resident_1" }
        rabbit_2: { $avg: "$rabbit_resident_2" }
    - $project:
        x: "$_id.threads"
        y0: { $divide: [ "$rabbit_0", 1048576 ] }
        y1: { $divide: [ "$rabbit_1", 1048576 ] }
        y2: { $divide: [ "$rabbit_2", 1048576 ] }
''' | chart_and_table
}}


.. references:

.. _message_queue_performance: http://docs.openstack.org/developer/performance-docs/test_plans/mq/plan.html
.. _Oslo.messaging Simulator: https://github.com/openstack/oslo.messaging/blob/master/tools/simulator.py
