import os
import sys
import base
import json
import random
import sqlite3
import pyAesCrypt

from PyQt5.QtGui import *
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QLineEdit, QApplication, QFileDialog, QMainWindow

buffer = 512 * 1024

class MainScreen(QMainWindow):
    def __init__(self):
        super(MainScreen, self).__init__()
        loadUi("main.ui",self)
        self.toolButton.clicked.connect(self.openDir)
        self.generatepass.clicked.connect(self.generatorPass)
        self.hideorseek.clicked.connect(self.hide)
        self.encryptButton.clicked.connect(self.Encrypt)
        self.decryptButton.clicked.connect(self.Decrypt)

        db = sqlite3.connect("cryptbase.db")
        curs = db.cursor()
        curs.execute("SELECT crypt FROM dir_items")
        
        for i in curs.fetchall():
            self.listDir.addItem(' '.join(str(x) for x in i))

    def openDir(self):
        path = QFileDialog.getExistingDirectory(None, "Select Directory", "")
        self.Dir.setText(path)

    def generatorPass(self):
        chars = '+-/*!&$#?=@<>abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        password = ''
        for i in range(12):
            password += random.choice(chars)
        self.password.setText(password)

    def hide(self):
        if self.hideorseek.isChecked():
            self.password.setEchoMode(QLineEdit.Normal)
            self.replacepassw.setEchoMode(QLineEdit.Normal)
            self.hideorseek.setIcon(QIcon(':/prefix1/icon/hidden.png'))
        else:
            self.password.setEchoMode(QLineEdit.Password)
            self.replacepassw.setEchoMode(QLineEdit.Password)
            self.hideorseek.setIcon(QIcon(':/prefix1/icon/eye.png'))


    def Encrypt(self):
        self.pixgreen = QPixmap(":/prefix1/icon/circle(4).png")
        self.pix = QPixmap(":/prefix1/icon/circle(5).png")

        def encr(file):
            pyAesCrypt.encryptFile(str(file), str(file + ".viva"), self.password.text(), buffer)
            os.remove(file)

        def load_dir(path_dir):
            for i in os.listdir(path_dir):
                path = os.path.join(path_dir, i)

                if os.path.isfile(path):
                    encr(path)
                else:
                    load_dir(path)

        if self.Dir.text() == "":
            self.statusbar.showMessage("Error. Please select directory")
        else:
            if self.password.text() == "":
                self.label_2.setPixmap(self.pix)
            elif self.replacepassw.text() == "":
                self.label_3.setPixmap(self.pix)
            else:
                if self.password.text() == self.replacepassw.text():
                    self.label_3.setPixmap(self.pixgreen)
                    self.label_2.setPixmap(self.pixgreen)
                    path_dir = self.Dir.text()
                    load_dir(path_dir)
                    db = sqlite3.connect("cryptbase.db")
                    curs = db.cursor()
                    curs.execute("INSERT INTO dir_items VALUES(?)", (path_dir,))
                    db.commit()
                    self.listDir.addItem(self.Dir.text())
                else:
                    self.label_3.setPixmap(self.pix)
                    self.label_2.setPixmap(self.pix)

    def Decrypt(self):
        self.pixgreen = QPixmap(":/prefix1/icon/circle(4).png")
        self.pix = QPixmap(":/prefix1/icon/circle(5).png")

        def decry(file):
            try:
                pyAesCrypt.decryptFile(str(file), str(os.path.splitext(file)[0]), self.password.text(), buffer)
                os.remove(file)
                self.statusbar.showMessage("Done! Decrypt.")
            except ValueError:
                self.statusbar.showMessage("Incorrect password")

        def load_dir_decry(path_dir):
            for i in os.listdir(path_dir):
                path = os.path.join(path_dir, i)
                
                if os.path.isfile(path):
                    decry(path)
                else:
                    load_dir_decry(path)

        if self.Dir.text() == "":
            self.statusbar.showMessage("Error. Please select directory")
        else:
            if self.password.text() == "":
                self.label_2.setPixmap(self.pix)
            elif self.replacepassw.text() == "":
                self.label_3.setPixmap(self.pix)
            else:
                if self.password.text() == self.replacepassw.text():
                    self.label_3.setPixmap(self.pixgreen)
                    self.label_2.setPixmap(self.pixgreen)
                    path_dir = self.Dir.text()
                    load_dir_decry(path_dir)
                    db = sqlite3.connect("cryptbase.db")
                    curs = db.cursor()
                    curs.execute(f"DELETE FROM dir_items WHERE crypt = '{self.Dir.text()}'")
                    db.commit()
                else:
                    self.label_3.setPixmap(self.pix)
                    self.label_2.setPixmap(self.pix)



if __name__ == "__main__":
    
    app = QtWidgets.QApplication(sys.argv)
    mainscreencast = MainScreen()
    widget = QtWidgets.QStackedWidget()
    widget.setFixedSize(370, 486)
    widget.setWindowTitle('vivaCrypt')
    widget.setWindowIcon(QIcon(':/prefix1/icon/cryptographic.png'))
    widget.addWidget(mainscreencast)
    widget.show()
    sys.exit(app.exec_())
