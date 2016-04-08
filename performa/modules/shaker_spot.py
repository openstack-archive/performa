#!/usr/bin/python

DIR = '/tmp/performa/shaker.venv/bin/'


def main():
    module = AnsibleModule(
        argument_spec=dict(
            duration=dict(type='int', default=10),
        ))

    cmd = (DIR + 'shaker-spot '
           '--help '
           ) % module.params

    start = int(time.time())
    rc, stdout, stderr = module.run_command(cmd)
    end = int(time.time())

    try:
        parsed = dict()
        parsed['start'] = start
        parsed['end'] = end

        result = dict(records=[parsed])
        module.exit_json(**result)
    except Exception as e:
        module.fail_json(msg=e, rc=rc, stderr=stderr, stdout=stdout)


from ansible.module_utils.basic import *  # noqa

if __name__ == '__main__':
    main()
