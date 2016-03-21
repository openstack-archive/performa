Oslo.messaging simulator HA report
----------------------------------

This report is result of `message_queue_performance`_ execution
with `Oslo.messaging Simulator`_


RPC CALL fail-over throughput test
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Summary**

{{'''
    title: Execution summary
    fields:
      a1: Client sent, msg
      b1: Server received, msg
      b2: Client received replies, msg
      b3: Loss, msg
      c1: Avg. request latency, ms
      c2: Max request latency, ms
      c3: Avg. round-trip latency, ms
      c4: Max round-trip latency, ms
    collection: records
    pipeline:
    - $match: { task: omsimulator, mode: call }
    - $project:
        a1: "$client.count"
        b1: "$server.count"
        b2: "$round_trip.count"
        b3: { $subtract: ["$client.count", "$round_trip.count" ] }
        c1: { $multiply: ["$server.latency", 1000] }
        c2: { $multiply: ["$server.max_latency", 1000] }
        c3: { $multiply: ["$round_trip.latency", 1000] }
        c4: { $multiply: ["$round_trip.max_latency", 1000] }
''' | info
}}


**Message flow**

{{'''
    title: RPC CALL message flow
    axes:
      x: time
      y1: sent, msg
      y2: received, msg
      y3: round-trip, msg
      y4: latency, ms
    chart: line
    collection: series
    pipelines:
    -
      - $match: { task: omsimulator, mode: call, name: client_0 }
      - $project:
          x: "$timestamp"
          y1: "$count"
    -
      - $match: { task: omsimulator, mode: call, name: server }
      - $project:
          x: "$timestamp"
          y2: "$count"
    -
      - $match: { task: omsimulator, mode: call, name: round_trip_0 }
      - $project:
          x: "$timestamp"
          y3: "$count"
          y4: { $multiply: ["$latency", 1000] }
''' | chart
}}


**Messages sent by the client**

{{'''
    title: RPC CALL sent messages
    axes:
      x: time
      y: sent, msg
    chart: line
    collection: series
    pipeline:
    - $match: { task: omsimulator, mode: call, name: client_0 }
    - $project:
        x: "$seq"
        y: "$count"
''' | chart_and_table
}}

**Messages received by the server**

{{'''
    title: RPC CALL received messages
    axes:
      x: time
      y: sent, msg
      y2: latency, ms
    chart: line
    collection: series
    pipeline:
    - $match: { task: omsimulator, mode: call, name: server }
    - $project:
        x: "$seq"
        y: "$count"
        y2: { $multiply: ["$latency", 1000] }
''' | chart_and_table
}}

**Round-trip messages received by the client**

{{'''
    title: RPC CALL round-trip messages
    axes:
      x: time
      y: round-trip, msg
      y2: latency, ms
    chart: line
    collection: series
    pipeline:
    - $match: { task: omsimulator, mode: call, name: round_trip_0 }
    - $project:
        x: "$seq"
        y: "$count"
        y2: { $multiply: ["$latency", 1000] }
''' | chart_and_table
}}
