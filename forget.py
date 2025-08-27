import os
import pandas as pd

for file in os.listdir('records/'):

    if '.csv' in file:
        content = pd.read_csv('records/{}'.format(file))
        print(content)

        for column in content.columns:
            if 'bbd' in column or 'bba' in column or 'bbf' in column:
                content = content.drop(column, axis = 1)

        content.to_csv('records/{}'.format(file), index = False)