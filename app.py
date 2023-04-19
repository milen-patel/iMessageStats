import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, date
from jinja2 import Template
import webbrowser
import os

# Make the graphs have a black background
plt.style.use('dark_background')

con = sqlite3.connect("/Users/milenpatel/Desktop/chat.db", check_same_thread=False)
cur = con.cursor()

# Get the total number of sent/receieved messages
res = cur.execute("select count(*) from message")
numTexts = res.fetchone()[0]

# Get the total number of characters sent over text
res = cur.execute("select sum(length(text)) from message;");
numChars = res.fetchone()[0]

# Get the total number of words sent over text
res = cur.execute("select sum(length(text) - length(replace(text, ' ', '')) + 1) from message;")
numWords = res.fetchone()[0]

# Number of Attachments transferred over text
res = cur.execute("select count(ROWID) FROM attachment;")
numAttachments = res.fetchone()[0]

# Num Convos 
res = cur.execute("select count(*) from chat;")
numConvos = res.fetchone()[0]

# Date of First Message
res = cur.execute("select strftime('%Y-%m-%d', datetime(min(message.date) / 1000000000 + strftime('%s', '2001-01-01'), 'unixepoch', 'localtime')) from message;")
firstText = res.fetchone()[0]
firstTextDT = datetime.strptime(firstText, "%Y-%m-%d").date()
numDays = (date.today() - firstTextDT).days
textPerDay = round(numTexts/numDays, 1)

res = cur.execute('SELECT chat.chat_identifier, count(chat.chat_identifier) AS message_count FROM chat JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id JOIN message ON chat_message_join.message_id = message. "ROWID" GROUP BY chat.chat_identifier ORDER BY message_count DESC;')

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
plt.savefig('figure1.png')

# Now, we look at texting activity by hour of day
query2 = ("SELECT is_from_me, strftime('%H', datetime(message.date / 1000000000 + strftime('%s', '2001-01-01'), 'unixepoch', 'localtime')) AS hour_sent, COUNT(*) AS num_texts_sent FROM message GROUP BY hour_sent, is_from_me ORDER BY hour_sent")
send_arr = []
recv_arr = []
for row in cur.execute(query2):
    # row = res.fetchone()
    if row[0] == 0:
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
plt.savefig('figure2.png')

# Now we will look at the number of texts sent per day
dates = []
values = []
for row in cur.execute("SELECT strftime('%Y-%m-%d', datetime(message.date / 1000000000 + strftime('%s', '2001-01-01'), 'unixepoch', 'localtime')) AS day_sent, COUNT(*) AS num_texts_sent FROM message GROUP BY day_sent ORDER BY day_sent;"):
   dates.append(datetime.strptime(row[0], "%Y-%m-%d").date())
   values.append(row[1])

plt.figure()
plt.plot(dates, values)
plt.gcf().autofmt_xdate()
plt.savefig('figure3.png')

import seaborn as sns
sns.set_theme()

plt.figure()
data = pd.DataFrame({'X': dates, 'Y': values})
sns.lineplot(data, x='X', y='Y', color='g')
plt.savefig('figure4.png')



# Now we look at % of texts sent vs. receieved
numSent = 0
numGot = 0
for row in cur.execute('SELECT is_from_me, COUNT(*) FROM message GROUP BY is_from_me'):
    if row[0] == 0:
        numGot = row[1]
    else:
        numSent = row[1]

plt.figure()
plt.title("Ratio of Texts Sent to Receieved")
plt.pie([numSent, numGot], labels = ['Sent', 'Receieved'], autopct='%1.1f%%', shadow=True, startangle=90)
plt.savefig('figure5.png')

# Look at iMessage vs SMS
imsg = 0
sms = 0
for row in cur.execute('select count(text), service from message GROUP BY service;'):
    if row[1] == 'SMS':
        sms = sms + row[0]
    else:
        imsg = imsg + row[0]

plt.figure()
plt.title("IMessage vs. SMS Activity")
plt.pie([imsg, sms], labels = ['IMessage', 'SMS'], autopct='%1.1f%%', shadow=True, startangle=90)
plt.savefig('figure6.png')

# Look at Attachment Types
labs = []
vals = []
for row in cur.execute('select count(ROWID), mime_type FROM attachment GROUP BY mime_type ORDER BY count(ROWID) DESC LIMIT 5;'):
    if row[1] is not None:
        vals.append(row[0])
        labs.append(row[1])

plt.figure()
plt.title("Breakdown of Attachements Sent")
plt.pie(vals, labels = labs, autopct='%1.1f%%', shadow=True, startangle=90)
plt.savefig('figure7.png')

template_str = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>iMessage Stats</title>
	<style>
		img {
			margin-left: auto;
			margin-right: auto;
  			width: 50%;
			display: block;
		}

		body {
			padding: 0px; 
			margin: 0; 
			// overflow: hidden;
		}
		* {transition: all 1s cubic-bezier(.25,.8,.25,1); 

		font-family: 'Montserrat', sans-serif;
		}
        
        p {
			color: #fff;
			width: 60%; display: block; margin: 0 auto;
			font-size: 70px;
		  	text-align: right; font-weight: bold;
		}
		
		.screen {
			background: #000; 
			width: 100vw;
		}

		.buttons {
		    position: fixed;
		    bottom: 0;
		    width: 100%;
		    height: 60px;
		    display: flex;
		    justify-content: center;
		    padding: 20px;
		}
		
		.card {
			width: 100%; 
			display: block;
			transform-style: preserve-3d; 
		   //transition-delay: 0.25s;
		}
		
		
		.dcard {
			position: relative; 
			display: block;
			height: 100vh;
		    width: 100vw;
			perspective: 00px;
		}
		.col-md-12, .col-md-4 {margin-bottom: 30px;}
		
		.col-md-12 .dcard {perspective: 3000px;}
		
		.frame {
			display: block; 
			width: 100%;   
			position: absolute; 
			top: 10%; 
			left: 50%; 
			transform: translateX(-50%);     
			transform-style: preserve-3d; 
		} 
		
		a.btn {background: #d3f971; border-radius: 30px; color: #000; padding: 10px 20px; line-height: 36px; text-decoration: none; margin: 0px 10px;} 
		a.btn-ghost {background: #000; border-radius: 30px; color: #d3f971; border: 2px solid #d3f971; padding: 10px 20px;}
		
		p {
			color: #fff;   
			width: 60%; display: block; margin: 0 auto;
			font-size: 70px;
		  	text-align: right; font-weight: bold;
		}

		p:nth-child(odd) {
			text-align: left;
			transform: translateZ(70px); position: relative;
		}
		
		p:nth-child(1) {
		  color: #d3f971;
		}
		p:nth-child(2) {
		  color: #4b917d;
		}
		p:nth-child(3) {
		  color: #fff;
		}
		p:nth-child(4) {
		  color: #ee209c;
		}
		
		p.underline {font-size: 28px; text-align: center; margin-top: 50px; color: #d3f971;}
		
		.trigger {position: absolute; height: 33.333333%; width: 33.333333%; display: block; z-index: 2; 
		
		  &:nth-child(1){  left: 0%; top: 0%;
		    &:hover ~ .card {transform: rotateY(8deg) rotateX(-5deg);}
		   }
		  &:nth-child(2){  left: 33.333333%; top: 0%;
		    &:hover ~ .card {transform: rotateY(0deg) rotateX(-5deg);;}
		   }
		  &:nth-child(3){  left: 66.666666%; top: 0%;
		    &:hover ~ .card {transform: rotateY(-8deg) rotateX(-5deg);}
		   }
		  &:nth-child(4){  left: 0%; top: 33.333333%;
		    &:hover ~ .card {transform: rotateY(8deg);}
		   }
		  &:nth-child(5){  left: 33.333333%; top: 33.333333%;
		    &:hover ~ .card {transform: rotateY(0deg) rotateX(0deg);}
		   }
		  &:nth-child(6){  left: 66.666666%; top: 33.333333%;
		    &:hover ~ .card {transform: rotateY(-8deg) rotateX(0deg);}
		   }
		  &:nth-child(7){  left: 0%; top: 66.666666%;
		    &:hover ~ .card {transform: rotateY(8deg) rotateX(5deg);}
		   }
		  &:nth-child(8){  left: 33.333333%; top: 66.666666%;
		    &:hover ~ .card {transform: rotateY(0deg) rotateX(5deg);}
		   }
		  &:nth-child(9){  left: 66.666666%; top: 66.666666%;
		    &:hover ~ .card {transform: rotateY(-8deg) rotateX(5deg);}
		   }
		}
		
		
		
			
	</style>
</head>
<body>
	<div class="container">
		<div class="screen">
			<div class="card">
				<p style="font-size:100px">Welcome to</p>
				<p style="font-size:100px">iMessage Stats</p>
				<p style="color:black">_</p>
   				<p>You have sent and receieved {{ numTotalTexts }} total messages</p>
   				<p>That is {{ numTotalChars }} characters and {{ numTotalWords }}  words!</p>
				<p style="color:black">_</p>
   				<p>You sent and receieved {{ numAttachments }} attachments over text</p>
				<p style="color:black">_</p>
   				<p>There are {{ numConvos }} different conversations (Individual + Group) in your library</p>
				<p style="color:black">_</p>
   				<p>Your first text was sent on {{ firstText }}  and you have averaged {{ textPerDay }} texts per day over {{ numDays }} days</p>
   				<img src="figure1.png" alt="TODO">
   				<img src="figure2.png" alt="TODO">
   				<img src="figure3.png" alt="TODO">
   				<img src="figure4.png" alt="TODO">
   				<img src="figure5.png" alt="TODO">
   				<img src="figure6.png" alt="TODO">
   				<img src="figure7.png" alt="TODO">
			</div>
		</div>
	</div>
</body>
</html>
'''

old_template_str = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>iMessage Stats</title>
</head>
<body>
   <h1>Welcome to iMessage Stats</h1>
   <h3>You have sent and receieved {{ numTotalTexts }} total messages</h3>
   <h3>That is {{ numTotalChars }} characters and {{ numTotalWords }} words!</h3>
   <h3>You sent and receieved {{ numAttachments }} attachments over text</h3>
   <h3>There are {{ numConvos }} different conversations (Individual + Group) in your library</h3>
   <h3>Your first text was sent on {{ firstText }}  and you have averaged {{ textPerDay }}  texts per day over {{ numDays }} days</h3>
   <img src="figure1.png" alt="TODO">
   <img src="figure2.png" alt="TODO">
   <img src="figure3.png" alt="TODO">
   <img src="figure4.png" alt="TODO">
   <img src="figure5.png" alt="TODO">
   <img src="figure6.png" alt="TODO">
   <img src="figure7.png" alt="TODO">
</body>
</html>
'''

# Create a Jinja2 template from the HTML string
template = Template(template_str)

# Render the template with the statistics
output = template.render(textPerDay = textPerDay, numDays = numDays, firstText = firstText, numConvos = f'{numConvos:,}', numAttachments = f'{numAttachments:,}', numTotalTexts = f'{numTexts:,}', numTotalChars = f'{numChars:,}', numTotalWords=f'{numWords:,}')

# Write the output to an HTML file
with open('statistics.html', 'w') as f:
    f.write(output)

# Define the full path to the HTML file
html_path = os.path.abspath('statistics.html')

# Open the generated HTML file in the default web browser
webbrowser.open('file://' + html_path)


# TODO: https://www.leozqin.me/how-many-miles-will-you-scroll/
