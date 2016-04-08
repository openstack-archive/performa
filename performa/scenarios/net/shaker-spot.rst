Shaker-Spot Report
------------------

This scenario is executed with `Sysbench`_ tool. There is one instance of
tool per tester node, each running in N threads.

Throughput
^^^^^^^^^^

The following chart shows the number of queries, read queries and transactions
depending on total thread count.

{{'''
    title: Throughput
    axes:
      x: threads
      y1: queries per sec
      y2: read queries per sec
      y3: transactions per sec
    chart: line
    pipeline:
    - $match: { task: sysbench_oltp }
    - $group:
        _id: { threads: { $multiply: [ "$threads", "$host_count" ] } }
        queries_total_per_sec: { $sum: { $divide: ["$queries_total", "$duration"] }}
        queries_read_per_sec: { $sum: { $divide: ["$queries_read", "$duration"] }}
        transactions_per_sec: { $sum: { $divide: ["$transactions", "$duration"] }}
    - $project:
        x: "$_id.threads"
        y1: "$queries_total_per_sec"
        y2: "$queries_read_per_sec"
        y3: "$transactions_per_sec"
''' | chart_and_table
}}


Throughput and server CPU consumption
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following chart shows how DB server CPU consumption depends on number
of concurrent threads and throughput.

{{'''
    title: CPU consumption
    axes:
      x: threads
      y1: queries per sec
      y2: CPU, %
    chart: line
    pipeline:
    - $match: { task: sysbench_oltp }
    - $group:
        _id: { threads: { $multiply: [ "$threads", "$host_count" ] } }
        queries_total_per_sec: { $sum: { $divide: ["$queries_total", "$duration"] }}
        mysqld_total: { $avg: "$mysqld_total" }
    - $project:
        x: "$_id.threads"
        y1: "$queries_total_per_sec"
        y2: { $multiply: [ "$mysqld_total", 100 ] }
''' | chart_and_table
}}


Operation latency
^^^^^^^^^^^^^^^^^

The following chart shows how operation latency depends on number of
concurrent threads.

{{'''
    title: Latency
    axes:
      x: threads
      y1: min latency, ms
      y2: avg latency, ms
      y3: max latency, ms
    chart: line
    pipeline:
    - $match: { task: sysbench_oltp }
    - $group:
        _id: { threads: { $multiply: [ "$threads", "$host_count" ] } }
        latency_min: { $min: "$latency_min" }
        latency_avg: { $avg: "$latency_avg" }
        latency_max: { $max: "$latency_max" }
    - $project:
        x: "$_id.threads"
        y1: "$latency_min"
        y2: "$latency_avg"
        y3: "$latency_max"
''' | chart_and_table
}}


.. references:

.. _Sysbench: https://github.com/akopytov/sysbench
