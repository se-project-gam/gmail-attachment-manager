#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import base64
import threading
import sys
import os

from email import message_from_string
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes


from PyQt4 import QtGui
from PyQt4 import QtCore

import httplib2

from apiclient import errors
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run


class GAM:
  def __init__(self):
    self.CLIENT_SECRET_FILE = 'client_secret.json'
    self.OAUTH_SCOPE = 'https://mail.google.com/'
    self.STORAGE = Storage('gmail.storage')
  
    flow = flow_from_clientsecrets(self.CLIENT_SECRET_FILE, scope=self.OAUTH_SCOPE)
    http = httplib2.Http()

    credentials = self.STORAGE.get()
    if credentials is None or credentials.invalid:
      credentials = run(flow, self.STORAGE, http=http)

    http = credentials.authorize(http)
    self.service = build('gmail', 'v1', http=http)

    print "CONNECT SUCCESS"
    print "INITIALIZE"
    self.profile = self.service.users().getProfile(userId = 'me').execute()
    print 'GET PROFILE'
    self.refresh()

  #def progress(self, width, percent):
    #sys.stdout.write ("SYNCHRONIZING [%s ]%d%%\r" % (('%%-%ds' % width) % (width * percent / 100 * '='), percent))
    #sys.stdout.flush()
    
  def refreshToken(self, tid, service_thread, idlist_thread, idlist_json):
    index = 0
    length = len(idlist_thread) 
    print "thread!"
    for lID in idlist_thread:
      index += 1
      if lID in idlist_json:
        continue
      msg = service_thread.users().messages().get(userId='me',id=lID).execute()
      print "thread!"
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
      self.maillist.append({'id' : lID, 'from' : lFrom, 'to' : lTo, 'subject' : lSubject,'date' : lDate, 'snippet' : lSnippet, 'attach' : attach})  

  def refresh(self):
    self.maillist = []
    idlist_json = []
    idlist_server = []
    try:
      fin = open('mail.json', 'r')
      data = fin.read().decode('utf-8')
      if data != '':
        self.maillist = json.loads(data)
      fin.close()
      for item in self.maillist:
        idlist_json.append(item['id'])
    except IOError, e:
      print "CREATE mail.json"
    lToken = ''
    idlist_threads = []
    while True:
      idlist_thread = []
      if lToken != '':
        messages = self.service.users().messages().list(userId = 'me', pageToken = lToken).execute()
      else:
        messages = self.service.users().messages().list(userId = 'me').execute()
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
        print 'TOKEN: REACH TAIL'
        break;

    toremove = []
    for item in self.maillist:
      if item['id'] not in idlist_server:
        toremove.append(item)

    for item in toremove:
        idlist_json.remove(item['id'])
        self.maillist.remove(item)
        
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
      flow_threads.append(flow_from_clientsecrets(self.CLIENT_SECRET_FILE, scope=self.OAUTH_SCOPE))
      http_threads.append(httplib2.Http())  

      credentials_threads.append(STORAGE_THREADS[tid].get())
      if credentials_threads[tid] is None or credentials_threads[tid].invalid:
        credentials_threads[tid] = run(flow_threads[tid], STORAGE_THREADS[tid], http=http_threads[tid])  

      http_threads[tid] = credentials_threads[tid].authorize(http_threads[tid])
      service_thread.append(build('gmail', 'v1', http=http_threads[tid]))
      threads.append(threading.Thread(target=self.refreshToken, args=(tid, service_thread[tid], idlist_thread, idlist_json)))
      tid += 1
    ######################
    for thread in threads:
      thread.start()  

    while len(self.maillist) <= len(idlist_server):
      if len(self.maillist) == len(idlist_server):
        break
      #print len(self.maillist)

    

    self.maillist = sorted(self.maillist,key=lambda mail: idlist_server.index(mail['id']))  

    fout = open('mail.json', 'w')
    fout.write(json.dumps(self.maillist, ensure_ascii=False).encode('utf-8'))
    fout.close()
    print "FINISH"  

  def printMail(self, msg):
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

  def printAttach(self, msg,attach):
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
  

  def showMail(self, lID):
    ret = ''
    for msg in self.maillist:
      if msg['id'] == lID:
        self.printMail(msg)
        print '----'
        message = self.service.users().messages().get(userId = 'me', id = lID, format = 'raw').execute()
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('utf-8'))
        msg = message_from_string(msg_str)
        for part in msg.get_payload():
          if part.get_content_type() == 'text/plain':
            ret = ret + part.get_payload(decode = True) + '\n'
            print part.get_payload(decode = True)
        return ret

  def listMail(self):
    cmd = ''
    for msg in self.maillist:
      self.printMail(msg)
      if cmd != 'q':
        cmd = raw_input('')
    print '----'
    print 'TOTAL:',len(self.maillist),'MAILS'  

  def listAttach(self):
    cmd = ''
    total = 0
    for msg in self.maillist:
      for attach in msg['attach']:
        self.printAttach(msg,attach)
        total += 1
        if cmd != 'q':
          cmd = raw_input('')
    print '----'
    print 'TOTAL:',total,'ATTACHMENTS'  

  def findMailBySend(self, lSend):
    for msg in self.maillist:
      if msg['from'] == lSend:
        self.printMail(msg)  

  def findMailByRecv(self, lRecv):
    for msg in self.maillist:
      if msg['to'] == lRecv:
        self.printMail(msg)  

  def findMailBySubj(self, lSubj):
    for msg in self.maillist:
      if msg['subject'] == lSubj:
        self.printMail(msg)  

  def findAttachByID(self, lAttachID):
    for msg in self.maillist:
      for attach in msg['attach']:
        if attach['attachId'] == lAttachID:
          self.printAttach(msg,attach)  

  def findAttachByName(self, lName):
    for msg in self.maillist:
      for attach in msg['attach']:
        if attach['filename'] == lName:
          self.printAttach(msg,attach)  

  def getAttach(self, lID, lAttachID):
    for msg in self.maillist:
      for attach in msg['attach']:
        if msg['id'] == lID and attach['attachId'] == lAttachID:
          print 'DOWNLOADING'
          filename = attach['filename']
          fout = open(filename.encode('utf-8'), 'w')
          attachment = self.service.users().messages().attachments().get(userId='me',messageId=lID,id=lAttachID).execute()
          fout.write(base64.urlsafe_b64decode(attachment['data'].encode('utf-8')))
          fout.close()
          print 'FINISH'
          return
    print 'NOT FOUND'  

  def getAttachByName(self, lName):
    for msg in self.maillist:
      for attach in msg['attach']:
        if attach['filename'] == lName:
          print 'DOWNLOADING'
          fout = open(lName.encode('utf-8'), 'w')
          attachment = self.service.users().messages().attachments().get(userId='me',messageId=msg['id'],id=attach['attachId']).execute()
          fout.write(base64.urlsafe_b64decode(attachment['data'].encode('utf-8')))
          fout.close()
          print 'FINISH'
          return
    print 'NOT FOUND'  

  def newMail(self, lFrom, lTo, lSubject, lText):
    message = MIMEText(lText.decode('utf-8'), 'plain', 'utf-8')
    message['From'] = lFrom.decode('utf-8')
    message['To'] = lTo.decode('utf-8')
    message['Subject'] = lSubject.decode('utf-8')
    return {'raw': base64.b64encode(message.as_string())}  

  def newMailWithNewAttach(self, lFrom, lTo, lSubject, lText, lDir, lName):
    message = MIMEMultipart()
    message['From'] = lFrom.decode('utf-8')
    message['To'] = lTo.decode('utf-8')
    message['Subject'] = lSubject.decode('utf-8')

    msg = MIMEText(lText.decode('utf-8'), 'plain', 'utf-8')
    message.attach(msg)  

    path = os.path.join(lDir.decode('utf-8'), lName.decode('utf-8'))
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

  def newMailWithAttach(self, lFrom, lTo, lSubject, lText, lMailId, lName):
    data = ""
    for msg in self.maillist:
      if msg['id'] == lMailId.decode('utf-8'):
        for attach in msg['attach']:
          if attach['filename'] == lName.decode('utf-8'):
            attachment = self.service.users().messages().attachments().get(userId='me',messageId=msg['id'],id=attach['attachId']).execute()
            data = base64.urlsafe_b64decode(attachment['data'].encode('utf-8'))
            message = MIMEMultipart()
            message['From'] = lFrom.decode('utf-8')
            message['To'] = lTo.decode('utf-8')
            message['Subject'] = lSubject.decode('utf-8')

            msg = MIMEText(lText.decode('utf-8'), 'plain', 'utf-8')
            message.attach(msg)

            content_type, encoding = mimetypes.guess_type(lName.decode('utf-8'))    

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

  def newMailWithAttachs(self, lFrom, lTo, lSubject, lText, lAttachs):
    message = MIMEMultipart()
    message['From'] = lFrom.decode('utf-8')
    message['To'] = lTo.decode('utf-8')
    message['Subject'] = lSubject.decode('utf-8')

    msg = MIMEText(lText.decode('utf-8'), 'plain', 'utf-8')
    message.attach(msg)

    for lAttach in lAttachs:
      if lAttach[0:6] == 'local:':
        lName, lDir = lAttach[6:].split('@')
        print lName.decode('utf-8'), lDir.decode('utf-8')
        path = os.path.join(lDir.decode('utf-8'), lName.decode('utf-8'))
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

      elif lAttach[0:6] == 'exist:':
        lName, lMailId = lAttach[6:].split('@')
        print lName.decode('utf-8'), lMailId.decode('utf-8')
        data = ""
        for msg in self.maillist:
          if msg['id'] == lMailId.decode('utf-8'):
            for attach in msg['attach']:
              if attach['filename'] == lName.decode('utf-8'):
                attachment = self.service.users().messages().attachments().get(userId='me',messageId=msg['id'],id=attach['attachId']).execute()
                data = base64.urlsafe_b64decode(attachment['data'].encode('utf-8'))
                content_type, encoding = mimetypes.guess_type(lName.decode('utf-8'))

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

  def sendMail(self, message):
    try:
      message = (self.service.users().messages().send(userId='me', body=message).execute())
      print 'Message Id: %s' % message['id']
      return message
    except errors.HttpError, error:
      print 'An error occurred: %s' % error  

  def trashMail(self, lID):
    self.service.users().messages().trash(userId='me',id=lID).execute()
    print 'MAIL TRASHED'  

  def untrashMail(self, lID):
    self.service.users().messages().untrash(userId='me',id=lID).execute()
    print 'MAIL UNTRASHED'  

  def deleteMail(self, lID):
    self.service.users().messages().delete(userId='me',id=lID).execute()
    print 'MAIL DELETED'

  def help(self):
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

#########################################################

class clwiMail (QtGui.QWidget):
  def __init__ (self, parent = None):
    super(clwiMail, self).__init__(parent)
    self.initUI()
  
  def initUI(self):
    self.layout = QtGui.QGridLayout()

    self.lblSend = QtGui.QLabel()
    self.lblTime = QtGui.QLabel()
    self.lblSubj = QtGui.QLabel()
    self.lblSnippet = QtGui.QLabel()
    self.lblAttach = QtGui.QLabel()
        
    self.layout.addWidget(self.lblSend,0,0)
    self.layout.addWidget(self.lblTime,0,1,QtCore.Qt.AlignRight)
    self.layout.addWidget(self.lblSubj,1,0)
    self.layout.addWidget(self.lblSnippet,2,0)

    self.setLayout(self.layout)

    self.lblSend.setStyleSheet("color: rgb(175, 175, 175);")
    self.lblTime.setStyleSheet("color: rgb(175, 175, 175);")
    self.lblSubj.setStyleSheet("color: rgb(80, 80, 80);")
    self.lblSnippet.setStyleSheet("color: rgb(175, 175, 175);")

  def setId(self, id):
    self.id = id
  def setSend(self, send):
    self.lblSend.setText(send)
  def setTime(self, time):
    self.lblTime.setText(time)
  def setSubj(self, subj):
    self.lblSubj.setText('<strong>' + ((subj[0:30] + '...') if len(subj) > 30 else subj) + '</strong>')
  def setSnippet(self, snippet):
    self.lblSnippet.setText(((snippet[0:30] + '...') if len(snippet) > 30 else snippet))
  def setAttach(self, names):
    if names:
      attachNames = 'Attachments:'
      for item in names:
        attachNames = attachNames + ' ' + item + '\n'
      self.lblAttach.setText(attachNames)
      self.layout.addWidget(self.lblAttach,3,0)
      self.lblAttach.setStyleSheet("color: rgb(175, 175, 175);")



class clwiAttach (QtGui.QWidget):
  def __init__ (self, parent = None):
    super(clwiAttach, self).__init__(parent)
    self.initUI()

  def initUI(self):
    self.layout = QtGui.QGridLayout()

    self.lblSend = QtGui.QLabel()
    self.lblTime = QtGui.QLabel()
    self.lblAttachInfo = QtGui.QLabel()
    self.lblSubj = QtGui.QLabel()
    self.lblSnippet = QtGui.QLabel()
        
    self.layout.addWidget(self.lblSend,0,0)
    self.layout.addWidget(self.lblTime,0,1,QtCore.Qt.AlignRight)
    self.layout.addWidget(self.lblAttachInfo,1,0)
    self.layout.addWidget(self.lblSubj,2,0)
    self.layout.addWidget(self.lblSnippet,3,0)

    self.setLayout(self.layout)

    self.lblSend.setStyleSheet("color: rgb(175, 175, 175);")
    self.lblTime.setStyleSheet("color: rgb(175, 175, 175);")
    self.lblAttachInfo.setStyleSheet("color: rgb(80, 80, 80);")
    self.lblSubj.setStyleSheet("color: rgb(175, 175, 175);")
    self.lblSnippet.setStyleSheet("color: rgb(175, 175, 175);")

  def setId(self, id):
    self.id = id
  def setMailId(self, mailid):
    self.mailid = mailid
  def setSend(self, send):
    self.lblSend.setText(send)
  def setTime(self, time):
    self.lblTime.setText(time)
  def setAttachInfo(self, name, size):
    self.lblAttachInfo.setText('<strong>' + name + ', size: ' + str(size) + '</strong>')
  def setSubj(self, subj):
    self.lblSubj.setText(((subj[0:30] + '...') if len(subj) > 30 else subj))
  def setSnippet(self, snippet):
   self.lblSnippet.setText(((snippet[0:30] + '...') if len(snippet) > 30 else snippet))

###################################

class GUIShowMail(QtGui.QWidget):
  
  def __init__(self,gam):
    super(GUIShowMail, self).__init__()
    self.gam = gam
    self.initUI()

  def initUI(self):
    self.setFixedSize(800,600)
    self.move(300,300)
    self.setWindowTitle('Show Mail')

    self.lblFrom = QtGui.QLabel('From:', self)
    self.lblTo = QtGui.QLabel('To:', self)
    self.lblSubj = QtGui.QLabel('Subject:', self)
    self.lblAttach = QtGui.QLabel('Attach:',self)
    self.leFrom = QtGui.QLineEdit(self)
    self.leTo = QtGui.QLineEdit(self)
    self.leSubj = QtGui.QLineEdit(self)
    self.leAttach = QtGui.QLineEdit(self)
    self.teContent = QtGui.QTextEdit(self)
    self.btnDownload = QtGui.QPushButton('Download Attachs', self)

    self.leFrom.resize(735,20)
    self.leTo.resize(735,20)
    self.leSubj.resize(735,20)
    self.leAttach.resize(590,20)
    self.teContent.resize(790,465)
    self.btnDownload.resize(150,35)

    self.lblFrom.move(18,10)
    self.leFrom.move(60,5)
    self.lblTo.move(34,40)
    self.lblSubj.move(5,70)
    self.lblAttach.move(11,100)
    self.leTo.move(60,35)
    self.leSubj.move(60,65)
    self.leAttach.move(60,95)
    self.teContent.move(5,130)
    self.btnDownload.move(650,90)

    self.btnDownload.clicked.connect(self.actDownload)

  def setmail(self, tfrom, tto, tsubj, tattach, tcontent, tmailid, tids):
    self.mailid = tmailid
    self.ids = tids
    self.leFrom.setText(tfrom)
    self.leTo.setText(tto)
    self.leSubj.setText(tsubj)
    self.leAttach.setText(tattach)
    self.teContent.setText(tcontent)

  def actDownload(self):
    for id in self.ids:
      self.gam.getAttach(self.mailid, id)

###################################
class clwiSelect (QtGui.QWidget):
  def __init__ (self, parent = None):
    super(clwiSelect, self).__init__(parent)
    self.initUI()

  def initUI(self):
    self.layout = QtGui.QGridLayout()

    self.lblFilename = QtGui.QLabel()
    self.lblSubj = QtGui.QLabel()
        
    self.layout.addWidget(self.lblFilename,0,0)
    self.layout.addWidget(self.lblSubj,1,0)
    
    self.setLayout(self.layout)

    self.lblFilename.setStyleSheet("color: rgb(80, 80, 80);")
    self.lblSubj.setStyleSheet("color: rgb(175, 175, 175);")

  def setMailid(self, mailid):
    self.mailid = mailid
    
  def setFname(self, fname):
    self.fname = fname
    self.lblFilename.setText('<strong>' + fname + '</strong>')
  
  def setSubj(self, subj):
    self.lblSubj.setText(((subj[0:30] + '...') if len(subj) > 30 else subj))
  
class GUISelect(QtGui.QDialog):
  def __init__(self,gam,parent=None):
    QtGui.QDialog.__init__(self)
    self.gam = gam
    self.initUI()

  def initUI(self):
    self.setFixedSize(560, 540)
    self.setWindowTitle('Select Attachment')

    self.lwgtList = QtGui.QListWidget(self)
    self.bbxYesNo = QtGui.QDialogButtonBox(self)

    self.lwgtList.setStyleSheet('''QListWidget::item:selected{color:black;background-color:rgb(233,233,233);}
                              QListWidget::item { border-bottom: 1px solid rgb(233,233,233); }''')

    for msg in self.gam.maillist:
      for attach in msg['attach']:
        fname = attach['filename']
        mailid = msg['id']
        subj = msg['subject']
    
        self.lwiSelect = clwiSelect()
        self.lwiSelect.setMailid(mailid)
        self.lwiSelect.setFname(fname)
        self.lwiSelect.setSubj(subj)

        self.lwgtItem = QtGui.QListWidgetItem(self.lwgtList)
        self.lwgtItem.setSizeHint(self.lwiSelect.sizeHint())
        self.lwgtList.addItem(self.lwgtItem)
        self.lwgtList.setItemWidget(self.lwgtItem,self.lwiSelect)

    self.lwgtList.move(5,5)
    self.bbxYesNo.move(400,510)

    self.lwgtList.resize(550,500)
    self.bbxYesNo.resize(150,30)

    self.bbxYesNo.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
    
    self.bbxYesNo.accepted.connect(self.actItem)
    self.bbxYesNo.rejected.connect(self.reject)
  
  def actItem(self):
    items = self.lwgtList.selectedItems()
    for item in items:
      self.fname = self.lwgtList.itemWidget(item).fname
      self.mailid = self.lwgtList.itemWidget(item).mailid
      break
    print self.fname,self.mailid
    self.accept()
      
  def fileName(self):
    return self.fname
   
  def mailId(self):
    return self.mailid
###################################

class GUINewMail(QtGui.QWidget):
  
  def __init__(self,gam):
    super(GUINewMail, self).__init__()
    self.gam = gam
    self.initUI()

  def initUI(self):
    self.setFixedSize(800,600)
    self.move(300,300)
    self.setWindowTitle('New Mail')

    self.lblFrom = QtGui.QLabel('From:', self)
    self.lblUserAddress = QtGui.QLabel(self.gam.profile['emailAddress'], self)
    self.lblTo = QtGui.QLabel('To:', self)
    self.lblSubj = QtGui.QLabel('Subject:', self)
    self.lblAttach = QtGui.QLabel('Attach:',self)
    self.leTo = QtGui.QLineEdit(self)
    self.leSubj = QtGui.QLineEdit(self)
    self.leAttach = QtGui.QLineEdit(self)
    self.teContent = QtGui.QTextEdit(self)
    self.btnSend = QtGui.QPushButton('Send', self)
    self.btnSelect = QtGui.QPushButton('Select From Existed', self)

    self.leTo.resize(735,20)
    self.leSubj.resize(735,20)
    self.leAttach.resize(590,20)
    self.teContent.resize(790,465)
    self.btnSend.resize(80,35)
    self.btnSelect.resize(150,35)

    self.lblFrom.move(18,10)
    self.lblUserAddress.move(62,10)
    self.lblTo.move(34,40)
    self.lblSubj.move(5,70)
    self.lblAttach.move(11,100)
    self.leTo.move(60,35)
    self.leSubj.move(60,65)
    self.leAttach.move(60,95)
    self.teContent.move(5,130)
    self.btnSend.move(720, 0)
    self.btnSelect.move(650,90)

    self.btnSend.clicked.connect(self.actSend)
    self.btnSelect.clicked.connect(self.actSelect)
  
  def actSend(self):
    tfrom = str(self.lblFrom.text().toUtf8())
    tto = str(self.leTo.text().toUtf8())
    tsubj = str(self.leSubj.text().toUtf8())
    tattach = str(self.leAttach.text().toUtf8())
    tcontent = str(self.teContent.toPlainText().toUtf8())
    if tto != '':
      if tattach == '':
        mail = self.gam.newMail(tfrom,tto,tsubj,tcontent)
      else:
        tattachs = tattach.split('|')
        mail = self.gam.newMailWithAttachs(tfrom,tto,tsubj,tcontent,tattachs)
      self.gam.sendMail(mail)
      self.leTo.setText('')
      self.leSubj.setText('')
      self.leAttach.setText('')
      self.teContent.setText('')
      self.close()

  def actSelect(self):
    self.dlgSelect = GUISelect(self.gam,self)
    if self.dlgSelect.exec_():
      if str(self.leAttach.text().toUtf8()) == '':
        self.leAttach.setText('exist:' + self.dlgSelect.fileName() + '@' + self.dlgSelect.mailId())
      else:
        self.leAttach.setText(str(self.leAttach.text().toUtf8()).decode('utf-8') + '|exist:' + self.dlgSelect.fileName() + '@' + self.dlgSelect.mailId())

###################################

class GUIMain(QtGui.QWidget):
  def __init__(self, gam):
    super(GUIMain, self).__init__()
    self.gam = gam
    self.initUI()
    self.winShow = GUIShowMail(gam)
    self.winNew = GUINewMail(gam)


  def initUI(self):
    self.setFixedSize(800,600)
    self.move(300,300)
    self.setWindowTitle('Gmail Attachment Manager')
    self.boolShowRes = False

    self.btnMails = QtGui.QPushButton('Mails', self)
    self.btnAttachs = QtGui.QPushButton('Attachments', self)
    self.btnNewMail = QtGui.QPushButton('New', self)
    self.btnTrash = QtGui.QPushButton('Trash', self)
    self.btnRefresh = QtGui.QPushButton('Refresh', self)
    self.btnSearch = QtGui.QPushButton('Search', self)
    self.leSerach = QtGui.QLineEdit(self)
    self.cmbSearch = QtGui.QComboBox(self)
    self.cmbSearch.addItem('Mail')
    self.cmbSearch.addItem('Attachment')

    self.lwgtMain = QtGui.QListWidget(self)

    self.lwgtMain.setStyleSheet('''QListWidget::item:selected{color:black;background-color:rgb(233,233,233);}
                              QListWidget::item { border-bottom: 1px solid rgb(233,233,233); }''')
    
    self.actMails()

    self.btnMails.resize(100,35)
    self.btnAttachs.resize(100,35)
    self.btnNewMail.resize(80,35)
    self.btnTrash.resize(80,35)
    self.btnRefresh.resize(80,35)
    self.btnSearch.resize(80,35)
    self.leSerach.resize(160,20)
    self.cmbSearch.resize(100,25)
    self.lwgtMain.resize(800,560)

    self.btnMails.move(0,0)
    self.btnAttachs.move(100,0)
    self.btnNewMail.move(220, 0)
    self.btnTrash.move(300, 0)
    self.btnRefresh.move(380,0)
    self.btnSearch.move(720, 0)
    self.leSerach.move(460,5)
    self.cmbSearch.move(620,2)
    self.lwgtMain.move(0,40)

    self.btnMails.clicked.connect(self.actMails)
    self.btnAttachs.clicked.connect(self.actAttachs)
    self.btnNewMail.clicked.connect(self.actNew)
    self.btnRefresh.clicked.connect(self.actRefresh)
    self.btnTrash.clicked.connect(self.actTrash)
    self.btnSearch.clicked.connect(self.actSearch)
    self.lwgtMain.itemDoubleClicked.connect(self.actItem)

    self.show()

  def actMails(self):
    self.lwgtMain.clear()
    itemlist = self.tmpmaillist if self.boolShowRes else self.gam.maillist
    
    for msg in itemlist:
      id = msg['id']
      send = msg['from']
      time = msg['date']
      subj = msg['subject']
      snippet = msg['snippet']
      names = []
      for attach in msg['attach']:
        names.append(attach['filename'])
      lwiMail = clwiMail()
      lwiMail.setId(id)
      lwiMail.setSend(send)
      lwiMail.setTime(time)
      lwiMail.setSubj(subj)
      lwiMail.setSnippet(snippet)
      lwiMail.setAttach(names)
  
      lwgtItem = QtGui.QListWidgetItem(self.lwgtMain)
      lwgtItem.setSizeHint(lwiMail.sizeHint())

      self.lwgtMain.addItem(lwgtItem)
      self.lwgtMain.setItemWidget(lwgtItem,lwiMail)

  def actAttachs(self):
    self.lwgtMain.clear()
    itemlist = self.tmpmaillist if self.boolShowRes else self.gam.maillist
    for msg in itemlist:
      for attach in msg['attach']:
        id = attach['attachId']
        mailid = msg['id']
        send = msg['from']
        time = msg['date']
        name = attach['filename']
        size = attach['size']
        subj = msg['subject']
        snippet = msg['snippet']
        lwiAttach = clwiAttach()
        lwiAttach.setMailId(mailid)
        lwiAttach.setId(id)
        lwiAttach.setSend(send)
        lwiAttach.setTime(time)
        lwiAttach.setAttachInfo(name, size)
        lwiAttach.setSubj(subj)
        lwiAttach.setSnippet(snippet)
    
        lwgtItem = QtGui.QListWidgetItem(self.lwgtMain)
        lwgtItem.setSizeHint(lwiAttach.sizeHint())
        self.lwgtMain.addItem(lwgtItem)
        self.lwgtMain.setItemWidget(lwgtItem,lwiAttach)

  def actRefresh(self):
    self.gam.refresh()
    self.actMails()

  def actTrash(self):
    items = self.lwgtMain.selectedItems()
    for item in items:
      if isinstance(self.lwgtMain.itemWidget(item),clwiMail):
        id = self.lwgtMain.itemWidget(item).id
        self.gam.trashMail(id)
        row = self.lwgtMain.row(item)
        self.lwgtMain.takeItem(row)

  def actSearch(self):
    if self.cmbSearch.currentText() == 'Mail':
      self.tmpmaillist = []
      text = self.leSerach.text().toUtf8()
      if text[0:6] == '[from]'.encode('utf8'):
        for msg in self.gam.maillist:
          if msg['from'].find(text[6:]) != -1:
            self.tmpmaillist.append(msg)
      else:
        for msg in self.gam.maillist:
          if msg['subject'].encode('utf-8').find(text) != -1:
            self.tmpmaillist.append(msg)
      self.boolShowRes = True
      self.actMails()
      self.boolShowRes = False
    else:
      self.tmpmaillist = []
      text = self.leSerach.text().toUtf8()
      for msg in self.gam.maillist:
        for attach in msg['attach']:
          if attach['filename'].encode('utf-8').find(text) != -1:
            self.tmpmaillist.append(msg)
      self.boolShowRes = True
      self.actAttachs()
      self.boolShowRes = False

  def actItem(self):
    items = self.lwgtMain.selectedItems()
    for item in items:
      if isinstance(self.lwgtMain.itemWidget(item),clwiMail):
        id = self.lwgtMain.itemWidget(item).id
        for msg in self.gam.maillist:
          if msg['id'] == id:
            send = msg['from']
            recv = msg['to']
            subj = msg['subject']
            attachs = ''
            content = self.gam.showMail(id).decode('utf8')
            attachids = []
            for attach in msg['attach']:
              attachs = attachs + attach['filename'] + ' '
              attachids.append(attach['attachId'])
            self.winShow.setmail(send,recv,subj,attachs,content,id,attachids)
            self.winShow.show()
            break
      elif isinstance(self.lwgtMain.itemWidget(item),clwiAttach):
        id = self.lwgtMain.itemWidget(item).id
        mailid = self.lwgtMain.itemWidget(item).mailid
        self.gam.getAttach(mailid, id)

  def actNew(self):
    self.winNew.show()

def main():
  gam = GAM()
  app = QtGui.QApplication(sys.argv)
  winMain = GUIMain(gam)
  sys.exit(app.exec_())
  #while True:
  #  cmd = raw_input("GAM$ ")
  #  exec cmd

if __name__ == '__main__':
  main()