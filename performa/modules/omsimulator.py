#!/usr/bin/python
import copy
import os
import tempfile

import signal

SERVER_PID = os.path.join(tempfile.gettempdir(), 'performa.oms.pid')
SERVER_FILE_NAME = os.path.join(tempfile.gettempdir(), 'performa.oms.srv')
CLIENT_FILE_NAME = os.path.join(tempfile.gettempdir(), 'performa.oms.cln')
UNIQUE_NAME = 'performa_omsimulator'
DIR = '/tmp/performa/oslo.messaging/tools/'

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
    cmd = ('daemon -n %(name)s -D %(dir)s -F %(pid)s -- %(cmd)s' %
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

    params['server_tool'] = server_tool
    params['client_tool'] = client_tool
    params['server_file'] = SERVER_FILE_NAME
    params['client_file'] = CLIENT_FILE_NAME

    server = ('python simulator.py '
              '--url %(url)s '
              '--json %(server_file)s '
              '%(server_tool)s ') % params
    client = ('python simulator.py '
              '--url=%(url)s '
              '--json %(client_file)s '
              '-l %(duration)s '
              '%(client_tool)s '
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
        client_summary['component'] = 'client'
        server_summary = server_data['summary']
        server_summary['component'] = 'server'

        series = transform_series(client_data['series'])
        series.extend(transform_series(server_data['series']))

        result = dict(records=[client_summary, server_summary], series=series)
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
            threads=dict(type='int', default=10),
            duration=dict(type='int', default=10),
        ))

    chdir(module)
    run(module)


from ansible.module_utils.basic import *  # noqa

if __name__ == '__main__':
    main()
