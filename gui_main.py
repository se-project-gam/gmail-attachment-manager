#Useage: newMail(From,To,Subject,Text)
#        newMailWithAttach(From,To,Subject,Text,FileName)
#        newMailWithNewAttach(From,To,Subject,Text,Dir,FileName)
#        sendMail()
#        findMailBySend()|findMailByRecv()|findMailBySubj()
#        trashMail()|untrashMail()|deleteMail()
#        showMail()
#        listMail()
#        ----
#        getAttach(MailID,AttachID)|getAttachByName()
#        findAttachByID()|findAttachByName()
#        listAttach()
#        ----
#        help()
#        exit()

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

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

  def setSend(self, send):
    self.lblSend.setText(send)
  def setTime(self, time):
    self.lblTime.setText(time)
  def setSubj(self, subj):
    self.lblSubj.setText('<strong>' + subj + '</strong>')
  def setSnippet(self, snippet):
    self.lblSnippet.setText(snippet)
  def setAttach(self, names):
    if names:
      attachNames = 'Attachments:'
      for item in names:
        attachNames = attachNames + ' ' + item
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
    self.lblAttachInfo.setStyleSheet("color: rgb(175, 175, 175);")
    self.lblSubj.setStyleSheet("color: rgb(175, 175, 175);")
    self.lblSnippet.setStyleSheet("color: rgb(175, 175, 175);")

  def setSend(self, send):
    self.lblSend.setText(send)
  def setTime(self, time):
    self.lblTime.setText(time)
  def setAttachInfo(self, name, size):
    self.lblAttachInfo.setText('<strong>' + name + ', size: ' + size + '</strong>')
  def setTime(self, subl):
    self.lblTime.setText(subl)
  def setSnippet(self, snippet):
   self.lblSnippet.setText(snippet)

###################################

class GUIMain(QtGui.QWidget):
  def __init__(self):
    super(GUIMain, self).__init__()
    self.initUI()

  def initUI(self):
    self.setFixedSize(800,600)
    self.move(300,300)
    self.setWindowTitle('Gmail Attachment Manager')

    btnMails = QtGui.QPushButton('Mails', self)
    btnAttachs = QtGui.QPushButton('Attachments', self)
    btnNewMail = QtGui.QPushButton('New', self)
    btnTrash = QtGui.QPushButton('Trash', self)
    btnRefresh = QtGui.QPushButton('Refresh', self)
    btnSearch = QtGui.QPushButton('Search', self)
    leSerach = QtGui.QLineEdit(self)
    cmbSearch = QtGui.QComboBox(self)
    cmbSearch.addItem('Mail')
    cmbSearch.addItem('Attachment')

    lwgtMain = QtGui.QListWidget(self)

    lwgtMain.setStyleSheet('''QListWidget::item:selected{color:black;background-color:rgb(233,233,233);}
                              QListWidget::item { border-bottom: 1px solid rgb(233,233,233); }''')
    ##
    for send, time, subj, snippet, names in [('send1', 'time1',  'subj1', 'snippet1',['attach1']),
                                             ('send2', 'time2',  'subj2', 'snippet2',[]),
                                             ('send3', 'time3',  'subj3', 'snippet3',['attach1','attach2','attach3'])]:
      lwiMail = clwiMail()
      lwiMail.setSend(send)
      lwiMail.setTime(time)
      lwiMail.setSubj(subj)
      lwiMail.setSnippet(snippet)
      lwiMail.setAttach(names)
  
      lwgtItem = QtGui.QListWidgetItem(lwgtMain)
      lwgtItem.setSizeHint(lwiMail.sizeHint())
      lwgtMain.addItem(lwgtItem)
      lwgtMain.setItemWidget(lwgtItem,lwiMail)

    btnMails.resize(100,35)
    btnAttachs.resize(100,35)
    btnNewMail.resize(80,35)
    btnTrash.resize(80,35)
    btnRefresh.resize(80,35)
    btnSearch.resize(80,35)
    leSerach.resize(160,20)
    cmbSearch.resize(100,25)
    lwgtMain.resize(800,560)

    btnMails.move(0,0)
    btnAttachs.move(100,0)
    btnNewMail.move(220, 0)
    btnTrash.move(300, 0)
    btnRefresh.move(380,0)
    btnSearch.move(720, 0)
    leSerach.move(460,5)
    cmbSearch.move(620,2)
    lwgtMain.move(0,40)

    self.show()

def main():
  app = QtGui.QApplication(sys.argv)
  winMain = GUIMain()
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()
