import module_cough_220927 as module_cough

import sys
import string
import time
import cv2
import os
import shutil
import datetime

import torch
import torch.nn as nn

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui


# 코로나 예측 모델 불러오기
class Model(nn.Module):
    def __init__(self, input_size, output_size):
        super(Model, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_size, 18),
            nn.ReLU(),
            nn.Linear(18, 9),
            nn.ReLU(),
            nn.Linear(9, output_size))
        
    def forward(self, x):
        output = self.model(x)
        result = output
        with torch.no_grad():
            value = torch.argmax(result, dim=1)
        return result, value


# 웸캠 생성 및 영상데이터 저장을 위한 클래스
class ShowVideo(QThread):
    VideoSignal1 = QtCore.pyqtSignal(QtGui.QImage)
    def __init__(self, parent=None):
        super(ShowVideo, self).__init__(parent)
        self.flag = 0
        self.camera = cv2.VideoCapture(0)
        self.ret, self.image = self.camera.read()
        self.height, self.width = self.image.shape[:2]
    
    def stop(self):
        self.run_video = False
        self.quit()
        self.wait(1000)

    @QtCore.pyqtSlot()
    def startVideo(self):
        global image

        self.run_video = True
        while self.run_video:
            ret, image = self.camera.read()
            color_swapped_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            self.qt_image1 = QtGui.QImage(color_swapped_image.data,
                                    self.width,
                                    self.height,
                                    color_swapped_image.strides[0],
                                    QtGui.QImage.Format_RGB888)
            self.VideoSignal1.emit(self.qt_image1)


            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(25, loop.quit) #25 ms
            loop.exec_()


    @QtCore.pyqtSlot()
    def savePicture(self, text):
        self.run_video = False
        self.ret, self.image = self.camera.read()
        if self.run_video == False:
            TIME_FILENAME = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            OUTPUT_PATH = "./image"
            if not os.path.exists(OUTPUT_PATH):
                os.mkdir(OUTPUT_PATH)
            OUTPUT_FILENAME = "./image/cough_test_"+TIME_FILENAME
            CCTV_OUTPUT_FILENAME = OUTPUT_FILENAME + ".png"
            filename = CCTV_OUTPUT_FILENAME
            self.qt_image1.save(filename)
            self.flag = self.flag + 1
            
            self.startVideo()



# 이미지뷰어를 위한 클래스
class ImageViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.image = QtGui.QImage()
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self.image)
        self.image = QtGui.QImage()

    def initUI(self):
        self.setWindowTitle('Test')

    @QtCore.pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        if image.isNull():
            print("Viewer Dropped frame!")

        self.image = image
        if image.size() != self.size():
            self.setFixedSize(image.size())
        self.update()



# 모델 추론결과 전달 클래스
class OtpTokenGenerator(QThread):
    value_changed_re = pyqtSignal(str, name="ValueChanged_re")
    value_changed_fi = pyqtSignal(str, name="ValueChanged_fi")
    expires_in = pyqtSignal(int, name="ExpiresIn")
    EXPIRE_TIME = 5

    def __init__(self):
        QThread.__init__(self)
        self.power = True
        self.characters = list(string.ascii_uppercase)
        self.token, self.file = self.generate()

    def __del__(self):
        self.wait()

    def generate(self):
        re, fi = module_cough.audio_rec()
        self.result = str(re)
        self.filename = str(fi)
        return self.result, self.filename

    def run(self):
        self.value_changed_re.emit(self.token)
        self.value_changed_fi.emit(self.file) 
        while self.power:
            t = int(time.time()) % self.EXPIRE_TIME
            self.expires_in.emit(self.EXPIRE_TIME - t)  
            if t != 0:
                self.usleep(1)
                continue
            self.token, self.file = self.generate()
            self.value_changed_re.emit(self.token)
            self.value_changed_fi.emit(self.file)
            self.msleep(1000)
    
    def stop(self):
        self.power = False
        self.quit()
        self.wait(1000)



# GUI 폼 생성을 위한 클래스
class Form(QWidget):
    def __init__(self):
        QWidget.__init__(self, flags=Qt.Widget)

    @pyqtSlot(str)
    def user_slot_1(self, str1):
        str1 = str(str1) + ".png"
        print("test=" +str1)
        if not os.path.isfile(str1):
            shutil.copy("./home.png", str1)
        self.dialog = QDialog()
        self.dialog.setWindowTitle("실시간음성내역")  
        self.dialog.move(10,985)         
        layout = QVBoxLayout()
        self.dialog.setLayout(layout)

        img_label = QLabel()  
        pixmap = QPixmap(str(str1))
        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(img_label)

        self.timer = QTimer(self)                   
        self.timer.start(10000)                    
        self.timer.timeout.connect(self.dialog.deleteLater)  
        self.dialog.exec_()

    def user_slot_2(self, str1):
        OUTPUT_PATH = "./image"
        if not os.path.exists(OUTPUT_PATH):
            os.mkdir(OUTPUT_PATH)
        shutil.copy("./home.png", "./image/test1.png")
        shutil.copy("./home.png", "./image/test2.png")


        print(str1)
        str_class = str1[-3:]
        folder_path = './image/'
        each_file_path_and_gen_time = []
        for each_file_name in os.listdir(folder_path):
            each_file_path = folder_path + each_file_name
            each_file_gen_time = os.path.getctime(each_file_path)
            each_file_path_and_gen_time.append((each_file_path, each_file_gen_time))

        most_recent_file1 = sorted(each_file_path_and_gen_time, key=lambda x: x[1], reverse=True)[0][0]
        most_recent_file2 = sorted(each_file_path_and_gen_time, key=lambda x: x[1], reverse=True)[1][0]

        print(most_recent_file1)
        print(most_recent_file2)

        str1 = str(most_recent_file1)

        if str1 != "./image/test.png":
            if (str_class != "0_2") :
                os.remove(str1)

        str1 = str(most_recent_file2)



        self.dialog = QDialog()
        self.dialog.setWindowTitle("코로나탐지내역")  
        self.dialog.move(660,410)         
        layout = QVBoxLayout()
        self.dialog.setLayout(layout)

        img_label = QLabel()  
        pixmap = QPixmap(str(str1))
        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(img_label)

        self.timer = QTimer(self)                   
        self.timer.start(10000)                    
        self.timer.timeout.connect(self.dialog.deleteLater)  
        self.dialog.exec_()





if __name__ == '__main__':


    app = QtWidgets.QApplication(sys.argv)

    thread1 = QtCore.QThread()
    thread1.start()
    vid = ShowVideo()
    vid.moveToThread(thread1)
    image_viewer1 = ImageViewer()
    vid.VideoSignal1.connect(image_viewer1.setImage)


    thread2 = QtCore.QThread()
    thread2.start()
    otp_gen = OtpTokenGenerator()
    otp_gen.moveToThread(thread2)

    fontDB = QFontDatabase()
    fontDB.addApplicationFont('./font/NanumSquareB.')

    push_button1 = QtWidgets.QPushButton('코로나 검사를 시작합니다.')
    push_button1.clicked.connect(vid.startVideo)
    push_button1.clicked.connect(otp_gen.start)

    push_button2 = QtWidgets.QPushButton('프로그램 종료')
    push_button2.clicked.connect(vid.stop)
    push_button2.clicked.connect(otp_gen.stop)
    push_button2.clicked.connect(QCoreApplication.instance().quit)

    token = QLabel()
    otp_gen.ValueChanged_re.connect(token.setText)
    token.setFont(QFont('나눔스퀘어OTF Bold',15))
    token.setStyleSheet("Color : red")
    token.setAlignment(Qt.AlignCenter)

    blank = QLabel()
    blank.setText(" ")
    blank.setFont(QFont("나눔명조",20))
    blank.setStyleSheet("Color : black")
    blank.setAlignment(Qt.AlignCenter)

    text_1 = QLabel()
    text_1.setText(" 코로나 탐지를 위한 AI기반 탐지기 ")

    text_1.setFont(QFont('나눔스퀘어OTF Bold',20))
    text_1.setStyleSheet("Color : black")
    text_1.setAlignment(Qt.AlignCenter)



    img_1 = QLabel()
    pixmap_1 = QPixmap('./dashboard.png')
    img_1.setPixmap(pixmap_1)
    img_1.setAlignment(Qt.AlignCenter)


    img_2 = QLabel()
    pixmap_2 = QPixmap('./home.png')
    img_2.setPixmap(pixmap_2)
    img_2.setAlignment(Qt.AlignCenter)



    vertical_layout = QtWidgets.QVBoxLayout()

    horizontal_layout1 = QtWidgets.QHBoxLayout()
    horizontal_layout1.addWidget(img_2)
    horizontal_layout1.addWidget(image_viewer1)

    horizontal_layout2 = QtWidgets.QHBoxLayout()
    horizontal_layout2.addWidget(blank)
    horizontal_layout2.addWidget(token)
    
    vertical_layout.addWidget(img_1)
    vertical_layout.addLayout(horizontal_layout1)
    vertical_layout.addLayout(horizontal_layout2)
    vertical_layout.addWidget(push_button1)
    vertical_layout.addWidget(push_button2)

    layout_widget = QtWidgets.QWidget()
    layout_widget.setLayout(vertical_layout)

    main_window = QtWidgets.QMainWindow()
    main_window.setCentralWidget(layout_widget)


    main_window.setWindowTitle("Corona_Detector")
    main_window.move(0,0)
    main_window.show()
    
    form = Form()
    otp_gen.ValueChanged_fi.connect(form.user_slot_1)
    otp_gen.ValueChanged_fi.connect(form.user_slot_2)

    TIME_FILENAME = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    OUTPUT_FILENAME = "./image/cough_test_"+TIME_FILENAME
    CCTV_OUTPUT_FILENAME = OUTPUT_FILENAME + ".png"
    print(CCTV_OUTPUT_FILENAME)
    otp_gen.ValueChanged_fi.connect(lambda: vid.savePicture(CCTV_OUTPUT_FILENAME))


    sys.exit(app.exec_())

