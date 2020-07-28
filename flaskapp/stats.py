import pandas as pd
import matplotlib.pyplot as plt, mpld3
from datetime import datetime, timedelta
import numpy as np
import math
from pytz import timezone
from flaskapp import db, app
from flaskapp.models.visit import Visit
from flaskapp.models.instructor import Instructor
from flask import render_template
import csv
import os

pd.options.mode.chained_assignment = None

graph_dict = {}

def export_csv():
    file_name = app.config['STATS_FILE']
    if os.path.exists(file_name):
        os.remove(file_name)
    try:
        output_file = open(file_name, 'w')
        out_csv = csv.writer(output_file, quotechar=',')
        out_csv.writerow(['id', 'eid', 'when_entered', 'when_left', 'was_helped', 'instructor_id'])
        visits = Visit.query.all()
        for visit in visits:
            out_csv.writerow([visit.id, visit.eid, visit.time_entered, visit.time_left, visit.was_helped, visit.instructor_id])
        output_file.close()
        return True
        #print("Export successful")
    except Exception as e:
        print("An error occurred when trying to export data to csv")
        print(e)
        return False


def renameWeekday(index):
    days = ["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"]
    return days[index]

def renameInstructor(id):
    instr = Instructor.query.filter_by(id=id).first()
    if instr:
        return instr.first_name
    else:
        return "None"

def get_graphs(range):
    stale_interval = timedelta(hours=1)
    if range in graph_dict:
        (time_generated, list, avg_wait, num_helped, num_removed) = graph_dict[range]
        tz = timezone('US/Central')
        now = datetime.utcnow()
        tzoffset = tz.utcoffset(now)
        now = now + tzoffset
        time_elapsed  = now - time_generated
        if time_elapsed > stale_interval:
            (graphs, avg_wait, num_helped, num_removed) = generate_graphs(range)
        else:
            graphs = list
    else:
        (graphs, avg_wait, num_helped, num_removed) = generate_graphs(range)
        (time_generated, list, avg_wait, num_helped, num_removed) = graph_dict[range]
    
    return render_template('stats_page.html', graphs=graphs, range=range, avg_wait=avg_wait, num_helped=num_helped, num_removed=num_removed, time_generated=time_generated)

def generate_graphs(range):
    if not export_csv():
        print("Failed to export to CSV")
        return render_template('reset_message', title="Error Occurred", body='An error occurred when trying to collect statistics for this class.')

    # open file, conversions
    raw = pd.read_csv(app.config['STATS_FILE'])
    raw.loc[:, 'when_entered'] = pd.to_datetime(raw['when_entered'])
    raw.loc[:, 'when_left'] = pd.to_datetime(raw['when_left'])
    raw.loc[:, 'id'] = raw['id'] - 1

    # filtered == only those who were helped
    filtered = raw[raw['when_left'].notna()]
    filtered = filtered.reset_index(drop=True)
    filtered = filtered.drop(columns='id')

    # generate timezone offset, database is stored in UTC
    tz = timezone('US/Central')
    now = datetime.utcnow()
    tzoffset = tz.utcoffset(now)

    # apply correct tz offset
    filtered.loc[:, 'when_entered'] = filtered['when_entered'].apply(lambda x: x + tzoffset)
    filtered.loc[:, 'when_left'] = filtered['when_left'].apply(lambda x: x + tzoffset)
    
    # calculate time in line
    time_in_line = (filtered['when_left'] - filtered['when_entered'])
    filtered.insert(3, "time_in_line", time_in_line)
    
    #generate all other necessary metrics
    time_entered = filtered['when_entered'].apply(lambda x: x.time())
    filtered.insert(4, "time_entered", time_entered)
    time_left = filtered['when_left'].apply(lambda x: x.time())
    filtered.insert(5, "time_left", time_left)
    date = filtered['when_entered'].apply(lambda x: x.date())
    filtered.insert(6, "date", date)
    weekday = filtered['when_entered'].apply(lambda x: x.weekday())
    filtered.insert(7, "weekday", weekday)
    filtered.loc[:, "weekday"] = filtered["weekday"].apply(renameWeekday)
    min_in_line = filtered['time_in_line'].apply(lambda x: int(x.total_seconds() / 60))
    filtered.insert(4, "min_in_line", min_in_line)

    # obtain relevant data for only last week, last month
    today = datetime.today().date()
    week_prior = today - timedelta(days=7)
    month_prior = today - timedelta(days=30)
    filtered_last_week = filtered[filtered['date'] >= week_prior]
    filtered_last_month = filtered[filtered['date'] >= month_prior]

    graphs = []

    helped = filtered[filtered['was_helped'] == 1]
    helped.loc[:,'instructor_id'] = helped['instructor_id'].map(renameInstructor)
    helped_last_week = helped[helped['date'] >= week_prior]
    helped_last_month = helped[helped['date'] >= month_prior]

    removed = filtered[filtered['was_helped'] == 0]
    removed_last_week = removed[removed['date'] >= week_prior]
    removed_last_month = removed[removed['date'] >= month_prior]

    num_helped = 0
    num_removed = 0
    avg_wait = 0

    if range=='all':
        plot_time_waiting(graphs, filtered, "Time waiting (all-time)", 10)
        plot_waiting_per_day(graphs, filtered, "Number of students per weekday (all-time)")
        plot_helped_per_TA(graphs, helped, "Number of students helped by TA (all-time)")
        num_helped = len(helped)
        num_removed = len(removed)
        avg_wait = helped['min_in_line'].mean()

    elif range=='month':
        plot_time_waiting(graphs, filtered_last_month, "Time waiting (last month)", 10)
        plot_waiting_per_day(graphs, filtered_last_month, "Number of students per weekday (last month)")
        plot_helped_per_TA(graphs, helped_last_month, "Number of students helped by TA (last month)")
        num_helped = len(helped_last_month)
        num_removed = len(removed_last_month)
        avg_wait = helped_last_month['min_in_line'].mean()

    elif range=='week':
        plot_time_waiting(graphs, filtered_last_week, "Time waiting (last week)", 10)
        plot_waiting_per_day(graphs, filtered_last_week, "Number of students per weekday (last week)")
        plot_helped_per_TA(graphs, helped_last_week, "Number of students helped by TA (last week)")
        num_helped = len(helped_last_week)
        num_removed = len(removed_last_week)
        avg_wait = helped_last_week['min_in_line'].mean()
    
    # incase none in time period x, will avoid funky text display.
    if math.isnan(avg_wait):
        avg_hr = '--'
        avg_min = '--'
    else:
        avg_hr = int(avg_wait // 60)
        avg_hr = str(avg_hr).zfill(2)
        avg_min = int(avg_wait % 60)
        avg_min = str(avg_min).zfill(2)
    avg_wait = avg_hr + ":" + avg_min

    global graph_dict
    graph_dict[range] = (now + tzoffset, graphs, avg_wait, num_helped, num_removed)
    return (graphs, avg_wait, num_helped, num_removed)



def plot_time_waiting(graphs, data, title, bins):
    data = data['min_in_line']
    plt.style.use('seaborn')
    fig = plt.figure(figsize=(5,5))
    plt.hist(data, bins=bins, rwidth = .75, align='mid')
    plt.title(title)
    plt.xlabel("Time waiting in line (min)")
    plt.ylabel("Num. of occurrences")
    graphs.append(mpld3.fig_to_html(fig, template_type="general"))
    plt.close()

def plot_waiting_per_day(graphs, data, title):
    indexing = ["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"]
    plt.style.use('seaborn')
    fig = plt.figure(figsize=(5,5))
    days = data.weekday.value_counts()
    days = days.reindex(indexing, fill_value = 0)
    plt.bar(x=days.index, height=days.values, tick_label = indexing, width = .5)
    plt.title(title)
    plt.xlabel("Day of week")
    plt.ylabel("Num. of occurrences")
    # days.set_xlabel("Day of week")
    # days.set_ylabel("Num. of occurrences")
    graphs.append(mpld3.fig_to_html(fig))
    plt.close()

def plot_helped_per_TA(graphs, data, title):
    TAs = data['instructor_id']
    plt.style.use('seaborn')
    fig = plt.figure(figsize=(5,5))
    plt.title(title)
    plt.xlabel("TA")
    plt.ylabel("Num. of students helped")
    counts = TAs.value_counts()
    if(len(counts) > 0):
        plt.bar(x=counts.index, height = counts.values, tick_label = counts.index, width = .5)
    graphs.append(mpld3.fig_to_html(fig))
    plt.close()


    
