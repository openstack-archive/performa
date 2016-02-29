#!/usr/bin/python

import os
import tempfile

ATOP_FILE_NAME = os.path.join(tempfile.gettempdir(), 'performa.atop')
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
    cmd = ('daemon -n %(name)s -D %(dir)s -- %(cmd)s' %
           dict(name=UNIQUE_NAME, dir=DIR, cmd=cmd))

    rc, stdout, stderr = module.run_command(cmd)
    result = dict(changed=True, rc=rc, stdout=stdout, stderr=stderr, cmd=cmd)

    if rc:
        module.fail_json(msg='Failed to start OMSimulator', **result)


def run(module):
    params = module.params

    if params['mode'] == 'notify':
        server_tool = 'notify-server'
        client_tool = 'notify-client'
    else:
        server_tool = 'rpc-server'
        client_tool = 'rpc-client'

    params['server_tool'] = server_tool
    params['client_tool'] = client_tool

    server = ('python simulator.py '
              '--url %(url)s '
              '%(server_tool)s '
              '--show-stats true') % params
    client = ('python simulator.py '
              '--url=%(url)s '
              '-l %(duration)s '
              '%(client_tool)s '
              '-p %(threads)s ') % params

    if params['mode'] == 'cast':
        client += '--is-cast True '

    if params['mode'] == 'fanout':
        client += '--is-fanout True '

    start_daemon(module, server)

    start = int(time.time())
    rc, stdout, stderr = module.run_command(client)
    end = int(time.time())

    if rc:
        module.fail_json(msg='Failed to run omsimulator client', stderr=stderr)

    try:
        parsed = parse_output(stdout)
        parsed['start'] = start
        parsed['end'] = end

        result = dict(records=[parsed])
        module.exit_json(**result)
    except Exception as e:
        msg = 'Failed to start omsimulator client %s' % e
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
