OMSimulator Report
------------------

This is the report of execution test plan
:ref:`mq_test_plan` with `Sysbench`_ tool.

Results
^^^^^^^

Messages per second depending on threads count:

{{'''
    title: Messages per second
    axes:
      x: threads
      y: messages per sec
    chart: line
    pipeline:
    - { $match: { task: omsimulator, status: OK }}
    - { $group: { _id: { threads: "$threads" },
                  msg_sent_per_sec: { $avg: { $divide: ["$msg_sent", "$duration"] }}
                }}
    - { $project: { x: "$_id.threads",
                    y: "$msg_sent_per_sec"
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
    - { $group: { _id: { threads: "$threads" },
                  msg_sent_per_sec: { $avg: { $divide: ["$msg_sent", "$duration"] }},
                  rabbit_total: { $avg: "$rabbit_total" }
                }}
    - { $project: { x: "$_id.threads",
                    y: "$msg_sent_per_sec",
                    y2: { $multiply: [ "$rabbit_total", 100 ] }
                  }}
    - { $sort: { x: 1 }}
''' | chart
}}

.. references:

.. _Sysbench: https://github.com/akopytov/sysbench
