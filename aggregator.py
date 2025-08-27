import pandas as pd
import os

summaries = pd.DataFrame()

for file in os.listdir('records'):

    if '.csv' in file:

        summary = pd.read_csv('records/{}'.format(file))
        # print(summary)

        summaries = pd.concat([summaries, summary])
        # print(summaries)

        print(file)

summaries.to_csv('aggregator.csv', index = False)
