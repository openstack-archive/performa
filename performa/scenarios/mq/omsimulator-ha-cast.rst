Oslo.messaging simulator HA report
----------------------------------

This report is result of `message_queue_performance`_ execution
with `Oslo.messaging Simulator`_


Test Case 1: RPC CAST Throughput Test
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Messages sent by the client**

{{'''
    title: RPC CAST sent messages
    axes:
      x: time
      y: sent, msg
    chart: line
    collection: series
    pipeline:
    - { $match: { task: omsimulator, mode: cast, name: client_0 }}
    - { $project: { x: "$seq",
                    y: "$count"
                  }}
    - { $sort: { x: 1 }}
''' | chart
}}

**Messages received by the server**

{{'''
    title: RPC CAST received messages
    axes:
      x: time
      y: round-trip, msg
      y2: latency, ms
    chart: line
    collection: series
    pipeline:
    - { $match: { task: omsimulator, mode: cast, name: server }}
    - { $project: { x: "$seq",
                    y: "$count",
                    y2: { $multiply: ["$latency", 1000] }
                  }}
    - { $sort: { x: 1 }}
''' | chart
}}
