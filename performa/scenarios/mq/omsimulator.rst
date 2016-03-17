Oslo.messaging simulator report
-------------------------------

This report is result of `message_queue_performance`_ execution
with `Oslo.messaging Simulator`_


Test Case 1: RPC CALL Throughput Test
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Message processing**

Messages are collected at 3 points: ``sent`` - messages sent by the client,
``received`` - messages received by the server, ``round-trip`` - replies
received by the client. Also the number of lost messages is calculated.

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
    - { $group: { _id: { threads: { $multiply: [ "$threads", "$host_count" ] } },
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
''' | chart
}}


**Message throughput, latency and RabbitMQ CPU utilization depending on thread count**

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
    - { $match: { task: omsimulator, mode: call }}
    - { $group: { _id: { threads: { $multiply: [ "$threads", "$host_count" ] } },
                  msg_sent_per_sec: { $avg: { $divide: ["$client.count", "$client.duration"] }},
                  msg_received_per_sec: { $avg: { $divide: ["$server.count", "$server.duration"] }},
                  msg_round_trip_per_sec: { $avg: { $divide: ["$round_trip.count", "$round_trip.duration"] }},
                  latency: { $avg: "$round_trip.latency" },
                  rabbit_total: { $avg: "$rabbit_total" }
                }}
    - { $project: { x: "$_id.threads",
                    y: "$msg_sent_per_sec",
                    y2: "$msg_received_per_sec",
                    y3: "$msg_round_trip_per_sec",
                    y4: { $multiply: [ "$latency", 1000 ] },
                    y5: { $multiply: [ "$rabbit_total", 100 ] }
                  }}
    - { $sort: { x: 1 }}
''' | chart
}}


Test Case 2: RPC CAST Throughput Test
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Message processing**

Messages are collected at 2 points: ``sent`` - messages sent by the client
and ``received`` - messages received by the server. Also the number of lost
messages is calculated.

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
    - { $group: { _id: { threads: { $multiply: [ "$threads", "$host_count" ] } },
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
''' | chart
}}


**Message throughput, latency and RabbitMQ CPU utilization depending on thread count**

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
    - { $match: { task: omsimulator, mode: cast }}
    - { $group: { _id: { threads: { $multiply: [ "$threads", "$host_count" ] } },
                  msg_sent_per_sec: { $avg: { $divide: ["$client.count", "$client.duration"] }},
                  msg_received_per_sec: { $avg: { $divide: ["$server.count", "$server.duration"] }},
                  latency: { $avg: "$server.latency" },
                  rabbit_total: { $avg: "$rabbit_total" }
                }}
    - { $project: { x: "$_id.threads",
                    y: "$msg_sent_per_sec",
                    y2: "$msg_received_per_sec",
                    y3: { $multiply: [ "$latency", 1000 ] },
                    y4: { $multiply: [ "$rabbit_total", 100 ] }
                  }}
    - { $sort: { x: 1 }}
''' | chart
}}


Test Case 3: Notification Throughput Test
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Message processing**

Messages are collected at 2 points: ``sent`` - messages sent by the client
and ``received`` - messages received by the server. Also the number of lost
messages is calculated.

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
    - { $group: { _id: { threads: { $multiply: [ "$threads", "$host_count" ] } },
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
''' | chart
}}


**Message throughput, latency and RabbitMQ CPU utilization depending on thread count**

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
    - { $match: { task: omsimulator, mode: notify }}
    - { $group: { _id: { threads: { $multiply: [ "$threads", "$host_count" ] } },
                  msg_sent_per_sec: { $avg: { $divide: ["$client.count", "$client.duration"] }},
                  msg_received_per_sec: { $avg: { $divide: ["$server.count", "$server.duration"] }},
                  latency: { $avg: "$server.latency" },
                  rabbit_total: { $avg: "$rabbit_total" }
                }}
    - { $project: { x: "$_id.threads",
                    y: "$msg_sent_per_sec",
                    y2: "$msg_received_per_sec",
                    y3: { $multiply: [ "$latency", 1000 ] },
                    y4: { $multiply: [ "$rabbit_total", 100 ] }
                  }}
    - { $sort: { x: 1 }}
''' | chart
}}

.. references:

.. _message_queue_performance: http://docs.openstack.org/developer/performance-docs/test_plans/mq/plan.html
.. _Oslo.messaging Simulator: https://github.com/openstack/oslo.messaging/blob/master/tools/simulator.py
