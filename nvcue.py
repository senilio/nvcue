#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Script for parsing your nvALT (or other plain text) notes for @(remind) tags, 
# and notify you via email.
#
# Source: https://github.com/senilio/nvcue

from datetime import datetime
import os
import re
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import argparse

#-----------------------------
def modify_remind_tag(from_string, to_string, filename):
    # Copy contents of original file to a new temporary file
    f_orig = open(filename, 'r')
    f_new = open(filename + '.nvcue', 'w')
    for line in f_orig:
        f_new.write(line.replace(from_string, to_string))
    
    # Overwrite original file with temporary file
    os.rename(filename + '.nvcue', filename)

    # Close files
    f_orig.close()
    f_new.close()

#-----------------------------
def send_reminder(sender, recipient, message, server, port):
    msg = MIMEMultipart()
    msg['From'] = 'nvCue Reminder <' + sender + '>'
    msg['To'] = recipient
    msg['Subject'] = u'nvCue: ' + unicode(message, "utf-8")
    body = u'Reminder sent from nvCue :D'
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    server = smtplib.SMTP(server, port)
    text = msg.as_string()
    server.sendmail(sender, recipient, text)
    server.quit()
    
#-----------------------------
def main():

    # Start with parsing command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--basedir', type=str, help='Directory containing your plain text notes', required=True)
    parser.add_argument('-e', '--email', type=str, help='Who will receive the email?', required=True)
    parser.add_argument('-s', '--server', type=str, help='Send email via this server', default='localhost', required=False)
    parser.add_argument('-p', '--port', type=int, help='SMTP port', default=25, required=False)
    parser.add_argument('-f', '--sender', type=str, help='Sender email address', required=True)
    args = parser.parse_args()

    # Get list of notes
    notes = os.listdir(args.basedir)

    # Loop through notes and look for @remind tags
    for note in notes:
        current_file = args.basedir + "/" + note
        f = open(current_file, 'r')
        for line in f.readlines():
            if '@remind(' in line:
                # Parse out @remind string
                remind_string = re.search(r'(@remind\(.*\))', line).group(1)

                # Extract date string from line
                parsed_date = re.search(r'@remind\((.*) "', line).group(1)

                # Make sure parsed date includes time stamp even if user left it out
                if not re.search(r"^\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}$", parsed_date):
                    parsed_date = parsed_date + ' 00:00'

                # Create datetime objects of parsed date and runtime date
                parsed_date_object = datetime.strptime(parsed_date, '%Y-%m-%d %H:%M')
                now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M') 
                now_date_object = datetime.strptime(now, '%Y-%m-%d %H:%M')

                # If now is newer than parsed date, carry on with notification and modify file,
                # else pass and continue scanning
                if parsed_date_object < now_date_object:

                    # Parse the message part from line and send the email to recipient
                    remind_message = re.search(r'"(.*)"', line).group(1)
                    send_reminder(args.sender, args.email, remind_message, args.server, args.port)

                    # Replace @remind tag with @reminded in current file
                    reminded_string = '@reminded(' + now + ' "' + remind_message + '")'
                    modify_remind_tag(remind_string, reminded_string, current_file)

        # Close current file and move on to the next
        f.close()

if __name__ == '__main__':
    main()
