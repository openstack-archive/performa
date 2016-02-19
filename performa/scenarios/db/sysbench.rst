Sysbench Report
---------------

This is the report of execution test plan
:ref:`sql_db_test_plan` with `Sysbench`_ tool.

Results
^^^^^^^

Chart and table:

{{'''
    title: Queries per second
    axes:
      x: threads
      y: queries per sec
    chart: line
    pipeline:
    - { $match: { class: sysbench-oltp, status: OK }}
    - { $group: { _id: { threads: "$threads" }, queries_total_per_sec: { $avg: { $divide: ["$queries_total", "$duration"] }}}}
    - { $project: { x: "$_id.threads", y: "$queries_total_per_sec" }}
    - { $sort: { x: 1 }}
''' | chart
}}

.. references:

.. _Sysbench: https://github.com/akopytov/sysbench
