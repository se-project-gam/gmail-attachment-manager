# -*- coding: utf-8 -*-
import httplib2
import json
import base64
import threading

from email import message_from_string
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os

from apiclient import errors
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

CLIENT_SECRET_FILE = 'client_secret.json'
OAUTH_SCOPE = 'https://mail.google.com/'
STORAGE = Storage('gmail.storage')

flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
http = httplib2.Http()

credentials = STORAGE.get()
if credentials is None or credentials.invalid:
  credentials = run(flow, STORAGE, http=http)

http = credentials.authorize(http)
service = build('gmail', 'v1', http=http)

print "CONNECT SUCCESS"

maillist = []

print "INIT"

def refreshToken(tid, service_thread, idlist_thread, idlist_json):
  global maillist
  index = 0
  length = len(idlist_thread) 
  for lID in idlist_thread:
    index += 1
    if lID in idlist_json:
      continue
    msg = service_thread.users().messages().get(userId='me',id=lID).execute()
    payload = msg['payload']
    lSnippet = msg['snippet']
    lFrom = ''
    lTo = ''
    lSubject = ''
    lDate = ''
    for item in payload['headers']:
      if item['name'] == 'From':
       lFrom = item['value']
      if item['name'] == 'To':
        lTo = item['value']
      if item['name'] == 'Subject':
        lSubject = item['value']
      if item['name'] == 'Date':
        lDate = item['value']
    attach = []
    if 'parts' in payload.keys():
      lFilename = ''
      lAttachID = ''
      lSize = ''
      for item in payload['parts']:
        if item['filename']:
          lFilename = item['filename']
          body = item['body']
          if 'attachmentId' in body.keys():
            lAttachID = body['attachmentId']
          else:
            continue;
          lSize = body['size']
          attach.append({'filename' : lFilename, 'attachId' : lAttachID, 'size' : lSize})
    maillist.append({'id' : lID, 'from' : lFrom, 'to' : lTo, 'subject' : lSubject,'date' : lDate, 'snippet' : lSnippet, 'attach' : attach})
    print tid,':',index,'OF',length,'MAILS'

def refresh():
  global maillist
  idlist_json = []
  idlist_server = []
  try:
    fin = open('mail.json', 'r')
    data = fin.read().decode('utf-8')
    if data != '':
      maillist = json.loads(data)
    fin.close()
    for item in maillist:
      idlist_json.append(item['id'])
  except IOError, e:
    print "CREATE mail.json"
  lToken = ''
  idlist_threads = []
  while True:
    idlist_thread = []
    if lToken != '':
      messages = service.users().messages().list(userId = 'me', pageToken = lToken).execute()
    else:
      messages = service.users().messages().list(userId = 'me').execute()
    lID = ''
    for message in messages['messages']:
      lID = message['id']
      idlist_server.append(lID)
      idlist_thread.append(lID)
    idlist_threads.append(idlist_thread)
    if 'nextPageToken' in messages.keys():
      lToken = messages['nextPageToken']
      print 'TOKEN:',lToken
    else:
      print 'REACH TAIL'
      break;
  
  for item in maillist:
    if item['id'] not in idlist_server:
      maillist.remove(item) 

  #multithread
  threads = []
  STORAGE_THREADS = []
  flow_threads = []
  http_threads = []
  credentials_threads = []
  service_thread = []
  tid = 0
  for idlist_thread in idlist_threads:
    STORAGE_THREADS.append(Storage('gamil_t%d.storage' % tid))
    flow_threads.append(flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE))
    http_threads.append(httplib2.Http())

    credentials_threads.append(STORAGE_THREADS[tid].get())
    if credentials_threads[tid] is None or credentials_threads[tid].invalid:
      credentials_threads[tid] = run(flow_threads[tid], STORAGE_THREADS[tid], http=http_threads[tid])

    http_threads[tid] = credentials_threads[tid].authorize(http_threads[tid])
    service_thread.append(build('gmail', 'v1', http=http_threads[tid]))
    threads.append(threading.Thread(target=refreshToken, args=(tid, service_thread[tid], idlist_thread, idlist_json)))
    tid += 1
  ######################
  for thread in threads:
    thread.start()

  for thread in threads:
    while thread.isAlive():
      continue;

  fout = open('mail.json', 'w')
  fout.write(json.dumps(maillist, ensure_ascii=False).encode('utf-8'))
  fout.close()
  print "FINISH"

def printMail(msg):
  print 'MAIL ID:', msg['id'].encode('utf-8')
  print 'From:',msg['from'].encode('utf-8')
  print 'To:',msg['to'].encode('utf-8')
  print 'Subject:',msg['subject'].encode('utf-8')
  print 'Date:',msg['date'].encode('utf-8')
  for attach in msg['attach']:
    print 'Filename:',attach['filename'].encode('utf-8')
    print 'AttachID:',attach['attachId'].encode('utf-8')
    print 'Size:',attach['size']
    print '----'
  print msg['snippet'].encode('utf-8')
  print

def printAttach(msg,attach):
  print 'Filename:',attach['filename'].encode('utf-8')
  print 'AttachID:',attach['attachId'].encode('utf-8')
  print 'Size:',attach['size']
  print '----'
  print 'MAIL ID:', msg['id'].encode('utf-8')
  print 'From:',msg['from'].encode('utf-8')
  print 'To:',msg['to'].encode('utf-8')
  print 'Subject:',msg['subject'].encode('utf-8')
  print 'Date:',msg['date'].encode('utf-8')
  print msg['snippet'].encode('utf-8')
  print


def showMail(lID):
  global maillist
  for msg in maillist:
    if msg['id'] == lID:
      printMail(msg)
      print '----'
      message = service.users().messages().get(userId = 'me', id = lID, format = 'raw').execute()
      msg_str = base64.urlsafe_b64decode(message['raw'].encode('utf-8'))
      msg = message_from_string(msg_str)
      for part in msg.get_payload():
        if part.get_content_type() == 'text/plain':
          print part.get_payload(decode = True)
      return

def listMail():
  global maillist
  for msg in maillist:
    printMail(msg)
  print '----'
  print 'TOTAL:',len(maillist),'MAILS'

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
  global maillist
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
  global maillist
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

def newMail(lFrom, lTo, lSubject, lText):
  message = MIMEText(lText)
  message['From'] = lFrom
  message['To'] = lTo
  message['Subject'] = lSubject
  return {'raw': base64.b64encode(message.as_string())}

def newMailWithNewAttach(lFrom, lTo, lSubject, lText, lDir, lName):
  message = MIMEMultipart()
  message['From'] = lFrom
  message['To'] = lTo
  message['Subject'] = lSubject

  msg = MIMEText(lText)
  message.attach(msg)

  path = os.path.join(lDir, lName)
  content_type, encoding = mimetypes.guess_type(path)

  if content_type is None or encoding is not None:
    content_type = 'application/octet-stream'
  main_type, sub_type = content_type.split('/', 1)
  if main_type == 'text':
    fp = open(path, 'rb')
    msg = MIMEText(fp.read(), _subtype=sub_type)
    fp.close()
  elif main_type == 'image':
    fp = open(path, 'rb')
    msg = MIMEImage(fp.read(), _subtype=sub_type)
    fp.close()
  elif main_type == 'audio':
    fp = open(path, 'rb')
    msg = MIMEAudio(fp.read(), _subtype=sub_type)
    fp.close()
  else:
    fp = open(path, 'rb')
    msg = MIMEBase(main_type, sub_type)
    msg.set_payload(fp.read())
    fp.close()

  msg.add_header('Content-Disposition', 'attachment', filename=lName)
  message.attach(msg)

  return {'raw': base64.urlsafe_b64encode(message.as_string())}

def newMailWithAttach(lFrom, lTo, lSubject, lText, lName):
  data = ""
  for msg in maillist:
    for attach in msg['attach']:
      if attach['filename'] == lName:
        attachment = service.users().messages().attachments().get(userId='me',messageId=msg['id'],id=attach['attachId']).execute()
        data = base64.urlsafe_b64decode(attachment['data'].encode('utf-8'))
        message = MIMEMultipart()
        message['From'] = lFrom
        message['To'] = lTo
        message['Subject'] = lSubject

        msg = MIMEText(lText)
        message.attach(msg)

        content_type, encoding = mimetypes.guess_type(lName)

        if content_type is None or encoding is not None:
          content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text' or main_type == 'image' or main_type == 'audio':
          msg = MIMEText(data, _subtype=sub_type)
        else:
          msg = MIMEBase(main_type, sub_type)
          msg.set_payload(data)

        msg.add_header('Content-Disposition', 'attachment', filename=lName)
        message.attach(msg)

        return {'raw': base64.urlsafe_b64encode(message.as_string())}

def sendMail(message):
  try:
    message = (service.users().messages().send(userId='me', body=message).execute())
    print 'Message Id: %s' % message['id']
    return message
  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def trashMail(lID):
  service.users().messages().trash(userId='me',id=lID).execute()
  print 'MAIL TRASHED'

def untrashMail(lID):
  service.users().messages().untrash(userId='me',id=lID).execute()
  print 'MAIL UNTRASHED'

def deleteMail(lID):
  service.users().messages().delete(userId='me',id=lID).execute()
  print 'MAIL DELETED'

def help():
  print "Useage: newMail(From,To,Subject,Text)"
  print "        newMailWithAttach(From,To,Subject,Text,FileName)"
  print "        newMailWithNewAttach(From,To,Subject,Text,Dir,FileName)"
  print "        sendMail()"
  print "        findMailBySend()|findMailByRecv()|findMailBySubj()"
  print "        trashMail()|untrashMail()|deleteMail()"
  print "        showMail()"
  print "        listMail()"
  print "        ----"
  print "        getAttach(MailID,AttachID)|getAttachByName()"
  print "        findAttachByID()|findAttachByName()"
  print "        listAttach()"
  print "        ----"
  print "        help()"
  print "        exit()"

#TO-DO
# MultiThread

refresh()

while True:
  cmd = raw_input("GAM$ ")
  exec cmd