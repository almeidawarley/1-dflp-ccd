from datetime import datetime
import common as cm
import git

def create_record(keyword):

    # Create a record for an instance
    instance = cm.load_instance(keyword)

    record = {}
    record['keyword'] = keyword

    for key, value in instance.parameters.items():
        record[key] = value

    return record

def load_record(keyword):

    # Load the record for an instance
    try:
        record = {}
        with open('records/{}.csv'.format(keyword), 'r') as content:
            head = content.readline().strip().split(',')
            row  = content.readline().strip().split(',')
            record = {head[i]: row[i] for i in range(len(head))}
    except:
        record = create_record(keyword)

    # Retrieve git repo information
    repo = git.Repo(search_parent_directories = True)
    record['updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    record['commit'] = repo.head.object.hexsha
    record['branch'] = repo.active_branch.name

    write_record(keyword, record)

    return record

def update_record(keyword, metadata):

    # Load the record for an instance
    record = load_record(keyword)

    for key, value in metadata.items():
        record[key] = value

    write_record(keyword, record)

def write_record(keyword, record):

    # Load the record for an instance
    with open('records/{}.csv'.format(keyword), 'w') as output:
        output.write(format_record(record))

def format_record(record):

    # Format the record for an instance
    head = ','.join([str(key) for key in record.keys()])
    row  = ','.join([str(value) for value in record.values()])
    return '{}\n{}'.format(head, row)