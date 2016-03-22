RPC CALL fail-over test report
------------------------------

This scenario is executed with help of oslo.messaging simulator. There is
one client-server pair of simulator running in single-threaded mode. The
stats are collected from both client and server and detailed report is shown
with one second precision.


Execution Summary
^^^^^^^^^^^^^^^^^

{{'''
    title: RPC CALL Execution summary
    fields:
      a1: Client sent, msg
      a2: Server received, msg
      a3: Client received replies, msg
      a4: Loss, msg
      a5: Errors, msg
      b1: Duration, sec
      c1: Throughput, msg/sec
      d1: Transfer, Mb
      d2: Bandwidth, Mb/sec
      e1: Avg. request latency, ms
      e2: Max request latency, ms
      e3: Avg. round-trip latency, ms
      e4: Max round-trip latency, ms
    collection: records
    pipeline:
    - $match: { task: omsimulator, mode: call }
    - $project:
        a1: "$client.count"
        a2: "$server.count"
        a3: "$round_trip.count"
        a4: { $subtract: ["$client.count", "$round_trip.count" ] }
        a5: "$error.count"
        b1: "$client.duration"
        c1: { $divide: ["$client.count", "$client.duration"] }
        d1: { $divide: ["$client.size", 1048576] }
        d2: { $divide: [$divide: ["$client.size", 1048576], "$client.duration"] }
        e1: { $multiply: ["$server.latency", 1000] }
        e2: { $multiply: ["$server.max_latency", 1000] }
        e3: { $multiply: ["$round_trip.latency", 1000] }
        e4: { $multiply: ["$round_trip.max_latency", 1000] }
''' | info
}}


Message flow
^^^^^^^^^^^^

This chart shows the message flow between client and server. It includes
messages sent by the client, received by the server, replies received by
the client and errors caught by the client.

{{'''
    title: RPC CALL message flow
    axes:
      x: time
      y1: sent, msg
      y2: received, msg
      y3: round-trip, msg
      y4: errors, msg
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
    -
      - $match: { task: omsimulator, mode: call, name: error_0 }
      - $project:
          x: "$timestamp"
          y4: "$count"
''' | chart
}}

where:
 * ``sent`` - messages sent by the client
 * ``received`` - messages received by the server
 * ``round-trip`` - replies to messages received by the client
 * ``errors`` - errors exposed and caught by the client


Messages sent by the client
^^^^^^^^^^^^^^^^^^^^^^^^^^^

This chart shows messages sent by client and error rate.

{{'''
    title: RPC CALL sent messages
    axes:
      x: time
      y: sent, msg
      y2: errors, msg
    chart: line
    collection: series
    pipelines:
    -
      - $match: { task: omsimulator, mode: call, name: client_0 }
      - $project:
          x: "$seq"
          y: "$count"
    -
      - $match: { task: omsimulator, mode: call, name: error_0 }
      - $project:
          x: "$seq"
          y2: "$count"
''' | chart_and_table
}}

Messages received by the server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This chart shows messages received by the server and their latency.

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

Replies received by the client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This chart shows replies received by the client and total round-trip latency.

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
