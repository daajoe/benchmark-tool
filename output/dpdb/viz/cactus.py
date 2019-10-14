#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

pd.options.display.max_rows = 2000
pd.set_option('max_colwidth', 40)
pd.set_option('max_columns', 40)
pd.set_option('display.width', 400)
pd.set_option('precision', 10)

filename = '../runtimes_other_solvers/runtime_CSAT_BE.csv'
df = pd.read_csv(filename, index_col='instance') #, header=[0,1])

filename_dpdb = '../dpdb-by-instance.csv'

df_dpdb = pd.read_csv(filename_dpdb)
df_dpdb = df_dpdb[['instance','time', 'solved']]
# df_dpdb = df_dpdb[df_dpdb['solved'] > 0]
df_dpdb = df_dpdb.drop('solved',axis=1)
df_dpdb.rename(columns={"time": "dpdb"}, inplace=True)

#drop first row
df_dpdb = df_dpdb.iloc[1:]
#if instance name starts without ./ add one
df_dpdb['instance'] = './' + df_dpdb['instance'].astype(str)
# replace datatype
df_dpdb['dpdb'] = df_dpdb['dpdb'].astype(float)
# set_index
df_dpdb = df_dpdb.set_index('instance')

# remove certain columns
remove = ['gpu_t_n', 'gpu_a', 'gpu_a_n', 'sts']
df.drop(remove, inplace = True, axis=1)

df = df.join(df_dpdb)

# print(df)
# exit(1)

sorted_cols = []

for column in df.columns:
    # remove timeouts
    x = df[[column]].sort_values(column).reset_index()[[column]]
    x = x[x[column] < 900]
    sorted_cols.append(x)



# print(sorted_cols[0].count())
sorted_cols.sort(key=lambda x: x[x.columns[0]].count())
sorted_cols.reverse()
sorted_cols = sorted_cols[:8]


df_nu = sorted_cols[0]
iter_cols = iter(enumerate(sorted_cols))
next(iter_cols)

for k,column in iter_cols:
    df_nu=df_nu.join(column)


plt.figure()

# color_dict = {'c2d': '#FF0000', 'miniC2D_sharp'}
colors = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c',
          '#fb9a99', '#e31a1c', '#fdbf6f']
color_dict = {k: c for k, c in zip(df_nu.columns, colors)}

print(color_dict)

# df_nu.plot(style='.-', marker='d', color=[color_dict.get(x, '#333333') for x in df.columns])

#Greens
df_nu.plot(style=':', marker='d', colormap='winter', linewidth=1)
#, figsize=(10,5))
# df_nu.plot(style='.-', marker='d', colormap='jet')

plt.xlim((750,1300))

plt.legend(loc='best')
plt.show()


# print(df.columns)



# print(df)