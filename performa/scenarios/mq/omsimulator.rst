OMSimulator Report
------------------

This is the report of execution test plan
:ref:`mq_test_plan` with `OMSimulator`_ tool.

Results
^^^^^^^

Messages per second depending on threads count:

{{'''
    title: Messages per second
    axes:
      x: threads
      y: messages per sec
      y2: latency
    chart: line
    pipeline:
    - { $match: { task: omsimulator, status: OK }}
    - { $group: { _id: { threads: { $multiply: [ "$threads", "$host_count" ] } },
                  msg_sent_per_sec: { $avg: { $divide: ["$count", "$duration"] }},
                  latency: { $avg: "$latency" }
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
    - { $match: { task: omsimulator, status: OK }}
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
    - { $match: { task: omsimulator, status: OK }}
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
