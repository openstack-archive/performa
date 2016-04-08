Shaker-Spot Report
------------------

This report is generated with help of `Shaker`_.

{{'''
    title: Throughput
    axes:
      x: Node
      y1: Latency, ms
      y2: TCP bandwidth, MBit/s
      y3: TCP retransmitted packets
      y4: UDP 32-byte packets
      y5: UDP loss, %
      y6: Jitter, us
    chart: line
    pipeline:
    - $match: { task: shaker_spot, type: agent }
    - $group:
        _id: { node: "$node" }
        latency: { $avg: "$stats.ping_icmp.avg" }
        bandwidth: { $avg: "$stats.bandwidth.avg" }
        retransmits: { $sum: "$stats.retransmits.max" }
        packets: { $avg: "$stats.packets.avg" }
        loss: { $avg: "$stats.loss.avg" }
        jitter: { $avg: "$stats.jitter.avg" }
    - $project:
        x: "$_id.node"
        y1: "$latency"
        y2: "$bandwidth"
        y3: "$retransmits"
        y4: "$packets"
        y5: "$loss"
        y6: {  $multiply: ["$jitter", 1000] }
''' | table
}}


.. references:

.. _Shaker: http://pyshaker.readthedocs.org/
