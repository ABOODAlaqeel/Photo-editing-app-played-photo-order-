import sys
import cv2
import numpy as np
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

class PuzzleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Grid')
        self.setGeometry(100, 100, 512, 512)

        # تحميل الصورة الأصلية
        self.img = cv2.imread("RR.jpg")
        self.img = cv2.resize(self.img, (512, 512))

        # إنشاء الصورة المصفوفة (صورة 512x512 باللون الأسود)
        self.img2 = np.zeros([512, 512, 3], np.uint8)

        # تقسيم الصورة إلى مربعات 128x128
        self.sds = 128
        self.ab = []
        for x in range(0, 512, self.sds):
            for y in range(0, 512, self.sds):
                coo = self.img[y:y+128, x:x+128]
                self.ab.append(coo)

        # مزج الخلايا بشكل عشوائي
        random.shuffle(self.ab)
        w = 0
        for x in range(0, 512, self.sds):
            for y in range(0, 512, self.sds):
                if w != 15:
                    ss = self.ab[w]
                    self.img2[y:y+128, x:x+128] = ss
                else:
                    self.img2[y:y+128, x:x+128] = [255, 255, 255]  # ترك الخلية رقم 15 بيضاء
                w += 1

        # تحويل الصورة إلى QPixmap لعرضها
        self.display_img = self.convert_cv_to_qt(self.img2)

        # إضافة الصورة إلى الواجهة
        self.label = QLabel(self)
        self.label.setPixmap(self.display_img)

        # ترتيب العناصر في واجهة المستخدم
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # تفعيل التفاعل مع النقرات
        self.setMouseTracking(True)
        self.clicked = False

    def mousePressEvent(self, event):
        # إذا تم النقر على الصورة
        if event.button() == Qt.LeftButton:
            x = event.x()
            y = event.y()

            # حساب الصف والعمود بناءً على النقرة
            row = y // 128
            col = x // 128
            print(f"{row}>>>>{col}")

            # تحديد المواقع المجاورة
            desd = {
                "ring": (row, col + 1),
                "left": (row, col - 1),
                "up": (row - 1, col),
                "down": (row + 1, col)
            }

            # التبديل بين الخلايا المجاورة
            for desds2, (ss_row, ss_col) in desd.items():
                if 0 <= ss_row < 4 and 0 <= ss_col < 4:
                    nef = self.img2[ss_row * 128:(ss_row + 1) * 128, ss_col * 128:(ss_col + 1) * 128]

                    if np.array_equal(nef, np.ones_like(nef) * 255):
                        print(desds2)

                        img_cop = self.img2[row * 128:(row + 1) * 128, col * 128:(col + 1) * 128].copy()
                        self.img2[ss_row * 128:(ss_row + 1) * 128, ss_col * 128:(ss_col + 1) * 128] = img_cop
                        self.img2[row * 128:(row + 1) * 128, col * 128:(col + 1) * 128] = np.ones_like(img_cop) * 255

                        self.display_img = self.convert_cv_to_qt(self.img2)
                        self.label.setPixmap(self.display_img)

    def convert_cv_to_qt(self, cv_img):
        """تحويل صورة OpenCV إلى QPixmap"""
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qt_img)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    puzzle_window = PuzzleWindow()
    puzzle_window.show()
    sys.exit(app.exec_())
