# Chuyi Wang
# Student's t-test for dependent samples
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import ttest_rel
from scipy import stats

filelist = ['match_result.txt','match_result_r.txt']

for filename in filelist:

    adjusted_match_rates = []

    with open(filename, 'r') as statistics:
        next(statistics)
        for line in statistics:
            #line = users.readline()
            row = line.split(',')
            adjusted_match_rate = float(row[5].strip())
            adjusted_match_rates.append(adjusted_match_rate)

        if filename == 'match_result.txt':
            adjusted_match_rates1 = adjusted_match_rates
        else:
            adjusted_match_rates2 = adjusted_match_rates

adjusted_match_rates1 = np.asarray(adjusted_match_rates1, dtype = np.float32)
adjusted_match_rates2 = np.asarray(adjusted_match_rates2, dtype = np.float32)

stat, p = ttest_rel(adjusted_match_rates1, adjusted_match_rates2)
print('t=%.3f, p=%.3f' % (stat, p))
stat2, p2 =stats.ttest_1samp(adjusted_match_rates1, 0.93)
print('t=%.3f, p=%.3f' % (stat2, p2))


# settings for seaborn plotting style
sns.set(color_codes=True)
# settings for seaborn plot sizes
sns.set(rc={'figure.figsize':(4.5,3)})


ax = sns.distplot(adjusted_match_rates1,
                  kde=False,
                  color='skyblue')
ax.set(ylabel='Frequencies', xlabel='Adjusted Match Rates')

ax = sns.distplot(adjusted_match_rates2,
                  kde=False,
                  color=sns.xkcd_rgb["rose pink"])
ax.set(ylabel='Frequencies', xlabel='Adjusted Match Rates')
plt.show()