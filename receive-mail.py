#!/usr/local/bin/python

from imaplib2 import IMAP4_SSL
from smtplib import SMTP_SSL
import email
import requests

EMAIL_ACCOUNT = 'support@goryd.in'
EMAIL_PASSWORD = 'password' # enter password here
TICKET = 1

def forward_mail(message):
    message['Subject'] = 'Ticket #' + str(TICKET) + ': ' + message['Subject']

    smtp = SMTP_SSL('mail.goryd.in', 465)
    smtp.set_debuglevel(1)
    mail_from = EMAIL_ACCOUNT
    smtp.login(EMAIL_ACCOUNT, EMAIL_PASSWORD) # enter correct password in stage environment

    mail_to = ["shubham.yadav@goryd.in", "pradeep.yadav@goryd.in", "sagar.agarwal@goryd.in"]
    smtp.sendmail(mail_from, mail_to, message.as_string())
    smtp.quit()

def reply_automatic_mail(message):
    subject = 'Ticket #' + str(TICKET) + ' Re: ' + message['Subject']

    smtp = SMTP_SSL('mail.goryd.in', 465)
    smtp.set_debuglevel(1)
    mail_from = EMAIL_ACCOUNT
    smtp.login(EMAIL_ACCOUNT, EMAIL_PASSWORD) # enter correct password in stage environment

    mail_to = message['From']
    reply_body_content = "Thanks for giving us the feedback. Our customres are our topmost priority. Our team will contact you soon."
    reply_body = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (mail_from, mail_to, subject, reply_body_content)

    smtp.sendmail(mail_from, mail_to, reply_body)
    smtp.quit()

def post_to_backend(TICKET, email, subject):
    r = requests.post("http://localhost:8000/api/support/ticket/", data={'ticketID': TICKET, 'email': email, 'subject': subject})
    print r
    return r

loginStatus = 0

try:
    imap = IMAP4_SSL('goryd.in')
    loginStatus, st = imap.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    if loginStatus == 'OK':
        loginStatus = 1
except:
    loginStatus = "Login Failed!"

if loginStatus == 1:
    imap.select('INBOX')
    while True:
        typ, data = imap.search(None, "(UNSEEN)")
        if typ=='OK':
            for num in data[0].split():
                typ, data = imap.fetch(num, '(RFC822)')
                emailData = data[0][1]
                message = email.message_from_string(emailData)
                forward_mail(message)
                reply_automatic_mail(message)
                post_to_backend(TICKET, message['From'], message['Subject'])
                TICKET +=1
                print message['Subject']
                print message['From']
        else:
            print "imap.search not OK"
        print "I am waiting"
        imap.idle(timeout=100000000000)
        print "I got one new mail"
else:
    print loginStatus
