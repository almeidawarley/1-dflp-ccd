from datetime import datetime

def create_record(project, instance):

    record = {}

    record['project'] = project
    record['keyword'] = instance.keyword
    record['created'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for key, value in instance.parameters.items():
        record[key] = value

    write_record(record)

    return record

def update_record(record, updates):

    for key, value in updates.items():
        record[key] = value

    write_record(record)

    return record

def write_record(record):

    with open('records/{}.csv'.format(record['keyword']), 'w') as output:
        head = ','.join([str(key) for key in record.keys()])
        row  = ','.join([str(value) for value in record.values()])
        output.write('{}\n{}'.format(head, row))