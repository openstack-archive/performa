OMSimulator Report
------------------

This is the report of execution test plan
:ref:`mq_test_plan` with `OMSimulator`_ tool.

Results
^^^^^^^

**Message processing**

The chart and table show the number of messages processed by a single process
depending on number of eventlet threads inside of it. Messages are collected
at 3 points: ``sent`` - messages sent by the client, ``received`` - messages
received by the server, ``round-trip`` - replies received by the client.

{{'''
    title: Throughput
    axes:
      x: threads
      y: sent, msg
      y2: received, msg
      y3: round-trip, msg
    chart: line
    pipeline:
    - { $match: { task: omsimulator, component: client }}
    - { $group: { _id: { threads: { $multiply: [ "$threads", "$host_count" ] } },
                  sent: { $avg: "$client.count" },
                  received: { $avg: "$server.count" },
                  round_trip: { $avg: "$round_trip.count" }
                }}
    - { $project: { x: "$_id.threads",
                    y: "$sent",
                    y2: "$received",
                    y3: "$round_trip"
                  }}
    - { $sort: { x: 1 }}
''' | chart
}}


**Message throughput, latency depending on thread count**

{{'''
    title: Throughput, latency depending on thread count
    axes:
      x: threads
      y: throughput, msg/sec
      y2: latency, ms
    chart: line
    pipeline:
    - { $match: { task: omsimulator, component: client }}
    - { $group: { _id: { threads: { $multiply: [ "$threads", "$host_count" ] } },
                  msg_sent_per_sec: { $avg: { $divide: ["$count", "$duration"] }},
                  latency: { $avg: "$latency" },
                }}
    - { $project: { x: "$_id.threads",
                    y: "$msg_sent_per_sec",
                    y2: { $multiply: ["$latency", 1000] }
                  }}
    - { $sort: { x: 1 }}
''' | chart
}}

Messages per second and rabbit CPU consumption depending on threads count:

{{'''
    title: Queries and and CPU util per second
    axes:
      x: threads
      y: queries per sec
      y2: rabbit CPU consumption, %
    chart: line
    pipeline:
    - { $match: { task: omsimulator }}
    - { $group: { _id: { threads: { $multiply: [ "$threads", "$host_count" ] } },
                  msg_sent_per_sec: { $avg: { $divide: ["$count", "$duration"] }},
                  rabbit_total: { $avg: "$rabbit_total" }
                }}
    - { $project: { x: "$_id.threads",
                    y: "$msg_sent_per_sec",
                    y2: { $multiply: [ "$rabbit_total", 100 ] }
                  }}
    - { $sort: { x: 1 }}
''' | chart
}}


{{'''
    title: Latency depending on msg/sec
    axes:
      x: messages per sec
      y: latency
    chart: line
    pipeline:
    - { $match: { task: omsimulator }}
    - { $group: { _id: { threads: { $multiply: [ "$threads", "$host_count" ] } },
                  msg_sent_per_sec: { $avg: { $divide: ["$count", "$duration"] }},
                  latency: { $avg: "$latency" }
                }}
    - { $project: { x: "$msg_sent_per_sec",
                    y: { $multiply: ["$latency", 1000] }
                  }}
    - { $sort: { x: 1 }}
''' | chart
}}
