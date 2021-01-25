#!/usr/bin/env python

import os, sys, time
import smtplib, sys, email.utils


def SendEmail(sender, to, subject, body, mailServer='prod-webmail.corp.ad.wrs.com'):
    """
    Input: sender, to, subject, body - string
        multiple receivers should be separated by ';' in to
    Output: return True or False which is the return value of sendmail
    """
    mailServer = mailServer
    From = sender
    To   = to
    Tos  = To.split(';')                           # allow a list of recipients
    Subj = subject
    Date = email.utils.formatdate()                # curr datetime, rfc2822
    # standard headers, followed by blank line, followed by text
    header = ('From: %s\nTo: %s\nDate: %s\nSubject: %s\n\n' % (From, To, Date, Subj))
    body = body
    text = header + body
    server = smtplib.SMTP(mailServer)              # connect, no log-in step
    failed = server.sendmail(From, Tos, text)
    server.quit()
    if failed:                                     # smtplib may raise exceptions
        return False                               # too, but let them pass here
    else:
        return True
