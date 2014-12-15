# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

class clwiSelect (QtGui.QWidget):
  def __init__ (self, parent = None):
    super(clwiSelect, self).__init__(parent)
    self.initUI()

  def initUI(self):
    self.layout = QtGui.QGridLayout()

    self.lblFilename = QtGui.QLabel()
    self.lblSubj = QtGui.QLabel()
        
    self.layout.addWidget(self.lblFilename,0,0)
    self.layout.addWidget(self.lblSubj,0,1,QtCore.Qt.AlignRight)
    
    self.setLayout(self.layout)

    self.lblFilename.setStyleSheet("color: rgb(80, 80, 80);")
    self.lblSubj.setStyleSheet("color: rgb(175, 175, 175);")
    
  def setFilename(self, filename):
    self.lblFilename.setText(filename)
  def setSubj(self, subj):
    self.lblSubj.setText(subj)
  
class Dialog(QtGui.QDialog):
  def __init__(self, parent=None):
    QtGui.QDialog.__init__(self)
    self.initUI()

  def initUI(self):
    self.setFixedSize(240, 200)
    self.setWindowTitle('Select Attachment')

    lwgtList = QtGui.QListWidget(self)
    bbxYesNo = QtGui.QDialogButtonBox(self)

    lwgtList.setStyleSheet('''QListWidget::item:selected{color:black;background-color:rgb(233,233,233);}
                              QListWidget::item { border-bottom: 1px solid rgb(233,233,233); }''')

    for filename,subj in [('f1','s1'),('f2','s2'),('f3','s3')]:
    	lwiSelect = clwiSelect()
    	lwiSelect.setFilename(filename)
    	lwiSelect.setSubj(subj)

    	lwgtItem = QtGui.QListWidgetItem(lwgtList)
    	lwgtItem.setSizeHint(lwiSelect.sizeHint())
    	lwgtList.addItem(lwgtItem)
    	lwgtList.setItemWidget(lwgtItem,lwiSelect)

    lwgtList.move(5,5)
    bbxYesNo.move(90,165)

    lwgtList.resize(230,160)
    bbxYesNo.resize(150,30)

    bbxYesNo.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
    
    bbxYesNo.accepted.connect(self.accept)
    bbxYesNo.rejected.connect(self.reject)

   
    def id(self):
      return self.id()
   
    def mailid(self):
      return self.mailid()

if __name__ == '__main__':
  app = QtGui.QApplication(sys.argv)
  dialog = Dialog()
  dialog.exec_()