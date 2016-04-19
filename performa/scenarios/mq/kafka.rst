Oslo.messaging simulator report
-------------------------------

This report contains results of `message_queue_performance`_ execution
with `Oslo.messaging Simulator`_ with Kafka driver.


Test Case: Notification Throughput Test
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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


The throughput and latency
~~~~~~~~~~~~~~~~~~~~~~~~~~

The chart shows the throughput and latency depending on number of concurrent threads.

{{'''
    title: NOTIFY throughput and latency depending on thread count
    axes:
      x: threads
      y: throughput, msg/sec
      y3: latency, ms
    chart: line
    pipeline:
    - $match: { task: omsimulator, mode: notify }
    - $group:
        _id: { threads: { $multiply: [ "$threads", "$host_count", "$processes" ] } }
        throughput: { $sum: { $divide: ["$client.count", "$client.duration"] }}
        latency: { $avg: "$server.latency" }
    - $project:
        x: "$_id.threads"
        y: "$throughput"
        y3: { $multiply: [ "$latency", 1000 ] }
''' | chart_and_table
}}


.. references:

.. _message_queue_performance: http://docs.openstack.org/developer/performance-docs/test_plans/mq/plan.html
.. _Oslo.messaging Simulator: https://github.com/openstack/oslo.messaging/blob/master/tools/simulator.py
