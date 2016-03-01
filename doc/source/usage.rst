=====
Usage
=====

**Example**::

    performa --mongo-url 127.0.0.1 --mongo-db performa --scenario db/sysbench \
        --hosts "{target: [192.168.20.20]}" --remote-user developer --debug \
        --book doc/source/test_results/db/sysbench

This example runs Performa tool with scenario 'sb/sysbench'. It uses MongoDB
located at localhost and database named 'performa'. The scenario is executed
against remote host 192.168.20.20 which can be accessed with user 'developer'.
The report is stored into 'doc/source/test_results/db/sysbench' folder.
