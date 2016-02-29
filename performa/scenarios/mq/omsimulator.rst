Sysbench Report
---------------

This is the report of execution test plan
:ref:`mq_test_plan` with `Sysbench`_ tool.

Results
^^^^^^^

Chart and table:

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

.. references:

.. _Sysbench: https://github.com/akopytov/sysbench
