#!/usr/local/bin/python

import os
import socket
import re
from fabric.api import local, lcd
from smtplib import SMTP_SSL

WEBMAIL_HOST = 'mail.goryd.in'
PORT = 465
LOGIN_USER = 'support@goryd.in'
LOGIN_PASSWORD = "password"
DEPLOYMENTPASSKEY = 'deploy_passkey'
SSHPASSKEY = 'ssh_passkey'

def pip_dependencies():
    os.system('pip install fabric')
    os.system('npm install -g npm')
    os.system('npm install -g bower')
    os.system('npm install -g gulp')

def init_variables():
    frontendDir = '/home/stage/81/'
    backendDir = '/home/stage/82/'
    backend = 'goryd-backend'
    frontend = 'goryd-frontend'
    return frontend, frontendDir, backend, backendDir

def send_mail_on_error(command, subject = 'FAILED - git merge on stage branch'):
    smtp = SMTP_SSL(WEBMAIL_HOST, PORT)
    smtp.set_debuglevel(1)
    content = "Hello team,\n\nThe following command failed while trying to merge stage branch with master.\n\n%s\n\nPlease look into this asap." % command
    mail_from = "support@goryd.in"
    smtp.login(LOGIN_USER, LOGIN_PASSWORD) # enter correct password in stage environment

    mail_from = LOGIN_USER
    mail_to = "pradeep.yadav@goryd.in"
    msg = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (mail_from, mail_to, subject, content)
    smtp.sendmail(mail_from, mail_to, msg)

    mail_to = "shubham.yadav@goryd.in"
    msg = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (mail_from, mail_to, subject, content)
    smtp.sendmail(mail_from, mail_to, msg)

    mail_to = "sagar.agarwal@goryd.in"
    msg = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (mail_from, mail_to, subject, content)
    smtp.sendmail(mail_from, mail_to, msg)

    smtp.quit()

def send_mail_on_success(subject):
    smtp = SMTP_SSL(WEBMAIL_HOST, PORT)
    smtp.set_debuglevel(1)
    content = "Deployment of master branch on stage environemnt successful. Happy coding!"
    mail_from = "support@goryd.in"
    smtp.login(LOGIN_USER, LOGIN_PASSWORD) # enter correct password in stage environment

    mail_from = LOGIN_USER
    mail_to = "pradeep.yadav@goryd.in"
    msg = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (mail_from, mail_to, subject, content)
    smtp.sendmail(mail_from, mail_to, msg)

    mail_to = "shubham.yadav@goryd.in"
    msg = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (mail_from, mail_to, subject, content)
    smtp.sendmail(mail_from, mail_to, msg)

    mail_to = "sagar.agarwal@goryd.in"
    msg = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (mail_from, mail_to, subject, content)
    smtp.sendmail(mail_from, mail_to, msg)

    smtp.quit()

def pulling_changes(hosted_branch, source_branch):
    frontend, frontendDir, backend, backendDir = init_variables()
    if os.path.exists(frontendDir+frontend) is False:
        with lcd(frontendDir):
            try:
                command = 'git clone /home/git/repositories/goryd-frontend.git'
                local(command)
                print "clone successful"
            except:
                print "error occurred while cloning"
                send_mail_on_error(command)
    frontendDir = frontendDir+frontend
    with lcd(frontendDir):
        local("git checkout "+hosted_branch)
        while True:
            try:
                command = "git pull origin "+source_branch
                local(command)
                break
            except:
                continue
        local("npm install")
        local("bower install --allow-root")
        try:
            local("gulp build-prod")
        except:
            send_mail_on_error("gulp build-prod failed")
    if os.path.exists(backendDir+backend) is False:
        with lcd(backendDir):
            try:
                command = 'git clone /home/git/repositories/goryd-backend.git'
                local(command)
                print "clone successful"
            except:
                print "error occurred while cloning"
                send_mail_on_error(command)
    backendDir = backendDir+backend
    with lcd(backendDir):
        local("git checkout "+hosted_branch)
        while True:
            try:
                command = "git pull origin "+source_branch
                local(command)
                break
            except:
                continue
        local("pip install -r requirements.pip")

def restart_apache_server():
    try:
        command = "sudo service apache2 restart"
        local(command)
    except:
        send_mail_on_error(command)

def trigger_deployment():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 8010
    s.bind(('', port))
    s.listen(1)
    while True:
        print "port openend at %d" %(port)
        (clientsocket, address) = s.accept()
        print "getting request from %s:%s" %(clientsocket, address)
        response = clientsocket.recv(1024)
        passKey = re.search(r"passKey=(.+?) ", response)
        if passKey:
            if passKey.group(1) == DEPLOYMENTPASSKEY: # change passKey with the correct passkey in stage environemnt
                clientsocket.send("Trigerred the deployment to stage branch")
                pip_dependencies()
                pulling_changes("stage", "master")
                restart_apache_server()
                send_mail_on_success('Deployment successful')
            elif passKey.group(1) == SSHPASSKEY:
                try:
                    command = 'service ssh restart'
                    local(command)
                    clientsocket.send("ssh server restarted successfully")
                except:
                    send_mail_on_error(command)
                    clientsocket.send("ssh server restart failed!")
            else:
                print "Incorrect key passed. Access denied."
                clientsocket.send("Incorrect key passed. Access denied")
            clientsocket.close()
        else:
            continue


if __name__ == "__main__":
    trigger_deployment()
