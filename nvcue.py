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
import email.utils
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import argparse
import codecs

#-----------------------------
def modify_remind_tag(from_string, to_string, filename):
    # Copy contents of original file to a new temporary file
    f_orig = codecs.open(filename, 'r', 'utf-8')
    f_new = codecs.open(filename + '.nvcue', 'w', 'utf-8')
    for line in f_orig:
        f_new.write(line.replace(from_string, to_string))
    
    # Overwrite original file with temporary file
    os.rename(filename + '.nvcue', filename)

    # Close files
    f_orig.close()
    f_new.close()

#-----------------------------
def send_reminder(sender, recipient, message, message_body, server, port):
    message_id = email.utils.make_msgid()
    msg = MIMEMultipart()
    msg['From'] = 'nvCue Reminder <' + sender + '>'
    msg['To'] = recipient
    msg['Subject'] = u'\u2605 ' + message
    msg.add_header("Message-ID", message_id)
    body = message_body
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
                print "Will work with:"
                print line
                # Parse out @remind string
                remind_string = unicode(re.search(r'(@remind\(.*\))', line).group(1), 'utf-8')

                # Extract date part from line
                parsed_date = re.search(r'(\d{4}-\d{2}-\d{2})', line).group(1)

                # Extract time part from line. If it doesn't exist, create one.
                try:
                    parsed_time = re.search(r'(\d{2}:\d{2})', line).group(1)
                except AttributeError:
                    parsed_time = '08:00'

                # Create datetime objects of parsed date and runtime date
                parsed_date_object = datetime.strptime(parsed_date + ' ' + parsed_time, '%Y-%m-%d %H:%M')
                now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M') 
                now_date_object = datetime.strptime(now, '%Y-%m-%d %H:%M')

                # If now is newer than parsed date, carry on with notification and modify file,
                # else pass and continue scanning
                if parsed_date_object < now_date_object:

                    # Try to parse the optional custom message part from line. In case it's left out, 
                    # use a default message as email subject.
                    try:
                        remind_message = unicode(re.search(r'"(.*)"', line).group(1), 'utf-8')
                        custom_message = True
                    except AttributeError:
                        remind_message = 'nvCue reminder'
                        custom_message = False

                    # Fill message_body with contents of file, but ignore lines with @remind tags
                    with open(current_file, 'r') as file_content:
                        message_body = ''
                        for line in file_content:
                            if '@remind' in line:
                                pass
                            else:
                                message_body += line

                    send_reminder(args.sender, args.email, remind_message, message_body, args.server, args.port)

                    # Replace @remind tag with @reminded in current file. 
                    if custom_message:
                        reminded_string = u'@reminded(' + unicode(now, 'utf-8') + u' "' + remind_message + u'")'
                    else:
                        reminded_string = u'@reminded(' + unicode(now, 'utf-8') + u')'

                    modify_remind_tag(remind_string, reminded_string, current_file)

        # Close current file and move on to the next
        f.close()

if __name__ == '__main__':
    main()
