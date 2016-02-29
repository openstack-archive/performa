Sysbench Report
---------------

This is the report of execution test plan
:ref:`sql_db_test_plan` with `Sysbench`_ tool.

Results
^^^^^^^

Queries per second depending on threads count:

{{'''
    title: Queries per second
    axes:
      x: threads
      y: queries per sec
      y2: read queries per sec
    chart: line
    pipeline:
    - { $match: { task: sysbench_oltp, status: OK }}
    - { $group: { _id: { threads: "$threads" },
                  queries_total_per_sec: { $avg: { $divide: ["$queries_total", "$duration"] }},
                  queries_read_per_sec: { $avg: { $divide: ["$queries_read", "$duration"] }}
                }}
    - { $project: { x: "$_id.threads",
                    y: "$queries_total_per_sec",
                    y2: "$queries_read_per_sec"
                  }}
    - { $sort: { x: 1 }}
''' | chart
}}

Queries per second and mysqld CPU consumption depending on threads count:

{{'''
    title: Queries and and CPU util per second
    axes:
      x: threads
      y: queries per sec
      y2: mysqld CPU consumption, %
    chart: line
    pipeline:
    - { $match: { task: sysbench_oltp, status: OK }}
    - { $group: { _id: { threads: "$threads" },
                  queries_total_per_sec: { $avg: { $divide: ["$queries_total", "$duration"] }},
                  mysqld_total: { $avg: "$mysqld_total" }
                }}
    - { $project: { x: "$_id.threads",
                    y: "$queries_total_per_sec",
                    y2: { $multiply: [ "$mysqld_total", 100 ] }
                  }}
    - { $sort: { x: 1 }}
''' | chart
}}

.. references:

.. _Sysbench: https://github.com/akopytov/sysbench
