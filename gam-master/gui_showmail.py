import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

class GUIShowMail(QtGui.QWidget):
  
  def __init__(self):
    super(GUIShowMail, self).__init__()
    self.initUI()

  def initUI(self):
    self.setFixedSize(800,600)
    self.move(300,300)
    self.setWindowTitle('Show Mail')

    lblFrom = QtGui.QLabel('From:', self)
    lblTo = QtGui.QLabel('To:', self)
    lblSubj = QtGui.QLabel('Subject:', self)
    lblAttach = QtGui.QLabel('Attach:',self)
    leFrom = QtGui.QLineEdit(self)
    leTo = QtGui.QLineEdit(self)
    leSubj = QtGui.QLineEdit(self)
    leAttach = QtGui.QLineEdit(self)
    teContent = QtGui.QTextEdit(self)
    btnClose = QtGui.QPushButton('Close', self)
    btnDownload = QtGui.QPushButton('Download Attachs', self)

    leFrom.resize(660,20)
    leTo.resize(735,20)
    leSubj.resize(735,20)
    leAttach.resize(590,20)
    teContent.resize(790,465)
    btnClose.resize(80,35)
    btnDownload.resize(150,35)

    lblFrom.move(18,10)
    leFrom.move(60,5)
    lblTo.move(34,40)
    lblSubj.move(5,70)
    lblAttach.move(11,100)
    leTo.move(60,35)
    leSubj.move(60,65)
    leAttach.move(60,95)
    teContent.move(5,130)
    btnClose.move(720, 0)
    btnDownload.move(650,90)

    self.show()

def main():
  app = QtGui.QApplication(sys.argv)
  winShowMail = GUIShowMail()
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()
