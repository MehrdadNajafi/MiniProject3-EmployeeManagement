import os
from functools import partial
import cv2
from PySide6.QtUiTools import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import database
import database_administrator
import filters

class LoginPage(QDialog):
    def __init__(self):
        super().__init__()
        
        loader = QUiLoader()
        self.ui = loader.load('UI/LoginWindow.ui', None)
        self.ui.show()
        
        data = database_administrator.getAll()
        
        self.user_name = data[0][0]
        self.password = data[0][1]
        
        self.ui.login_btn.clicked.connect(self.check_For_Login)
    
    def check_For_Login(self):
        user_name = self.ui.username_tb.text()
        password = self.ui.password_tb.text()
        
        if self.user_name == user_name and self.password == password:
            self.ui = EmployeeRegistration()
        else:
            mb = QMessageBox()
            mb.setWindowIcon(QIcon('icons/alert-circle.svg'))
            mb.setWindowTitle('Warning')
            mb.setText('Invalid Username or Password, Try again')
            mb.exec()
            
class AddPage(QDialog):
    def __init__(self, img=None):
        super().__init__()
        self.mb = QMessageBox()
        self.mb.setWindowIcon(QIcon('icons/alert-circle.svg'))
        self.mb.setWindowTitle('Warning')
        self.mb.setIcon(QMessageBox.Warning)
        self.mb.setText('Something went wrong,\nPlease try again')
        try:
            loader = QUiLoader()
            self.ui = loader.load('UI/AddWindow.ui')
            self.ui.show()
            
            try:
                self.load_Img(img)
            except:
                pass
            
            self.ui.apply_btn.clicked.connect(self.apply_Changes)
            self.ui.back_btn.clicked.connect(self.back_To_MainWindow)
            self.ui.cam_btn.clicked.connect(self.open_Cam)
        except:
            self.mb.exec()
            self.ui = EmployeeRegistration()
        
    def open_Cam(self):
        self.ui = CamPage()
        
    def load_Img(self, img):
        self.img = img
        img = cv2.resize(img, (100, 100))
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        except:
            pass
        
        img = QImage(img, img.shape[1], img.shape[0], QImage.Format_RGB888)
        img = QPixmap(img)
        self.ui.img_label.setPixmap(img)
        
    def apply_Changes(self):
        try:
            name = self.ui.name_tb.text()
            family = self.ui.family_tb.text()
            try:
                nc = int(self.ui.nc_tb.text())
                next_page = True
            except:
                mb = QMessageBox()
                mb.setWindowIcon(QIcon('icons/alert-circle.svg'))
                mb.setWindowTitle('Warning')
                mb.setIcon(QMessageBox.Warning)
                mb.setText('The national code should only contain numbers')
                mb.exec()
                next_page = False
            birthday = self.ui.birthday_tb.text()
            
            results = database.getAll()
            
            id = 1
            generate_id = True
            while generate_id :
                for i in range(len(results)):
                    if id == results[i][0]:
                        id += 1
                        generate_id = True
                    elif id != results[i][0]:
                        generate_id = False
            
            try:
                cv2.imwrite(f'face_images/{id}.jpg', self.img)
                img_received = True
            except:
                mb = QMessageBox()
                mb.setWindowIcon(QIcon('icons/alert-circle.svg'))
                mb.setWindowTitle('Warning')
                mb.setIcon(QMessageBox.Warning)
                mb.setText('You should first take a img of yourself.')
                mb.exec()
                img_received = False
                
            if next_page and img_received:
                database.add_Employee(id, name, family, nc, birthday)
                self.ui = EmployeeRegistration()
        except:
            self.mb.exec()
            pass
    
    def back_To_MainWindow(self):
        self.ui = EmployeeRegistration()

class CamPage(QDialog):
    def __init__(self):
        super().__init__()
        self.mb = QMessageBox()
        self.mb.setWindowIcon(QIcon('icons/alert-circle.svg'))
        self.mb.setWindowTitle('Warning')
        self.mb.setIcon(QMessageBox.Warning)
        self.mb.setText('Something went wrong,\nMake sure the camera is connected to the device\nAnd try again')
        try:
            loader = QUiLoader()
            self.ui = loader.load('UI\CameraWindow.ui', None)
            self.ui.show()
            self.stop_camera = False
            self.ui.cam_btn.clicked.connect(self.stopCam)

            face_detector = cv2.CascadeClassifier('Packages\haarcascade_frontalface_default.xml')
            
            video_cap = cv2.VideoCapture(0)
            while True:
                ret, frame = video_cap.read()
                if not ret or self.stop_camera:
                    break
                
                frame_bgr = frame.copy()
                frame_bgr = cv2.resize(frame_bgr, (500, 500))
                
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                faces = face_detector.detectMultiScale(frame_bgr, 1.3, 10)
                for face in faces:
                    x, y, w, h = face
                    self.face_pic = frame_bgr[y:y+h, x:x+w, :]
                    
                frame_rgb = cv2.resize(frame_rgb, (500, 500))
                frame_rgb = QImage(frame_rgb, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
                
                pixmap = QPixmap(frame_rgb)
                self.ui.cam_label.setPixmap(pixmap)
                    
                cv2.waitKey(1)
            cv2.destroyAllWindows()
        except:
            self.mb.exec()
            self.ui = AddPage()
    
    def stopCam(self):
        try:
            self.stop_camera = True
            self.ui = FilterPage(self.face_pic)
        except:
            self.mb.exec()
            self.ui = AddPage()
        
class FilterPage(QDialog):
    def __init__(self, face_img):
        super().__init__()
        self.mb = QMessageBox()
        self.mb.setWindowIcon(QIcon('icons/alert-circle.svg'))
        self.mb.setWindowTitle('Warning')
        self.mb.setIcon(QMessageBox.Warning)
        self.mb.setText('Something went wrong,\nPlease try again')
        try:
            loader = QUiLoader()
            self.ui = loader.load('UI\FilterWindow.ui', None)
            self.ui.show()
            
            img = face_img.copy()
            pixmap = self.make_pixmap_img(img)
            self.ui.original_btn.setIcon(QIcon(pixmap))
            self.ui.original_btn.setIconSize(QSize(120,120))
            self.ui.original_btn.clicked.connect(partial(self.return_Img, img))
            
            img = face_img.copy()
            blureed_img = filters.blur(img)
            pixmap = self.make_pixmap_img(blureed_img)
            self.ui.blur_btn.setIcon(QIcon(pixmap))
            self.ui.blur_btn.setIconSize(QSize(120,120))
            self.ui.blur_btn.clicked.connect(partial(self.return_Img, blureed_img))
            
            img = face_img.copy()
            checkered_face = filters.checkered_Face(img)
            pixmap = self.make_pixmap_img(checkered_face)
            self.ui.checkered_btn.setIcon(QIcon(pixmap))
            self.ui.checkered_btn.setIconSize(QSize(120,120))
            self.ui.checkered_btn.clicked.connect(partial(self.return_Img, checkered_face))
            
            img = face_img.copy()
            cartoon_img = filters.img2cartoon(img)
            pixmap = self.make_pixmap_img(cartoon_img)
            self.ui.cartoon_btn.setIcon(QIcon(pixmap))
            self.ui.cartoon_btn.setIconSize(QSize(120,120))
            self.ui.cartoon_btn.clicked.connect(partial(self.return_Img, cartoon_img))
            
            img = face_img.copy()
            invert_img = filters.invert_Filter(img)
            pixmap = self.make_pixmap_img(invert_img)
            self.ui.invert_btn.setIcon(QIcon(pixmap))
            self.ui.invert_btn.setIconSize(QSize(120,120))
            self.ui.invert_btn.clicked.connect(partial(self.return_Img, invert_img))
            
            img = face_img.copy()
            sharpen_img = filters.sharpen(img)
            pixmap = self.make_pixmap_img(sharpen_img)
            self.ui.sharp_btn.setIcon(QIcon(pixmap))
            self.ui.sharp_btn.setIconSize(QSize(120,120))
            self.ui.sharp_btn.clicked.connect(partial(self.return_Img, sharpen_img))
            
            img = face_img.copy()
            pencil_img = filters.pencil_sketch_gray(img)
            pixmap = self.make_pixmap_img(pencil_img)
            self.ui.pencil_btn.setIcon(QIcon(pixmap))
            self.ui.pencil_btn.setIconSize(QSize(120,120))
            self.ui.pencil_btn.clicked.connect(partial(self.return_Img, pencil_img))
            
            img = face_img.copy()
            red_img = filters.redFilter(img)
            pixmap = self.make_pixmap_img(red_img)
            self.ui.red_btn.setIcon(QIcon(pixmap))
            self.ui.red_btn.setIconSize(QSize(120,120))
            self.ui.red_btn.clicked.connect(partial(self.return_Img, red_img))
            
            img = face_img.copy()
            cyan_img = filters.cyanFilter(img)
            pixmap = self.make_pixmap_img(cyan_img)
            self.ui.cyan_btn.setIcon(QIcon(pixmap))
            self.ui.cyan_btn.setIconSize(QSize(120,120))
            self.ui.cyan_btn.clicked.connect(partial(self.return_Img, cyan_img))
        except:
            self.mb.exec()
            self.ui = AddPage()
    
    def make_pixmap_img(self, img):
        img = cv2.resize(img, (120, 120))
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        except:
            pass
        
        img = QImage(img, img.shape[1], img.shape[0], QImage.Format_RGB888)
        img = QPixmap(img)
        
        return img
    
    def return_Img(self, img):
        self.ui = AddPage(img=img)
        
class EditPage(QDialog):
    def __init__(self, id):
        super().__init__()
        self.mb = QMessageBox()
        self.mb.setWindowIcon(QIcon('icons/alert-circle.svg'))
        self.mb.setWindowTitle('Warning')
        self.mb.setIcon(QMessageBox.Warning)
        self.mb.setText('Something went wrong,\nPlease try again')
        
        try:
            loader = QUiLoader()
            self.ui = loader.load('UI/EditWindow.ui', None)
            self.ui.show()
            
            self.id = id
            
            data = database.getAll()
            
            for i in range(len(data)):
                if self.id == data[i][0]:
                    self.ui.name_tb.setText(f"{data[i][1]}")
                    self.ui.family_tb.setText(f"{data[i][2]}")
                    self.ui.nc_tb.setText(f"{data[i][3]}")
                    self.ui.birthday_tb.setText(f"{data[i][4]}")
            
            self.ui.apply_btn.clicked.connect(self.apply_Changes)
        except:
            self.mb.exec()
            self.ui = EmployeeRegistration()
        
    def apply_Changes(self):
        try:
            name = self.ui.name_tb.text()
            family = self.ui.family_tb.text()
            try:
                nc = int(self.ui.nc_tb.text())
                next_page = True
            except:
                mb = QMessageBox()
                mb.setWindowIcon(QIcon('icons/alert-circle.svg'))
                mb.setWindowTitle('Warning')
                mb.setIcon(QMessageBox.Warning)
                mb.setText('The national code should only contain numbers')
                mb.exec()
                next_page = False
            birthday = self.ui.birthday_tb.text()

            if next_page:
                database.edit_Employee(self.id, name, family, nc, birthday)
                self.ui = EmployeeRegistration()
        except:
            self.mb.exec()
            self.ui = EmployeeRegistration()

class SettingPage(QDialog):
    def __init__(self):
        super().__init__()
        self.mb = QMessageBox()
        self.mb.setWindowIcon(QIcon('icons/alert-circle.svg'))
        self.mb.setWindowTitle('Warning')
        self.mb.setIcon(QMessageBox.Warning)
        self.mb.setText('Something went wrong,\nPlease make sure the database is in the file\nAnd try again')
        
        try:
            loader = QUiLoader()
            self.ui = loader.load('UI/SettingWindow.ui', None)
            self.ui.show()
            
            data = database_administrator.getAll()
            
            self.ui.username_tb.setText(data[0][0])
            self.ui.pass_tb.setText(data[0][1])
            
            self.ui.apply_btn.clicked.connect(self.apply_Changes)
        except:
            self.mb.exec()
            self.ui = EmployeeRegistration()
        
    def apply_Changes(self):
        try:
            username = str(self.ui.username_tb.text())
            password = str(self.ui.pass_tb.text())
            database_administrator.apply_Changes(username, password)
            
            self.ui = EmployeeRegistration()
        except:
            self.mb.exec()
            self.ui = EmployeeRegistration()

class EmployeeRegistration(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mb = QMessageBox()
        self.mb.setWindowIcon(QIcon('icons/alert-circle.svg'))
        self.mb.setWindowTitle('Warning')
        self.mb.setIcon(QMessageBox.Warning)
        self.mb.setText('Something went wrong,\nPlease make sure the database is in the file\nAnd try again')
        try:
            loader = QUiLoader()
            self.ui = loader.load('UI/MainWindow.ui', None)
            self.ui.show()
            
            self.ui.add_btn.clicked.connect(self.add_New_Employee)
            self.ui.setting_btn.clicked.connect(self.go_To_Setting)
            
            self.readFromDatabase()
        except:
            self.mb.exec()
            pass
    
    def readFromDatabase(self):
        try:
            layout = self.ui.employee_layout
            for i in reversed(range(layout.count())): 
                layout.itemAt(i).widget().setParent(None)
            
            result = database.getAll()
            
            for i in range(len(result)):
                new_label = QLabel()
                employee_id = result[i][0]
                img_path = f"face_images\{employee_id}.jpg"
                
                img = cv2.imread(img_path)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (100, 100))
                img = QImage(img, img.shape[1], img.shape[0], QImage.Format_RGB888)
                pixmap = QPixmap(img)
                new_label.setPixmap(pixmap)
                layout.addWidget(new_label, i, 0)

                new_label = QLabel()
                name = result[i][1]
                family = result[i][2]
                full_name = f"{name} {family}"
                new_label.setText(full_name)
                layout.addWidget(new_label, i, 1)
                
                new_push_btn = QPushButton()
                new_push_btn.setIcon(QIcon('icons\info_white.svg'))
                new_push_btn.setMinimumHeight(23)
                new_push_btn.setMaximumHeight(23)
                new_push_btn.setMinimumWidth(30)
                new_push_btn.setMaximumWidth(30)
                new_push_btn.setStyleSheet("background-color: rgb(179, 185, 247);")
                new_push_btn.clicked.connect(partial(self.show_Info, result[i][1], result[i][2], result[i][3], result[i][4]))
                layout.addWidget(new_push_btn, i, 2)
                
                new_push_btn = QPushButton()
                new_push_btn.setIcon(QIcon('icons\edit.svg'))
                new_push_btn.setStyleSheet("background-color: rgb(179, 185, 247);")
                new_push_btn.clicked.connect(partial(self.edit_Page, result[i][0]))
                layout.addWidget(new_push_btn, i, 3)
                
                new_push_btn = QPushButton()
                new_push_btn.setIcon(QIcon('icons/trash.svg'))
                new_push_btn.setStyleSheet("background-color: rgb(179, 185, 247);")
                new_push_btn.clicked.connect(partial(self.delete_Employee_From_Database, result[i][0]))
                layout.addWidget(new_push_btn, i, 4)
                
                layout.setVerticalSpacing(10)
        except:
            self.mb.exec()
            pass
            
    def show_Info(self, name, family, nc, birthday):
        try:
            mb = QMessageBox()
            mb.setWindowIcon(QIcon('icons\info_black.svg'))
            mb.setWindowTitle("Info")
            mb.setText(f"Name: {name}\nFamily: {family}\nNational code: {nc}\nBirthday: {birthday}")
            mb.exec()
        except:
            self.mb.exec()
            
    def edit_Page(self, id):
        self.ui = EditPage(id)
        
    def add_New_Employee(self):
        self.ui = AddPage()
        
    def delete_Employee_From_Database(self, id):
        try:
            database.delete_Employee(id)
            os.remove(f"face_images/{id}.jpg")
            self.readFromDatabase()
        except:
            self.mb.exec()
    
    def go_To_Setting(self):
        self.ui = SettingPage()
        
app = QApplication([])
login_window = LoginPage()
app.exec()