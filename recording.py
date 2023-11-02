from datetime import datetime
import git

def load_record(project, instance):

    record = {}

    try:
        with open('records/{}.csv'.format(instance.keyword), 'r') as input:
            head = input.readline().strip().split(',')
            row  = input.readline().strip().split(',')
            record = {head[i]: row[i] for i in range(len(head))}
    except:
        record = {}
        record['project'] = project
        record['keyword'] = instance.keyword
        record['created'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for key, value in instance.parameters.items():
            record[key] = value

    repo = git.Repo(search_parent_directories = True)

    # Update repo information
    record['updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    record['commit'] = repo.head.object.hexsha
    record['branch'] = repo.active_branch.name

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
        output.write(format_record(record))

def format_record(record):

    head = ','.join([str(key) for key in record.keys()])
    row  = ','.join([str(value) for value in record.values()])
    return '{}\n{}'.format(head, row)