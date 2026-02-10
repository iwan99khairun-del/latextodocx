import sys
import numpy as np
import pandas as pd
import cv2
from PIL import Image
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox, QFormLayout, QGridLayout,
    QSpinBox, QDoubleSpinBox, QSlider, QRadioButton, QFileDialog,
    QScrollArea, QSplitter, QMessageBox
)
from PySide6.QtGui import QPixmap, QImage, QColor
from PySide6.QtCore import Qt, QCoreApplication

def rgb_to_hsv(r: int, g: int, b: int):
    pixel = np.uint8([[[r, g, b]]])
    hsv = cv2.cvtColor(pixel, cv2.COLOR_RGB2HSV)
    return hsv[0][0]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📈 Ekstrak Data dari Gambar Grafik")
        self.resize(1600, 900)

        # Variabel utama
        self.original_img = None  # np.array RGB
        self.cropped_img = None
        self.h_crop = 0
        self.w_crop = 0
        self.df_grouped_px = None  # DataFrame dengan px_x dan px_y (grouped)
        self.final_df = None
        self.target_color = QColor("#FF9900")
        self.chart_type = "Garis (Line)"

        # Widget utama
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # === HEADER ===
        header_layout = QHBoxLayout()
        title_label = QLabel("<h1>📈 Ekstrak Data dari Gambar Grafik</h1>")
        header_layout.addWidget(title_label)

        open_button = QPushButton("📤 Upload Gambar Grafik (JPG/PNG)")
        open_button.clicked.connect(self.open_image)
        header_layout.addWidget(open_button)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # === SPLITTER UTAMA (kiri: kontrol | tengah: cropped | kanan: viz) ===
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # --- Kiri: Kontrol ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Instruksi
        intro_label = QLabel("""
        <h3>📋 Cara Pakai:</h3>
        1. Upload Gambar.<br>
        2. <b>CROP (Potong)</b> gambar sampai angka/tulisan sumbu & judul HILANG.<br>
        3. Atur warna, sensitivitas, kalibrasi, lalu simpan ke Excel.
        """)
        intro_label.setWordWrap(True)
        left_layout.addWidget(intro_label)

        # Pengaturan umum
        settings_group = QGroupBox("🔧 Pengaturan")
        settings_layout = QVBoxLayout(settings_group)

        # 1. Tipe grafik
        type_group = QGroupBox("1. Tipe Grafik")
        type_layout = QHBoxLayout(type_group)
        self.radio_line = QRadioButton("Garis (Line)")
        self.radio_bar = QRadioButton("Batang (Bar)")
        self.radio_line.setChecked(True)
        self.radio_line.toggled.connect(self.on_chart_type_changed)
        type_layout.addWidget(self.radio_line)
        type_layout.addWidget(self.radio_bar)
        settings_layout.addWidget(type_group)

        # 2. Kalibrasi sumbu
        calib_group = QGroupBox("2. Kalibrasi Sumbu")
        calib_grid = QGridLayout(calib_group)
        calib_grid.addWidget(QLabel("X Min"), 0, 0)
        self.spin_xmin = QDoubleSpinBox()
        self.spin_xmin.setValue(0.0)
        self.spin_xmin.setDecimals(3)
        self.spin_xmin.setRange(-1e9, 1e9)
        self.spin_xmin.valueChanged.connect(self.compute_data)
        calib_grid.addWidget(self.spin_xmin, 0, 1)

        calib_grid.addWidget(QLabel("X Max"), 0, 2)
        self.spin_xmax = QDoubleSpinBox()
        self.spin_xmax.setValue(100.0)
        self.spin_xmax.valueChanged.connect(self.compute_data)
        calib_grid.addWidget(self.spin_xmax, 0, 3)

        calib_grid.addWidget(QLabel("Y Min"), 1, 0)
        self.spin_ymin = QDoubleSpinBox()
        self.spin_ymin.setValue(0.0)
        self.spin_ymin.valueChanged.connect(self.compute_data)
        calib_grid.addWidget(self.spin_ymin, 1, 1)

        calib_grid.addWidget(QLabel("Y Max"), 1, 2)
        self.spin_ymax = QDoubleSpinBox()
        self.spin_ymax.setValue(100.0)
        self.spin_ymax.valueChanged.connect(self.compute_data)
        calib_grid.addWidget(self.spin_ymax, 1, 3)

        settings_layout.addWidget(calib_group)

        # 3. Deteksi warna
        color_group = QGroupBox("3. Deteksi Warna")
        color_layout = QVBoxLayout(color_group)

        self.color_button = QPushButton("Pilih Warna")
        self.color_button.setStyleSheet(f"background-color: {self.target_color.name()}; min-height: 40px;")
        self.color_button.clicked.connect(self.pick_color)
        color_layout.addWidget(self.color_button)

        self.tol_slider = QSlider(Qt.Horizontal)
        self.tol_slider.setRange(10, 180)
        self.tol_slider.setValue(60)
        self.tol_slider.valueChanged.connect(self.update_viz)
        color_layout.addWidget(QLabel("Sensitivitas Warna"))
        color_layout.addWidget(self.tol_slider)

        settings_layout.addWidget(color_group)
        left_layout.addWidget(settings_group)

        # Crop
        crop_group = QGroupBox("✂️ POTONG (CROP)")
        crop_layout = QFormLayout(crop_group)

        warning_label = QLabel("⚠️ Potong sampai angka sumbu & judul HILANG!")
        warning_label.setStyleSheet("background-color: #ffff99; padding: 8px; font-weight: bold;")
        warning_label.setWordWrap(True)
        crop_layout.addRow(warning_label)

        self.crop_top = QSpinBox()
        self.crop_top.valueChanged.connect(self.update_crop)
        crop_layout.addRow("Atas:", self.crop_top)

        self.crop_bottom = QSpinBox()
        self.crop_bottom.valueChanged.connect(self.update_crop)
        crop_layout.addRow("Bawah:", self.crop_bottom)

        self.crop_left = QSpinBox()
        self.crop_left.valueChanged.connect(self.update_crop)
        crop_layout.addRow("Kiri:", self.crop_left)

        self.crop_right = QSpinBox()
        self.crop_right.valueChanged.connect(self.update_crop)
        crop_layout.addRow("Kanan:", self.crop_right)

        self.size_label = QLabel("")
        crop_layout.addRow("Ukuran:", self.size_label)

        left_layout.addWidget(crop_group)
        left_layout.addStretch()

        splitter.addWidget(left_widget)

        # --- Tengah: Cropped ---
        mid_widget = QWidget()
        mid_layout = QVBoxLayout(mid_widget)
        mid_layout.addWidget(QLabel("<h3>✂️ Area Bersih (Cropped)</h3>"))
        self.scroll_cropped = QScrollArea()
        self.label_cropped = QLabel("Belum ada gambar")
        self.label_cropped.setAlignment(Qt.AlignCenter)
        self.scroll_cropped.setWidget(self.label_cropped)
        self.scroll_cropped.setWidgetResizable(True)
        mid_layout.addWidget(self.scroll_cropped)
        splitter.addWidget(mid_widget)

        # --- Kanan: Visualisasi deteksi ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel("<h3>👀 Hasil Deteksi (Hijau = Data Terambil)</h3>"))
        self.scroll_viz = QScrollArea()
        self.label_viz = QLabel("Belum ada gambar")
        self.label_viz.setAlignment(Qt.AlignCenter)
        self.scroll_viz.setWidget(self.label_viz)
        self.scroll_viz.setWidgetResizable(True)
        right_layout.addWidget(self.scroll_viz)
        splitter.addWidget(right_widget)

        splitter.setSizes([400, 600, 600])

        # === FOOTER ===
        footer_layout = QHBoxLayout()
        self.status_label = QLabel("Upload gambar untuk memulai.")
        self.status_label.setStyleSheet("font-weight: bold;")
        footer_layout.addWidget(self.status_label)

        self.save_button = QPushButton("📥 SIMPAN KE EXCEL")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_excel)
        footer_layout.addWidget(self.save_button)
        footer_layout.addStretch()
        main_layout.addLayout(footer_layout)

    # ===================================================================
    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih Gambar", "", "Images (*.jpg *.jpeg *.png)")
        if not path:
            return

        pil_img = Image.open(path).convert('RGB')
        self.original_img = np.array(pil_img)
        height, width, _ = self.original_img.shape

        # Set batas crop
        self.crop_top.setRange(0, height)
        self.crop_top.setValue(0)
        self.crop_bottom.setRange(0, height)
        self.crop_bottom.setValue(height)
        self.crop_left.setRange(0, width)
        self.crop_left.setValue(0)
        self.crop_right.setRange(0, width)
        self.crop_right.setValue(width)

        self.update_crop()

    def update_crop(self):
        if self.original_img is None:
            return

        top = self.crop_top.value()
        bottom = self.crop_bottom.value()
        left = self.crop_left.value()
        right = self.crop_right.value()

        if bottom <= top or right <= left:
            return

        self.cropped_img = self.original_img[top:bottom, left:right]
        self.h_crop, self.w_crop, _ = self.cropped_img.shape
        self.size_label.setText(f"{self.w_crop} × {self.h_crop} px")

        self.display_cropped()
        self.update_viz()

    def display_cropped(self):
        if self.cropped_img is None:
            return
        pixmap = self.np_to_pixmap(self.cropped_img)
        self.label_cropped.setPixmap(pixmap)

    def update_viz(self):
        if self.cropped_img is None:
            return

        # Hitung mask
        hsv_img = cv2.cvtColor(self.cropped_img, cv2.COLOR_RGB2HSV)
        r, g, b = self.target_color.red(), self.target_color.green(), self.target_color.blue()
        target_hsv = rgb_to_hsv(r, g, b)
        tolerance = self.tol_slider.value()

        lower = np.array([max(0, target_hsv[0] - tolerance), 30, 30])
        upper = np.array([min(179, target_hsv[0] + tolerance), 255, 255])
        mask = cv2.inRange(hsv_img, lower, upper)

        # Visualisasi overlay hijau
        dimmed_img = (self.cropped_img * 0.5).astype(np.uint8)
        green_layer = np.zeros_like(self.cropped_img)
        green_layer[:] = [0, 255, 0]
        result_viz = np.where(mask[:, :, None] > 0, green_layer, dimmed_img)
        final_viz = cv2.addWeighted(self.cropped_img, 0.3, result_viz, 0.7, 0)

        pixmap = self.np_to_pixmap(final_viz)
        self.label_viz.setPixmap(pixmap)

        # Grouping pixel berdasarkan tipe grafik
        ys, xs = np.where(mask > 0)
        if len(xs) > 0:
            df_pixel = pd.DataFrame({'px_x': xs, 'px_y': ys})
            if self.chart_type == "Batang (Bar)":
                self.df_grouped_px = df_pixel.groupby('px_x')['px_y'].min().reset_index()
            else:
                self.df_grouped_px = df_pixel.groupby('px_x')['px_y'].mean().reset_index()
        else:
            self.df_grouped_px = None

        self.compute_data()

    def compute_data(self):
        if self.df_grouped_px is None or self.cropped_img is None:
            self.final_df = None
            self.status_label.setText("⚠️ Masih kosong? Coba naikkan 'Sensitivitas Warna' atau pilih ulang warnanya.")
            self.save_button.setEnabled(False)
            return

        df = self.df_grouped_px.copy()
        x_min = self.spin_xmin.value()
        x_max = self.spin_xmax.value()
        y_min = self.spin_ymin.value()
        y_max = self.spin_ymax.value()

        df['Data_X'] = x_min + (df['px_x'] / self.w_crop) * (x_max - x_min)
        df['Data_Y'] = y_min + ((self.h_crop - df['px_y']) / self.h_crop) * (y_max - y_min)

        self.final_df = df[['Data_X', 'Data_Y']].sort_values('Data_X')
        self.status_label.setText(f"✅ Oke! {len(self.final_df)} titik ditemukan.")
        self.save_button.setEnabled(True)

    def on_chart_type_changed(self):
        self.chart_type = "Garis (Line)" if self.radio_line.isChecked() else "Batang (Bar)"
        self.update_viz()

    def pick_color(self):
        color = QColorDialog.getColor(self.target_color, self, "Pilih Warna Garis/Batang")
        if color.isValid():
            self.target_color = color
            self.color_button.setStyleSheet(f"background-color: {color.name()}; min-height: 40px;")
            self.update_viz()

    def save_excel(self):
        if self.final_df is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Simpan ke Excel", "data_grafik.xlsx", "Excel Files (*.xlsx)")
        if path:
            self.final_df.to_excel(path, index=False)
            QMessageBox.information(self, "Sukses", "Data berhasil disimpan ke Excel!")

    def np_to_pixmap(self, np_img: np.ndarray) -> QPixmap:
        np_img = np_img.astype(np.uint8)
        h, w = np_img.shape[:2]
        bytes_per_line = w * 3
        qimg = QImage(np_img.tobytes(), w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qimg)


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
