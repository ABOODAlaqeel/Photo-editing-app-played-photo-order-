from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QInputDialog, QVBoxLayout, QWidget, QGridLayout
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint, QTimer
import cv2
import sys
from PIL import Image
from puzzle_window import PuzzleWindow 

class ImageEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("برنامج تعديل الصور")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("background-color: #f5f5f5;")  # تغيير لون خلفية النافذة

        # إنشاء واجهة المستخدم مع تخطيط شبكي للأزرار (3 أزرار في كل صف)
        self.central_widget = QWidget(self)  # عنصر رئيسي يحتوي على الواجهة
        self.setCentralWidget(self.central_widget)

        grid_layout = QGridLayout(self.central_widget)  # تخطيط شبكي (GridLayout)

        self.image_label = QLabel(self)
        self.image_label.setStyleSheet("border: 2px solid #aaa; border-radius: 10px; background-color: white;")
        self.image_label.setFixedSize(800, 480)
        grid_layout.addWidget(self.image_label, 0, 0, 1, 3)  # إضافة الصورة في الصف الأول والعمود الأول إلى العمود الثالث

        # إضافة الأزرار
        self.load_button = self.create_button("إدراج صورة", self.load_image)
        self.filter_button = self.create_button("إضافة فلاتر", self.add_filter)
        self.resize_button = self.create_button("تغيير الأبعاد", self.resize_image)
        self.camera_button = self.create_button("فتح الكاميرا", self.open_camera)
        self.capture_button = self.create_button("التقاط صورة", self.capture_image, disabled=True)
        self.draw_button = self.create_button("الرسم على الصورة", self.enable_drawing)
        self.info_button = self.create_button("معلومات الصورة", self.show_image_info)
        self.save_button = self.create_button("حفظ الصورة", self.save_image)
        self.puzzle_button = self.create_button("فتح لعبة ترتيب الصور", self.start_puzzle_game)

        # إضافة الأزرار إلى التخطيط الشبكي (3 أزرار في كل صف)
        grid_layout.addWidget(self.load_button, 1, 0)
        grid_layout.addWidget(self.filter_button, 1, 1)
        grid_layout.addWidget(self.resize_button, 1, 2)
        grid_layout.addWidget(self.camera_button, 2, 0)
        grid_layout.addWidget(self.capture_button, 2, 1)
        grid_layout.addWidget(self.draw_button, 2, 2)
        grid_layout.addWidget(self.info_button, 3, 0)
        grid_layout.addWidget(self.save_button, 3, 1)
        grid_layout.addWidget(self.puzzle_button, 3, 2)

        self.image = None
        self.drawing = False
        self.last_point = QPoint()
        self.pixmap = None  # لتخزين نسخة من الصورة للرسم عليها
        self.cap = None  # متغير الكاميرا
        self.timer = None  # مؤقت لتحديث عرض الكاميرا

    def create_button(self, text, on_click, disabled=False):
        """دالة لإنشاء الأزرار مع ضبط خصائصها"""
        button = QPushButton(text, self)
        button.setStyleSheet(self.button_style())
        button.clicked.connect(on_click)
        button.setEnabled(not disabled)  # تعطيل الزر إذا كان disabled=True
        return button

    def button_style(self):
        """دالة لإرجاع تصميم موحد للأزرار"""
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388e3c;
            }
        """

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "اختر صورة", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.image = Image.open(file_path)
            self.display_image()

    def add_filter(self):
        if self.image:
            from PIL import ImageFilter
            self.image = self.image.filter(ImageFilter.BLUR)
            self.display_image()

    def resize_image(self):
        if self.image:
            width, ok1 = QInputDialog.getInt(self, "تغيير العرض", "أدخل العرض الجديد:")
            height, ok2 = QInputDialog.getInt(self, "تغيير الطول", "أدخل الطول الجديد:")
            if ok1 and ok2:
                self.image = self.image.resize((width, height))
                self.display_image()

    def open_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.show_message("فشل فتح الكاميرا.")
            return

        self.capture_button.setEnabled(True)  # تمكين زر التقاط الصورة بعد فتح الكاميرا

        # إعداد المؤقت لالتقاط إطار من الكاميرا وتحديث العرض
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # تحديث الإطار كل 30 مللي ثانية

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # تحويل الإطار إلى صورة قابلة للعرض في QLabel
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, _ = rgb_frame.shape
            qimage = QImage(rgb_frame.data, w, h, 3 * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            self.image_label.setPixmap(pixmap)

    def capture_image(self):
        ret, frame = self.cap.read()
        if ret:
            image_path = "captured_image.jpg"
            cv2.imwrite(image_path, frame)
            self.image = Image.open(image_path)  # هنا يتم فتح الصورة باستخدام Image من مكتبة Pillow
            self.display_image()
            self.cap.release()  # أغلق الكاميرا بعد التقاط الصورة
            self.timer.stop()  # إيقاف المؤقت
        else:
            self.show_message("فشل في التقاط الصورة.")

    def enable_drawing(self):
        if self.image:
            self.drawing = True
            self.pixmap = self.image_label.pixmap().copy()  # نسخة للرسم عليها

    def mousePressEvent(self, event):
        if self.drawing:
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing and event.buttons() == Qt.LeftButton:
            painter = QPainter(self.pixmap)
            pen = QPen(Qt.GlobalColor.black, 3, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawLine(self.last_point, event.pos())
            painter.end()
            self.last_point = event.pos()
            self.image_label.setPixmap(self.pixmap)  # تحديث QLabel

    def mouseReleaseEvent(self, event):
        if self.drawing:
            self.drawing = False

    def show_image_info(self):
        if self.image:
            info = f"الأبعاد: {self.image.size[0]}x{self.image.size[1]}\n"
            info += f"صيغة الصورة: {self.image.format}"
            self.show_message(info)

    def save_image(self):
        if self.image:
            file_path, _ = QFileDialog.getSaveFileName(self, "حفظ الصورة", "", "Images (*.png *.jpg *.jpeg *.bmp)")
            if file_path:
                self.image.save(file_path)

    def display_image(self):
         if self.image:
            # تحويل صورة Pillow إلى QImage
            image_qt = self.pil_to_qimage(self.image)
            pixmap = QPixmap.fromImage(image_qt)
        
            # تغيير حجم الصورة لتناسب QLabel بشكل كامل مع الحفاظ على النسب
            scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
            # تعيين الصورة المعدلة إلى QLabel
            self.image_label.setPixmap(scaled_pixmap)

    def pil_to_qimage(self, pil_image):
        """تحويل صورة PIL إلى QImage باستخدام PyQt5"""
        image = pil_image.convert("RGBA")  # تحويل الصورة إلى نمط RGBA
        data = image.tobytes("raw", "RGBA")  # تحويل الصورة إلى بايتات
        qim = QImage(data, image.width, image.height, QImage.Format_RGBA8888)
        return qim

    def show_message(self, message):
        msg = QInputDialog(self)
        msg.setLabelText(message)
        msg.exec_()

    def start_puzzle_game(self):
        # سيتم إضافة لعبة ترتيب الصور هنا
        self.puzzle_window = PuzzleWindow()  # إنشاء النافذة الثانية
        self.puzzle_window.show()  # عرض النافذة الثانية

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageEditor()
    window.show()
    sys.exit(app.exec_())
