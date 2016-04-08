#!/usr/bin/python

import copy

DIR = '/tmp/performa/shaker.venv/bin/'
OUTPUT = '/tmp/performa/shaker.output.json'


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


def get_series(shaker_report):
    series = []
    agent_records = (r for r in shaker_report['records'].values()
                     if r['type'] == 'agent')
    for record in agent_records:
        meta = record['meta']
        samples = record['samples']
        offset = record['start']

        for sample in samples:
            point = {'meta': dict(tuple(a) for a in meta)}
            for i in range(len(meta)):
                point[meta[i][0]] = sample[i]

            point['time'] += offset
            series.append(point)

    return series


def get_records(shaker_report):
    records = []
    agent_records = (r for r in shaker_report['records'].values()
                     if r['type'] == 'agent')
    for record in agent_records:
        for key in ['verbose', 'chart', 'samples']:
            if key in record:
                del record[key]
        records.append(record)

    return records


def main():
    module = AnsibleModule(
        argument_spec=dict(
            duration=dict(type='int', default=10),
            scenario=dict(),
            targets=dict(type='list'),
        ))

    params = copy.copy(module.params)
    params['targets_str'] = ','.join(params['targets'])
    params['output'] = OUTPUT

    cmd = (DIR + 'shaker-spot '
           '--scenario %(scenario)s '
           '--report-template json '
           '--report %(output)s '
           '--matrix "{host: [%(targets_str)s], time: %(duration)s}" '
           ) % params

    start = int(time.time())
    rc, stdout, stderr = module.run_command(cmd)
    end = int(time.time())

    try:
        shaker_report = read_file(OUTPUT)
        series = get_series(shaker_report)
        records = get_records(shaker_report)

        parsed = dict()
        parsed['start'] = start
        parsed['end'] = end
        parsed['cmd'] = cmd
        # records.append(parsed)

        result = dict(records=records, series=series)
        module.exit_json(**result)
    except Exception as e:
        module.fail_json(msg=str(e), rc=rc, stderr=stderr, stdout=stdout)


from ansible.module_utils.basic import *  # noqa

if __name__ == '__main__':
    main()
