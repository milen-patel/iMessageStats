import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from flask import Flask

app = Flask(__name__)

@app.route("/")
def site_entry():
    return '<p>Welcome </p>' + str(numTexts) + '</p>'

print("Connecting to Database...")
con = sqlite3.connect("/Users/milenpatel/Desktop/chat.db")
print("Connected to Database!")
cur = con.cursor()

res = cur.execute("select count(*) from message")
numTexts = res.fetchone()[0]
print('You have sent/receieved ' + str(numTexts) + ' messages in total.')

res = cur.execute('SELECT chat.chat_identifier, count(chat.chat_identifier) AS message_count FROM chat JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id JOIN message ON chat_message_join.message_id = message. "ROWID" GROUP BY chat.chat_identifier ORDER BY message_count DESC LIMIT 10;')

x_axis_data = []
y_axis_data = []
for i in range(1,10):
     row = res.fetchone()
     x_axis_data.append(row[0]);
     y_axis_data.append(row[1]);

y_axis = np.array(y_axis_data)
x_labels = np.array(x_axis_data,dtype='|S13')

w = 6
nitems = len(y_axis)
x_axis = np.arange(0, nitems*w, w)    # set up a array of x-coordinates

fig, ax = plt.subplots(1)
ax.bar(x_axis, y_axis, width=w, align='center')
ax.set_xticks(x_axis);
ax.set_xticklabels(x_labels, rotation=90);

plt.title("TITLE")
plt.xlabel("Phone Numbers")
plt.ylabel("Total Messages (Sent + Receieved)")
plt.xticks(rotation = -80)
plt.show()

# Now, we look at texting activity by hour of day
query2 = ("SELECT is_from_me, strftime('%H', datetime(message.date / 1000000000 + strftime('%s', '2001-01-01'), 'unixepoch', 'localtime')) AS hour_sent, COUNT(*) AS num_texts_sent FROM message GROUP BY hour_sent, is_from_me ORDER BY hour_sent")
send_arr = []
recv_arr = []
for row in cur.execute(query2):
    # row = res.fetchone()
    if row[0] is 0:
        recv_arr.append(row[2])
    else:
        send_arr.append(row[2])

hours = ['12 AM', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM', '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM', '8 PM', '9 PM', '10 PM', '11 PM']
x = []
for i in range(0,24):
    x.append(i)

plt.figure()  # create another new figure
plt.xticks(x, hours, rotation=45)
plt.title("Your Texting Activity by Hour of the Day");
plt.ylabel("Total Texts Sent/Receieved at Hour")
plt.xlabel("Hour of Day")
plt.bar(x, send_arr, color='r')
plt.bar(x, recv_arr, bottom=send_arr, color='b')
plt.legend(['Sent', 'Receieved'], loc='upper left')
plt.show()

# Now we look at % of texts sent vs. receieved
numSent = 0
numGot = 0
for row in cur.execute('SELECT is_from_me, COUNT(*) FROM message GROUP BY is_from_me'):
    if row[0] is 0:
        numGot = row[1]
    else:
        numSent = row[1]

plt.figure()
plt.title("Ratio of Texts Sent to Receieved")
plt.pie([numSent, numGot], labels = ['Sent', 'Receieved'], autopct='%1.1f%%', shadow=True, startangle=90)
plt.show()



# Now we will look at the number of texts sent per day
dates = []
values = []
for row in cur.execute("SELECT strftime('%Y-%m-%d', datetime(message.date / 1000000000 + strftime('%s', '2001-01-01'), 'unixepoch', 'localtime')) AS day_sent, COUNT(*) AS num_texts_sent FROM message GROUP BY day_sent ORDER BY day_sent;"):
   dates.append(datetime.strptime(row[0], "%Y-%m-%d").date())
   values.append(row[1])

plt.figure()
plt.plot(dates, values)
plt.gcf().autofmt_xdate()
plt.show()

import seaborn as sns
sns.set_theme()

plt.figure()
data = pd.DataFrame({'X': dates, 'Y': values})
sns.lineplot(data, x='X', y='Y', color='g')
plt.show()
