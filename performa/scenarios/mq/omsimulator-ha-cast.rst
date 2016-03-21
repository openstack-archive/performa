Oslo.messaging simulator HA report
----------------------------------

This report is result of `message_queue_performance`_ execution
with `Oslo.messaging Simulator`_


RPC CAST fail-over throughput test
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Summary**

{{'''
    title: Execution summary
    fields:
      a1: Client sent, msg
      b1: Server received, msg
      b2: Loss, msg
      c1: Avg. latency, ms
      c2: Max latency, ms
    collection: records
    pipeline:
    - $match: { task: omsimulator, mode: cast }
    - $project:
        a1: "$client.count"
        b1: "$server.count"
        b2: { $subtract: ["$client.count", "$server.count" ] }
        c1: { $multiply: ["$server.latency", 1000] }
        c2: { $multiply: ["$server.max_latency", 1000] }
''' | info
}}

**Message flow**

{{'''
    title: RPC CAST message flow
    axes:
      x: time
      y1: sent, msg
      y2: received, msg
      y3: latency, ms
    chart: line
    collection: series
    pipelines:
    -
      - $match: { task: omsimulator, mode: cast, name: client_0 }
      - $project:
          x: "$timestamp"
          y1: "$count"
    -
      - $match: { task: omsimulator, mode: cast, name: server }
      - $project:
          x: "$timestamp"
          y2: "$count"
          y3: { $multiply: ["$latency", 1000] }
''' | chart
}}


**Messages sent by the client**

{{'''
    title: RPC CAST sent messages
    axes:
      x: time
      y: sent, msg
    chart: line
    collection: series
    pipeline:
    - $match: { task: omsimulator, mode: cast, name: client_0 }
    - $project:
        x: "$seq"
        y: "$count"
''' | chart_and_table
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
    - $match: { task: omsimulator, mode: cast, name: server }
    - $project:
        x: "$seq",
        y: "$count"
        y2: { $multiply: ["$latency", 1000] }
''' | chart_and_table
}}
