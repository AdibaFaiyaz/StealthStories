from voice import speak
import sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets
from secret_diary import Ui_MainWindow
import threading
import face_recognition
import os
import cv2
import uuid
import time
import smtplib
from email.message import EmailMessage
import subprocess
import win32api


conn = sqlite3.connect("credentials.db")
cursor = conn.cursor()

global isCredentialsCorrect
files = ["credentials.db", "diary_data.db", "intruder.jpg"]


try:
    cursor.execute("CREATE TABLE credential (Email TEXT, Password TEXT)")
    conn.commit()

except:
    pass


class Ui_Dialoge(object):
    def face_rec(self, KNOWN_FACES_DIR="Images", TOLERANCE=0.6, MODEL="hog"):
        video = cv2.VideoCapture(0)

        print("Loading known faces...")
        known_faces = []
        known_names = []

        # We oranize known faces as subfolders of KNOWN_FACES_DIR
        # Each subfolder's name becomes our label (name)
        for name in os.listdir(KNOWN_FACES_DIR):

            # Next we load every file of faces of known person
            for filename in os.listdir(f"{KNOWN_FACES_DIR}/{name}"):
                # Load an image
                image = face_recognition.load_image_file(
                    f"{KNOWN_FACES_DIR}/{name}/{filename}")


                # Get 128-dimension face encoding
                # Always returns a list of found faces, for this purpose we take first face only (assuming one face per image as you can't be twice on one image)
                encoding = face_recognition.face_encodings(image)[0]
                print("done")

                # Append encodings and name
                known_faces.append(encoding)
                known_names.append(name)

        print("Processing unknown faces...")
        # Now let's loop over a folder of faces we want to label
        isCredentialsCorrect = True
        while isCredentialsCorrect:

            # Load image
            print(f"Filename {filename}", end="")
            ret, image = video.read()

            # This time we first grab face locations - we'll need them to draw boxes
            locations = face_recognition.face_locations(image, model=MODEL)

            # Now since we know loctions, we can pass them to face_encodings as second argument
            # Without that it will search for faces once again slowing down whole process
            encodings = face_recognition.face_encodings(image, locations)

            # We passed our image through face_locations and face_encodings, so we can modify it
            # First we need to convert it from RGB to BGR as we are going to work with cv2

            # But this time we assume that there might be more faces in an image - we can find faces of dirrerent people
            print(f", found {len(encodings)} face(s)")
            for face_encoding, face_location in zip(encodings, locations):

                # We use compare_faces (but might use face_distance as well)
                # Returns array of True/False values in order of passed known_faces
                results = face_recognition.compare_faces(
                    known_faces, face_encoding, TOLERANCE
                )

                if True in results:

                    isCredentialsCorrect = False

                    return True

                if False in results:
                    isCredentialsCorrect = False
                    cv2.imwrite("Intruder.jpg", image)

                    return False

    def data_collector(self):

        video = cv2.VideoCapture(0)

        def wait_timer():
            time.sleep(0.4)

            return True

        x = threading.Thread(target=wait_timer)
        x.start()

        while True:

            ret, image = video.read()

            imgname = "./Images/user/{}.jpg".format(str(uuid.uuid1()))

            cv2.imwrite(imgname, image)

            if threading.active_count() == 1:
                break

    def open_secret_diary(self):
        self.window3 = QtWidgets.QMainWindow()
        self.ui3 = Ui_MainWindow()
        self.ui3.setupUi(self.window3)
        Dialog.hide()
        self.window3.show()
        x = threading.Thread(
            target=speak,
            args=("opening secret diary. Now you can write here safely and securely",),
        )
        x.start()

    def send_mail(self, Email, files):
        Email_sender = "xyz@gmail.com"
        Password = ""
        Email_Reciever = Email

        msg = EmailMessage()
        msg["Subject"] = "Intruder! Someone is Trying to access your secret diary"
        msg["From"] = Email_sender
        msg["To"] = Email_Reciever
        msg.set_content(
            "We have attached the db files and the face of the intruder. We blocked the intruder from accessing your personal data and scared him/her by our super special restart sequence"
        )

        for file in files:
            with open(file, "rb") as f:
                file_data = f.read()
                file_name = f.name

            msg.add_attachment(
                file_data,
                maintype="application",
                subtype="octet-stream",
                filename=file_name,
            )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(Email_sender, Password)

            smtp.send_message(msg)

    def login_system(self):
        email_value = self.email_log_in_plain_text.text()
        password_value = self.password_log_in_plain_text.text()

        cursor.execute("SELECT * FROM credential")
        items = cursor.fetchall()

        if len(items) == 0:

            cursor.execute(
                "INSERT INTO credential (Email, Password) VALUES (?, ?)",
                (email_value, password_value),
            )
            conn.commit()
            speak("Taking you photo please Stay still")
            self.data_collector()
            self.email_log_in_plain_text.setText("")
            self.password_log_in_plain_text.setText("")
            speak(
                "Successfully signed up. Please enter you credentials again to log in"
            )

        else:
            if self.face_rec():

                if items[0][0] == email_value and items[0][1] == password_value:
                    self.open_secret_diary()
                    x = threading.Thread(
                        target=speak,
                        args=(
                            "User identified. Welcome Now you can access you secret diary",
                        ),
                    )
                    x.start()

                else:
                    speak("Wrong Credentials. Please Try again")
            else:
                speak("wrong user")

                def god_sound():
                    for i in range(0, 999999999999999999999):
                        win32api.Beep(25, 10)

                def laag(programme="Notepad.exe"):

                    for i in range(1, 300):
                        subprocess.Popen([programme, "message_intruder.txt"])


                x = threading.Thread(target=laag)
                x.start()


                z = threading.Thread(target=god_sound)
                z.start()

                self.send_mail('"' + items[0][0] + '"', files)
                os.system("shutdown /r /t 1")

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(641, 480)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setStyleSheet("background-color: rgb(252, 221, 136)")
        self.email_log_in_label = QtWidgets.QLabel(Dialog)
        self.email_log_in_label.setGeometry(QtCore.QRect(110, 120, 181, 81))
        font = QtGui.QFont()
        font.setPointSize(40)
        self.email_log_in_label.setFont(font)
        self.email_log_in_label.setObjectName("email_log_in_label")

        self.password_log_in_label = QtWidgets.QLabel(Dialog)
        self.password_log_in_label.setGeometry(QtCore.QRect(110, 210, 231, 81))
        font = QtGui.QFont()
        font.setPointSize(40)
        self.password_log_in_label.setFont(font)
        self.password_log_in_label.setObjectName("password_log_in_label")
        self.email_log_in_plain_text = QtWidgets.QLineEdit(Dialog)
        self.email_log_in_plain_text.setGeometry(QtCore.QRect(300, 150, 211, 31))
        self.email_log_in_plain_text.setObjectName("email_log_in_plain_text")
        self.email_log_in_plain_text.setPlaceholderText("Email")
        self.email_log_in_plain_text.setStyleSheet(
            "background-color: rgb(230, 210, 133)"
        )
        self.password_log_in_plain_text = QtWidgets.QLineEdit(Dialog)
        self.password_log_in_plain_text.setGeometry(QtCore.QRect(350, 240, 191, 31))
        self.password_log_in_plain_text.setObjectName("password_log_in_plain_text")
        self.password_log_in_plain_text.setPlaceholderText("Password")
        self.password_log_in_plain_text.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_log_in_plain_text.setStyleSheet(
            "background-color: rgb(230, 210, 133)"
        )
        self.log_in_button = QtWidgets.QPushButton(Dialog)
        self.log_in_button.setGeometry(QtCore.QRect(290, 350, 75, 23))
        self.log_in_button.setAutoFillBackground(False)
        self.log_in_button.setStyleSheet("background-color: rgb(131, 193, 202)")
        self.log_in_button.setDefault(False)
        self.log_in_button.setFlat(False)
        self.log_in_button.setObjectName("log_in_button")
        self.log_in_button.setStyleSheet("background-color: rgb(222, 140, 78);")
        self.log_in_button.clicked.connect(self.login_system)
        self.invalid_user_name_or_password = QtWidgets.QLabel(Dialog)
        self.invalid_user_name_or_password.setGeometry(QtCore.QRect(310, 320, 47, 13))
        self.invalid_user_name_or_password.setText("")
        self.invalid_user_name_or_password.setObjectName(
            "invalid_user_name_or_password"
        )

        font = QtGui.QFont()
        font.setPointSize(40)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.email_log_in_label.setText(_translate("Dialog", "Email"))
        self.password_log_in_label.setText(_translate("Dialog", "Password"))
        self.log_in_button.setText(_translate("Dialog", "Log in"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialoge()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
