#!/bin/bash python


import os
import math
import datetime
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def convert_size(size_bytes,precision=2):
    if size_bytes == 0:
        return "0B"
    size_name = ("b", "Kb", "Mb", "Gb", "Tb", "Pb", "Eb", "Zb", "Yb")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, precision)
    return "{} {}".format(s, size_name[i])


def get_usage_data():

	capacity = pd.read_csv('./capacity_log.txt',sep=' ',header=None,names=['date','time','capacity','usage'])
	capacity['capacity'] = capacity.capacity.str.rstrip('%').astype(float)
	capacity['datetime'] = (capacity.date + ' ' + capacity.time).apply(
	    lambda x: datetime.datetime.strptime(x,'%d/%m/%Y %H:%M:%S'))

	frames = []
	current = {}

	for fname in os.listdir('./usage'):

		user = fname.split('.')[0].replace('usage_','')
		df = pd.read_csv('./usage/'+fname,sep=' ',header=None, names=['date','time','usage'])
		df['user'] = user

		current[user] = df.usage.values[-1]
		frames.append(df)

	df_all = pd.concat(frames)
	df_all = df_all.reset_index().drop(columns='index')
	df_all = df_all.dropna(0,'any')

	df_all['datetime'] = (df_all.date + ' ' + df_all.time).apply(
	    lambda x: datetime.datetime.strptime(x,'%d/%m/%Y %H:%M:%S'))
	df_all = pd.concat([df_all, capacity])

	return df_all


def plot_usage(df_all):

	users = df_all.user.dropna().unique()

	current = pd.Series({
		user:df_all.loc[df_all.user==user].sort_values('datetime')['usage'].values[-1]
		for user in users
	}).sort_values()

	top_users = current.index.values[-5:]
	user2color = dict(zip(top_users,['green','blue','purple','orange','red']))
	for user in users: user2color[user] = user2color[user] if user in top_users else 'gray'

	fig = plt.figure(figsize=(6,3), dpi=200)

	ax = plt.subplot(2,1,1)
	# plt.title('HARDAC capacity: {}'.format(df_all))
	sns.lineplot(x="datetime", y="usage",
	                  hue="user", hue_order=current.index[::-1], ci=0, alpha=0.75,
	                  data=df_all, palette=user2color, ax=ax)
	ax.get_legend().remove()
	yticks = np.arange(0,2e10,2e9)
	plt.yticks(yticks, [ convert_size(1024*y,0) for y in yticks ],fontsize=6)
	plt.ylim(0,1.25*current.max())
	plt.ylabel('Individual Usage',fontsize=8)
	plt.xticks(fontsize=6)
	plt.xlabel('')

	ax2 = plt.twinx()
	sns.lineplot(x="datetime", y="capacity", data=df_all, ax=ax2, color="gray", lw=4, alpha=0.5)
	sns.lineplot(x="datetime", y="capacity", data=df_all, ax=ax2, color="black", lw=2)
	plt.yticks(np.linspace(0,100,5),['{:.0f}%'.format(p) for p in np.linspace(0,100,5)],fontsize=6)
	plt.ylabel('HARDAC Capacity',fontsize=8)
	ax2.xaxis.set_major_locator(mdates.WeekdayLocator())
	ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
	ax2.set_xlim([datetime.datetime.now() - datetime.timedelta(days=60), datetime.datetime.now()])

	pct_capacity = int(df_all.sort_values('datetime')['capacity'].dropna().values[-1])
	plt.title('HARDAC is at {}% capacity'.format(pct_capacity),fontsize=10)

	ax3 = plt.subplot(2,1,2)
	sns.barplot(x=current.index, y=current.values, palette=user2color, ax=ax3)
	plt.ylabel('Individual Usage',fontsize=8)
	plt.yticks(yticks, [ convert_size(1024*y,0) for y in yticks ],fontsize=6)
	plt.ylim(0,1.25*current.max())
	plt.xticks(fontsize=4)

	for i, name in enumerate(current.index): #, y=current.values
	    size = current.loc[name]
	    plt.text(i,size,convert_size(1024*size,precision=1).replace(' ','\n'),ha='center',va='bottom',fontsize=4)

	# plt.show()
	plt.savefig('usage_report.pdf')

if __name__ == "__main__":

	df_all = get_usage_data()
	plot_usage(df_all)
