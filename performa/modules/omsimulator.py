#!/usr/bin/python
import copy
import os
import signal
import tempfile

SERVER_PID = os.path.join(tempfile.gettempdir(), 'performa.oms.pid')
SERVER_FILE_NAME = os.path.join(tempfile.gettempdir(), 'performa.oms.srv')
CLIENT_FILE_NAME = os.path.join(tempfile.gettempdir(), 'performa.oms.cln')
UNIQUE_NAME = 'performa_omsimulator'
DIR = '/tmp/performa/oslo.messaging/tools/'
PYTHON = '/tmp/performa/oslo.messaging/.venv/bin/python'

PATTERNS = [
    r'(?P<msg_sent>\d+) messages were sent for (?P<duration>\d+) sec',
    r'(?P<bytes_sent>\d+) bytes were sent for',
]
TRANSFORM_FIELDS = {
    'msg_sent': int,
    'bytes_sent': int,
    'duration': int,
}


def parse_output(raw):
    result = {}

    for pattern in PATTERNS:
        for parsed in re.finditer(pattern, raw):
            result.update(parsed.groupdict())

    for k in result.keys():
        if k in TRANSFORM_FIELDS:
            result[k] = TRANSFORM_FIELDS[k](result[k])

    result['msg_sent_bandwidth'] = (result.get('msg_sent', 0) /
                                    result.get('duration', 1))
    result['bytes_sent_bandwidth'] = (result.get('bytes_sent', 0) /
                                      result.get('duration', 1))

    return result


def chdir(module):
    try:
        os.chdir(DIR)
    except Exception as e:
        module.fail_json(msg='Failed to change dir to %s: %s' % (DIR, e))


def start_daemon(module, cmd):
    cmd = ('daemon -n %(name)s -D %(dir)s -F %(pid)s -U -- %(cmd)s' %
           dict(name=UNIQUE_NAME, dir=DIR, pid=SERVER_PID, cmd=cmd))

    rc, stdout, stderr = module.run_command(cmd)
    result = dict(changed=True, rc=rc, stdout=stdout, stderr=stderr, cmd=cmd)

    if rc:
        module.fail_json(msg='Failed to start omsimulator', **result)


def stop_daemon(module):
    rc, stdout, stderr = module.run_command('/bin/cat %s' % SERVER_PID)

    if rc:
        return

    rc, stdout, stderr = module.run_command('pgrep -P %s' % stdout)
    os.kill(int(stdout), signal.SIGINT)

    time.sleep(2)


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


def run(module):
    params = copy.deepcopy(module.params)

    if params['mode'] == 'notify':
        server_tool = 'notify-server'
        client_tool = 'notify-client'
    else:
        server_tool = 'rpc-server'
        client_tool = 'rpc-client'

    params['python'] = PYTHON
    # todo: fix topic support in omsimulator
    # params['topic'] = 'performa-%d' % (random.random() * 1000000)
    params['server_tool'] = server_tool
    params['client_tool'] = client_tool
    params['server_file'] = SERVER_FILE_NAME
    params['client_file'] = CLIENT_FILE_NAME

    params['url'] = params['server_url'] or params['url']
    server = ('%(python)s simulator.py '
              # '--topic %(topic)s '
              '--url %(url)s '
              '--json %(server_file)s '
              '%(server_tool)s ') % params

    params['url'] = params['client_url'] or params['url']
    client = ('%(python)s simulator.py '
              # '--topic %(topic)s '
              '--url=%(url)s '
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

    start_daemon(module, server)

    rc, stdout, stderr = module.run_command(client)

    if rc:
        module.fail_json(msg='Failed to start omsimulator',
                         stderr=stderr, rc=rc, cmd=client)

    stop_daemon(module)

    try:
        client_data = read_file(CLIENT_FILE_NAME)
        server_data = read_file(SERVER_FILE_NAME)

        client_summary = client_data['summary']['client']

        record = dict(start=client_summary['start'],
                      end=client_summary['end'],
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

        result = dict(records=[record], series=series)
        module.exit_json(**result)
    except Exception as e:
        msg = 'Failed to read omsimulator output: %s' % e
        module.fail_json(msg=msg, rc=rc, stderr=stderr, stdout=stdout)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            mode=dict(required=True,
                      choices=['call', 'cast', 'fanout', 'notify']),
            url=dict(required=True),
            client_url=dict(),
            server_url=dict(),
            threads=dict(type='int', default=10),
            duration=dict(type='int', default=10),
            timeout=dict(type='int', default=5),
            sending_delay=dict(type='float', default=-1.0),
        ))

    chdir(module)
    run(module)


from ansible.module_utils.basic import *  # noqa

if __name__ == '__main__':
    main()
