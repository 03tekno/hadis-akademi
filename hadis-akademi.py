import sys
import json
import re
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QSplitter, QTextBrowser, 
                             QListWidget, QVBoxLayout, QHBoxLayout, QWidget, 
                             QLabel, QLineEdit, QPushButton, QStatusBar, QComboBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QGuiApplication, QIcon

class AkademikHadisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hadis Akademi v1.0")
        
        self.setWindowIcon(QIcon("hadis.png"))
        
        self.ayar_dosyasi = os.path.expanduser("~/.hadis-akademi_config.json")
        self.mevcut_font_boyutu = 22 
        self.ekrandaki_hadisler = [] 
        self.son_arama_metni = "" 
        self.aktif_tema = "Klasik Fildişi"
        self.hadisler = []
        self.serhler = {}
        self.fasillar = []

        self.temalar = {
            "Klasik Fildişi": {"bg": "#f5f5f0", "kart": "#ffffff", "txt": "#1a1a1a", "vrg": "#2d5a4c", "pnl": "#e7e5d1", "serh": "#fcfaf5"},
            "Modern Koyu": {"bg": "#121212", "kart": "#1e1e1e", "txt": "#e0e0e0", "vrg": "#bb86fc", "pnl": "#2c2c2c", "serh": "#252525"},
            "Orman (Forest)": {"bg": "#1a2421", "kart": "#2d3a35", "txt": "#e8f5e9", "vrg": "#81c784", "pnl": "#3e4d48", "serh": "#34423d"},
            "Mint Fresh": {"bg": "#f0f7f4", "kart": "#ffffff", "txt": "#2d3a3a", "vrg": "#3eb489", "pnl": "#d1e8e2", "serh": "#f9fffb"},
            "Kahve (Mocha)": {"bg": "#2b2622", "kart": "#3e362e", "txt": "#ede0d4", "vrg": "#ddb892", "pnl": "#4a4036", "serh": "#453b32"},
            "Gece Mavisi": {"bg": "#0a192f", "kart": "#112240", "txt": "#ccd6f6", "vrg": "#64ffda", "pnl": "#1d2d50", "serh": "#1b2a4e"},
            "Kömür (Charcoal)": {"bg": "#212121", "kart": "#333333", "txt": "#f5f5f5", "vrg": "#ff5252", "pnl": "#424242", "serh": "#3a3a3a"},
            "Toprak & Gül": {"bg": "#dfd3c3", "kart": "#f8ede3", "txt": "#7d5a50", "vrg": "#8d4925", "pnl": "#d0b8a8", "serh": "#f2e8da"},
            "Okyanus": {"bg": "#e0f2f1", "kart": "#ffffff", "txt": "#004d40", "vrg": "#00acc1", "pnl": "#b2dfdb", "serh": "#f4fffe"},
            "Nordic Frost": {"bg": "#eceff4", "kart": "#ffffff", "txt": "#2e3440", "vrg": "#88c0d0", "pnl": "#d8dee9", "serh": "#f0f4f8"},
            "Şafak Vakti": {"bg": "#23074d", "kart": "#4b1248", "txt": "#ffffff", "vrg": "#ff512f", "pnl": "#320b3c", "serh": "#5a1854"},
            "Bambu": {"bg": "#f1f8e9", "kart": "#ffffff", "txt": "#33691e", "vrg": "#7cb342", "pnl": "#dcedc8", "serh": "#f9fbe7"},
            "Eski Kitap": {"bg": "#d4c4a8", "kart": "#e6d5b8", "txt": "#3e2723", "vrg": "#5d4037", "pnl": "#c3b091", "serh": "#efe0ca"},
            "Uzay Gri": {"bg": "#2c3e50", "kart": "#34495e", "txt": "#ecf0f1", "vrg": "#3498db", "pnl": "#1a252f", "serh": "#3d566e"},
            "Petrol": {"bg": "#071e22", "kart": "#052f32", "txt": "#80ced7", "vrg": "#00a896", "pnl": "#021114", "serh": "#083d41"},
            "Kardelen": {"bg": "#f8f9fa", "kart": "#ffffff", "txt": "#343a40", "vrg": "#007bff", "pnl": "#e9ecef", "serh": "#f1f3f5"},
            "Zeytin Dalı": {"bg": "#556b2f", "kart": "#6b8e23", "txt": "#ffffff", "vrg": "#f5f5dc", "pnl": "#4b5d26", "serh": "#7a9e31"}
        }
        
        self.verileri_yukle()
        self.init_ui()
        self.tema_uygula(self.aktif_tema)
        
        # İlk açılışta ilk hadisi yükleyen mantık
        if self.fasillar:
            self.fasil_list.setCurrentRow(0)
            self.konu_yukle(self.fasil_list.currentItem())
            if self.konu_list.count() > 0:
                self.konu_list.setCurrentRow(0)
                self.hadis_yukle(self.konu_list.currentItem())

        QTimer.singleShot(150, self.oranlari_uygula)
        QTimer.singleShot(300, self.son_konumu_yukle) 
        self.showMaximized() 

    def verileri_yukle(self):
        try:
            if os.path.exists('hdslr.json'):
                with open('hdslr.json', 'r', encoding='utf-8') as f:
                    ham_data = json.load(f)
                    self.hadisler = sorted(ham_data, key=lambda x: int(x.get('_id', 0)))
            
            if os.path.exists('serh.json'):
                with open('serh.json', 'r', encoding='utf-8') as f:
                    self.serhler = {str(item.get('_id')): item.get('serh', '') for item in json.load(f)}
            
            fasillar_set = []
            for h in self.hadisler:
                f = h.get('fasil')
                if f and f not in fasillar_set: fasillar_set.append(f)
            self.fasillar = fasillar_set
        except Exception as e: print(f"Veri hatası: {e}")

    def init_ui(self):
        ana_widget = QWidget()
        ana_layout = QVBoxLayout(ana_widget)
        ana_layout.setContentsMargins(0, 5, 0, 0) 
        ana_layout.setSpacing(2)
        
        ust_panel = QHBoxLayout()
        ust_panel.setContentsMargins(10, 0, 10, 5)

        self.arama_input = QLineEdit()
        self.arama_input.setPlaceholderText("Arama...")
        self.arama_input.textChanged.connect(self.ara_guvenli)
        
        self.tema_combo = QComboBox()
        self.tema_combo.addItems(self.temalar.keys())
        self.tema_combo.currentTextChanged.connect(self.tema_uygula)

        btn_artir = QPushButton("A +")
        btn_azalt = QPushButton("A -")
        btn_artir.clicked.connect(lambda: self.font_ayarla(2))
        btn_azalt.clicked.connect(lambda: self.font_ayarla(-2))

        ust_panel.addWidget(QLabel("🔍"), 0)
        ust_panel.addWidget(self.arama_input, 4)
        ust_panel.addWidget(QLabel("🎨"), 0)
        ust_panel.addWidget(self.tema_combo, 2)
        ust_panel.addWidget(btn_azalt, 0)
        ust_panel.addWidget(btn_artir, 0)
        ana_layout.addLayout(ust_panel)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: rgba(0,0,0,0.1); }")
        
        self.fasil_list = QListWidget()
        self.fasil_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.fasil_list.addItems(self.fasillar)
        self.fasil_list.itemClicked.connect(self.konu_yukle)
        
        self.konu_list = QListWidget()
        self.konu_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.konu_list.itemClicked.connect(self.hadis_yukle)
        
        self.icerik_alani = QTextBrowser()
        self.icerik_alani.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.icerik_alani.setOpenLinks(False)
        self.icerik_alani.anchorClicked.connect(self.kopyalama_tetikle)

        self.splitter.addWidget(self.panel_sarici("Fasıl", self.fasil_list))
        self.splitter.addWidget(self.panel_sarici("Konu", self.konu_list))
        self.splitter.addWidget(self.panel_sarici("Hadis Metni", self.icerik_alani))
        
        ana_layout.addWidget(self.splitter)
        self.setCentralWidget(ana_widget)
        
        st_bar = QStatusBar()
        st_bar.setMaximumHeight(20)
        self.setStatusBar(st_bar)

    def tema_uygula(self, tema_adi):
        if tema_adi not in self.temalar: return
        self.aktif_tema = tema_adi
        t = self.temalar[tema_adi]
        
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ background-color: {t['bg']}; color: {t['txt']}; }}
            #panelBaslik {{ color: {t['vrg']}; font-weight: bold; background: {t['pnl']}; padding: 5px; }}
            QListWidget {{ background-color: {t['kart']}; border: 1px solid {t['pnl']}; color: {t['txt']}; outline: none; }}
            QListWidget::item {{ padding: 8px; border-bottom: 1px solid {t['bg']}; }}
            QListWidget::item:selected {{ background-color: {t['vrg']}; color: white; }}
            QLineEdit, QComboBox {{ background: {t['kart']}; color: {t['txt']}; border: 1px solid {t['pnl']}; padding: 5px; }}
            QPushButton {{ background-color: {t['vrg']}; color: white; padding: 5px 15px; border-radius: 3px; font-weight: bold; }}
            QTextBrowser {{ background-color: {t['bg']}; border: none; }}
        """)
        if self.ekrandaki_hadisler:
            self.render_hadis_html(self.ekrandaki_hadisler)

    def konu_yukle(self, item):
        if not item: return
        self.konu_list.clear()
        secili_fasil = item.text()
        ilgili_konular = []
        for h in self.hadisler:
            if h.get('fasil') == secili_fasil:
                k = h.get('konu')
                if k and k not in ilgili_konular:
                    ilgili_konular.append(k)
        self.konu_list.addItems(ilgili_konular)

    def hadis_yukle(self, item):
        if not item: return
        secili_konu = item.text()
        ilgili_hadisler = [h for h in self.hadisler if h.get('konu') == secili_konu]
        self.render_hadis_html(ilgili_hadisler)

    def render_hadis_html(self, liste):
        self.ekrandaki_hadisler = liste 
        if not liste:
            self.icerik_alani.clear()
            return

        t = self.temalar[self.aktif_tema]
        html = f"""
        <style>
            body {{ font-family: 'Times New Roman', serif; background-color: {t['bg']}; color: {t['txt']}; padding: 10px; word-wrap: break-word; overflow-x: hidden; }}
            .hadis-kart {{ background-color: {t['kart']}; border: 1px solid {t['pnl']}; border-radius: 10px; margin-bottom: 25px; font-size: {self.mevcut_font_boyutu}px; line-height: 1.6; word-wrap: break-word; }}
            .hadis-header {{ background-color: {t['pnl']}; padding: 10px; border-radius: 10px 10px 0 0; border-bottom: 1px solid {t['bg']}; }}
            .hadis-no {{ color: {t['vrg']}; font-weight: bold; font-family: sans-serif; }}
            .kopyala-btn {{ color: {t['txt']} !important; text-decoration: none; border: 1px solid {t['vrg']}; padding: 3px 10px; font-size: 12px; border-radius: 4px; }}
            .hadis-body {{ padding: 20px; word-wrap: break-word; }}
            .ravi {{ color: {t['vrg']}; font-weight: bold; font-size: 85%; margin-bottom: 10px; }}
            .serh {{ background-color: {t['serh']}; border-left: 4px solid {t['vrg']}; padding: 15px; margin-top: 15px; font-size: 85%; word-wrap: break-word; }}
        </style>
        """
        for h in liste:
            h_id = str(h.get('_id'))
            v_hadis = self.metni_vurgula(h.get('hadis', ''))
            v_ravi = self.metni_vurgula(h.get('ravi', ''))
            s_key = str(h.get('serh1', ''))
            s_metni = self.serhler.get(s_key, "Açıklama mevcut değil.")
            
            html += f"""
            <div class="hadis-kart">
                <div class="hadis-header">
                    <table width="100%"><tr>
                        <td align="right"><span class="hadis-no">HADİS NO: {h_id}</span></td>
                        <td align="right"><a href="copy:{h_id}" class="kopyala-btn">📋 KOPYALA</a></td>
                    </tr></table>
                </div>
                <div class="hadis-body">
                    <div class="ravi">Ravi: {v_ravi}</div>
                    <div style="font-weight: bold;">{v_hadis}</div>
                    <div style="font-size: 12px; margin-top: 10px; opacity: 0.7;">Kaynak: {h.get('kaynak')}</div>
                    <div class="serh"><b>[ ŞERH ]</b><br>{s_metni}</div>
                </div>
            </div>
            """
        self.icerik_alani.setHtml(html)

    def panel_sarici(self, baslik, widget):
        kapsayici = QWidget()
        l = QVBoxLayout(kapsayici)
        l.setContentsMargins(0, 0, 0, 0) 
        lbl = QLabel(baslik.upper()); lbl.setObjectName("panelBaslik")
        l.addWidget(lbl); l.addWidget(widget)
        return kapsayici

    def ara_guvenli(self, metin):
        self.son_arama_metni = metin 
        if not metin: 
            self.icerik_alani.clear()
            return
        metin_low = metin.lower()
        res = [h for h in self.hadisler if metin_low in str(h.get('hadis','')).lower() or metin_low in str(h.get('ravi','')).lower() or metin_low == str(h.get('_id'))]
        self.render_hadis_html(res[:50])

    def metni_vurgula(self, metin):
        if not self.son_arama_metni or len(self.son_arama_metni) < 2: return metin
        try:
            pattern = re.compile(re.escape(self.son_arama_metni), re.IGNORECASE)
            return pattern.sub(lambda m: f"<span style='background-color: #ffcccc; color: black;'>{m.group(0)}</span>", metin)
        except: return metin

    def font_ayarla(self, d):
        self.mevcut_font_boyutu = max(12, min(60, self.mevcut_font_boyutu + d))
        if self.ekrandaki_hadisler: self.render_hadis_html(self.ekrandaki_hadisler)

    def oranlari_uygula(self):
        w = self.splitter.width()
        if w > 0: self.splitter.setSizes([int(w*0.2), int(w*0.2), int(w*0.6)])

    def kopyalama_tetikle(self, url):
        if url.scheme() == "copy":
            h_id = url.path()
            h = next((item for item in self.hadisler if str(item['_id']) == h_id), None)
            if h:
                txt = f"Hadis {h_id}\nRavi: {h.get('ravi')}\nMetin: {h.get('hadis')}"
                QGuiApplication.clipboard().setText(txt)
                self.statusBar().showMessage(f"Hadis {h_id} kopyalandı.", 1000)

    def son_konumu_kaydet(self):
        try:
            ayarlar = {
                "font": self.mevcut_font_boyutu, 
                "tema": self.aktif_tema,
                "fasil_index": self.fasil_list.currentRow(),
                "konu_index": self.konu_list.currentRow()
            }
            with open(self.ayar_dosyasi, "w", encoding="utf-8") as f:
                json.dump(ayarlar, f)
        except: pass

    def son_konumu_yukle(self):
        if os.path.exists(self.ayar_dosyasi):
            try:
                with open(self.ayar_dosyasi, "r", encoding="utf-8") as f:
                    a = json.load(f)
                    self.aktif_tema = a.get("tema", "Klasik Fildişi")
                    self.mevcut_font_boyutu = a.get("font", 22)
                    self.tema_combo.setCurrentText(self.aktif_tema)
                    self.tema_uygula(self.aktif_tema)
                    
                    f_idx = a.get("fasil_index", -1)
                    k_idx = a.get("konu_index", -1)
                    
                    if f_idx != -1:
                        self.fasil_list.setCurrentRow(f_idx)
                        self.konu_yukle(self.fasil_list.currentItem())
                        if k_idx != -1:
                            self.konu_list.setCurrentRow(k_idx)
                            self.hadis_yukle(self.konu_list.currentItem())
            except: pass

    def closeEvent(self, e):
        self.son_konumu_kaydet(); e.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    if os.name == 'nt':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("akademik.hadis.kutuphanesi.v11")
        
    ex = AkademikHadisApp()
    ex.show()
    sys.exit(app.exec())