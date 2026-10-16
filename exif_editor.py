"""
EXIF Metadata Editor
Редактор метаданных фотографий
Требует: pip install piexif Pillow
Для сборки в EXE: pip install pyinstaller && pyinstaller --onefile --windowed exif_editor.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkfont
import piexif
import piexif.helper
from PIL import Image
import struct
import os
import shutil
import random
from datetime import datetime, timedelta
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pillow_heif = None


# ─── Цветовая схема ────────────────────────────────────────────────
BG        = "#0f0f0f"
BG2       = "#1a1a1a"
BG3       = "#242424"
ACCENT    = "#c8a84b"       # золото
ACCENT2   = "#8c7235"
FG        = "#e8e8e8"
FG2       = "#888888"
RED       = "#c0392b"
GREEN     = "#27ae60"
BORDER    = "#2e2e2e"
FONT_MAIN = ("Segoe UI", 11)
FONT_MONO = ("Consolas", 11)
FONT_HEAD = ("Segoe UI", 12, "bold")
FONT_BIG  = ("Segoe UI", 15, "bold")


# ─── ПРЕСЕТЫ (УСТРОЙСТВА) ───────────────────────────────────────────
# Метаданные для популярных и будущих моделей (на основе 2026 года)
PRESETS_DEVICES = {
    "iPhone 17 Pro": {
        "Make": "Apple", "Model": "iPhone 17 Pro", "Software": "26.4.1",
        "FocalLength": "6.86", "FocalLengthIn35mm": "24", "FNumber": "1.78",
        "LensModel": "iPhone 17 Pro back triple camera 6.86mm f/1.78", "LensMake": "Apple",
        "ISO": "50", "ExposureTime": "1/120"
    },
    "iPhone 16 Pro": {
        "Make": "Apple", "Model": "iPhone 16 Pro", "Software": "25.6.1",
        "FocalLength": "6.86", "FocalLengthIn35mm": "24", "FNumber": "1.78",
        "LensModel": "iPhone 16 Pro back triple camera 6.86mm f/1.78", "LensMake": "Apple",
        "ISO": "50", "ExposureTime": "1/120"
    },
    "iPhone 15 Pro": {
        "Make": "Apple", "Model": "iPhone 15 Pro", "Software": "17.4.1",
        "FocalLength": "6.86", "FocalLengthIn35mm": "24", "FNumber": "1.78",
        "LensModel": "iPhone 15 Pro back triple camera 6.86mm f/1.78", "LensMake": "Apple",
        "ISO": "50", "ExposureTime": "1/120"
    },
    "iPhone 14 Pro": {
        "Make": "Apple", "Model": "iPhone 14 Pro", "Software": "16.7.1",
        "FocalLength": "6.86", "FocalLengthIn35mm": "24", "FNumber": "1.78",
        "LensModel": "iPhone 14 Pro back triple camera 6.86mm f/1.78", "LensMake": "Apple",
        "ISO": "50", "ExposureTime": "1/120"
    },
    "iPhone 13 Pro": {
        "Make": "Apple", "Model": "iPhone 13 Pro", "Software": "15.8.1",
        "FocalLength": "5.7", "FocalLengthIn35mm": "26", "FNumber": "1.5",
        "LensModel": "iPhone 13 Pro back triple camera 5.7mm f/1.5", "LensMake": "Apple",
        "ISO": "50", "ExposureTime": "1/120"
    },
    "iPhone 12 Pro": {
        "Make": "Apple", "Model": "iPhone 12 Pro", "Software": "14.8.1",
        "FocalLength": "4.2", "FocalLengthIn35mm": "26", "FNumber": "1.6",
        "LensModel": "iPhone 12 Pro back triple camera 4.2mm f/1.6", "LensMake": "Apple",
        "ISO": "50", "ExposureTime": "1/120"
    },
    "Samsung S25 Ultra": {
        "Make": "Samsung", "Model": "SM-S938B", "Software": "S938BXXU1AXA1",
        "FocalLength": "6.3", "FocalLengthIn35mm": "23", "FNumber": "1.7",
        "LensModel": "Samsung S25 Ultra main camera", "LensMake": "Samsung",
        "ISO": "50", "ExposureTime": "1/100"
    },
    "Samsung S24 Ultra": {
        "Make": "Samsung", "Model": "SM-S928B", "Software": "S928BXXU1AXB5",
        "FocalLength": "6.3", "FocalLengthIn35mm": "23", "FNumber": "1.7",
        "LensModel": "Samsung S24 Ultra main camera", "LensMake": "Samsung",
        "ISO": "50", "ExposureTime": "1/100"
    },
    "Samsung S23 Ultra": {
        "Make": "Samsung", "Model": "SM-S918B", "Software": "S918BXXU1AWA6",
        "FocalLength": "6.3", "FocalLengthIn35mm": "23", "FNumber": "1.7",
        "LensModel": "Samsung S23 Ultra main camera", "LensMake": "Samsung",
        "ISO": "50", "ExposureTime": "1/100"
    },
    "Samsung S22 Ultra": {
        "Make": "Samsung", "Model": "SM-S908B", "Software": "S908BXXU1AVBF",
        "FocalLength": "6.4", "FocalLengthIn35mm": "23", "FNumber": "1.8",
        "LensModel": "Samsung S22 Ultra main camera", "LensMake": "Samsung",
        "ISO": "50", "ExposureTime": "1/100"
    },
    "Samsung S21 Ultra": {
        "Make": "Samsung", "Model": "SM-G998B", "Software": "G998BXXU1AUB6",
        "FocalLength": "6.7", "FocalLengthIn35mm": "24", "FNumber": "1.8",
        "LensModel": "Samsung S21 Ultra main camera", "LensMake": "Samsung",
        "ISO": "50", "ExposureTime": "1/100"
    },
    "Pixel 10 Pro": {
        "Make": "Google", "Model": "Pixel 10 Pro", "Software": "Android 16",
        "FocalLength": "6.9", "FocalLengthIn35mm": "24", "FNumber": "1.68",
        "LensModel": "Pixel 10 Pro back camera", "LensMake": "Google",
        "ISO": "50", "ExposureTime": "1/120"
    },
    "Pixel 9 Pro": {
        "Make": "Google", "Model": "Pixel 9 Pro", "Software": "Android 15",
        "FocalLength": "6.9", "FocalLengthIn35mm": "24", "FNumber": "1.68",
        "LensModel": "Pixel 9 Pro back camera", "LensMake": "Google",
        "ISO": "50", "ExposureTime": "1/120"
    },
    "Pixel 8 Pro": {
        "Make": "Google", "Model": "Pixel 8 Pro", "Software": "Android 14",
        "FocalLength": "6.9", "FocalLengthIn35mm": "24", "FNumber": "1.68",
        "LensModel": "Pixel 8 Pro back camera", "LensMake": "Google",
        "ISO": "50", "ExposureTime": "1/120"
    },
    "Pixel 7 Pro": {
        "Make": "Google", "Model": "Pixel 7 Pro", "Software": "Android 13",
        "FocalLength": "6.81", "FocalLengthIn35mm": "24", "FNumber": "1.85",
        "LensModel": "Pixel 7 Pro back camera", "LensMake": "Google",
        "ISO": "50", "ExposureTime": "1/120"
    },
    "Pixel 6 Pro": {
        "Make": "Google", "Model": "Pixel 6 Pro", "Software": "Android 12",
        "FocalLength": "6.81", "FocalLengthIn35mm": "24", "FNumber": "1.85",
        "LensModel": "Pixel 6 Pro back camera", "LensMake": "Google",
        "ISO": "50", "ExposureTime": "1/120"
    },
    "Pixel 5": {
        "Make": "Google", "Model": "Pixel 5", "Software": "Android 11",
        "FocalLength": "4.38", "FocalLengthIn35mm": "27", "FNumber": "1.7",
        "LensModel": "Pixel 5 back camera", "LensMake": "Google",
        "ISO": "50", "ExposureTime": "1/120"
    },
}

# ─── ПРЕСЕТЫ (СТРАНЫ) ──────────────────────────────────────────────
PRESETS_COUNTRIES = {
    "Россия (Москва)": {"lat": 55.7558, "lon": 37.6173, "ref_n": "N", "ref_e": "E"},
    "США (Нью-Йорк)": {"lat": 40.7128, "lon": -74.0060, "ref_n": "N", "ref_e": "W"},
    "Германия (Берлин)": {"lat": 52.5200, "lon": 13.4050, "ref_n": "N", "ref_e": "E"},
    "Франция (Париж)": {"lat": 48.8566, "lon": 2.3522, "ref_n": "N", "ref_e": "E"},
    "ОАЭ (Дубай)": {"lat": 25.2048, "lon": 55.2708, "ref_n": "N", "ref_e": "E"},
    "Турция (Стамбул)": {"lat": 41.0082, "lon": 28.9784, "ref_n": "N", "ref_e": "E"},
    "Казахстан (Астана)": {"lat": 51.1605, "lon": 71.4272, "ref_n": "N", "ref_e": "E"},
    "Украина (Киев)": {"lat": 50.4501, "lon": 30.5234, "ref_n": "N", "ref_e": "E"},
    "Великобритания (Лондон)": {"lat": 51.5074, "lon": -0.1278, "ref_n": "N", "ref_e": "W"},
    "Япония (Токио)": {"lat": 35.6762, "lon": 139.6503, "ref_n": "N", "ref_e": "E"},
}

# ─── ПРЕСЕТЫ (ЛОКАЦИИ) ─────────────────────────────────────────────
# Реальные координаты (Кафе, Парк, Жилой сектор) для каждой страны
PRESETS_LOCATIONS = {
    "Россия (Москва)": [
        {"name": "Cafe Pushkin", "lat": 55.7645, "lon": 37.6042},
        {"name": "Gorky Park", "lat": 55.7275, "lon": 37.6006},
        {"name": "Khamovniki Residential", "lat": 55.7333, "lon": 37.5833},
    ],
    "США (Нью-Йорк)": [
        {"name": "Cafe Grumpy", "lat": 40.7456, "lon": -73.9984},
        {"name": "Central Park", "lat": 40.7851, "lon": -73.9683},
        {"name": "Upper West Side Residential", "lat": 40.7879, "lon": -73.9742},
    ],
    "Германия (Берлин)": [
        {"name": "Cafe Einstein", "lat": 52.5065, "lon": 13.3592},
        {"name": "Tiergarten", "lat": 52.5145, "lon": 13.3501},
        {"name": "Prenzlauer Berg Residential", "lat": 52.5383, "lon": 13.4150},
    ],
    "Франция (Париж)": [
        {"name": "Café de Flore", "lat": 48.8542, "lon": 2.3325},
        {"name": "Jardin du Luxembourg", "lat": 48.8462, "lon": 2.3372},
        {"name": "Le Marais Residential", "lat": 48.8585, "lon": 2.3599},
    ],
    "ОАЭ (Дубай)": [
        {"name": "Arabian Tea House", "lat": 25.2657, "lon": 55.3045},
        {"name": "Zabeel Park", "lat": 25.2355, "lon": 55.3000},
        {"name": "Dubai Marina Residential", "lat": 25.0847, "lon": 55.1436},
    ],
    "Турция (Стамбул)": [
        {"name": "Cafe Privato", "lat": 41.0345, "lon": 28.9745},
        {"name": "Yıldız Park", "lat": 41.0475, "lon": 29.0078},
        {"name": "Kadıköy Residential", "lat": 40.9819, "lon": 29.0571},
    ],
    "Казахстан (Астана)": [
        {"name": "Rafe Cafe", "lat": 51.1345, "lon": 71.4285},
        {"name": "Presidential Park", "lat": 51.1325, "lon": 71.4260},
        {"name": "Yesil Residential", "lat": 51.1167, "lon": 71.4333},
    ],
    "Украина (Киев)": [
        {"name": "Honey Cafe", "lat": 50.4552, "lon": 30.5185},
        {"name": "Mariinskyi Park", "lat": 50.4485, "lon": 30.5348},
        {"name": "Pechersk Residential", "lat": 50.4350, "lon": 30.5450},
    ],
    "Великобритания (Лондон)": [
        {"name": "Monmouth Coffee", "lat": 51.5126, "lon": -0.1245},
        {"name": "Hyde Park", "lat": 51.5073, "lon": -0.1657},
        {"name": "Kensington Residential", "lat": 51.4990, "lon": -0.1937},
    ],
    "Япония (Токио)": [
        {"name": "Fuglen Tokyo", "lat": 35.6675, "lon": 139.6885},
        {"name": "Shinjuku Gyoen", "lat": 35.6853, "lon": 139.7094},
        {"name": "Setagaya Residential", "lat": 35.6465, "lon": 139.6533},
    ],
}

# ────────────────────────────────────────────────────────────────────
def rational(num, denom=1):
    return (int(num), int(denom))

def parse_exposure(s):
    s = s.strip()
    if "/" in s:
        a, b = s.split("/")
        return rational(int(a), int(b))
    return rational(float(s) * 10000, 10000)

def parse_focal(s):
    s = s.replace("mm", "").strip()
    if "." in s:
        a, b = s.split(".")
        denom = 10 ** len(b)
        return rational(int(a) * denom + int(b), denom)
    return rational(int(s))

def gps_dms(decimal):
    d = int(decimal)
    m = int((decimal - d) * 60)
    s = ((decimal - d) * 60 - m) * 60
    return ((d, 1), (m, 1), (int(s * 10000), 10000))


# ────────────────────────────────────────────────────────────────────
class ExifEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EXIF Metadata Editor")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(780, 860)

        self.file_list = [] # Список выбранных файлов
        self.overwrite_var = tk.BooleanVar(value=True)

        self._build_ui()
        self._load_defaults()
        self.update_idletasks()
        w, h = 860, 960
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── Построение интерфейса ──────────────────────────────────────
    def _build_ui(self):
        # Шапка
        header = tk.Frame(self, bg=BG, pady=16)
        header.pack(fill="x", padx=24)
        tk.Label(header, text="EXIF METADATA EDITOR",
                 font=FONT_BIG, bg=BG, fg=ACCENT).pack(side="left")
        tk.Label(header, text="  //  редактор метаданных",
                 font=FONT_MAIN, bg=BG, fg=FG2).pack(side="left", pady=4)

        # Выбор файла
        file_frame = tk.Frame(self, bg=BG2, pady=12, padx=16,
                              highlightbackground=BORDER, highlightthickness=1)
        file_frame.pack(fill="x", padx=20, pady=(0, 8))

        tk.Label(file_frame, text="ФАЙЛ", font=FONT_HEAD,
                 bg=BG2, fg=ACCENT).grid(row=0, column=0, sticky="w")

        self.file_var = tk.StringVar(value="Файлы не выбраны")
        tk.Label(file_frame, textvariable=self.file_var, font=FONT_MAIN,
                 bg=BG2, fg=FG2, anchor="w").grid(row=1, column=0, sticky="ew", pady=4)
        file_frame.columnconfigure(0, weight=1)

        btn_row = tk.Frame(file_frame, bg=BG2)
        btn_row.grid(row=2, column=0, sticky="w")
        self._btn(btn_row, "📂  Выбрать фото (одно или пачкой)", self._choose_files).pack(side="left", padx=(0, 8))
        self._btn(btn_row, "🚀  Запустить авто-обработку", self._apply_batch,
                  accent=True).pack(side="left")

        # Быстрая настройка
        quick_frame = tk.Frame(self, bg=BG2, pady=12, padx=16,
                               highlightbackground=BORDER, highlightthickness=1)
        quick_frame.pack(fill="x", padx=20, pady=(0, 8))

        tk.Label(quick_frame, text="БЫСТРАЯ НАСТРОЙКА (SMART)", font=FONT_HEAD,
                 bg=BG2, fg=ACCENT).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        # Устройство
        tk.Label(quick_frame, text="Устройство:", font=FONT_MAIN, bg=BG2, fg=FG).grid(row=1, column=0, sticky="w")
        self.device_var = tk.StringVar()
        device_cb = ttk.Combobox(quick_frame, textvariable=self.device_var, values=list(PRESETS_DEVICES.keys()), state="readonly", width=30)
        device_cb.grid(row=1, column=1, sticky="w", padx=8, pady=4)
        device_cb.bind("<<ComboboxSelected>>", self._on_device_select)

        # Страна
        tk.Label(quick_frame, text="Страна/Координаты:", font=FONT_MAIN, bg=BG2, fg=FG).grid(row=2, column=0, sticky="w")
        self.country_var = tk.StringVar()
        country_cb = ttk.Combobox(quick_frame, textvariable=self.country_var, values=list(PRESETS_COUNTRIES.keys()), state="readonly", width=30)
        country_cb.grid(row=2, column=1, sticky="w", padx=8, pady=4)
        country_cb.bind("<<ComboboxSelected>>", self._on_country_select)

        # Формат
        tk.Label(quick_frame, text="Формат:", font=FONT_MAIN, bg=BG2, fg=FG).grid(row=3, column=0, sticky="w")
        self.format_var = tk.StringVar(value="JPEG")
        format_cb = ttk.Combobox(quick_frame, textvariable=self.format_var, values=["JPEG", "HEIC"], state="readonly", width=10)
        format_cb.grid(row=3, column=1, sticky="w", padx=8, pady=4)

        # Перезапись
        chk = tk.Checkbutton(quick_frame, text="Перезаписывать оригиналы", variable=self.overwrite_var,
                             bg=BG2, fg=FG, selectcolor=BG, activebackground=BG2, font=("Segoe UI", 10))
        chk.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))

        # Текущее время
        btn_time = self._btn(quick_frame, "⏰  Установить текущее время", self._set_current_time)
        btn_time.grid(row=1, column=2, rowspan=2, padx=20, sticky="ns")

        # Вкладки
        nb_frame = tk.Frame(self, bg=BG)
        nb_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook",           background=BG,  borderwidth=0)
        style.configure("TNotebook.Tab",       background=BG3, foreground=FG2,
                        padding=[14, 6], font=FONT_MAIN, borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT2)],
                  foreground=[("selected", ACCENT)])
        style.configure("TScrollbar", background=BG3, troughcolor=BG2,
                        bordercolor=BG, arrowcolor=FG2)

        nb = ttk.Notebook(nb_frame)
        nb.pack(fill="both", expand=True)

        self.fields = {}   # name → StringVar

        pages = [
            ("📷  Камера",   self._camera_fields()),
            ("📅  Дата/Время", self._datetime_fields()),
            ("🔭  Оптика",   self._optics_fields()),
            ("⚙️  Экспозиция", self._exposure_fields()),
            ("🌍  GPS",      self._gps_fields()),
            ("🎨  Прочее",   self._misc_fields()),
        ]

        for title, field_list in pages:
            frame = tk.Frame(nb, bg=BG2)
            nb.add(frame, text=title)
            self._populate_tab(frame, field_list)

        # Лог
        log_frame = tk.Frame(self, bg=BG, pady=4)
        log_frame.pack(fill="x", padx=20, pady=(0, 12))
        self.log_var = tk.StringVar(value="Готов к работе.")
        tk.Label(log_frame, textvariable=self.log_var, font=FONT_MAIN,
                 bg=BG, fg=FG2, anchor="w").pack(fill="x")

    def _btn(self, parent, text, cmd, accent=False):
        bg = ACCENT if accent else BG3
        fg = "#0f0f0f" if accent else FG
        b = tk.Button(parent, text=text, command=cmd,
                      bg=bg, fg=fg, font=FONT_MAIN,
                      relief="flat", padx=14, pady=6, cursor="hand2",
                      activebackground=ACCENT2, activeforeground=FG,
                      bd=0)
        b.bind("<Enter>", lambda e: b.config(bg=ACCENT2 if accent else "#333"))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def _populate_tab(self, frame, field_list):
        canvas = tk.Canvas(frame, bg=BG2, highlightthickness=0)
        sb = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG2, padx=16, pady=12)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_resize(e):
            canvas.itemconfig(win_id, width=e.width)
        canvas.bind("<Configure>", _on_resize)
        inner.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        for key, label, hint in field_list:
            var = tk.StringVar()
            self.fields[key] = var

            row = tk.Frame(inner, bg=BG2, pady=3)
            row.pack(fill="x")

            tk.Label(row, text=label, font=FONT_HEAD,
                     bg=BG2, fg=FG, anchor="w", width=22).pack(side="left")

            sub = tk.Frame(row, bg=BG2)
            sub.pack(side="left", fill="x", expand=True, padx=(6, 0))

            ent = tk.Entry(sub, textvariable=var, font=FONT_MONO,
                           bg=BG3, fg=ACCENT, insertbackground=ACCENT,
                           relief="flat", bd=0, highlightthickness=1,
                           highlightbackground=BORDER,
                           highlightcolor=ACCENT)
            ent.pack(fill="x", ipady=6)
            if hint:
                tk.Label(sub, text=hint, font=("Segoe UI", 9),
                         bg=BG2, fg=FG2, anchor="w").pack(fill="x")

    # ── Определения полей ──────────────────────────────────────────
    def _camera_fields(self):
        return [
            ("Make",    "Make",    "пр. Apple"),
            ("Model",   "Model",   "пр. iPhone 13"),
            ("Software","Software","пр. 17.4.1"),
        ]

    def _datetime_fields(self):
        return [
            ("DateTimeOriginal",  "DateTimeOriginal",  "YYYY:MM:DD HH:MM:SS"),
            ("DateTimeDigitized", "DateTimeDigitized", "YYYY:MM:DD HH:MM:SS"),
        ]

    def _optics_fields(self):
        return [
            ("FocalLength",           "FocalLength",           "пр. 5.7 (мм)"),
            ("FocalLengthIn35mm",     "FocalLengthIn35mm",     "пр. 26 (мм)"),
            ("FNumber",               "FNumber",               "пр. 1.6"),
            ("LensModel",             "LensModel",             "пр. iPhone 13 back…"),
            ("LensMake",              "LensMake",              "пр. Apple"),
        ]

    def _exposure_fields(self):
        return [
            ("ExposureTime", "ExposureTime",  "пр. 1/120"),
            ("ISO",          "ISO",           "пр. 320"),
            ("WhiteBalance", "WhiteBalance",  "0=авто, 1=ручной"),
            ("Flash",        "Flash",         "пр. 16"),
            ("ExposureMode", "ExposureMode",  "0=авто"),
            ("ExposureProgram","ExposureProgram","2=обычная"),
            ("MeteringMode", "MeteringMode",  "5=матричный"),
            ("DigitalZoomRatio","DigitalZoomRatio","пр. 1"),
        ]

    def _gps_fields(self):
        return [
            ("GPSLatitude",    "GPSLatitude",    "десятичные градусы, пр. 60.1699"),
            ("GPSLatitudeRef", "GPSLatitudeRef", "N или S"),
            ("GPSLongitude",   "GPSLongitude",   "десятичные градусы, пр. 24.9384"),
            ("GPSLongitudeRef","GPSLongitudeRef","E или W"),
            ("GPSAltitude",    "GPSAltitude",    "метры, пр. 12"),
            ("GPSAltitudeRef", "GPSAltitudeRef", "0=над уровнем моря"),
            ("GPSTimeStamp",   "GPSTimeStamp",   "HH:MM:SS"),
            ("GPSDateStamp",   "GPSDateStamp",   "YYYY:MM:DD"),
            ("GPSMapDatum",    "GPSMapDatum",    "пр. WGS-84"),
        ]

    def _misc_fields(self):
        return [
            ("ColorSpace",        "ColorSpace",        "1=sRGB"),
            ("ExifImageWidth",    "ExifImageWidth",     "пр. 4032"),
            ("ExifImageHeight",   "ExifImageHeight",    "пр. 3024"),
            ("Orientation",       "Orientation",        "1=нормальная"),
            ("SceneType",         "SceneType",          "1=снято напрямую"),
            ("CustomRendered",    "CustomRendered",     "0=обычный"),
            ("SceneCaptureType",  "SceneCaptureType",   "0=стандартный"),
        ]

    # ── Дефолтные значения ─────────────────────────────────────────
    def _load_defaults(self):
        defaults = {
            "Make":               "Apple",
            "Model":              "iPhone 13",
            "Software":           "17.4.1",
            "DateTimeOriginal":   "2026:04:05 18:23:41",
            "DateTimeDigitized":  "2026:04:05 18:23:41",
            "FocalLength":        "5.7",
            "FocalLengthIn35mm":  "26",
            "FNumber":            "1.6",
            "LensModel":          "iPhone 13 back camera 5.7mm f/1.6",
            "LensMake":           "Apple",
            "ExposureTime":       "1/120",
            "ISO":                "320",
            "WhiteBalance":       "0",
            "Flash":              "16",
            "ExposureMode":       "0",
            "ExposureProgram":    "2",
            "MeteringMode":       "5",
            "DigitalZoomRatio":   "1",
            "GPSLatitude":        "60.1699",
            "GPSLatitudeRef":     "N",
            "GPSLongitude":       "24.9384",
            "GPSLongitudeRef":    "E",
            "GPSAltitude":        "12",
            "GPSAltitudeRef":     "0",
            "GPSTimeStamp":       "15:23:41",
            "GPSDateStamp":       "2026:04:05",
            "GPSMapDatum":        "WGS-84",
            "ColorSpace":         "1",
            "ExifImageWidth":     "4032",
            "ExifImageHeight":    "3024",
            "Orientation":        "1",
            "SceneType":          "1",
            "CustomRendered":     "0",
            "SceneCaptureType":   "0",
        }
        for k, v in defaults.items():
            if k in self.fields:
                self.fields[k].set(v)

    # ── ПРЕСЕТЫ ────────────────────────────────────────────────────
    def _on_device_select(self, event=None):
        name = self.device_var.get()
        if name in PRESETS_DEVICES:
            p = PRESETS_DEVICES[name]
            for k, v in p.items():
                if k in self.fields:
                    self.fields[k].set(v)
            
            # Авто-переключение формата для iPhone
            if "iPhone" in name:
                self.format_var.set("HEIC")
            else:
                self.format_var.set("JPEG")

            self._log(f"Устройство: {name} применено", "ok")

    def _on_country_select(self, event=None):
        name = self.country_var.get()
        if name in PRESETS_LOCATIONS:
            # Выбираем случайную реальную точку из списка
            poi = random.choice(PRESETS_LOCATIONS[name])
            self.fields["GPSLatitude"].set(str(poi["lat"]))
            self.fields["GPSLongitude"].set(str(poi["lon"]))
            
            # Определяем полушария
            self.fields["GPSLatitudeRef"].set("N" if poi["lat"] >= 0 else "S")
            self.fields["GPSLongitudeRef"].set("E" if poi["lon"] >= 0 else "W")
            
            self._log(f"Локация: {poi['name']} ({name}) выбрана", "ok")
        elif name in PRESETS_COUNTRIES:
            p = PRESETS_COUNTRIES[name]
            self.fields["GPSLatitude"].set(str(p["lat"]))
            self.fields["GPSLatitudeRef"].set(p["ref_n"])
            self.fields["GPSLongitude"].set(str(p["lon"]))
            self.fields["GPSLongitudeRef"].set(p["ref_e"])
            self._log(f"Координаты {name} установлены", "ok")

    def _set_current_time(self):
        now = datetime.now()
        dt_str = now.strftime("%Y:%m:%d %H:%M:%S")
        self.fields["DateTimeOriginal"].set(dt_str)
        self.fields["DateTimeDigitized"].set(dt_str)
        self.fields["GPSDateStamp"].set(now.strftime("%Y:%m:%d"))
        self.fields["GPSTimeStamp"].set(now.strftime("%H:%M:%S"))
        self._log("Установлено текущее время", "ok")

    # ── Выбор файлов ───────────────────────────────────────────────
    def _choose_files(self):
        paths = filedialog.askopenfilenames(
            title="Выберите фотографии",
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.webp *.JPG *.JPEG *.PNG *.WEBP"), ("Все файлы", "*.*")]
        )
        if paths:
            self.file_list = list(paths)
            if len(paths) == 1:
                self.file_var.set(paths[0])
                self._log(f"Выбран 1 файл", "ok")
            else:
                self.file_var.set(f"Выбрано файлов: {len(paths)}")
                self._log(f"Выбрано файлов: {len(paths)}", "ok")

    def _apply_batch(self):
        if not self.file_list:
            messagebox.showwarning("Нет файлов", "Сначала выберите фото!")
            return

        # Получаем базовое время
        base_time_str = self.fields["DateTimeOriginal"].get()
        try:
            base_dt = datetime.strptime(base_time_str, "%Y:%M:%D %H:%M:%S")
        except:
            try:
                # Пытаемся распарсить как YYYY:MM:DD HH:MM:SS (стандарт EXIF)
                base_dt = datetime.strptime(base_time_str, "%Y:%m:%d %H:%M:%S")
            except Exception as e:
                messagebox.showerror("Ошибка даты", f"Неверный формат даты: {base_time_str}\nНужно YYYY:MM:DD HH:MM:SS")
                return

        count = 0
        errors = 0
        
        # Если не перезаписываем, спросим папку
        out_dir = None
        if not self.overwrite_var.get():
            out_dir = filedialog.askdirectory(title="Выберите папку для сохранения")
            if not out_dir: return

        for i, src in enumerate(self.file_list):
            try:
                # Рассчитываем время (+10 сек для каждого фото)
                offset = i * 10
                current_dt = base_dt.replace(second=(base_dt.second + offset) % 60) # Упрощенно, лучше через timedelta
                # Но лучше по-честному:
                from datetime import timedelta
                current_dt = base_dt + timedelta(seconds=offset)
                
                dt_str = current_dt.strftime("%Y:%m:%d %H:%M:%S")
                self.fields["DateTimeOriginal"].set(dt_str)
                self.fields["DateTimeDigitized"].set(dt_str)
                self.fields["GPSDateStamp"].set(current_dt.strftime("%Y:%m:%d"))
                self.fields["GPSTimeStamp"].set(current_dt.strftime("%H:%M:%S"))

                # Добавляем рандомный разброс GPS (имитация разных мест: кафе, дом, парк)
                try:
                    lat = float(self.fields["GPSLatitude"].get())
                    lon = float(self.fields["GPSLongitude"].get())
                    # Смещение на ~100-500 метров
                    lat += random.uniform(-0.003, 0.003)
                    lon += random.uniform(-0.003, 0.003)
                    self.fields["GPSLatitude"].set(f"{lat:.6f}")
                    self.fields["GPSLongitude"].set(f"{lon:.6f}")
                except:
                    pass

                # Определяем путь назначения
                ext = ".heic" if self.format_var.get() == "HEIC" else ".jpg"
                if self.overwrite_var.get():
                    base, _ = os.path.splitext(src)
                    dst = base + ext
                else:
                    dst = os.path.join(out_dir, os.path.basename(src))
                    base, _ = os.path.splitext(dst)
                    dst = base + ext

                self._write_exif(src, dst)
                
                # Если перезаписываем и расширение было другое, удаляем оригинал
                if self.overwrite_var.get() and src.lower() != dst.lower():
                    try: os.remove(src)
                    except: pass
                
                count += 1
            except Exception as e:
                print(f"Error processing {src}: {e}")
                errors += 1

        self._log(f"Готово! Обработано: {count}, Ошибок: {errors}", "ok" if errors == 0 else "info")
        messagebox.showinfo("Готово", f"Обработка завершена!\nУспешно: {count}\nОшибок: {errors}")

    # ── Запись EXIF ────────────────────────────────────────────────
    def _write_exif(self, src, dst):
        # Открываем изображение (Pillow поддерживает разные форматы)
        img = Image.open(src)
        
        # Если это не JPEG, конвертируем в RGB
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        elif img.mode != "RGB":
            img = img.convert("RGB")

        f = {k: v.get() for k, v in self.fields.items()}

        # IFD 0
        ifd0 = {
            piexif.ImageIFD.Make:        f["Make"].encode(),
            piexif.ImageIFD.Model:       f["Model"].encode(),
            piexif.ImageIFD.Software:    f["Software"].encode(),
            piexif.ImageIFD.Orientation: int(f["Orientation"]),
        }

        # Exif IFD
        # Правильный парсинг даты для EXIF (замена : в дате не всегда нужна, но формат YYYY:MM:DD HH:MM:SS важен)
        dt_orig = f["DateTimeOriginal"].replace("-", ":")
        dt_dig  = f["DateTimeDigitized"].replace("-", ":")
        
        exif_ifd = {
            piexif.ExifIFD.ExifVersion:           b"0232",
            piexif.ExifIFD.FlashpixVersion:        b"0100",
            piexif.ExifIFD.ColorSpace:             int(f["ColorSpace"]),
            piexif.ExifIFD.PixelXDimension:        img.width,
            piexif.ExifIFD.PixelYDimension:        img.height,
            piexif.ExifIFD.DateTimeOriginal:       dt_orig.encode(),
            piexif.ExifIFD.DateTimeDigitized:      dt_dig.encode(),
            piexif.ExifIFD.FocalLength:            parse_focal(f["FocalLength"]),
            piexif.ExifIFD.FocalLengthIn35mmFilm:  int(float(f["FocalLengthIn35mm"])),
            piexif.ExifIFD.FNumber:                rational(int(float(f["FNumber"]) * 100), 100),
            piexif.ExifIFD.ExposureTime:           parse_exposure(f["ExposureTime"]),
            piexif.ExifIFD.ISOSpeedRatings:        int(f["ISO"]),
            piexif.ExifIFD.LensModel:              f["LensModel"].encode(),
            piexif.ExifIFD.LensMake:               f["LensMake"].encode(),
            piexif.ExifIFD.WhiteBalance:           int(f["WhiteBalance"]),
            piexif.ExifIFD.Flash:                  int(f["Flash"]),
            piexif.ExifIFD.ExposureMode:           int(f["ExposureMode"]),
            piexif.ExifIFD.ExposureProgram:        int(f["ExposureProgram"]),
            piexif.ExifIFD.MeteringMode:           int(f["MeteringMode"]),
            piexif.ExifIFD.SceneType:              struct.pack("B", int(f["SceneType"])),
            piexif.ExifIFD.CustomRendered:         int(f["CustomRendered"]),
            piexif.ExifIFD.DigitalZoomRatio:       rational(int(float(f["DigitalZoomRatio"]) * 100), 100),
            piexif.ExifIFD.SceneCaptureType:       int(f["SceneCaptureType"]),
        }

        # GPS IFD
        ts = f["GPSTimeStamp"].split(":")
        gps_ifd = {
            piexif.GPSIFD.GPSLatitudeRef:   f["GPSLatitudeRef"].encode(),
            piexif.GPSIFD.GPSLatitude:      gps_dms(float(f["GPSLatitude"])),
            piexif.GPSIFD.GPSLongitudeRef:  f["GPSLongitudeRef"].encode(),
            piexif.GPSIFD.GPSLongitude:     gps_dms(float(f["GPSLongitude"])),
            piexif.GPSIFD.GPSAltitudeRef:   int(f["GPSAltitudeRef"]),
            piexif.GPSIFD.GPSAltitude:      rational(int(f["GPSAltitude"])),
            piexif.GPSIFD.GPSTimeStamp:     [(int(x), 1) for x in ts],
            piexif.GPSIFD.GPSDateStamp:     f["GPSDateStamp"].encode(),
            piexif.GPSIFD.GPSMapDatum:      f["GPSMapDatum"].encode(),
        }

        exif_bytes = piexif.dump(exif_dict)
        
        fmt = self.format_var.get()
        if fmt == "HEIC" and pillow_heif:
            img.save(dst, "HEIF", exif=exif_bytes, quality=90)
        else:
            if fmt == "HEIC":
                self._log("pillow-heif не установлен! Сохраняем в JPEG", "err")
            img.save(dst, "JPEG", exif=exif_bytes, quality=95)

    def _log(self, msg, kind="info"):
        colors = {"ok": GREEN, "err": RED, "info": FG2}
        self.log_var.set(msg)


# ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    app = ExifEditor()
    app.mainloop()
