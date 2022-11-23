import sys

filename = sys.argv[1]
lines = int(sys.argv[2])

keyword = filename.replace('.sh', '')

counter = 0
identifier = 1

with open('{}.sh'.format(keyword), 'r') as content:

    for line in content:

        with open('{}{}.sh'.format(keyword, identifier), 'a') as output:

            output.write(line)

        counter += 1

        if counter >= lines:

            counter = 0
            identifier += 1