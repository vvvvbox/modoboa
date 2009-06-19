#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import smtplib
from email.mime.text import MIMEText
import datetime
from django.conf import settings
from mailng.admin.models import Mailbox
from mailng.main.models import ARmessage, ARhistoric

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Not enough arguments, aborting."
        sys.exit(1)

    sender = sys.argv[1]
    mailbox = sys.argv[2]
    mbox = Mailbox.objects.get(full_address=mailbox)
    try:
        armessage = ARmessage.objects.get(mbox=mbox.id, enabled=True)
    except ARmessage.DoesNotExist:
        sys.exit(0)
    try:
        lastar = ARhistoric.objects.get(armessage=armessage.id, sender=sender)
        try:
            timeout = getattr(settings, "AUTOREPLIES_TIMEOUT")
        except AttributeError:
            timeout = 86400 # 24h
        delta = datetime.timedelta(seconds=timeout)
        if lastar.last_sent + delta > datetime.datetime.now():
            sys.exit(0)
    except ARhistoric.DoesNotExist:
        lastar = ARhistoric()
        lastar.armessage = armessage
        lastar.sender = sender

    msg = MIMEText(armessage.content.encode('utf-8'), _charset='utf-8')
    msg['Subject'] = armessage.subject
    msg['From'] = mailbox
    msg['To'] = sender
    
    s = smtplib.SMTP()
    s.connect()
    s.sendmail(mailbox, sender, msg.as_string())
    s.quit()
    
    lastar.last_sent = datetime.datetime.now()
    lastar.save()
    sys.exit(0)
