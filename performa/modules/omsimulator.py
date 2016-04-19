#!/usr/bin/python
import copy
import multiprocessing
import os
import random
import tempfile

SERVER_PID = os.path.join(tempfile.gettempdir(), 'performa.oms.pid')
SERVER_FILE_NAME = os.path.join(tempfile.gettempdir(), 'performa.oms.srv')
CLIENT_FILE_NAME = os.path.join(tempfile.gettempdir(), 'performa.oms.cln')
UNIQUE_NAME = 'performa_omsimulator'
DIR = '/tmp/performa/oslo.messaging/tools/'
PYTHON = '/tmp/performa/oslo.messaging/.venv/bin/python'


def chdir(module):
    try:
        os.chdir(DIR)
    except Exception as e:
        module.fail_json(msg='Failed to change dir to %s: %s' % (DIR, e))


def read_file(filename):
    fd = None
    try:
        fd = open(filename)
        return json.loads(fd.read())
    except IOError:
        raise
    finally:
        if fd:
            fd.close()


def transform_series(series):
    result = []
    for k, v in series.items():
        for x in v:
            x['name'] = k
        result += v
    return result


def make_file_name(base, index):
    return '%s-%s' % (base, index)


def make_client_cmd(params, i):
    params['client_file'] = make_file_name(CLIENT_FILE_NAME, i)
    params['url'] = params['client_url'] or params['url']

    params['this_topic'] = params['topic']
    if params['unique_topic_per_pair']:
        params['this_topic'] += '_%s' % i

    client = ('%(python)s simulator.py '
              '--url %(url)s '
              '--json %(client_file)s '
              '-l %(duration)s '
              '--topic %(this_topic)s '
              '%(client_tool)s '
              '--timeout %(timeout)s '
              '-w %(sending_delay)s '
              '-p %(threads)s ') % params

    if params['mode'] == 'cast':
        client += '--is-cast True '

    if params['mode'] == 'fanout':
        client += '--is-fanout True '

    return client


def make_server_cmd(params, i):
    params['server_file'] = make_file_name(SERVER_FILE_NAME, i)
    params['url'] = params['server_url'] or params['url']
    params['server_duration'] = (params['duration'] +
                                 params['server_teardown_duration'])
    params['this_topic'] = params['topic']
    if params['unique_topic_per_pair']:
        params['this_topic'] += '_%s' % i

    server = ('%(python)s simulator.py '
              '--url %(url)s '
              '--json %(server_file)s '
              '-l %(server_duration)s '
              '--topic %(this_topic)s '
              '%(server_tool)s ') % params

    return server


def run_pool(module, params):
    processes = []

    for i in range(params['processes']):
        cmd = make_client_cmd(params, i)
        p = multiprocessing.Process(target=module.run_command, args=(cmd,))
        processes.append(p)
        p.start()

        cmd = make_server_cmd(params, i)
        p = multiprocessing.Process(target=module.run_command, args=(cmd,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()


def cleanup_old_files(module, params):
    for i in range(params['processes']):
        try:
            os.unlink(make_file_name(CLIENT_FILE_NAME, i))
            os.unlink(make_file_name(SERVER_FILE_NAME, i))
        except OSError:
            pass  # ignore


def collect_results(params):
    result = dict(records=[], series=[])

    for i in range(params['processes']):
        client_data = read_file(make_file_name(CLIENT_FILE_NAME, i))
        server_data = read_file(make_file_name(SERVER_FILE_NAME, i))

        client_summary = client_data['summary']['client']
        record = dict(start=client_summary['start'], end=client_summary['end'],
                      client=client_summary)
        if 'round_trip' in client_data['summary']:
            round_trip_summary = client_data['summary']['round_trip']
            record['round_trip'] = round_trip_summary
        if 'error' in client_data['summary']:
            error_summary = client_data['summary']['error']
            record['error'] = error_summary
        server_summary = server_data['summary']
        record['server'] = server_summary
        series = transform_series(client_data['series'])
        series.extend(transform_series(server_data['series']))

        result['records'].append(record)
        result['series'] += series

    return result


def run(module):
    params = copy.deepcopy(module.params)

    if params['mode'] == 'notify':
        server_tool = 'notify-server'
        client_tool = 'notify-client'
    else:
        server_tool = 'rpc-server'
        client_tool = 'rpc-client'

    params['python'] = PYTHON
    params['server_tool'] = server_tool
    params['client_tool'] = client_tool

    if not params['topic']:
        params['topic'] = 'performa_%s' % random.random()

    cleanup_old_files(module, params)

    run_pool(module, params)

    try:
        result = collect_results(params)
        module.exit_json(**result)
    except Exception as e:
        msg = 'Failed to read omsimulator output: %s' % e
        module.fail_json(msg=msg)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            mode=dict(required=True,
                      choices=['call', 'cast', 'fanout', 'notify']),
            url=dict(),
            client_url=dict(),
            server_url=dict(),
            threads=dict(type='int', default=10),
            processes=dict(type='int', default=1),
            duration=dict(type='int', default=10),
            timeout=dict(type='int', default=5),
            sending_delay=dict(type='float', default=-1.0),
            topic=dict(),
            unique_topic_per_pair=dict(type='bool', default=False),
            server_teardown_duration=dict(type='int', default=15),
        ))

    chdir(module)
    run(module)


from ansible.module_utils.basic import *  # noqa

if __name__ == '__main__':
    main()
