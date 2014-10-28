# -*- coding: utf-8 -*-
import httplib2
import json
import base64

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

CLIENT_SECRET_FILE = 'client_secret.json'
OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'
STORAGE = Storage('gmail.storage')

flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
http = httplib2.Http()

credentials = STORAGE.get()
if credentials is None or credentials.invalid:
  credentials = run(flow, STORAGE, http=http)

http = credentials.authorize(http)
service = build('gmail', 'v1', http=http)

print "CONNECT SUCCESS"

maillist = [];
print "INIT"

def refresh():
  global maillist
  fin = open('mail.json', 'r')
  maillist = json.loads(fin.read().decode('utf-8'))
  fin.close()
  
  idlist = []
  for item in maillist:
    idlist.append(item['id'])
  
  messages = service.users().messages().list(userId='me').execute()
  length = len(messages['messages'])
  index = 0
  for message in messages['messages']:
    index += 1
    lID = message['id']
    if lID in idlist:
    	continue
    msg = service.users().messages().get(userId='me',id=lID).execute()
    payload = msg['payload']
    lSnippet = msg['snippet']
    for item in payload['headers']:
      if item['name'] == 'From':
  	lFrom = item['value']
      if item['name'] == 'To':
        lTo = item['value']
      if item['name'] == 'Subject':
        lSubject = item['value']
    attach = []
    if 'parts' in payload.keys():
      for item in payload['parts']:
        if item['filename']:
          lFilename = item['filename']
          body = item['body']
          lAttachID = body['attachmentId']
          lSize = body['size']
          attach.append({'filename' : lFilename, 'attachId' : lAttachID, 'size' : lSize})
    maillist.append({'id' : lID, 'from' : lFrom, 'to' : lTo, 'subject' : lSubject, 'snippet' : lSnippet, 'attach' : attach})
    print index,'OF',length,'MAILS'
  fout = open('mail.json', 'w')
  fout.write(json.dumps(maillist, ensure_ascii=False).encode('utf8'))
  fout.close()
  print "FINISH"

def printMail(msg):
  print 'MAIL ID:', msg['id'].encode('utf-8')
  print 'From:',msg['from'].encode('utf-8')
  print 'To:',msg['to'].encode('utf-8')
  print 'Subject:',msg['subject'].encode('utf-8')
  for attach in msg['attach']:
    print 'Filename:',attach['filename'].encode('utf-8')
    print 'AttachID:',attach['attachId'].encode('utf-8')
    print 'Size:',attach['size']
    print '------------'
  print msg['snippet'].encode('utf-8')
  print

def printAttach(msg,attach):
  print 'Filename:',attach['filename'].encode('utf-8')
  print 'AttachID:',attach['attachId'].encode('utf-8')
  print 'Size:',attach['size']
  print '------------'
  print 'MAIL ID:', msg['id'].encode('utf-8')
  print 'From:',msg['from'].encode('utf-8')
  print 'To:',msg['to'].encode('utf-8')
  print 'Subject:',msg['subject'].encode('utf-8')
  print msg['snippet'].encode('utf-8')
  print

def listMail():
  global maillist
  for msg in maillist:
    printMail(msg)

def listAttach():
  global maillist
  for msg in maillist:
    for attach in msg['attach']:
    	printAttach(msg,attach)

def findMailBySend(lSend):
  global maillist
  for msg in maillist:
    if msg['from'] == lSend:
      printMail(msg)

def findMailByRecv(lRecv):
  global maillist
  for msg in maillist:
    if msg['to'] == lRecv:
      printMail(msg)

def findMailBySubj(lSubj):
  global maillist
  for msg in maillist:
    if msg['subject'] == lSubj:
      printMail(msg)

def findAttachByID(lAttachID):
  global maillist
  for msg in maillist:
    for attach in msg['attach']:
      if attach['attachId'] == lAttachID:
        printAttach(msg,attach)

def findAttachByName(lName):
  global maillist
  for msg in maillist:
    for attach in msg['attach']:
      if attach['filename'] == lName:
        printAttach(msg,attach)

def getAttach(lID, lAttachID):
  for msg in maillist:
    for attach in msg['attach']:
      if msg['id'] == lID and attach['attachId'] == lAttachID:
      	print 'DOWNLOADING'
        filename = attach['filename']
        fout = open(filename.encode('utf-8'), 'w')
        attachment = service.users().messages().attachments().get(userId='me',messageId=lID,id=lAttachID).execute()
        fout.write(base64.urlsafe_b64decode(attachment['data'].encode('utf-8')))
        fout.close()
        print 'FINISH'
        return
  print 'NOT FOUND'

def getAttachByName(lName):
  for msg in maillist:
    for attach in msg['attach']:
      if attach['filename'] == lName:
      	print 'DOWNLOADING'
        fout = open(lName.encode('utf-8'), 'w')
        attachment = service.users().messages().attachments().get(userId='me',messageId=msg['id'],id=attach['attachId']).execute()
        fout.write(base64.urlsafe_b64decode(attachment['data'].encode('utf-8')))
        fout.close()
        print 'FINISH'
        return
  print 'NOT FOUND'

def newMail(lFrom, lTo, lSubject):
  #ToDo
  return

def help():
  print "Useage: newMail(From,To,Subject)"
  print "        findMailBySend()|findMailByRecv()|findMailBySubj()"
  print "        listMail()"
  print "========================"
  print "        getAttach(MailID,AttachID)|getAttachByName()"
  print "        findAttachByID()|findAttachByName()"
  print "        listAttach()"
  print "========================"
  print "        help()"
  print "        exit()"

refresh()

while True:
  cmd = raw_input("GAM$ ")
  exec cmd