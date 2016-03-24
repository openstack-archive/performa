#!/usr/bin/python
import copy
import multiprocessing
import os
import signal
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

    client = ('%(python)s simulator.py '
              '--url %(url)s '
              '--json %(client_file)s '
              '-l %(duration)s '
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

    server = ('%(python)s simulator.py '
              '--url %(url)s '
              '--json %(server_file)s '
              '%(server_tool)s ') % params

    return server


def run_client(module, command):
    module.run_command(command)


def run_client_pool(module, params):
    processes = []

    for i in range(params['processes']):
        cmd = make_client_cmd(params, i)
        p = multiprocessing.Process(target=run_client, args=(module, cmd))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()


def run_server(module, command):
    module.run_command(command)


def start_server_pool(module, params):
    processes = []

    for i in range(params['processes']):
        cmd = make_server_cmd(params, i)
        p = multiprocessing.Process(target=run_client, args=(module, cmd))
        processes.append(p)
        p.start()

    return processes


def stop_server_pool(module, processes):
    for p in processes:
        rc, stdout, stderr = module.run_command('pgrep -P %s' % p.pid)

        for child in (int(p) for p in stdout.split('\n') if p):
            os.kill(child, signal.SIGINT)

    time.sleep(3)  # let simulators handle the signal

    for p in processes:
        os.kill(p.pid, signal.SIGINT)
        p.join()


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

    server_processes = start_server_pool(module, params)

    run_client_pool(module, params)

    stop_server_pool(module, server_processes)

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
        ))

    chdir(module)
    run(module)


from ansible.module_utils.basic import *  # noqa

if __name__ == '__main__':
    main()
