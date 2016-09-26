# nvcue
### What's this?
This script scans your plain text notes and notifies you via email of any reminders you put in there.
Basically a python rewrite of nvremind by Brett Terpsta: https://github.com/ttscoff/nvremind

### Why?
I'm a long time user of nvALT and nvremind, but lately I've had to modify the Ruby code to make it fit my needs. While Bretts code is great, I can only conclude I'm not a Ruby kind of guy, so here's my take on writing a similar service in python.

### How?
First of all, script expects tag format like this, with date in ISO-8601 format.

    @remind(2016-10-24 "Call mom today")

Timestamp is optional:

    @remind(2016-10-24 10:00 "Call mom today")

As the script scans through your notes, it will send an email notification for each tag it finds. When a tag is processed, it will be changed to @reminded. The timestamp will also be updated to reflect the time when the tag was processed.

    @reminded(2016-10-24 10:30 "Call mom today")

You may also leave out the "stuff inside quotes":
    @remind(2016-10-24)
    @remind(2016-10-24 10:00)

... in which case the email subject will be replaced by a default one.

The email body will be the same as the contents in your note.


### Usage
    $ python nvcue.py -h
    usage: nvcue.py [-h] -b BASEDIR -e EMAIL [-s SERVER] [-p PORT] -f SENDER

    optional arguments:
      -h, --help        show this help message and exit
      -b BASEDIR, --basedir BASEDIR
                        Directory containing your plain text notes
      -e EMAIL, --email EMAIL
                        Who will receive the email?
      -s SERVER, --server SERVER
                        Send email via this server
      -p PORT, --port PORT  SMTP port
      -f SENDER, --sender SENDER
                        Sender email address

Run this script from crontab, and point it to a Dropbox directory containing your nvALT notes.

    0,30 6-23 * * * ~/nvcue/nvcue.py -b ~/Dropbox/Apps/nvALT -e recipient@x.com -f nvCue@y.com

