import json
import os
import shutil
import calendar
from datetime import datetime

import bildirimler
from fotograf import FotografSecici
from ses import SesKaydedici

from kivy.app import App
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.uix.screenmanager import (
    ScreenManager,
    Screen,
    FadeTransition
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import (
    Color,
    RoundedRectangle,
    Rectangle,
    Line,
    StencilPush,
    StencilUse,
    StencilUnUse,
    StencilPop
)

# Makbuz (PDF) oluşturma için, hiçbir dış pakete ihtiyaç
# duymayan kendi PDF yazıcımız (mini_pdf.py) kullanılır.
# Android derlemesinde (buildozer/python-for-android) fpdf2
# ve Pillow'un neden olduğu bağımlılık çakışmalarından
# tamamen kaçınmak için tasarlandı - buildozer.spec'e ekstra
# hiçbir requirement eklemeye gerek yoktur.
from mini_pdf import MiniPDF

# Android paylaşım menüsü ARTIK plyer ÜZERİNDEN DEĞİL, doğrudan
# Android Intent API'siyle (pyjnius) açılıyor.
#
# SEBEP: plyer kütüphanesinde "share" diye bir modül/facade HİÇBİR
# ZAMAN olmadı (plyer'ın desteklediği özellik listesinde dosya
# paylaşımı yok). Bu yüzden "from plyer import share" satırı
# HER ZAMAN "cannot import name 'share' from 'plyer'" hatası
# veriyordu ve paylaşım özelliği hiç çalışmamış oluyordu -
# ekran görüntüsündeki hata tam olarak buydu.
#
# Yeni yöntem aşağıdaki makbuz_paylas() / _android_paylas()
# fonksiyonlarında, bildirimler.py'deki bildirim gönderme
# fonksiyonuyla aynı mantıkla (doğrudan pyjnius) uygulanıyor.


# =========================================================
# DOSYALAR
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ISLER_DOSYASI = os.path.join(
    BASE_DIR,
    "isler.json"
)

YERLER_DOSYASI = os.path.join(
    BASE_DIR,
    "yerler.json"
)

YEDEK_KLASORU = os.path.join(
    BASE_DIR,
    "yedekler"
)

SES_DOSYASI = os.path.join(
    BASE_DIR,
    "acilis_sesi.mp3"
)

# İlk kurulumda kaydedilen Firma/Kişi adı
# ve telefon numarası burada saklanır.
AYAR_DOSYASI = os.path.join(
    BASE_DIR,
    "ayarlar.json"
)

# Oluşturulan PDF makbuzlar bu klasöre
# kaydedilir.
MAKBUZ_KLASORU = os.path.join(
    BASE_DIR,
    "makbuzlar"
)

# Firma logosu. Sabit bir dosyadır (logo.png), ayarlardan
# değiştirilemez; uygulama klasöründe bu isimle bulunur.
LOGO_DOSYASI = os.path.join(
    BASE_DIR,
    "logo.png"
)


# =========================================================
# TEMA
# =========================================================

ARKA = (0.12, 0.13, 0.15, 1)
KART = (0.20, 0.21, 0.24, 1)

BUTON = (0.10, 0.12, 0.16, 1)
BUTON_BASILDI = (0.16, 0.19, 0.24, 1)
BUTON_METIN = (0.08, 0.09, 0.11, 1)

BEYAZ = (0.96, 0.97, 0.98, 1)
SOLUK = (0.70, 0.72, 0.76, 1)

GIRIS = (0.94, 0.95, 0.97, 1)
GIRIS_METIN = (0.08, 0.09, 0.11, 1)

YESIL = (0.20, 0.65, 0.30, 1)
KIRMIZI = (0.85, 0.20, 0.20, 1)
SARI = (0.96, 0.78, 0.10, 1)
SARI_METIN = (0.10, 0.08, 0.02, 1)

# ---- ANA MENÜ (yeni tasarım) ----
KOYU_ZEMIN = (0.055, 0.075, 0.10, 1)
KART_KOYU = (0.09, 0.11, 0.145, 1)
KART_CIZGI = (1, 1, 1, 0.06)

KAR_KART_KOYU = (0.015, 0.16, 0.12, 1)
KAR_KART_ACIK = (0.03, 0.42, 0.28, 1)
KAR_YAZI = (0.24, 0.95, 0.62, 1)

ALACAK_KART_KOYU = (0.20, 0.05, 0.06, 1)
ALACAK_KART_ACIK = (0.46, 0.10, 0.13, 1)
ALACAK_YAZI = (1.0, 0.45, 0.45, 1)

MENU_IKON_RENKLERI = {
    "malzeme": (0.28, 0.42, 0.62, 1),
    "yeni": (0.24, 0.48, 0.42, 1),
    "gelir": (0.62, 0.52, 0.30, 1),
    "rapor": (0.44, 0.38, 0.56, 1),
    "gecmis": (0.58, 0.32, 0.34, 1),
    "ayar": (0.38, 0.42, 0.48, 1)
}

# ---- YENİ İŞ / İŞ DETAYI (koyu kart tabanlı form tasarımı) ----
# Sadece YeniIs ve IsDetay ekranlarında kullanılır; diğer
# ekranlardaki mevcut (açık renkli) giris()/Spinner stilleri
# değişmeden kalır.
FORM_GIRIS = (0.13, 0.15, 0.19, 1)
FORM_GIRIS_CIZGI = (1, 1, 1, 0.08)
FORM_GIRIS_YAZI = (0.96, 0.97, 0.98, 1)
FORM_GIRIS_ONER = (0.52, 0.55, 0.60, 1)

GIDER_IKONLARI = {
    "Yakıt": "⛽",
    "Malzeme Özel": "🧰",
    "Gıda": "🍔",
    "Yardımcı Eleman": "🧑‍🔧"
}

# Yeni (henüz kullanıcı tarafından seçilmemiş) bir gider
# satırında Spinner'da görünen yer tutucu metin. Kasıtlı
# olarak GIDER_KATEGORILERI listesinde YER ALMAZ; böylece
# kaydetme sırasında "hâlâ bu metinse kullanıcı seçim
# yapmamış demektir" diye ayırt edilebilir.
GIDER_PLACEHOLDER = "Gider Seç"


# =========================================================
# JSON
# =========================================================

def oku(dosya, varsayilan=None):

    if varsayilan is None:
        varsayilan = []

    if not os.path.exists(dosya):
        return varsayilan

    try:
        with open(
            dosya,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except Exception:
        return varsayilan


def kaydet(dosya, veri):

    with open(
        dosya,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            veri,
            f,
            ensure_ascii=False,
            indent=4
        )


def para(deger):

    try:

        if isinstance(deger, str):
            deger = deger.replace(",", ".")

        return float(deger or 0)

    except Exception:
        return 0.0


# =========================================================
# AYARLAR (FİRMA / TELEFON)
# =========================================================

def ayarlari_oku():

    return oku(
        AYAR_DOSYASI,
        {}
    )


def ayarlari_kaydet(veri):

    kaydet(
        AYAR_DOSYASI,
        veri
    )


def telefon_formatla(ham):

    # Sadece rakamları al, en fazla 11
    # hane (0532 123 45 67).
    rakamlar = "".join(
        ch for ch in (ham or "")
        if ch.isdigit()
    )[:11]

    parcalar = []

    if len(rakamlar) > 0:
        parcalar.append(rakamlar[0:4])

    if len(rakamlar) > 4:
        parcalar.append(rakamlar[4:7])

    if len(rakamlar) > 7:
        parcalar.append(rakamlar[7:9])

    if len(rakamlar) > 9:
        parcalar.append(rakamlar[9:11])

    return " ".join(
        p for p in parcalar if p
    )


class TelefonInput(TextInput):

    # Telefon numarasını "0532 123 45 67" biçiminde
    # canlı olarak biçimlendiren giriş kutusu.
    #
    # NOT: Bu biçimlendirme kasıtlı olarak text=
    # property'sine bind() ile DEĞİL, insert_text /
    # do_backspace metodlarını override ederek yapılır.
    # TextInput.text'i bir "text değişti" callback'i
    # içinden değiştirmek Kivy'de imleç/satır durumunun
    # bozulmasına ve girişin belirli bir haneden sonra
    # tıkanmasına yol açar (bilinen bir Kivy davranışı).

    def __init__(
        self,
        hint="",
        **kwargs
    ):

        kwargs.setdefault(
            "multiline", False
        )

        kwargs.setdefault(
            "size_hint_y", None
        )

        kwargs.setdefault(
            "height", dp(58)
        )

        super().__init__(
            hint_text=hint,
            font_size=19,
            padding=[
                dp(13),
                dp(13)
            ],
            background_normal="",
            background_color=GIRIS,
            foreground_color=GIRIS_METIN,
            hint_text_color=(
                0.42,
                0.44,
                0.48,
                1
            ),
            cursor_color=GIRIS_METIN,
            **kwargs
        )

    def insert_text(
        self,
        substring,
        from_undo=False
    ):

        mevcut = "".join(
            ch for ch in self.text
            if ch.isdigit()
        )

        yeni = "".join(
            ch for ch in substring
            if ch.isdigit()
        )

        rakamlar = (mevcut + yeni)[:11]

        self.text = telefon_formatla(
            rakamlar
        )

        self.cursor = (
            len(self.text), 0
        )

    def do_backspace(
        self,
        from_undo=False,
        mode="bkspc"
    ):

        rakamlar = "".join(
            ch for ch in self.text
            if ch.isdigit()
        )[:-1]

        self.text = telefon_formatla(
            rakamlar
        )

        self.cursor = (
            len(self.text), 0
        )


def telefon_girisi(hint=""):

    return TelefonInput(hint=hint)


# =========================================================
# BUTON
# =========================================================

class YuvarlakButon(Button):

    def __init__(
        self,
        ozel_renk=None,
        **kwargs
    ):

        self.ozel_renk = ozel_renk

        kwargs.setdefault(
            "background_normal",
            ""
        )

        kwargs.setdefault(
            "background_color",
            (0, 0, 0, 0)
        )

        kwargs.setdefault(
            "color",
            BUTON_METIN
        )

        kwargs.setdefault(
            "halign",
            "center"
        )

        kwargs.setdefault(
            "valign",
            "middle"
        )

        super().__init__(**kwargs)

        with self.canvas.before:

            self._renk = Color(
                *(
                    self.ozel_renk
                    if self.ozel_renk
                    else BUTON
                )
            )

            self._arka = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(14)]
            )

            self._cerceve = None

            if not self.ozel_renk:

                Color(0.20, 0.85, 0.55, 0.35)

                self._cerceve = Line(
                    rounded_rectangle=(
                        self.x, self.y,
                        self.width, self.height,
                        dp(14)
                    ),
                    width=dp(1.2)
                )

        self.bind(
            pos=self._guncelle,
            size=self._guncelle,
            state=self._durum
        )

    def _guncelle(self, *args):

        self._arka.pos = self.pos
        self._arka.size = self.size

        if self._cerceve:

            self._cerceve.rounded_rectangle = (
                self.x, self.y,
                self.width, self.height,
                dp(14)
            )

    def _durum(self, *args):

        if self.state == "down":

            if self.ozel_renk:

                self._renk.rgba = tuple(
                    max(0, x * 0.8)
                    if i < 3
                    else x
                    for i, x
                    in enumerate(self.ozel_renk)
                )

            else:

                self._renk.rgba = (
                    BUTON_BASILDI
                )

        else:

            self._renk.rgba = (
                self.ozel_renk
                if self.ozel_renk
                else BUTON
            )

    def renk_degistir(self, yeni_renk):

        self.ozel_renk = yeni_renk

        self._renk.rgba = (
            yeni_renk
            if yeni_renk
            else BUTON
        )


def buton(
    yazi,
    renk=None,
    yukseklik=58,
    font=18
):

    ekstra = {}

    if renk is None:

        # Renk verilmemiş (varsayılan/gri) butonlar artık
        # koyu zeminli; yazı bu yüzden beyaz olmalı. Özel
        # renkli (kırmızı/sarı/yeşil) butonlar eskisi gibi
        # BUTON_METIN (koyu yazı) kullanmaya devam eder.
        ekstra["color"] = BEYAZ

    return YuvarlakButon(
        text=yazi,
        size_hint_y=None,
        height=dp(yukseklik),
        font_size=font,
        ozel_renk=renk,
        **ekstra
    )


# =========================================================
# UYARI POPUP
# =========================================================
#
# Basit, tek-butonlu bir "Tamam" uyarı penceresi. Kaydetme
# gibi işlemlerden önce eksik/hatalı bir alan olduğunda
# kullanıcıyı bilgilendirmek için kullanılır (ör. gider türü
# seçilmeden tutar girilmesi, aşırı sayıda ses kaydı vb).

def uyari_popup(
    mesaj,
    baslik="Uyarı"
):

    icerik = BoxLayout(
        orientation="vertical",
        padding=dp(16),
        spacing=dp(12)
    )

    etiket = Label(
        text=mesaj,
        font_size=16,
        color=BEYAZ,
        halign="center",
        valign="middle"
    )

    etiket.bind(
        size=lambda obj, val:
        setattr(obj, "text_size", val)
    )

    icerik.add_widget(etiket)

    tamam_btn = buton(
        "TAMAM",
        renk=SARI,
        yukseklik=50
    )

    icerik.add_widget(tamam_btn)

    popup = Popup(
        title=baslik,
        content=icerik,
        size_hint=(.82, None),
        height=dp(210),
        separator_color=SARI,
        title_color=BEYAZ,
        background_color=(
            0.09, 0.11, 0.145, 1
        )
    )

    tamam_btn.bind(
        on_press=popup.dismiss
    )

    popup.open()

    return popup


# =========================================================
# KIRMIZI KUTU
# =========================================================

class KirmiziKutu(Label):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        with self.canvas.before:

            self._renk = Color(*KIRMIZI)

            self._arka = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(14)]
            )

        self.bind(
            pos=self._guncelle,
            size=self._guncelle
        )

    def _guncelle(self, *args):

        self._arka.pos = self.pos
        self._arka.size = self.size

    def renk_ayarla(self, renk):

        self._renk.rgba = renk


# =========================================================
# GİRİŞ
# =========================================================

def giris(
    hint="",
    multiline=False,
    height=58,
    input_filter=None
):

    return TextInput(
        hint_text=hint,
        multiline=multiline,
        input_filter=input_filter,
        size_hint_y=None,
        height=dp(height),
        font_size=19,
        padding=[
            dp(13),
            dp(13)
        ],
        background_normal="",
        background_color=GIRIS,
        foreground_color=GIRIS_METIN,
        hint_text_color=(
            0.42,
            0.44,
            0.48,
            1
        ),
        cursor_color=GIRIS_METIN
    )


def baslik(
    yazi,
    boyut=25
):

    return Label(
        text=yazi,
        font_size=boyut,
        bold=True,
        color=BEYAZ,
        size_hint_y=None,
        height=dp(52)
    )


def etiketli_alan(
    yazi,
    alan
):

    kutu = BoxLayout(
        orientation="vertical",
        spacing=dp(2),
        size_hint_y=None
    )

    kutu.bind(
        minimum_height=
        kutu.setter("height")
    )

    etiket = Label(
        text=yazi,
        font_size=14,
        color=SOLUK,
        bold=True,
        size_hint_y=None,
        height=dp(20),
        halign="left",
        valign="middle"
    )

    etiket.bind(
        size=lambda obj, val:
        setattr(
            obj,
            "text_size",
            val
        )
    )

    kutu.add_widget(etiket)
    kutu.add_widget(alan)

    return kutu


def etiketli_alan_tarihli(
    yazi,
    alan,
    tarih_alani
):
    # "Alınan" gibi hem bir tutar girişi hem de o tutarın
    # alındığı tarihi seçen bir takvim alanı olan satırlar
    # için: üstte etiket, altında tutar kutusu ve hemen
    # yanında (sağında) tarih seçme kutusu yan yana durur.

    kutu = BoxLayout(
        orientation="vertical",
        spacing=dp(2),
        size_hint_y=None
    )

    kutu.bind(
        minimum_height=
        kutu.setter("height")
    )

    etiket = Label(
        text=yazi,
        font_size=14,
        color=SOLUK,
        bold=True,
        size_hint_y=None,
        height=dp(20),
        halign="left",
        valign="middle"
    )

    etiket.bind(
        size=lambda obj, val:
        setattr(
            obj,
            "text_size",
            val
        )
    )

    kutu.add_widget(etiket)

    satir = BoxLayout(
        size_hint_y=None,
        height=dp(58),
        spacing=dp(7)
    )

    alan.size_hint_x = 0.5
    tarih_alani.size_hint_x = 0.5

    satir.add_widget(alan)
    satir.add_widget(tarih_alani)

    kutu.add_widget(satir)

    return kutu


# =========================================================
# KOYU GİRİŞ KUTUSU (Yeni İş / İş Detayı yeni tasarımı)
# =========================================================
#
# giris()'in koyu temalı karşılığı. Yuvarlak köşeli, koyu
# zeminli, açık renk yazılı bir kutu çizer (YuvarlakButon'daki
# çizim yöntemiyle aynı mantık). SADECE YeniIs ve IsDetay
# ekranlarında kullanılır; diğer ekranlar hâlâ giris()'i
# (açık renkli kutu) kullanmaya devam eder, bu yüzden onlar
# etkilenmez.

class TextInputKoyu(TextInput):

    def __init__(self, **kwargs):

        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_active", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("foreground_color", FORM_GIRIS_YAZI)
        kwargs.setdefault("cursor_color", FORM_GIRIS_YAZI)
        kwargs.setdefault("hint_text_color", FORM_GIRIS_ONER)

        super().__init__(**kwargs)

        with self.canvas.before:

            Color(*FORM_GIRIS)

            self._form_zemin = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )

            Color(*FORM_GIRIS_CIZGI)

            self._form_cizgi = Line(
                rounded_rectangle=(
                    self.x, self.y,
                    self.width, self.height,
                    dp(12)
                ),
                width=1.1
            )

        self.bind(
            pos=self._form_guncelle,
            size=self._form_guncelle
        )

    def _form_guncelle(self, *args):

        self._form_zemin.pos = self.pos
        self._form_zemin.size = self.size

        self._form_cizgi.rounded_rectangle = (
            self.x, self.y,
            self.width, self.height,
            dp(12)
        )


def giris_koyu(
    hint="",
    multiline=False,
    height=58,
    input_filter=None
):

    return TextInputKoyu(
        hint_text=hint,
        multiline=multiline,
        input_filter=input_filter,
        size_hint_y=None,
        height=dp(height),
        font_size=17,
        padding=[
            dp(14),
            dp(13)
        ]
    )


def spinner_koyu_stili(spinner):
    # Mevcut bir Spinner'ı (oluşturulduktan sonra) koyu
    # temaya çevirir; YeniIs/IsDetay'daki Spinner'lar için.
    spinner.background_normal = ""
    spinner.background_color = FORM_GIRIS
    spinner.color = FORM_GIRIS_YAZI
    return spinner


# =========================================================
# BÖLÜM KARTI
# =========================================================
#
# İş ekleme / iş detayı ekranlarındaki uzun, tek parça form
# artık başlıklı bölümlere (Genel Bilgiler / Ekler / Mali
# Bilgiler / Diğer Giderler / Malzemeler gibi) ayrılıyor. Bu
# fonksiyon, koyu zeminli, yuvarlak köşeli, üstünde ikon +
# başlık olan bir kart döndürür; ekrandaki her bölüm bu kartın
# içine eklenir. Amaç: uzun formu daha temiz ve derli toplu
# göstermek. Hiçbir alan/buton kaldırılmıyor, sadece görsel
# olarak gruplanıyor.

def bolum_karti(baslik_yazi):

    kart = BoxLayout(
        orientation="vertical",
        spacing=dp(10),
        padding=[dp(12), dp(12), dp(12), dp(14)],
        size_hint_y=None
    )

    kart.bind(
        minimum_height=
        kart.setter("height")
    )

    with kart.canvas.before:

        Color(*KART_KOYU)

        kart._zemin = RoundedRectangle(
            pos=kart.pos,
            size=kart.size,
            radius=[dp(16)]
        )

        Color(*KART_CIZGI)

        kart._cizgi = Line(
            rounded_rectangle=(
                kart.x,
                kart.y,
                kart.width,
                kart.height,
                dp(16)
            ),
            width=1.1
        )

    def _kart_guncelle(obj, val):

        obj._zemin.pos = obj.pos
        obj._zemin.size = obj.size

        obj._cizgi.rounded_rectangle = (
            obj.x,
            obj.y,
            obj.width,
            obj.height,
            dp(16)
        )

    kart.bind(
        pos=_kart_guncelle,
        size=_kart_guncelle
    )

    baslik_satir = BoxLayout(
        size_hint_y=None,
        height=dp(30),
        spacing=dp(8)
    )

    # Bölüm başlığının solunda ince kırmızı bir vurgu
    # çubuğu (yeni tasarımdaki kırmızı aksan çizgisiyle
    # uyumlu olması için).
    aksan = Widget(
        size_hint_x=None,
        width=dp(4)
    )

    with aksan.canvas.before:

        Color(*KIRMIZI)

        aksan._cubuk = RoundedRectangle(
            pos=aksan.pos,
            size=aksan.size,
            radius=[dp(2)]
        )

    def _aksan_guncelle(obj, val):
        obj._cubuk.pos = obj.pos
        obj._cubuk.size = obj.size

    aksan.bind(
        pos=_aksan_guncelle,
        size=_aksan_guncelle
    )

    baslik_satir.add_widget(aksan)

    baslik_lbl = Label(
        text=baslik_yazi,
        font_size=18,
        bold=True,
        color=BEYAZ,
        halign="left",
        valign="middle",
        size_hint_y=None,
        height=dp(30)
    )

    baslik_lbl.bind(
        size=lambda obj, val:
        setattr(obj, "text_size", val)
    )

    baslik_satir.add_widget(baslik_lbl)

    kart.add_widget(baslik_satir)

    return kart


# =========================================================
# HESAPLAMA
# =========================================================

def toplam_malzeme(is_):

    toplam = 0

    for m in is_.get(
        "malzemeler",
        []
    ):

        toplam += para(
            m.get("fiyat", 0)
        )

    return toplam


def is_durumu(is_):

    return is_.get(
        "durum",
        "Devam ediyor"
    )


def is_fiilen_bitti(is_):

    # "Durum" alanı elle "Bitti" seçilmemiş olsa bile,
    # alınan tutar ile işçilik tutarı birbirine eşit ve
    # sıfırdan farklıysa (ör. 5000 - 5000, 0 - 0 hariç)
    # iş arka planda bitti kabul edilir. Ekrandaki "Durum"
    # yazısı değiştirilmez; sadece kâr/tahsilat
    # hesaplarına dahil edilip edilmeyeceğine karar verilir.

    if is_durumu(is_) == "Bitti":
        return True

    iscilik = para(
        is_.get("iscilik", 0)
    )

    alinan = para(
        is_.get("gelir", 0)
    )

    if (
        iscilik > 0
        and alinan > 0
        and iscilik == alinan
    ):
        return True

    return False


def alinacak_hesapla(
    malzemeli,
    iscilik,
    malzeme_toplami,
    alinan
):
    # Malzemeli işlerde malzeme tutarı zaten
    # işçilik rakamına dahil edilmiş kabul
    # edilir; bu yüzden alınacak tutara
    # tekrar eklenmez. Malzemesiz işlerde
    # malzeme tutarı ayrıca eklenir.

    if malzemeli:

        return iscilik - alinan

    return (
        iscilik
        + malzeme_toplami
        - alinan
    )


def bu_ay_mi(
    tarih,
    yil=None,
    ay=None
):

    try:

        tarih = datetime.strptime(
            tarih,
            "%d.%m.%Y %H:%M"
        )

        if yil is None or ay is None:

            simdi = datetime.now()

            yil = simdi.year
            ay = simdi.month

        return (
            tarih.month == ay
            and
            tarih.year == yil
        )

    except Exception:
        return False


def kayit_tarihi(baslangic_metni):

    try:

        secilen = datetime.strptime(
            baslangic_metni.strip(),
            "%d.%m.%Y"
        )

        saat = datetime.now().strftime(
            "%H:%M"
        )

        return (
            secilen.strftime("%d.%m.%Y")
            + " "
            + saat
        )

    except Exception:

        return datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        )


def hesaplar(
    yil=None,
    ay=None
):

    isler = oku(
        ISLER_DOSYASI
    )

    ay_gelir = 0
    ay_gider = 0
    ay_malzeme = 0
    ay_malzeme_kar = 0
    ay_iscilik = 0
    ay_kalan_tahsilat = 0
    ay_kalan_isler = []

    # ---- Gerçek (durum bakılmaksızın) aylık toplamlar ----
    # Gelir/Gider ekranındaki 2x2 kartlar için: iş "Bitti"
    # olsun ya da olmasın, o ay içinde fiilen alınan/harcanan
    # tutarları gösterir. Ana ekrandaki kazanç kartları ve
    # aşağıdaki "ay_net" / "ay_alinacak" (kâr / kalan tahsilat)
    # bu bloktan ETKİLENMEZ; onlar hâlâ sadece bitmiş işlerden
    # hesaplanır.
    ay_gelir_gercek = 0
    ay_gider_gercek = 0
    ay_malzeme_gercek = 0
    ay_iscilik_gercek = 0

    toplam_gelir = 0
    toplam_gider = 0
    toplam_malzeme_para = 0
    toplam_malzeme_kar = 0
    toplam_iscilik = 0

    for is_ in isler:

        gelir = para(
            is_.get("gelir", 0)
        )

        gider = para(
            is_.get("gider", 0)
        )

        malzeme = toplam_malzeme(
            is_
        )

        malzemeli = is_.get(
            "malzemeli",
            True
        )

        malzeme_kar = (
            malzeme
            if malzemeli
            else 0
        )

        iscilik = para(
            is_.get("iscilik", 0)
        )

        bu_ay = bu_ay_mi(
            is_.get("tarih", ""),
            yil,
            ay
        )

        # Durum ne olursa olsun bu ay için gerçek
        # tahsilat / gider / malzeme / işçilik toplamı.
        if bu_ay:

            ay_gelir_gercek += gelir
            ay_gider_gercek += gider
            ay_malzeme_gercek += malzeme
            ay_iscilik_gercek += iscilik

        # Sadece "Bitti" seçilen ya da alınan/işçilik
        # eşitliğiyle arka planda bitti sayılan işler
        # kâr / tahsilat hesabına girer.
        if not is_fiilen_bitti(is_):
            continue

        # Bu işten kalan (henüz tahsil edilmemiş) tutar
        alinacak = alinacak_hesapla(
            malzemeli,
            iscilik,
            malzeme,
            gelir
        )

        toplam_gelir += gelir
        toplam_gider += gider
        toplam_malzeme_para += malzeme
        toplam_malzeme_kar += malzeme_kar
        toplam_iscilik += iscilik

        if bu_ay:

            ay_gelir += gelir
            ay_gider += gider
            ay_malzeme += malzeme
            ay_malzeme_kar += malzeme_kar
            ay_iscilik += iscilik

            if alinacak > 0:

                ay_kalan_tahsilat += alinacak

                ay_kalan_isler.append({
                    "is_adi": is_.get(
                        "is_adi",
                        "İsimsiz İş"
                    ),
                    "tutar": alinacak
                })

    return {

        # "ay_gelir" artık sadece bitmiş işlerden
        # yapılan tahsilatı ifade eder. Ana ekran
        # kazanç kartları bunu kullanmaya devam eder.
        "ay_gelir": ay_gelir,

        "ay_gider": ay_gider,

        "ay_malzeme": ay_malzeme,

        "ay_iscilik": ay_iscilik,

        # Durum ne olursa olsun (bitmiş/bitmemiş fark
        # etmeksizin) bu ay içindeki gerçek tutarlar.
        # Gelir/Gider ekranındaki 2x2 kartlar bunları
        # kullanır.
        "ay_gelir_gercek": ay_gelir_gercek,
        "ay_gider_gercek": ay_gider_gercek,
        "ay_malzeme_gercek": ay_malzeme_gercek,
        "ay_iscilik_gercek": ay_iscilik_gercek,

        # Geriye dönük uyumluluk için isim korunuyor,
        # artık sadece bitmiş işlerin kalan
        # (tahsil edilmemiş) tutarlarının toplamı.
        "ay_alinacak": ay_kalan_tahsilat,

        # Kalan tahsilatı olan bitmiş işlerin listesi:
        # [{"is_adi": ..., "tutar": ...}, ...]
        "ay_kalan_isler": ay_kalan_isler,

        "ay_net":
            ay_gelir
            - ay_gider
            - ay_malzeme_kar,

        "toplam_gelir":
            toplam_gelir,

        "toplam_gider":
            toplam_gider,

        "toplam_malzeme":
            toplam_malzeme_para,

        "toplam_iscilik":
            toplam_iscilik,

        "toplam_net":
            toplam_gelir
            - toplam_gider
            - toplam_malzeme_kar
    }


# =========================================================
# KLAVYE
# =========================================================

def klavye_uyumu(
    scroll,
    widget
):

    def odak(
        instance,
        value
    ):

        if value:

            Clock.schedule_once(
                lambda dt:
                scroll.scroll_to(
                    widget,
                    padding=dp(150)
                ),
                0.15
            )

    widget.bind(
        focus=odak
    )


# =========================================================
# ÜST BAŞLIK
# =========================================================

def ust_baslik(
    screen,
    yazi,
    geri_ekran
):

    satir = BoxLayout(
        size_hint_y=None,
        height=dp(62),
        spacing=dp(8)
    )

    geri = buton(
        "←",
        renk=KIRMIZI,
        yukseklik=56,
        font=30
    )

    geri.size_hint_x = None
    geri.width = dp(58)

    geri.bind(
        on_press=lambda *_:
        setattr(
            screen.manager,
            "current",
            geri_ekran
        )
    )

    bas = Label(
        text=yazi,
        font_size=25,
        bold=True,
        color=BEYAZ,
        halign="left",
        valign="middle"
    )

    bas.bind(
        size=lambda obj, val:
        setattr(
            obj,
            "text_size",
            val
        )
    )

    satir.add_widget(geri)
    satir.add_widget(bas)

    return satir


# =========================================================
# TAKVİM
# =========================================================

class TakvimPopup(Popup):

    AY_ISIMLERI = [
        "Ocak",
        "Şubat",
        "Mart",
        "Nisan",
        "Mayıs",
        "Haziran",
        "Temmuz",
        "Ağustos",
        "Eylül",
        "Ekim",
        "Kasım",
        "Aralık"
    ]

    HAFTA = [
        "Pzt",
        "Sal",
        "Çar",
        "Per",
        "Cum",
        "Cmt",
        "Paz"
    ]

    def __init__(
        self,
        hedef,
        **kwargs
    ):

        self.hedef = hedef

        bugun = datetime.now()

        self.yil = bugun.year
        self.ay = bugun.month

        try:

            mevcut = datetime.strptime(
                hedef.text.strip(),
                "%d.%m.%Y"
            )

            self.yil = mevcut.year
            self.ay = mevcut.month

        except Exception:
            pass

        super().__init__(
            title="Tarih Seç",
            size_hint=(0.94, 0.82),
            auto_dismiss=True,
            **kwargs
        )

        self.govde = BoxLayout(
            orientation="vertical",
            padding=dp(8),
            spacing=dp(6)
        )

        self.content = self.govde

        self.guncelle()

    def guncelle(self):

        self.govde.clear_widgets()

        ust = BoxLayout(
            size_hint_y=None,
            height=dp(56),
            spacing=dp(5)
        )

        onceki = buton(
            "‹",
            yukseklik=54,
            font=30
        )

        onceki.size_hint_x = .18

        onceki.bind(
            on_press=self.onceki_ay
        )

        ay_baslik = Label(
            text=(
                f"{self.AY_ISIMLERI[self.ay - 1]} "
                f"{self.yil}"
            ),
            font_size=20,
            bold=True,
            color=BEYAZ
        )

        sonraki = buton(
            "›",
            yukseklik=54,
            font=30
        )

        sonraki.size_hint_x = .18

        sonraki.bind(
            on_press=self.sonraki_ay
        )

        ust.add_widget(onceki)
        ust.add_widget(ay_baslik)
        ust.add_widget(sonraki)

        self.govde.add_widget(ust)

        hafta = GridLayout(
            cols=7,
            size_hint_y=None,
            height=dp(35)
        )

        for gun in self.HAFTA:

            hafta.add_widget(
                Label(
                    text=gun,
                    font_size=14,
                    bold=True,
                    color=BEYAZ
                )
            )

        self.govde.add_widget(hafta)

        grid = GridLayout(
            cols=7,
            spacing=dp(3),
            size_hint_y=None,
            height=dp(6 * 49)
        )

        ilk_gun, gun_sayisi = calendar.monthrange(
            self.yil,
            self.ay
        )

        for _ in range(ilk_gun):

            grid.add_widget(
                Label(text="")
            )

        for gun in range(
            1,
            gun_sayisi + 1
        ):

            b = buton(
                str(gun),
                yukseklik=46,
                font=16
            )

            b.bind(
                on_press=lambda _, g=gun:
                self.gun_sec(g)
            )

            grid.add_widget(b)

        kalan = 42 - (
            ilk_gun + gun_sayisi
        )

        for _ in range(kalan):

            grid.add_widget(
                Label(text="")
            )

        self.govde.add_widget(grid)

        kapat = buton(
            "KAPAT",
            yukseklik=50,
            font=17
        )

        kapat.bind(
            on_press=lambda *_:
            self.dismiss()
        )

        self.govde.add_widget(kapat)

    def onceki_ay(self, instance):

        self.ay -= 1

        if self.ay == 0:
            self.ay = 12
            self.yil -= 1

        self.guncelle()

    def sonraki_ay(self, instance):

        self.ay += 1

        if self.ay == 13:
            self.ay = 1
            self.yil += 1

        self.guncelle()

    def gun_sec(self, gun):

        self.hedef.text = (
            f"{gun:02d}."
            f"{self.ay:02d}."
            f"{self.yil}"
        )

        self.dismiss()


class TarihInput(TextInputKoyu):

    # Yalnızca YeniIs / IsDetay'da kullanıldığı için
    # koyu temalı TextInputKoyu'dan miras alır; böylece
    # tarih kutuları da diğer alanlarla aynı yeni
    # tasarımda (koyu zemin, açık yazı) görünür.

    def __init__(
        self,
        on_tarih=None,
        **kwargs
    ):

        self.on_tarih = on_tarih

        super().__init__(
            readonly=True,
            multiline=False,
            **kwargs
        )

        self.font_size = 19

        self.padding = [
            dp(13),
            dp(13)
        ]

    def on_touch_down(
        self,
        touch
    ):

        if self.collide_point(
            *touch.pos
        ):

            if self.on_tarih:
                self.on_tarih(self)

            return True

        return super().on_touch_down(touch)


# =========================================================
# AÇILIŞ EKRANI (SPLASH)
# =========================================================

class NabizHalkasi(Widget):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        with self.canvas:

            self._renk = Color(1, 1, 1, 0)

            self._cember = Line(
                circle=(0, 0, 0),
                width=dp(2)
            )

        self._devam_olay = None

        self.bind(
            pos=self._guncelle,
            size=self._guncelle
        )

    def _guncelle(self, *args):

        self._cember.circle = (
            self.center_x,
            self.center_y,
            self.width / 2
        )

    def baslat(self, gecikme=0):

        Clock.schedule_once(
            lambda dt: self._dongu(),
            gecikme
        )

    def _dongu(self):

        self.size = (dp(24), dp(24))
        self._renk.a = .55

        Animation(
            size=(dp(230), dp(230)),
            duration=1.7,
            t="out_quad"
        ).start(self)

        Animation(
            a=0,
            duration=1.7,
            t="out_quad"
        ).start(self._renk)

        self._devam_olay = Clock.schedule_once(
            lambda dt: self._dongu(),
            1.7
        )

    def durdur(self):

        if self._devam_olay:
            self._devam_olay.cancel()

        Animation.cancel_all(self)
        Animation.cancel_all(self._renk)


# =========================================================
# MAKBUZ (PDF) OLUŞTURMA
# =========================================================

# MiniPDF, standart PDF fontlarını (Helvetica) kullanır ve
# bu fontlar Türkçe karakterleri (ş, ğ, ı, ö, ü, ç) doğru
# gösteremez. Bu yüzden makbuz metinlerinde bu karakterler
# en yakın ASCII karşılığına çevrilir - PDF'in her cihazda
# (özel font aramaya/gömmeye gerek kalmadan) bire bir aynı
# görünmesini sağlar.
_TURKCE_CEVIRI = str.maketrans({
    "ş": "s", "Ş": "S",
    "ğ": "g", "Ğ": "G",
    "ı": "i", "İ": "I",
    "ö": "o", "Ö": "O",
    "ü": "u", "Ü": "U",
    "ç": "c", "Ç": "C",
})


def _mt(metin, unicode_destekli=False):

    metin = str(
        metin
        if metin is not None
        else ""
    )

    if unicode_destekli:
        return metin

    return metin.translate(
        _TURKCE_CEVIRI
    )


def makbuz_no_uret():

    ayar = ayarlari_oku()

    son_no = int(
        ayar.get(
            "son_makbuz_no",
            0
        )
    ) + 1

    ayar["son_makbuz_no"] = son_no

    ayarlari_kaydet(ayar)

    return f"MK-{son_no:06d}"


def makbuz_pdf_olustur(is_):

    ayar = ayarlari_oku()

    firma_adi = ayar.get(
        "firma_adi", ""
    )

    firma_telefon = ayar.get(
        "telefon", ""
    )

    iscilik = para(
        is_.get("iscilik", 0)
    )

    malzeme_toplami = toplam_malzeme(
        is_
    )

    malzemeli = is_.get(
        "malzemeli", True
    )

    alinan = para(
        is_.get("gelir", 0)
    )

    toplam = (
        iscilik
        if malzemeli
        else iscilik + malzeme_toplami
    )

    kalan = alinacak_hesapla(
        malzemeli,
        iscilik,
        malzeme_toplami,
        alinan
    )

    if kalan <= 0.009:
        odeme_durumu = "TAMAMI ÖDENDİ"
        durum_renk = (30, 140, 60)
    elif alinan > 0:
        odeme_durumu = "KISMİ ÖDENDİ"
        durum_renk = (200, 140, 10)
    else:
        odeme_durumu = "ÖDENME BEKLİYOR"
        durum_renk = (190, 40, 40)

    makbuz_numarasi = makbuz_no_uret()

    tarih = datetime.now().strftime(
        "%d.%m.%Y %H:%M"
    )

    pdf = MiniPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.set_auto_page_break(
        auto=True, margin=18
    )

    pdf.add_page()

    # MiniPDF sadece standart Helvetica fontunu içerdiği için
    # Türkçe karakterler her zaman ASCII karşılığına çevrilir
    # (bkz. _mt / _TURKCE_CEVIRI).
    yazi_tipi = "helvetica"

    def T(metin):
        return _mt(metin)

    sol = 15
    sag = 195

    # NOT: Logo/görsel ekleme özelliği kaldırıldı - MiniPDF
    # sıfır bağımlılık hedefiyle görsel gömme desteklemiyor.
    # Makbuz artık her zaman sadece metinle (firma adı,
    # telefon vb.) başlıyor.
    metin_x = sol

    pdf.set_xy(metin_x, 14)
    pdf.set_font(yazi_tipi, "B", 18)
    pdf.set_text_color(25, 25, 30)
    pdf.cell(
        0, 8,
        T(firma_adi or "Firma / Kişi Adı"),
        ln=1
    )

    if firma_telefon:

        pdf.set_x(metin_x)
        pdf.set_font(yazi_tipi, "", 11)
        pdf.set_text_color(90, 90, 95)
        pdf.cell(
            0, 6,
            T("Tel: " + firma_telefon),
            ln=1
        )

    # ---- MAKBUZ başlığı + no/tarih ----
    pdf.set_xy(sol, 34)
    pdf.set_draw_color(220, 220, 224)
    pdf.line(sol, 33, sag, 33)

    pdf.set_font(yazi_tipi, "B", 22)
    pdf.set_text_color(20, 20, 24)
    pdf.set_xy(sol, 37)
    pdf.cell(0, 10, T("MAKBUZ"), ln=1)

    pdf.set_font(yazi_tipi, "", 11)
    pdf.set_text_color(90, 90, 95)
    pdf.set_xy(sol, 48)
    pdf.cell(
        0, 6,
        T(f"Makbuz No: {makbuz_numarasi}"),
        ln=1
    )
    pdf.set_x(sol)
    pdf.cell(
        0, 6, T(f"Tarih: {tarih}"), ln=1
    )

    # ---- Müşteri bilgileri ----
    y = 64
    pdf.set_fill_color(244, 245, 247)
    pdf.rect(sol, y, sag - sol, 26, "F")

    pdf.set_xy(sol + 4, y + 3)
    pdf.set_font(yazi_tipi, "B", 12)
    pdf.set_text_color(30, 30, 34)
    pdf.cell(
        0, 6, T("MÜŞTERİ BİLGİLERİ"), ln=1
    )

    pdf.set_x(sol + 4)
    pdf.set_font(yazi_tipi, "", 11)
    pdf.set_text_color(60, 60, 65)
    pdf.cell(
        0, 6,
        T(
            "Müşteri: "
            + (is_.get("musteri") or "-")
        ),
        ln=1
    )

    pdf.set_x(sol + 4)
    pdf.cell(
        0, 6,
        T(
            "Telefon: "
            + (is_.get("telefon") or "-")
        ),
        ln=1
    )

    # ---- İş açıklaması ----
    y = 96
    pdf.set_xy(sol, y)
    pdf.set_font(yazi_tipi, "B", 12)
    pdf.set_text_color(30, 30, 34)
    pdf.cell(0, 6, T("İŞ AÇIKLAMASI"), ln=1)

    pdf.set_x(sol)
    pdf.set_font(yazi_tipi, "", 11)
    pdf.set_text_color(60, 60, 65)

    aciklama_metni = (
        is_.get("is_adi", "")
        + (
            "\n" + is_.get("aciklama", "")
            if is_.get("aciklama")
            else ""
        )
    )

    pdf.multi_cell(
        sag - sol, 6, T(aciklama_metni)
    )

    # ---- Tutar tablosu ----
    y = max(pdf.get_y() + 8, 130)

    satirlar = [
        ("İşçilik Ücreti", iscilik)
    ]

    if not malzemeli:
        satirlar.append(
            ("Malzeme", malzeme_toplami)
        )

    pdf.set_xy(sol, y)
    pdf.set_draw_color(220, 220, 224)

    for etiket, tutar in satirlar:

        pdf.set_font(yazi_tipi, "", 12)
        pdf.set_text_color(60, 60, 65)
        pdf.set_x(sol)
        pdf.cell(
            (sag - sol) * 0.6, 8, T(etiket)
        )
        pdf.cell(
            (sag - sol) * 0.4,
            8,
            T(f"{tutar:,.2f} TL"),
            align="R",
            ln=1
        )

        pdf.set_x(sol)
        pdf.cell(
            sag - sol, 0, "",
            border="T", ln=1
        )

    pdf.set_font(yazi_tipi, "B", 13)
    pdf.set_text_color(20, 20, 24)
    pdf.set_x(sol)
    pdf.cell(
        (sag - sol) * 0.6, 10, T("TOPLAM")
    )
    pdf.cell(
        (sag - sol) * 0.4,
        10,
        T(f"{toplam:,.2f} TL"),
        align="R",
        ln=1
    )

    pdf.set_font(yazi_tipi, "", 12)
    pdf.set_text_color(60, 60, 65)
    pdf.set_x(sol)
    pdf.cell(
        (sag - sol) * 0.6, 8, T("Ödenen")
    )
    pdf.cell(
        (sag - sol) * 0.4,
        8,
        T(f"{alinan:,.2f} TL"),
        align="R",
        ln=1
    )

    alinan_tarihi = is_.get(
        "alinan_tarihi", ""
    )

    if alinan_tarihi:

        pdf.set_font(yazi_tipi, "", 10)
        pdf.set_text_color(120, 120, 125)
        pdf.set_x(sol)
        pdf.cell(
            sag - sol,
            6,
            T("Ödenen Tarihi: " + alinan_tarihi),
            ln=1
        )

    pdf.set_font(yazi_tipi, "", 12)
    pdf.set_text_color(60, 60, 65)
    pdf.set_x(sol)
    pdf.cell(
        (sag - sol) * 0.6, 8, T("Kalan")
    )
    pdf.cell(
        (sag - sol) * 0.4,
        8,
        T(f"{max(kalan, 0):,.2f} TL"),
        align="R",
        ln=1
    )

    # ---- Ödeme durumu rozeti ----
    y = pdf.get_y() + 6
    pdf.set_fill_color(*durum_renk)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(yazi_tipi, "B", 13)
    pdf.set_xy(sol, y)
    pdf.cell(
        sag - sol, 11, T(odeme_durumu),
        align="C", fill=True, ln=1
    )

    # ---- Alt bilgi ----
    pdf.set_y(-25)
    pdf.set_font(yazi_tipi, "", 9)
    pdf.set_text_color(150, 150, 155)
    pdf.cell(
        0, 6,
        T(
            "Bu makbuz otomatik olarak "
            "oluşturulmuştur."
        ),
        align="C"
    )

    os.makedirs(
        MAKBUZ_KLASORU, exist_ok=True
    )

    dosya_adi = (
        makbuz_numarasi
        + "_"
        + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        + ".pdf"
    )

    dosya_yolu = os.path.join(
        MAKBUZ_KLASORU, dosya_adi
    )

    pdf.output(dosya_yolu)

    # ---- Uygulama içi önizleme için özet veri ----
    # PDF sayfasını piksel piksel çizmek (görsel önizleme)
    # ekstra bir PDF-render kütüphanesi gerektirir; proje
    # sıfır ekstra bağımlılık hedefinde olduğu için bunun
    # yerine PDF'teki AYNI bilgileri kullanıcı dostu bir
    # kart olarak gösteren bir özet döndürülür. Paylaş
    # butonuna basmadan önce kullanıcı makbuzun içeriğini
    # (müşteri, tutarlar, ödeme durumu) burada kontrol
    # edebilir.
    ozet = {
        "firma_adi": firma_adi or "Firma / Kişi Adı",
        "firma_telefon": firma_telefon,
        "makbuz_no": makbuz_numarasi,
        "tarih": tarih,
        "musteri": is_.get("musteri") or "-",
        "telefon": is_.get("telefon") or "-",
        "aciklama": aciklama_metni,
        "satirlar": satirlar,
        "toplam": toplam,
        "alinan": alinan,
        "alinan_tarihi": alinan_tarihi,
        "kalan": max(kalan, 0),
        "odeme_durumu": odeme_durumu,
        "durum_renk": tuple(
            kanal / 255 for kanal in durum_renk
        ) + (1,)
    }

    return dosya_yolu, ozet


def _android_paylas(dosya_yolu, baslik):
    """
    PDF makbuzu Android'in kendi paylaşım (share sheet) menüsüyle
    paylaşır. Android 7 (API 24) ve üzerinde uygulamalar arası
    ham "file://" yolu paylaşmak FileUriExposedException
    fırlatır; bu yüzden dosya, androidx FileProvider üzerinden
    güvenli bir "content://" adresine çevrilerek paylaşılır.

    Bunun çalışması için proje kökünde:
      - android_extra/file_paths.xml
      - android_extra/manifest_provider.xml
    dosyaları ve buildozer.spec'teki ilgili satırlar gereklidir
    (bkz. buildozer.spec içindeki açıklamalar).
    """
    from jnius import autoclass, cast
    from android import mActivity

    Intent = autoclass("android.content.Intent")
    JavaFile = autoclass("java.io.File")
    FileProvider = autoclass("androidx.core.content.FileProvider")
    Parcelable = autoclass("android.os.Parcelable")
    JavaString = autoclass("java.lang.String")

    activity = mActivity
    context = activity.getApplicationContext()

    dosya = JavaFile(dosya_yolu)
    yetki_adi = context.getPackageName() + ".fileprovider"
    uri = FileProvider.getUriForFile(context, yetki_adi, dosya)

    gonderme_intent = Intent(Intent.ACTION_SEND)
    gonderme_intent.setType("application/pdf")
    gonderme_intent.putExtra(
        Intent.EXTRA_STREAM, cast(Parcelable, uri)
    )
    gonderme_intent.addFlags(
        Intent.FLAG_GRANT_READ_URI_PERMISSION
    )

    # NOT: Intent.createChooser(...) iki taşıma imzasına (overload)
    # sahip statik bir metottur ve pyjnius, çıplak bir Python str
    # verildiğinde bunu hangi Java CharSequence taşımasıyla
    # eşleştireceğine bazen karar veremiyor ("No static methods
    # called createChooser ... matching your arguments" hatası
    # buradan geliyordu). Çözüm: başlığı önce gerçek bir
    # java.lang.String'e çevirip CharSequence'a cast etmek, böylece
    # pyjnius hangi taşımanın çağrılacağını kesin olarak biliyor.
    baslik_cs = cast("java.lang.CharSequence", JavaString(baslik))

    try:
        secici = Intent.createChooser(gonderme_intent, baslik_cs)
        secici.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        activity.startActivity(secici)
    except Exception as e:
        # createChooser yine de bir sebepten başarısız olursa
        # (ör. farklı bir pyjnius/Android sürümü), paylaşım
        # tamamen çökmesin diye seçici olmadan doğrudan gönderme
        # intent'ini başlatmayı dene: kullanıcı yine paylaşabilir,
        # sadece uygulama seçim penceresinin başlığı olmaz.
        print(f"[paylaşım] createChooser başarısız, doğrudan deneniyor: {e}")
        gonderme_intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        activity.startActivity(gonderme_intent)


def makbuz_paylas(dosya_yolu):

    try:
        from kivy.utils import platform
    except Exception:
        platform = None

    if platform != "android":
        return False, (
            "Paylaşım menüsü sadece Android cihazlarda "
            "desteklenir."
        )

    try:

        _android_paylas(dosya_yolu, "Makbuzu Paylaş")

        return True, None

    except Exception as e:

        hata = str(e)
        print(f"[paylaşım] hata: {hata}")
        return False, hata


class AcilisEkrani(Screen):

    # Eskiden burada halkalar/animasyonlu başlık/ilerleme
    # çubuğu olan gösterişli bir açılış (intro) ekranı vardı.
    # Kullanıcı isteği üzerine kaldırıldı: artık sadece düz
    # beyaz bir zemin üzerinde logo gösteren, çok kısa süren
    # sade bir yüklenme ekranı var. Logo oranı bozulmadan
    # (16:9'a yakın bir kutu içinde, keep_ratio ile) gösterilir.

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.kok = FloatLayout()

        with self.kok.canvas.before:

            Color(1, 1, 1, 1)

            self._zemin = RoundedRectangle(
                pos=self.kok.pos,
                size=self.kok.size,
                radius=[0]
            )

        self.kok.bind(
            pos=self._zemin_guncelle,
            size=self._zemin_guncelle
        )

        self.logo = Image(
            source=LOGO_DOSYASI,
            size_hint=(None, None),
            size=(dp(320), dp(180)),
            allow_stretch=True,
            keep_ratio=True,
            pos_hint={
                "center_x": .5,
                "center_y": .5
            }
        )

        self.kok.add_widget(self.logo)

        self.add_widget(self.kok)

    def _zemin_guncelle(self, *args):

        self._zemin.pos = self.kok.pos
        self._zemin.size = self.kok.size

    def on_enter(self):

        Clock.schedule_once(
            self._devam_et,
            .5
        )

    def _devam_et(self, dt):

        if self.manager:

            self.manager.transition = (
                FadeTransition(
                    duration=.25
                )
            )

            self._kurulum_kontrol()

    def _kurulum_kontrol(self):

        ayar = ayarlari_oku()

        hedef = (
            "ana"
            if ayar.get(
                "kurulum_tamam", False
            )
            else "kurulum"
        )

        self.manager.current = hedef


# =========================================================
# İLK KURULUM
# =========================================================

class IlkKurulum(Screen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        ana = BoxLayout(
            orientation="vertical",
            padding=dp(22),
            spacing=dp(14)
        )

        ana.add_widget(
            Label(
                text="👋 HOŞ GELDİNİZ",
                font_size=28,
                bold=True,
                color=BEYAZ,
                size_hint_y=None,
                height=dp(50)
            )
        )

        ana.add_widget(
            Label(
                text=(
                    "Başlamadan önce birkaç "
                    "bilgiye ihtiyacımız var. "
                    "Bu bilgiler makbuzlarda "
                    "otomatik kullanılacak."
                ),
                font_size=16,
                color=SOLUK,
                size_hint_y=None,
                height=dp(70)
            )
        )

        self.firma_adi = giris(
            "Firma Adı / Kişi Adı"
        )

        self.telefon = telefon_girisi(
            "Telefon Numarası"
        )

        ana.add_widget(
            etiketli_alan(
                "Firma Adı / Kişi Adı",
                self.firma_adi
            )
        )

        ana.add_widget(
            etiketli_alan(
                "Telefon Numarası",
                self.telefon
            )
        )

        self.uyari = Label(
            text="",
            font_size=14,
            color=KIRMIZI,
            size_hint_y=None,
            height=dp(24)
        )

        ana.add_widget(self.uyari)

        ana.add_widget(Widget())

        devam = buton(
            "DEVAM ET",
            renk=YESIL,
            yukseklik=64,
            font=20
        )

        devam.bind(
            on_press=self.devam_et
        )

        ana.add_widget(devam)

        self.add_widget(ana)

    def devam_et(self, instance):

        firma_adi = (
            self.firma_adi.text.strip()
        )

        telefon = self.telefon.text.strip()

        if not firma_adi:

            self.uyari.text = (
                "Lütfen Firma Adı / Kişi "
                "Adı girin."
            )

            return

        if not telefon:

            self.uyari.text = (
                "Lütfen Telefon Numarası "
                "girin."
            )

            return

        self.uyari.text = ""

        ayarlari_kaydet({
            "firma_adi": firma_adi,
            "telefon": telefon,
            "kurulum_tamam": True,
            "son_makbuz_no": 0
        })

        self.manager.current = "ana"


# =========================================================
# ANA SAYFA - YENİ TASARIM BİLEŞENLERİ
# =========================================================

def _ekrana_git(widget, ekran_adi):

    # Bir alt widget'tan (menü kartı / alt menü ikonu) yukarı
    # doğru giderek en yakın ScreenManager'ı bulur ve o ekrana
    # geçer. Böylece her bileşenin ayrıca manager referansı
    # taşımasına gerek kalmaz.

    if not ekran_adi:
        return

    gezinen = widget.parent

    while gezinen is not None and not hasattr(
        gezinen, "manager"
    ):
        gezinen = gezinen.parent

    if gezinen is not None and gezinen.manager:
        gezinen.manager.current = ekran_adi

class GradyanKart(BoxLayout):

    # Üstteki "Kârım" kutusunun koyu -> açık yeşil (veya
    # alınacak varsa kırmızı) gradyanlı, köşeleri yuvarlak
    # arka planı. Gradyan, StencilPush/Use ile yuvarlak
    # dikdörtgen şekline kırpılan ince dikey bantlarla
    # simüle edilir (Kivy'de doğrudan gradient çizim
    # nesnesi yoktur).

    def __init__(
        self,
        renk_koyu=KAR_KART_KOYU,
        renk_acik=KAR_KART_ACIK,
        **kwargs
    ):

        self.renk_koyu = renk_koyu
        self.renk_acik = renk_acik

        super().__init__(**kwargs)

        self.bind(
            pos=self._ciz,
            size=self._ciz
        )

        self._ciz()

    def renkleri_ayarla(self, koyu, acik):

        self.renk_koyu = koyu
        self.renk_acik = acik
        self._ciz()

    def _ciz(self, *args):

        self.canvas.before.clear()

        if self.width <= 0 or self.height <= 0:
            return

        bant_sayisi = 28

        with self.canvas.before:

            StencilPush()

            Color(1, 1, 1, 1)

            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(22)]
            )

            StencilUse()

            bant_genislik = (
                self.width / bant_sayisi
            ) + 1.5

            for i in range(bant_sayisi):

                t = i / (bant_sayisi - 1)

                Color(
                    self.renk_koyu[0]
                    + (self.renk_acik[0]
                       - self.renk_koyu[0]) * t,
                    self.renk_koyu[1]
                    + (self.renk_acik[1]
                       - self.renk_koyu[1]) * t,
                    self.renk_koyu[2]
                    + (self.renk_acik[2]
                       - self.renk_koyu[2]) * t,
                    1
                )

                Rectangle(
                    pos=(
                        self.x + i * (
                            self.width / bant_sayisi
                        ),
                        self.y
                    ),
                    size=(
                        bant_genislik,
                        self.height
                    )
                )

            # Sağ üstte yükselen ince "grafik" çizgisi
            Color(1, 1, 1, 0.16)

            genislik = self.width
            yukseklik = self.height

            Line(
                points=[
                    self.x + genislik * 0.55,
                    self.y + yukseklik * 0.42,
                    self.x + genislik * 0.68,
                    self.y + yukseklik * 0.60,
                    self.x + genislik * 0.80,
                    self.y + yukseklik * 0.50,
                    self.x + genislik * 0.92,
                    self.y + yukseklik * 0.88
                ],
                width=dp(1.6)
            )

            StencilUnUse()

            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(22)]
            )

            StencilPop()


class MenuKarti(ButtonBehavior, BoxLayout):

    # Ana menüdeki 2 sütunlu ızgarada yer alan kart.
    # Artık ayrı bir ikon kutusu yok - kartın tamamı
    # kategoriye özel soft renkle boyanıyor, başlık
    # yazısı doğrudan bu renkli zeminin üstünde, büyük
    # punto ile duruyor.

    def __init__(
        self,
        renk,
        yazi,
        ekran,
        **kwargs
    ):

        self.ekran = ekran
        self._renk_taban = renk

        kwargs.setdefault(
            "orientation",
            "horizontal"
        )

        kwargs.setdefault(
            "size_hint",
            (1, None)
        )

        kwargs.setdefault(
            "height",
            dp(128)
        )

        kwargs.setdefault(
            "padding",
            [dp(18), dp(12)]
        )

        kwargs.setdefault(
            "spacing",
            dp(8)
        )

        super().__init__(**kwargs)

        with self.canvas.before:

            self._renk = Color(*renk)

            self._arka = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(20)]
            )

        self.bind(
            pos=self._guncelle,
            size=self._guncelle,
            state=self._durum
        )

        baslik_lbl = Label(
            text=yazi,
            font_size=24,
            bold=True,
            color=BEYAZ,
            halign="left",
            valign="middle",
            size_hint_x=1
        )

        baslik_lbl.bind(
            size=lambda obj, val:
            setattr(
                obj,
                "text_size",
                val
            )
        )

        self.add_widget(baslik_lbl)

        self.add_widget(
            Label(
                text=">",
                font_size=22,
                bold=True,
                color=(1, 1, 1, 0.55),
                size_hint_x=None,
                width=dp(18)
            )
        )

    def _guncelle(self, *args):

        self._arka.pos = self.pos
        self._arka.size = self.size

    def _durum(self, *args):

        r, g, b, a = self._renk_taban

        if self.state == "down":

            self._renk.rgba = (
                r * 0.78,
                g * 0.78,
                b * 0.78,
                a
            )

        else:

            self._renk.rgba = self._renk_taban

    def on_release(self):

        _ekrana_git(self, self.ekran)


class IstatistikKarti(BoxLayout):

    # Gelir/Gider ekranındaki küçük istatistik kutucukları.
    # MenuKarti ile aynı yuvarlak / renkli görsel dili
    # kullanır ama tıklanamaz, sadece bir başlık + tutar
    # gösterir. Ana sayfa ile aynı "cool" his için.

    def __init__(
        self,
        renk,
        ikon,
        baslik,
        **kwargs
    ):

        self._renk_taban = renk

        kwargs.setdefault(
            "orientation",
            "vertical"
        )

        kwargs.setdefault(
            "size_hint",
            (1, None)
        )

        kwargs.setdefault(
            "height",
            dp(96)
        )

        kwargs.setdefault(
            "padding",
            [dp(14), dp(10)]
        )

        kwargs.setdefault(
            "spacing",
            dp(2)
        )

        super().__init__(**kwargs)

        with self.canvas.before:

            Color(*renk)

            self._arka = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(18)]
            )

        self.bind(
            pos=self._guncelle,
            size=self._guncelle
        )

        self.baslik_lbl = Label(
            text=f"{ikon}  {baslik}",
            font_size=15,
            bold=True,
            color=(1, 1, 1, 0.85),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(22)
        )

        self.baslik_lbl.bind(
            size=lambda obj, val:
            setattr(
                obj,
                "text_size",
                val
            )
        )

        self.add_widget(self.baslik_lbl)

        self.tutar_lbl = Label(
            text="0 TL",
            font_size=21,
            bold=True,
            color=BEYAZ,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(30)
        )

        self.tutar_lbl.bind(
            size=lambda obj, val:
            setattr(
                obj,
                "text_size",
                val
            )
        )

        self.add_widget(self.tutar_lbl)

    def _guncelle(self, *args):

        self._arka.pos = self.pos
        self._arka.size = self.size

    def tutar_ayarla(self, metin):

        self.tutar_lbl.text = metin


class PilButon(ButtonBehavior, BoxLayout):

    # Alttaki "Kaydet ve Çık" yeşil çerçeveli, tam
    # yuvarlak (hap biçimli) buton.

    def __init__(
        self,
        yazi="KAYDET VE ÇIK",
        **kwargs
    ):

        kwargs.setdefault(
            "size_hint",
            (1, None)
        )

        kwargs.setdefault(
            "height",
            dp(60)
        )

        kwargs.setdefault(
            "padding",
            [dp(20), 0]
        )

        kwargs.setdefault(
            "spacing",
            dp(10)
        )

        super().__init__(**kwargs)

        with self.canvas.before:

            self._dolgu_renk = Color(
                0.04, 0.22, 0.16, 0.55
            )

            self._dolgu = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.height / 2]
            )

            Color(0.16, 0.85, 0.55, 0.9)

            self._cerceve = Line(
                rounded_rectangle=(
                    self.x, self.y,
                    self.width, self.height,
                    self.height / 2
                ),
                width=dp(1.6)
            )

        self.bind(
            pos=self._guncelle,
            size=self._guncelle,
            state=self._durum
        )

        self.add_widget(
            Label(
                text="💾",
                font_size=20,
                size_hint_x=None,
                width=dp(30)
            )
        )

        self.add_widget(
            Label(
                text=yazi,
                font_size=18,
                bold=True,
                color=BEYAZ,
                size_hint_x=1,
                halign="left",
                valign="middle"
            )
        )

        self.add_widget(
            Label(
                text="»",
                font_size=22,
                color=(0.16, 0.85, 0.55, 1),
                size_hint_x=None,
                width=dp(30)
            )
        )

    def _guncelle(self, *args):

        self._dolgu.pos = self.pos
        self._dolgu.size = self.size
        self._dolgu.radius = [self.height / 2]

        self._cerceve.rounded_rectangle = (
            self.x, self.y,
            self.width, self.height,
            self.height / 2
        )

    def _durum(self, *args):

        if self.state == "down":
            self._dolgu_renk.rgba = (
                0.04, 0.22, 0.16, 0.85
            )
        else:
            self._dolgu_renk.rgba = (
                0.04, 0.22, 0.16, 0.55
            )


# NOT: Alt gezinme çubuğu (kısayollar) kaldırıldı. Ana
# sayfadaki menü kartları zaten aynı ekranlara götürdüğü
# için ayrı bir alt çubuğa gerek kalmadı.


# =========================================================
# ANA SAYFA
# =========================================================

class AnaSayfa(Screen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        with self.canvas.before:

            Color(*KOYU_ZEMIN)

            self._zemin = Rectangle(
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=lambda obj, val: setattr(
                self._zemin, "pos", val
            ),
            size=lambda obj, val: setattr(
                self._zemin, "size", val
            )
        )

        ana = BoxLayout(
            orientation="vertical",
            padding=[dp(16), dp(14), dp(16), dp(6)],
            spacing=dp(14)
        )

        # ---- ÜST KART SATIRI: SOLDA KAZANÇ, SAĞDA ALINACAK ----
        ust_kartlar = BoxLayout(
            size_hint_y=None,
            height=dp(190),
            spacing=dp(12)
        )

        # -- SOL (BÜYÜK) KART: KAZANÇ / KÂR --
        self.kazanc_kart = GradyanKart(
            renk_koyu=KAR_KART_KOYU,
            renk_acik=KAR_KART_ACIK,
            orientation="vertical",
            size_hint_x=0.58,
            padding=[dp(18), dp(14)],
            spacing=dp(2)
        )

        kazanc_ust = BoxLayout(
            size_hint_y=None,
            height=dp(26)
        )

        kazanc_ust.add_widget(
            Label(
                text="↑",
                font_size=20,
                size_hint_x=None,
                width=dp(26),
                halign="left"
            )
        )

        kazanc_ust.add_widget(Widget())

        self.kazanc_kart.add_widget(kazanc_ust)

        self.kar_baslik = Label(
            text="Kazancım",
            font_size=17,
            bold=True,
            color=BEYAZ,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(24)
        )

        self.kar_baslik.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )

        self.kazanc_kart.add_widget(self.kar_baslik)

        self.kar_tutar = Label(
            text="0 TL",
            font_size=32,
            bold=True,
            color=KAR_YAZI,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(44)
        )

        self.kar_tutar.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )

        self.kazanc_kart.add_widget(self.kar_tutar)

        self.kar_alt_satir = Label(
            text="",
            font_size=14,
            bold=True,
            color=KAR_YAZI,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(22),
            markup=True
        )

        self.kar_alt_satir.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )

        self.kazanc_kart.add_widget(self.kar_alt_satir)

        ust_kartlar.add_widget(self.kazanc_kart)

        # -- SAĞ (KÜÇÜK) KART: ALINACAK TAHSİLAT --
        # Alınacak bir tutar varsa gösterir, yoksa "0 TL"
        # yazar - artık iki kart aynı anda hep görünür.
        self.tahsilat_kart = GradyanKart(
            renk_koyu=KAR_KART_KOYU,
            renk_acik=KAR_KART_ACIK,
            orientation="vertical",
            size_hint_x=0.42,
            padding=[dp(14), dp(14)],
            spacing=dp(2)
        )

        tahsilat_ust = BoxLayout(
            size_hint_y=None,
            height=dp(26)
        )

        tahsilat_ust.add_widget(
            Label(
                text="⏳",
                font_size=18,
                size_hint_x=None,
                width=dp(26),
                halign="left"
            )
        )

        tahsilat_ust.add_widget(Widget())

        self.tahsilat_kart.add_widget(tahsilat_ust)

        self.tahsilat_baslik = Label(
            text="Kalan Tahsilat",
            font_size=16,
            bold=True,
            color=BEYAZ,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(24)
        )

        self.tahsilat_baslik.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )

        self.tahsilat_kart.add_widget(
            self.tahsilat_baslik
        )

        self.tahsilat_tutar = Label(
            text="0 TL",
            font_size=24,
            bold=True,
            color=KAR_YAZI,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(38)
        )

        self.tahsilat_tutar.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )

        self.tahsilat_kart.add_widget(
            self.tahsilat_tutar
        )

        self.tahsilat_alt_satir = Label(
            text="",
            font_size=12,
            bold=True,
            color=KAR_YAZI,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(18)
        )

        self.tahsilat_alt_satir.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )

        self.tahsilat_kart.add_widget(
            self.tahsilat_alt_satir
        )

        ust_kartlar.add_widget(self.tahsilat_kart)

        ana.add_widget(ust_kartlar)

        # ---- 2 SÜTUNLU MENÜ IZGARASI ----
        izgara = GridLayout(
            cols=2,
            spacing=dp(12),
            size_hint_y=None
        )

        izgara.bind(
            minimum_height=
            izgara.setter("height")
        )

        menuler = [
            ("yeni", "Yeni İş"),
            ("gecmis", "Geçmiş İşler"),
            ("gelir", "Gelir / Gider"),
            ("rapor", "Raporlar"),
            ("malzeme", "Malzeme"),
            ("ayar", "Ayarlar")
        ]

        for ekran, yazi in menuler:

            izgara.add_widget(
                MenuKarti(
                    MENU_IKON_RENKLERI[ekran],
                    yazi,
                    ekran
                )
            )

        ana.add_widget(izgara)

        ana.add_widget(Widget())

        # ---- KAYDET VE ÇIK (HAP BUTON) ----
        cikis_btn = PilButon(
            "Kaydet ve Çık"
        )

        cikis_btn.bind(
            on_release=self.kaydet_ve_cik
        )

        ana.add_widget(cikis_btn)

        # Bazı telefonlarda alttaki gezinme çubuğu / ekran
        # kenarı "Kaydet ve Çık" butonunu kapatıp basılmasını
        # zorlaştırabiliyor. Butonun altına görünmez, işlevsiz
        # bir boşluk (buton) ekleyerek yukarıdaki esnek boşluğun
        # tamamını yutmasını engelliyor; böylece "Kaydet ve Çık"
        # butonu ekranın en altına yapışmadan biraz yukarıda
        # kalıyor. Gerekirse bu yüksekliği artırıp butonu daha da
        # yukarı taşımak mümkün.
        gorunmez_bosluk = Widget(
            size_hint_y=None,
            height=dp(30)
        )

        ana.add_widget(gorunmez_bosluk)

        self.add_widget(ana)

    def kaydet_ve_cik(
        self,
        instance
    ):

        try:

            os.makedirs(
                YEDEK_KLASORU,
                exist_ok=True
            )

            zaman = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            if os.path.exists(
                ISLER_DOSYASI
            ):

                shutil.copy2(
                    ISLER_DOSYASI,
                    os.path.join(
                        YEDEK_KLASORU,
                        f"isler_{zaman}.json"
                    )
                )

            if os.path.exists(
                YERLER_DOSYASI
            ):

                shutil.copy2(
                    YERLER_DOSYASI,
                    os.path.join(
                        YEDEK_KLASORU,
                        f"yerler_{zaman}.json"
                    )
                )

        except Exception:
            pass

        App.get_running_app().stop()

    def on_enter(self):

        isler = oku(
            ISLER_DOSYASI
        )

        toplam_alinacak = 0
        toplam_iscilik = 0
        toplam_diger_gider = 0
        toplam_malzeme_kar = 0

        for is_ in isler:

            # İş "Bitti" olarak seçilmediyse (ve alınan/işçilik
            # eşitliğiyle arka planda da bitti sayılmıyorsa)
            # ana ekrandaki kâr ve tahsilat tutarına dahil
            # edilmez.
            if not is_fiilen_bitti(is_):
                continue

            iscilik = para(
                is_.get("iscilik", 0)
            )

            alinan = para(
                is_.get("gelir", 0)
            )

            malzeme_toplami = toplam_malzeme(
                is_
            )

            alinacak = alinacak_hesapla(
                is_.get("malzemeli", True),
                iscilik,
                malzeme_toplami,
                alinan
            )

            if alinacak > 0:
                toplam_alinacak += alinacak

            toplam_iscilik += iscilik

            toplam_diger_gider += para(
                is_.get("gider", 0)
            )

            if is_.get("malzemeli", True):

                toplam_malzeme_kar += (
                    malzeme_toplami
                )

        karim = (
            toplam_iscilik
            - toplam_diger_gider
            - toplam_malzeme_kar
        )

        def tl_bicimle(deger):

            return "{:,.0f}".format(
                deger
            ).replace(",", ".")

        # -- SOL KART: HER ZAMAN KAZANÇ / KÂR --
        self.kar_tutar.text = (
            f"{tl_bicimle(karim)} TL"
        )

        if toplam_iscilik > 0:

            marj = (
                karim / toplam_iscilik
            ) * 100

        else:
            marj = 0

        ok = "↗" if karim >= 0 else "↘"

        marj_metin = "{:.1f}".format(
            marj
        ).replace(".", ",")

        self.kar_alt_satir.text = (
            f"{ok} Kâr Marjı  (%{marj_metin})"
        )

        # -- SAĞ KART: ALINACAK TAHSİLAT (yoksa 0 TL) --
        self.tahsilat_tutar.text = (
            f"{tl_bicimle(toplam_alinacak)} TL"
        )

        if toplam_alinacak > 0:

            self.tahsilat_kart.renkleri_ayarla(
                ALACAK_KART_KOYU,
                ALACAK_KART_ACIK
            )

            self.tahsilat_tutar.color = ALACAK_YAZI

            self.tahsilat_alt_satir.text = (
                "🔴 Bekliyor"
            )

            self.tahsilat_alt_satir.color = ALACAK_YAZI

        else:

            self.tahsilat_kart.renkleri_ayarla(
                KAR_KART_KOYU,
                KAR_KART_ACIK
            )

            self.tahsilat_tutar.color = KAR_YAZI

            self.tahsilat_alt_satir.text = (
                "✅ Tümü tahsil edildi"
            )

            self.tahsilat_alt_satir.color = KAR_YAZI


# =========================================================
# YENİ İŞ
# =========================================================

class YeniIs(Screen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.malzemeler = []
        self.secili_yer = ""

        # Yeni tasarım: ekran zemini koyu lacivert (ana
        # menüdeki KOYU_ZEMIN ile aynı), diğer ekranlar
        # etkilenmeden sadece bu ekrana özel çizilir.
        with self.canvas.before:

            Color(*KOYU_ZEMIN)

            self._form_zemin = Rectangle(
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=lambda obj, val:
            setattr(self._form_zemin, "pos", val),
            size=lambda obj, val:
            setattr(self._form_zemin, "size", val)
        )

        ana = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(7)
        )

        ana.add_widget(
            ust_baslik(
                self,
                "＋ YENİ İŞ",
                "ana"
            )
        )

        scroll = ScrollView()

        self.scroll = scroll

        form = BoxLayout(
            orientation="vertical",
            spacing=dp(14),
            size_hint_y=None
        )

        form.bind(
            minimum_height=
            form.setter("height")
        )

        # ---- BÖLÜM 1: GENEL BİLGİLER ----
        kart_genel = bolum_karti(
            "📋 Genel Bilgiler"
        )

        self.gorusme_tarihi = TarihInput(
            hint_text=
            "📅 Görüşme / Anlaşma tarihi - "
            "dokun ve seç",
            size_hint_y=None,
            height=dp(58),
            on_tarih=self.tarih_sec
        )

        self.musteri = giris_koyu(
            "Müşteri / iş sahibi"
        )

        self.telefon = giris_koyu(
            "Telefon (isteğe bağlı)"
        )

        kart_genel.add_widget(self.gorusme_tarihi)
        kart_genel.add_widget(self.musteri)
        kart_genel.add_widget(self.telefon)

        yer_satir = BoxLayout(
            size_hint_y=None,
            height=dp(58),
            spacing=dp(7)
        )

        yer_btn = buton(
            "📍 İŞ YERİ SEÇ",
            yukseklik=58,
            font=17
        )

        yer_btn.bind(
            on_press=self.yer_sec
        )

        self.yer_label = Label(
            text="Yer: seçilmedi",
            font_size=17,
            color=SOLUK
        )

        yer_satir.add_widget(yer_btn)
        yer_satir.add_widget(
            self.yer_label
        )

        kart_genel.add_widget(yer_satir)

        durum_satir = BoxLayout(
            size_hint_y=None,
            height=dp(58),
            spacing=dp(7)
        )

        durum_satir.add_widget(
            Label(
                text="Durum:",
                font_size=18,
                color=BEYAZ
            )
        )

        self.durum = Spinner(
            text="Devam ediyor",
            values=(
                "Devam ediyor",
                "Bitti",
                "Beklemede"
            ),
            size_hint_y=None,
            height=dp(58),
            font_size=18,
            background_normal="",
            background_color=FORM_GIRIS,
            color=FORM_GIRIS_YAZI
        )

        durum_satir.add_widget(
            self.durum
        )

        kart_genel.add_widget(
            durum_satir
        )

        self.aciklama = giris_koyu(
            "İş açıklaması / notlar",
            multiline=True,
            height=125
        )

        self.baslangic = TarihInput(
            hint_text="📅 Başlangıç tarihi - dokun ve seç",
            size_hint_y=None,
            height=dp(58),
            on_tarih=self.tarih_sec
        )

        self.bitis = TarihInput(
            hint_text="📅 Bitiş tarihi - dokun ve seç",
            size_hint_y=None,
            height=dp(58),
            on_tarih=self.tarih_sec
        )

        self.gelir = giris_koyu(
            "Alınan (TL)",
            input_filter="float"
        )

        self.alinan_tarihi = TarihInput(
            hint_text="📅 Alınan tarihi",
            size_hint_y=None,
            height=dp(58),
            on_tarih=self.tarih_sec
        )

        self.iscilik = giris_koyu(
            "İşçilik (TL)",
            input_filter="float"
        )

        kart_genel.add_widget(self.aciklama)
        kart_genel.add_widget(self.baslangic)
        kart_genel.add_widget(self.bitis)

        form.add_widget(kart_genel)

        # ---- BÖLÜM 2: EKLER (FOTOĞRAF / SES) ----
        kart_ekler = bolum_karti(
            "📎 Ekler (Fotoğraf / Ses)"
        )

        self.foto_secici = FotografSecici()
        kart_ekler.add_widget(self.foto_secici)

        self.ses_kaydedici = SesKaydedici(
            uyari_callback=uyari_popup
        )
        kart_ekler.add_widget(self.ses_kaydedici)

        form.add_widget(kart_ekler)

        # ---- BÖLÜM 3: MALİ BİLGİLER ----
        kart_mali = bolum_karti(
            "💰 Mali Bilgiler"
        )

        self.malzemeli = True

        malzeme_secim_satir = BoxLayout(
            size_hint_y=None,
            height=dp(58),
            spacing=dp(8)
        )

        self.malzemeli_btn = buton(
            "📦 MALZEMELİ İŞ",
            renk=YESIL,
            yukseklik=56,
            font=16
        )

        self.malzemesiz_btn = buton(
            "🚫 MALZEMESİZ İŞ",
            yukseklik=56,
            font=16
        )

        self.malzemeli_btn.bind(
            on_press=lambda *_:
            self.malzeme_secim(True)
        )

        self.malzemesiz_btn.bind(
            on_press=lambda *_:
            self.malzeme_secim(False)
        )

        malzeme_secim_satir.add_widget(
            self.malzemeli_btn
        )

        malzeme_secim_satir.add_widget(
            self.malzemesiz_btn
        )

        kart_mali.add_widget(
            malzeme_secim_satir
        )

        kart_mali.add_widget(
            etiketli_alan(
                "İşçilik",
                self.iscilik
            )
        )

        kart_mali.add_widget(
            etiketli_alan_tarihli(
                "Alınan",
                self.gelir,
                self.alinan_tarihi
            )
        )

        form.add_widget(kart_mali)

        # ---- BÖLÜM 4: DİĞER GİDERLER ----
        kart_gider = bolum_karti(
            "💸 Diğer Giderler"
        )

        self.gider_kutusu = BoxLayout(
            orientation="vertical",
            spacing=dp(7),
            size_hint_y=None
        )

        self.gider_kutusu.bind(
            minimum_height=
            self.gider_kutusu.setter("height")
        )

        kart_gider.add_widget(
            self.gider_kutusu
        )

        self.gider_satirlari = []

        self.gider_satiri_ekle()

        form.add_widget(kart_gider)

        # ---- BÖLÜM 5: MALZEMELER ----
        kart_malzeme = bolum_karti(
            "📦 Malzemeler"
        )

        malzeme_satir = BoxLayout(
            size_hint_y=None,
            height=dp(58),
            spacing=dp(5)
        )

        self.malzeme_adi = giris_koyu(
            "Malzeme"
        )

        self.malzeme_adet = giris_koyu(
            "Miktar",
            input_filter="int"
        )

        self.malzeme_adet.size_hint_x = .20

        self.malzeme_birim = Spinner(
            text="Adet",
            values=(
                "Adet",
                "LT",
                "M",
                "KG",
                "Kutu",
                "Çuval"
            ),
            size_hint_x=.23,
            size_hint_y=None,
            height=dp(58),
            font_size=16,
            background_normal="",
            background_color=FORM_GIRIS,
            color=FORM_GIRIS_YAZI
        )

        self.malzeme_fiyat = giris_koyu(
            "Fiyat",
            input_filter="float"
        )

        self.malzeme_fiyat.size_hint_x = .27

        ekle = buton(
            "+",
            yukseklik=58,
            font=27
        )

        ekle.size_hint_x = .16

        ekle.bind(
            on_press=self.malzeme_ekle
        )

        malzeme_satir.add_widget(
            self.malzeme_adi
        )

        malzeme_satir.add_widget(
            self.malzeme_adet
        )

        malzeme_satir.add_widget(
            self.malzeme_birim
        )

        malzeme_satir.add_widget(
            self.malzeme_fiyat
        )

        malzeme_satir.add_widget(ekle)

        kart_malzeme.add_widget(
            malzeme_satir
        )

        self.malzeme_listesi = Label(
            text="Henüz malzeme yok.",
            font_size=17,
            color=SOLUK,
            size_hint_y=None,
            height=dp(130)
        )

        kart_malzeme.add_widget(
            self.malzeme_listesi
        )

        form.add_widget(kart_malzeme)

        # ---- SONUÇ + KAYDET (kartların dışında, öne çıkar) ----
        # Yeni tasarımda ikisi tek bir satırda yan yana durur;
        # iki alan da (tutar kutusu, kaydet butonu) aynen
        # korunuyor, sadece yerleşimi yan yana.
        self.alinacak_kutu = KirmiziKutu(
            text="ALINACAK TUTAR: 0.00 TL",
            font_size=15,
            bold=True,
            color=BEYAZ,
            halign="center",
            valign="middle",
            size_hint_x=0.40,
            size_hint_y=None,
            height=dp(66)
        )

        self.alinacak_kutu.bind(
            size=lambda obj, val:
            setattr(
                obj,
                "text_size",
                val
            )
        )

        kaydet_btn = buton(
            "💾 İŞİ KAYDET",
            renk=YESIL,
            yukseklik=66,
            font=19
        )

        kaydet_btn.size_hint_x = 0.60

        kaydet_btn.bind(
            on_press=self.kaydet
        )

        sonuc_satir = BoxLayout(
            size_hint_y=None,
            height=dp(66),
            spacing=dp(10)
        )

        sonuc_satir.add_widget(
            self.alinacak_kutu
        )

        sonuc_satir.add_widget(
            kaydet_btn
        )

        form.add_widget(
            sonuc_satir
        )

        # Bazı telefonlarda alttaki gezinme çubuğu / ekran
        # kenarı kaydet butonunu kapatıp basılmasını
        # zorlaştırabiliyor. Butonun altına görünmez, işlevsiz
        # bir boşluk ekleyerek butonu biraz yukarı taşıyoruz;
        # buton yine de formun en altında kalıyor.
        form.add_widget(
            Widget(
                size_hint_y=None,
                height=dp(48)
            )
        )

        scroll.add_widget(form)

        ana.add_widget(scroll)

        self.add_widget(ana)

        for widget in (
            self.musteri,
            self.telefon,
            self.aciklama,
            self.gelir,
            self.iscilik,
            self.malzeme_adi,
            self.malzeme_adet,
            self.malzeme_fiyat
        ):

            klavye_uyumu(
                scroll,
                widget
            )

        self.gelir.bind(
            text=self._alinacak_guncelle
        )

        self.iscilik.bind(
            text=self._alinacak_guncelle
        )

        self._alinacak_guncelle()

    def _alinacak_guncelle(self, *args):

        iscilik = para(
            self.iscilik.text
        )

        malzeme_toplami = sum(
            para(m.get("fiyat", 0))
            for m in self.malzemeler
        )

        alinan = para(
            self.gelir.text
        )

        alinacak = alinacak_hesapla(
            self.malzemeli,
            iscilik,
            malzeme_toplami,
            alinan
        )

        self.alinacak_kutu.text = (
            "ALINACAK TUTAR: "
            f"{alinacak:.2f} TL"
        )

    def tarih_sec(
        self,
        widget
    ):

        TakvimPopup(widget).open()

    def yer_sec(
        self,
        instance
    ):

        varsayilan = [
            "Mavikent",
            "Karaöz",
            "Kumluca",
            "Hasyurt",
            "Finike"
        ]

        yerler = oku(
            YERLER_DOSYASI,
            varsayilan
        )

        if not yerler:

            yerler = varsayilan

            kaydet(
                YERLER_DOSYASI,
                yerler
            )

        kutu = BoxLayout(
            orientation="vertical",
            padding=dp(8),
            spacing=dp(7)
        )

        popup = Popup(
            title="İş Yeri Seç",
            content=kutu,
            size_hint=(.90, .84)
        )

        for yer in yerler:

            b = buton(
                "📍 " + yer,
                yukseklik=52,
                font=17
            )

            b.bind(
                on_press=lambda x, y=yer:
                self.yer_secildi(
                    y,
                    popup
                )
            )

            kutu.add_widget(b)

        yeni = buton(
            "＋ YENİ YER EKLE",
            yukseklik=54,
            font=17
        )

        yeni.bind(
            on_press=lambda x:
            self.yeni_yer(popup)
        )

        kutu.add_widget(yeni)

        popup.open()

    def yer_secildi(
        self,
        yer,
        popup
    ):

        self.secili_yer = yer

        self.yer_label.text = (
            "Yer: " + yer
        )

        popup.dismiss()

    def yeni_yer(
        self,
        ana_popup
    ):

        kutu = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(9)
        )

        isim = giris_koyu(
            "Yeni yer adı"
        )

        ekle = buton(
            "EKLE",
            yukseklik=54,
            font=18
        )

        kutu.add_widget(isim)
        kutu.add_widget(ekle)

        popup = Popup(
            title="Yeni İş Yeri",
            content=kutu,
            size_hint=(.86, .40)
        )

        def ekle_yer(instance):

            yer = isim.text.strip()

            if not yer:
                return

            yerler = oku(
                YERLER_DOSYASI,
                [
                    "Mavikent",
                    "Karaöz",
                    "Kumluca",
                    "Hasyurt",
                    "Finike"
                ]
            )

            if yer not in yerler:

                yerler.append(yer)

                kaydet(
                    YERLER_DOSYASI,
                    yerler
                )

            popup.dismiss()
            ana_popup.dismiss()

            self.secili_yer = yer

            self.yer_label.text = (
                "Yer: " + yer
            )

        ekle.bind(
            on_press=ekle_yer
        )

        popup.open()

    GIDER_KATEGORILERI = (
        "Yakıt",
        "Gıda",
        "Malzeme Özel",
        "Yardımcı Eleman"
    )

    def gider_satiri_ekle(self):

        satir = BoxLayout(
            size_hint_y=None,
            height=dp(58),
            spacing=dp(7)
        )

        kategori = Spinner(
            text=GIDER_PLACEHOLDER,
            values=self.GIDER_KATEGORILERI,
            size_hint_x=.42,
            size_hint_y=None,
            height=dp(58),
            font_size=16,
            background_normal="",
            background_color=FORM_GIRIS,
            color=FORM_GIRIS_YAZI
        )

        tutar = giris_koyu(
            "Tutar (TL)",
            input_filter="float"
        )

        satir.add_widget(kategori)
        satir.add_widget(tutar)

        self.gider_kutusu.add_widget(satir)

        kayit = {
            "satir": satir,
            "kategori": kategori,
            "tutar": tutar
        }

        self.gider_satirlari.append(kayit)

        klavye_uyumu(
            self.scroll,
            tutar
        )

        tutar.bind(
            text=lambda instance, deger, kayit=kayit:
            self._gider_yazildi(kayit, deger)
        )

    def _gider_yazildi(
        self,
        kayit,
        deger
    ):

        if (
            deger.strip()
            and kayit is self.gider_satirlari[-1]
        ):
            self.gider_satiri_ekle()

    def malzeme_secim(self, malzemeli):

        self.malzemeli = malzemeli

        if malzemeli:

            self.malzemeli_btn.renk_degistir(
                YESIL
            )

            self.malzemesiz_btn.renk_degistir(
                None
            )

        else:

            self.malzemeli_btn.renk_degistir(
                None
            )

            self.malzemesiz_btn.renk_degistir(
                KIRMIZI
            )

    def malzeme_ekle(
        self,
        instance
    ):

        ad = (
            self.malzeme_adi.text
            .strip()
        )

        if not ad:
            return

        try:
            adet = int(
                self.malzeme_adet.text or 1
            )
        except Exception:
            adet = 1

        try:
            birim = float(
                self.malzeme_fiyat.text or 0
            )
        except Exception:
            birim = 0

        birim_turu = (
            self.malzeme_birim.text
            or "Adet"
        )

        self.malzemeler.append({

            "ad": ad,

            "adet": adet,

            "birim": birim_turu,

            "birim_fiyat": birim,

            "fiyat": adet * birim,

            "odendi": False
        })

        self.malzeme_adi.text = ""
        self.malzeme_adet.text = ""
        self.malzeme_fiyat.text = ""

        self.malzeme_birim.text = "Adet"

        self.malzemeleri_goster()

    def malzemeleri_goster(self):

        if not self.malzemeler:

            self.malzeme_listesi.text = (
                "Henüz malzeme yok."
            )

            self._alinacak_guncelle()

            return

        toplam = 0
        metin = ""

        for i, m in enumerate(
            self.malzemeler,
            1
        ):

            fiyat = para(
                m.get("fiyat", 0)
            )

            toplam += fiyat

            birim = m.get(
                "birim",
                "Adet"
            )

            metin += (
                f"{i}. {m.get('ad', '')} "
                f"{m.get('adet', 1)} "
                f"{birim} → "
                f"{fiyat:.2f} TL\n"
            )

        metin += (
            f"\nTOPLAM: "
            f"{toplam:.2f} TL"
        )

        self.malzeme_listesi.text = metin

        self._alinacak_guncelle()

    def kaydet(
        self,
        instance
    ):

        try:
            gelir = float(
                self.gelir.text or 0
            )
        except Exception:
            gelir = 0

        try:
            iscilik = float(
                self.iscilik.text or 0
            )
        except Exception:
            iscilik = 0

        diger_giderler = []
        gider = 0

        for kayit in self.gider_satirlari:

            tutar = para(
                kayit["tutar"].text
            )

            if tutar > 0:

                if (
                    kayit["kategori"].text
                    == GIDER_PLACEHOLDER
                ):

                    uyari_popup(
                        "Tutar girdiğiniz gider "
                        "satırı için lütfen bir "
                        "gider türü seçin."
                    )

                    return

                gider += tutar

                diger_giderler.append({
                    "kategori":
                        kayit["kategori"].text,
                    "tutar":
                        tutar
                })

        veri = {

            "is_adi":
                self.musteri.text.strip()
                or "İsimsiz İş",

            "gorusme_tarihi":
                self.gorusme_tarihi.text.strip(),

            "yer":
                self.secili_yer,

            "musteri":
                self.musteri.text.strip(),

            "telefon":
                self.telefon.text.strip(),

            "aciklama":
                self.aciklama.text.strip(),

            "durum":
                self.durum.text,

            "baslangic":
                self.baslangic.text.strip(),

            "bitis":
                self.bitis.text.strip(),

            "gelir":
                gelir,

            "alinan_tarihi":
                self.alinan_tarihi.text.strip(),

            "iscilik":
                iscilik,

            "gider":
                gider,

            "diger_giderler":
                diger_giderler,

            "malzemeli":
                self.malzemeli,

            "malzemeler":
                self.malzemeler,

            "fotograflar":
                self.foto_secici.dosyalar,

            "ses_kayitlari":
                self.ses_kaydedici.dosyalar,

            "tarih":
                kayit_tarihi(
                    self.baslangic.text
                )
        }

        isler = oku(
            ISLER_DOSYASI
        )

        isler.append(veri)

        kaydet(
            ISLER_DOSYASI,
            isler
        )

        self.temizle()

        self.manager.current = "ana"

    def temizle(self):

        kutular = [
            self.gorusme_tarihi,
            self.musteri,
            self.telefon,
            self.aciklama,
            self.baslangic,
            self.bitis,
            self.gelir,
            self.alinan_tarihi,
            self.iscilik,
            self.malzeme_adi,
            self.malzeme_adet,
            self.malzeme_fiyat
        ]

        for kutu in kutular:
            kutu.text = ""

        self.secili_yer = ""

        self.yer_label.text = (
            "Yer: seçilmedi"
        )

        self.durum.text = (
            "Devam ediyor"
        )

        self.gider_kutusu.clear_widgets()

        self.gider_satirlari = []

        self.gider_satiri_ekle()

        self.malzemeler = []

        self.malzeme_birim.text = "Adet"

        self.malzemeleri_goster()

        self.foto_secici.yukle([])

        self.ses_kaydedici.yukle([])


# =========================================================
# GEÇMİŞ İŞLER
# =========================================================

class Gecmis(Screen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        ana = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )

        ana.add_widget(
            ust_baslik(
                self,
                "📚 GEÇMİŞ İŞLER",
                "ana"
            )
        )

        filtre = BoxLayout(
            size_hint_y=None,
            height=dp(58),
            spacing=dp(6)
        )

        self.arama = giris(
            "🔎 İş / müşteri / yer ara"
        )

        self.filtre_durum = Spinner(
            text="Tümü",
            values=(
                "Tümü",
                "Devam ediyor",
                "Bitti",
                "Beklemede"
            ),
            font_size=17,
            background_normal="",
            background_color=GIRIS,
            color=GIRIS_METIN
        )

        filtre.add_widget(
            self.arama
        )

        filtre.add_widget(
            self.filtre_durum
        )

        self.arama.bind(
            text=lambda *_:
            self.yenile()
        )

        self.filtre_durum.bind(
            text=lambda *_:
            self.yenile()
        )

        ana.add_widget(filtre)

        scroll = ScrollView()

        self.liste = BoxLayout(
            orientation="vertical",
            spacing=dp(11),
            size_hint_y=None
        )

        self.liste.bind(
            minimum_height=
            self.liste.setter("height")
        )

        scroll.add_widget(
            self.liste
        )

        ana.add_widget(scroll)

        self.add_widget(ana)

        klavye_uyumu(
            scroll,
            self.arama
        )

    def on_enter(self):

        self.yenile()

    def _tarih_rozeti(self, baslik, tarih):

        # Küçük, koyu zeminli, yuvarlak köşeli bir "rozet"
        # kart: üstte soluk küçük başlık (📅 Başlangıç gibi),
        # altında büyük+kalın+beyaz tarih. Eskiden tek bir
        # soluk gri Label içinde üst üste iki satırdı ve
        # tarih kısmı okunmuyordu; artık kendi kartı ve
        # yüksek kontrastlı beyaz rengiyle net okunuyor.

        kutu = BoxLayout(
            orientation="vertical",
            padding=[dp(6), dp(5)],
            spacing=dp(2)
        )

        with kutu.canvas.before:

            Color(*KART_KOYU)

            kutu._zemin = RoundedRectangle(
                pos=kutu.pos,
                size=kutu.size,
                radius=[dp(8)]
            )

        kutu.bind(
            pos=lambda o, v:
            setattr(o._zemin, "pos", v),
            size=lambda o, v:
            setattr(o._zemin, "size", v)
        )

        baslik_lbl = Label(
            text=baslik,
            font_size=12,
            bold=True,
            color=SOLUK,
            halign="center",
            valign="middle",
            size_hint_y=0.42
        )

        baslik_lbl.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )

        tarih_lbl = Label(
            text=str(tarih),
            font_size=15,
            bold=True,
            color=BEYAZ,
            halign="center",
            valign="middle",
            size_hint_y=0.58
        )

        tarih_lbl.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )

        kutu.add_widget(baslik_lbl)
        kutu.add_widget(tarih_lbl)

        return kutu

    def yenile(self):

        self.liste.clear_widgets()

        isler = oku(
            ISLER_DOSYASI
        )

        arama = (
            self.arama.text
            .lower()
            .strip()
        )

        for index in range(
            len(isler) - 1,
            -1,
            -1
        ):

            is_ = isler[index]

            durum = is_durumu(
                is_
            )

            arama_metni = (
                f"{is_.get('is_adi', '')} "
                f"{is_.get('musteri', '')} "
                f"{is_.get('yer', '')}"
            ).lower()

            if (
                arama
                and
                arama not in arama_metni
            ):
                continue

            if (
                self.filtre_durum.text
                != "Tümü"
                and
                durum
                != self.filtre_durum.text
            ):
                continue

            musteri = is_.get(
                "musteri",
                "Belirtilmemiş"
            ) or "Belirtilmemiş"

            yer = is_.get(
                "yer",
                "Yer belirtilmemiş"
            )

            baslangic_tarihi = (
                is_.get("baslangic", "")
                or "-"
            )

            gorusme_tarihi = (
                is_.get("gorusme_tarihi", "")
                or "-"
            )

            kart = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(155),
                spacing=dp(7)
            )

            ust_satir = BoxLayout(
                size_hint_y=None,
                height=dp(110),
                spacing=dp(6)
            )

            if durum == "Bitti":
                is_renk = KIRMIZI
            elif durum == "Beklemede":
                is_renk = YESIL
            else:
                is_renk = BEYAZ

            # Başlıkta artık iş/proje adı değil, iş sahibinin
            # (müşterinin) adı gösterilir.
            detay_btn = buton(
                f"👤  {musteri}\n\n"
                f"📍  {yer}",
                renk=is_renk,
                yukseklik=110,
                font=20
            )

            detay_btn.halign = "left"
            detay_btn.valign = "middle"

            detay_btn.size_hint_x = 0.60

            detay_btn.bind(
                width=lambda obj, val:
                setattr(
                    obj,
                    "text_size",
                    (
                        val - dp(28),
                        None
                    )
                )
            )

            detay_btn.bind(
                on_press=lambda _, i=index:
                self.detay_ac(i)
            )

            ust_satir.add_widget(
                detay_btn
            )

            # Butonun sağ tarafında, iki ayrı "rozet" kart
            # halinde: işin başladığı (seçilen) tarih ve
            # görüşme/anlaşma tarihi. Önceden tek satırlık
            # soluk gri yazıydı ve tarih kısmı zor okunuyordu;
            # şimdi her biri kendi koyu zeminli kartında, küçük
            # soluk bir başlık + büyük beyaz kalın tarih olarak
            # gösteriliyor.
            tarih_kutusu = BoxLayout(
                orientation="vertical",
                size_hint_x=0.40,
                spacing=dp(6)
            )

            tarih_kutusu.add_widget(
                self._tarih_rozeti(
                    "📅 Başlangıç",
                    baslangic_tarihi
                )
            )

            tarih_kutusu.add_widget(
                self._tarih_rozeti(
                    "🤝 Görüşme",
                    gorusme_tarihi
                )
            )

            ust_satir.add_widget(
                tarih_kutusu
            )

            kart.add_widget(
                ust_satir
            )

            sil = buton(
                "🗑 BU İŞİ SİL",
                yukseklik=42,
                font=16
            )

            sil.bind(
                on_press=lambda _, i=index:
                self.sil(i)
            )

            kart.add_widget(sil)

            self.liste.add_widget(
                kart
            )

        if not self.liste.children:

            self.liste.add_widget(
                Label(
                    text="Kayıt bulunamadı.",
                    font_size=20,
                    color=SOLUK,
                    size_hint_y=None,
                    height=dp(70)
                )
            )

    def detay_ac(
        self,
        index
    ):

        detay = self.manager.get_screen(
            "detay"
        )

        detay.is_index = index

        detay.yukle()

        self.manager.current = "detay"

    def sil(
        self,
        index
    ):

        isler = oku(
            ISLER_DOSYASI
        )

        if 0 <= index < len(isler):

            del isler[index]

            kaydet(
                ISLER_DOSYASI,
                isler
            )

            self.yenile()


# =========================================================
# İŞ DETAY
# =========================================================

class IsDetay(Screen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.is_index = None
        self.malzemeler = []

        # Yeni tasarım: YeniIs ile aynı koyu lacivert zemin.
        with self.canvas.before:

            Color(*KOYU_ZEMIN)

            self._form_zemin = Rectangle(
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=lambda obj, val:
            setattr(self._form_zemin, "pos", val),
            size=lambda obj, val:
            setattr(self._form_zemin, "size", val)
        )

        ana = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(7)
        )

        ana.add_widget(
            ust_baslik(
                self,
                "🔨 İŞ DETAYI",
                "gecmis"
            )
        )

        makbuz_btn = buton(
            "🧾 GEÇMİŞTEN MAKBUZ ÇIKAR",
            renk=SARI,
            yukseklik=58,
            font=17
        )

        makbuz_btn.color = SARI_METIN

        makbuz_btn.bind(
            on_press=self.makbuz_olustur
        )

        ana.add_widget(makbuz_btn)

        scroll = ScrollView()

        self.scroll = scroll

        form = BoxLayout(
            orientation="vertical",
            spacing=dp(14),
            size_hint_y=None
        )

        form.bind(
            minimum_height=
            form.setter("height")
        )

        # ---- BÖLÜM 1: GENEL BİLGİLER ----
        kart_genel = bolum_karti(
            "📋 Genel Bilgiler"
        )

        self.gorusme_tarihi = TarihInput(
            hint_text=
            "📅 Görüşme / Anlaşma tarihi - "
            "dokun ve seç",
            size_hint_y=None,
            height=dp(58),
            on_tarih=self.tarih_sec
        )

        self.musteri = giris_koyu(
            "Müşteri / iş sahibi"
        )

        self.telefon = giris_koyu(
            "Telefon"
        )

        self.yer = giris_koyu(
            "Yer"
        )

        self.aciklama = giris_koyu(
            "Açıklama / notlar",
            multiline=True,
            height=125
        )

        self.baslangic = giris_koyu(
            "Başlangıç tarihi"
        )

        self.bitis = giris_koyu(
            "Bitiş tarihi"
        )

        self.gelir = giris_koyu(
            "Gelir",
            input_filter="float"
        )

        self.alinan_tarihi = TarihInput(
            hint_text="📅 Alınan tarihi",
            size_hint_y=None,
            height=dp(58),
            on_tarih=self.tarih_sec
        )

        self.iscilik = giris_koyu(
            "İşçilik",
            input_filter="float"
        )

        self.durum = Spinner(
            text="Devam ediyor",
            values=(
                "Devam ediyor",
                "Bitti",
                "Beklemede"
            ),
            size_hint_y=None,
            height=dp(58),
            font_size=18,
            background_normal="",
            background_color=FORM_GIRIS,
            color=FORM_GIRIS_YAZI
        )

        kart_genel.add_widget(self.gorusme_tarihi)
        kart_genel.add_widget(self.musteri)
        kart_genel.add_widget(self.telefon)
        kart_genel.add_widget(self.yer)
        kart_genel.add_widget(self.durum)
        kart_genel.add_widget(self.aciklama)
        kart_genel.add_widget(self.baslangic)
        kart_genel.add_widget(self.bitis)

        form.add_widget(kart_genel)

        # ---- BÖLÜM 2: EKLER (FOTOĞRAF / SES) ----
        kart_ekler = bolum_karti(
            "📎 Ekler (Fotoğraf / Ses)"
        )

        self.foto_secici = FotografSecici()
        kart_ekler.add_widget(self.foto_secici)

        self.ses_kaydedici = SesKaydedici(
            uyari_callback=uyari_popup
        )
        kart_ekler.add_widget(self.ses_kaydedici)

        form.add_widget(kart_ekler)

        # ---- BÖLÜM 3: MALİ BİLGİLER ----
        kart_mali = bolum_karti(
            "💰 Mali Bilgiler"
        )

        kart_mali.add_widget(
            etiketli_alan(
                "İşçilik",
                self.iscilik
            )
        )

        kart_mali.add_widget(
            etiketli_alan_tarihli(
                "Alınan",
                self.gelir,
                self.alinan_tarihi
            )
        )

        form.add_widget(kart_mali)

        # ---- BÖLÜM 4: DİĞER GİDERLER ----
        kart_gider = bolum_karti(
            "💸 Diğer Giderler"
        )

        self.gider_kutusu = BoxLayout(
            orientation="vertical",
            spacing=dp(7),
            size_hint_y=None
        )

        self.gider_kutusu.bind(
            minimum_height=
            self.gider_kutusu.setter("height")
        )

        kart_gider.add_widget(
            self.gider_kutusu
        )

        self.gider_satirlari = []

        form.add_widget(kart_gider)

        # ---- BÖLÜM 5: MALZEMELER ----
        kart_malzeme = bolum_karti(
            "📦 Malzemeler"
        )

        self.malzemeli = True

        malzeme_secim_satir = BoxLayout(
            size_hint_y=None,
            height=dp(58),
            spacing=dp(8)
        )

        self.malzemeli_btn = buton(
            "📦 MALZEMELİ İŞ",
            renk=YESIL,
            yukseklik=56,
            font=16
        )

        self.malzemesiz_btn = buton(
            "🚫 MALZEMESİZ İŞ",
            yukseklik=56,
            font=16
        )

        self.malzemeli_btn.bind(
            on_press=lambda *_:
            self.malzeme_secim(True)
        )

        self.malzemesiz_btn.bind(
            on_press=lambda *_:
            self.malzeme_secim(False)
        )

        malzeme_secim_satir.add_widget(
            self.malzemeli_btn
        )

        malzeme_secim_satir.add_widget(
            self.malzemesiz_btn
        )

        kart_malzeme.add_widget(
            malzeme_secim_satir
        )

        self.malzeme_listesi = BoxLayout(
            orientation="vertical",
            spacing=dp(7),
            size_hint_y=None
        )

        self.malzeme_listesi.bind(
            minimum_height=
            self.malzeme_listesi.setter(
                "height"
            )
        )

        kart_malzeme.add_widget(
            self.malzeme_listesi
        )

        yeni_malzeme = buton(
            "＋ MALZEME EKLE",
            yukseklik=58,
            font=18
        )

        yeni_malzeme.bind(
            on_press=self.yeni_malzeme_ekle
        )

        kart_malzeme.add_widget(
            yeni_malzeme
        )

        form.add_widget(kart_malzeme)

        # ---- SONUÇ + KAYDET (kartların dışında, öne çıkar) ----
        # Yeni tasarımda ikisi tek satırda yan yana durur.
        self.alinacak_kutu = KirmiziKutu(
            text="ALINACAK TUTAR: 0.00 TL",
            font_size=15,
            bold=True,
            color=BEYAZ,
            halign="center",
            valign="middle",
            size_hint_x=0.40,
            size_hint_y=None,
            height=dp(66)
        )

        self.alinacak_kutu.bind(
            size=lambda obj, val:
            setattr(
                obj,
                "text_size",
                val
            )
        )

        kaydet_btn = buton(
            "💾 DEĞİŞİKLİKLERİ KAYDET",
            renk=YESIL,
            yukseklik=66,
            font=16
        )

        kaydet_btn.size_hint_x = 0.60

        kaydet_btn.bind(
            on_press=self.kaydet
        )

        sonuc_satir = BoxLayout(
            size_hint_y=None,
            height=dp(66),
            spacing=dp(10)
        )

        sonuc_satir.add_widget(
            self.alinacak_kutu
        )

        sonuc_satir.add_widget(
            kaydet_btn
        )

        form.add_widget(
            sonuc_satir
        )

        # Bazı telefonlarda alttaki gezinme çubuğu / ekran
        # kenarı kaydet butonunu kapatıp basılmasını
        # zorlaştırabiliyor. Butonun altına görünmez, işlevsiz
        # bir boşluk ekleyerek butonu biraz yukarı taşıyoruz;
        # buton yine de formun en altında kalıyor.
        form.add_widget(
            Widget(
                size_hint_y=None,
                height=dp(48)
            )
        )

        scroll.add_widget(form)

        ana.add_widget(scroll)

        self.add_widget(ana)

        self.gelir.bind(
            text=self._alinacak_guncelle
        )

        self.iscilik.bind(
            text=self._alinacak_guncelle
        )

        self._alinacak_guncelle()

    def _alinacak_guncelle(self, *args):

        iscilik = para(
            self.iscilik.text
        )

        malzeme_toplami = sum(
            para(m.get("fiyat", 0))
            for m in self.malzemeler
        )

        alinan = para(
            self.gelir.text
        )

        alinacak = alinacak_hesapla(
            self.malzemeli,
            iscilik,
            malzeme_toplami,
            alinan
        )

        self.alinacak_kutu.text = (
            "ALINACAK TUTAR: "
            f"{alinacak:.2f} TL"
        )

    def tarih_sec(
        self,
        widget
    ):

        TakvimPopup(widget).open()

    GIDER_KATEGORILERI = (
        "Yakıt",
        "Gıda",
        "Malzeme Özel",
        "Yardımcı Eleman"
    )

    def gider_satiri_ekle(
        self,
        kategori_sec=GIDER_PLACEHOLDER,
        tutar_deger=""
    ):

        satir = BoxLayout(
            size_hint_y=None,
            height=dp(58),
            spacing=dp(7)
        )

        kategori = Spinner(
            text=kategori_sec,
            values=self.GIDER_KATEGORILERI,
            size_hint_x=.42,
            size_hint_y=None,
            height=dp(58),
            font_size=16,
            background_normal="",
            background_color=FORM_GIRIS,
            color=FORM_GIRIS_YAZI
        )

        tutar = giris_koyu(
            "Tutar (TL)",
            input_filter="float"
        )

        tutar.text = tutar_deger

        satir.add_widget(kategori)
        satir.add_widget(tutar)

        self.gider_kutusu.add_widget(satir)

        kayit = {
            "satir": satir,
            "kategori": kategori,
            "tutar": tutar
        }

        self.gider_satirlari.append(kayit)

        klavye_uyumu(
            self.scroll,
            tutar
        )

        tutar.bind(
            text=lambda instance, deger, kayit=kayit:
            self._gider_yazildi(kayit, deger)
        )

    def _gider_yazildi(
        self,
        kayit,
        deger
    ):

        if (
            deger.strip()
            and kayit is self.gider_satirlari[-1]
        ):
            self.gider_satiri_ekle()

    def malzeme_secim(self, malzemeli):

        self.malzemeli = malzemeli

        if malzemeli:

            self.malzemeli_btn.renk_degistir(
                YESIL
            )

            self.malzemesiz_btn.renk_degistir(
                None
            )

        else:

            self.malzemeli_btn.renk_degistir(
                None
            )

            self.malzemesiz_btn.renk_degistir(
                KIRMIZI
            )

        # Malzemeli/malzemesiz değiştirilse
        # bile malzeme listesi ekrandan
        # kaybolmasın, her zaman güncel
        # listeyle tekrar çizilsin.
        if hasattr(
            self,
            "malzeme_listesi"
        ):
            self.malzemeleri_goster()

    def on_enter(self):

        if self.is_index is not None:
            self.yukle()

    def yukle(self):

        isler = oku(
            ISLER_DOSYASI
        )

        if not (
            0 <= self.is_index < len(isler)
        ):
            return

        is_ = isler[self.is_index]

        self.gorusme_tarihi.text = is_.get(
            "gorusme_tarihi",
            ""
        )

        self.musteri.text = is_.get(
            "musteri",
            ""
        )

        self.telefon.text = is_.get(
            "telefon",
            ""
        )

        self.yer.text = is_.get(
            "yer",
            ""
        )

        self.durum.text = is_.get(
            "durum",
            "Devam ediyor"
        )

        self.aciklama.text = is_.get(
            "aciklama",
            ""
        )

        self.baslangic.text = is_.get(
            "baslangic",
            ""
        )

        self.bitis.text = is_.get(
            "bitis",
            ""
        )

        self.gelir.text = str(
            is_.get(
                "gelir",
                0
            )
        )

        self.alinan_tarihi.text = is_.get(
            "alinan_tarihi",
            ""
        )

        self.iscilik.text = str(
            is_.get(
                "iscilik",
                0
            )
        )

        self.gider_kutusu.clear_widgets()
        self.gider_satirlari = []

        diger_giderler = is_.get(
            "diger_giderler",
            []
        )

        if diger_giderler:

            for dg in diger_giderler:

                self.gider_satiri_ekle(
                    kategori_sec=dg.get(
                        "kategori",
                        "Yakıt"
                    ),
                    tutar_deger=str(
                        para(dg.get("tutar", 0))
                    )
                )

        elif para(is_.get("gider", 0)) > 0:

            self.gider_satiri_ekle(
                kategori_sec="Yakıt",
                tutar_deger=str(
                    para(is_.get("gider", 0))
                )
            )

        self.gider_satiri_ekle()

        self.malzemeler = list(
            is_.get(
                "malzemeler",
                []
            )
        )

        self.malzeme_secim(
            is_.get("malzemeli", True)
        )

        self.malzemeleri_goster()

        self.foto_secici.yukle(
            is_.get("fotograflar", [])
        )

        self.ses_kaydedici.yukle(
            is_.get("ses_kayitlari", [])
        )

    def malzemeleri_goster(self):

        self.malzeme_listesi.clear_widgets()

        if not self.malzemeler:

            self.malzeme_listesi.add_widget(
                Label(
                    text="Malzeme yok.",
                    font_size=17,
                    color=SOLUK,
                    size_hint_y=None,
                    height=dp(45)
                )
            )

            self._alinacak_guncelle()

            return

        for i, m in enumerate(
            self.malzemeler
        ):

            odendi = m.get(
                "odendi",
                False
            )

            durum = (
                "✅ ÖDENDİ"
                if odendi
                else "⏳ ÖDENECEK"
            )

            birim = m.get(
                "birim",
                "Adet"
            )

            b = buton(
                f"{m.get('ad', '')}  "
                f"{m.get('adet', 1)} "
                f"{birim} • "
                f"{para(m.get('fiyat', 0)):.2f} TL\n"
                f"{durum}",
                yukseklik=65,
                font=16
            )

            b.bind(
                on_press=lambda _, x=i:
                self.odeme_degistir(x)
            )

            self.malzeme_listesi.add_widget(
                b
            )

            sil = buton(
                "🗑 MALZEMEYİ SİL",
                yukseklik=38,
                font=14
            )

            sil.bind(
                on_press=lambda _, x=i:
                self.malzeme_sil(x)
            )

            self.malzeme_listesi.add_widget(
                sil
            )

        self._alinacak_guncelle()

    def odeme_degistir(
        self,
        index
    ):

        if 0 <= index < len(
            self.malzemeler
        ):

            self.malzemeler[index][
                "odendi"
            ] = not self.malzemeler[index].get(
                "odendi",
                False
            )

            self.malzemeleri_goster()

    def malzeme_sil(
        self,
        index
    ):

        if not (
            0 <= index < len(
                self.malzemeler
            )
        ):
            return

        malzeme = self.malzemeler[index]

        kutu = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(12)
        )

        kutu.add_widget(
            Label(
                text=(
                    "🗑 "
                    f"{malzeme.get('ad', '')} "
                    "silinsin mi?\n"
                    "Emin misiniz?"
                ),
                font_size=18,
                color=BEYAZ,
                halign="center"
            )
        )

        butonlar = BoxLayout(
            size_hint_y=None,
            height=dp(56),
            spacing=dp(8)
        )

        vazgec = buton(
            "VAZGEÇ",
            yukseklik=54,
            font=17
        )

        evet = buton(
            "EVET, SİL",
            renk=KIRMIZI,
            yukseklik=54,
            font=17
        )

        butonlar.add_widget(vazgec)
        butonlar.add_widget(evet)

        kutu.add_widget(butonlar)

        popup = Popup(
            title="Malzemeyi Sil",
            content=kutu,
            size_hint=(.86, .40)
        )

        vazgec.bind(
            on_press=lambda *_:
            popup.dismiss()
        )

        def sil_onayla(instance):

            del self.malzemeler[index]

            popup.dismiss()

            self.malzemeleri_goster()

        evet.bind(
            on_press=sil_onayla
        )

        popup.open()

    def yeni_malzeme_ekle(
        self,
        instance
    ):

        kutu = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )

        ad = giris_koyu(
            "Malzeme adı"
        )

        adet = giris_koyu(
            "Miktar",
            input_filter="int"
        )

        birim = Spinner(
            text="Adet",
            values=(
                "Adet",
                "LT",
                "M",
                "KG",
                "Kutu",
                "Çuval"
            ),
            size_hint_y=None,
            height=dp(58),
            font_size=17,
            background_normal="",
            background_color=FORM_GIRIS,
            color=FORM_GIRIS_YAZI
        )

        fiyat = giris_koyu(
            "Fiyat",
            input_filter="float"
        )

        ekle = buton(
            "EKLE",
            yukseklik=56,
            font=18
        )

        kutu.add_widget(ad)
        kutu.add_widget(adet)
        kutu.add_widget(birim)
        kutu.add_widget(fiyat)
        kutu.add_widget(ekle)

        popup = Popup(
            title="Malzeme Ekle",
            content=kutu,
            size_hint=(.90, .72)
        )

        def ekle_malzeme(instance):

            ad_ = ad.text.strip()

            if not ad_:
                return

            try:
                adet_ = int(
                    adet.text or 1
                )
            except Exception:
                adet_ = 1

            try:
                fiyat_ = float(
                    fiyat.text or 0
                )
            except Exception:
                fiyat_ = 0

            self.malzemeler.append({

                "ad": ad_,

                "adet": adet_,

                "birim": birim.text,

                "birim_fiyat": fiyat_,

                "fiyat":
                    adet_ * fiyat_,

                "odendi": False
            })

            popup.dismiss()

            self.malzemeleri_goster()

        ekle.bind(
            on_press=ekle_malzeme
        )

        popup.open()

    def kaydet(
        self,
        instance
    ):

        isler = oku(
            ISLER_DOSYASI
        )

        if not (
            0 <= self.is_index < len(isler)
        ):
            return

        is_ = isler[
            self.is_index
        ]

        is_["gorusme_tarihi"] = (
            self.gorusme_tarihi.text.strip()
        )

        if not is_.get("is_adi"):

            is_["is_adi"] = (
                self.musteri.text.strip()
                or "İsimsiz İş"
            )

        is_["musteri"] = (
            self.musteri.text.strip()
        )

        is_["telefon"] = (
            self.telefon.text.strip()
        )

        is_["yer"] = (
            self.yer.text.strip()
        )

        is_["durum"] = (
            self.durum.text
        )

        is_["aciklama"] = (
            self.aciklama.text.strip()
        )

        is_["baslangic"] = (
            self.baslangic.text.strip()
        )

        is_["bitis"] = (
            self.bitis.text.strip()
        )

        is_["gelir"] = para(
            self.gelir.text
        )

        is_["alinan_tarihi"] = (
            self.alinan_tarihi.text.strip()
        )

        is_["iscilik"] = para(
            self.iscilik.text
        )

        diger_giderler = []
        gider = 0

        for kayit in self.gider_satirlari:

            tutar = para(
                kayit["tutar"].text
            )

            if tutar > 0:

                if (
                    kayit["kategori"].text
                    == GIDER_PLACEHOLDER
                ):

                    uyari_popup(
                        "Tutar girdiğiniz gider "
                        "satırı için lütfen bir "
                        "gider türü seçin."
                    )

                    return

                gider += tutar

                diger_giderler.append({
                    "kategori":
                        kayit["kategori"].text,
                    "tutar":
                        tutar
                })

        is_["gider"] = gider

        is_["diger_giderler"] = (
            diger_giderler
        )

        is_["malzemeli"] = (
            self.malzemeli
        )

        is_["malzemeler"] = (
            self.malzemeler
        )

        is_["fotograflar"] = (
            self.foto_secici.dosyalar
        )

        is_["ses_kayitlari"] = (
            self.ses_kaydedici.dosyalar
        )

        # Rapor/ay filtresi başlangıç
        # tarihine göre güncellensin.
        if self.baslangic.text.strip():

            is_["tarih"] = kayit_tarihi(
                self.baslangic.text
            )

        elif "tarih" not in is_:

            is_["tarih"] = (
                datetime.now().strftime(
                    "%d.%m.%Y %H:%M"
                )
            )

        kaydet(
            ISLER_DOSYASI,
            isler
        )

        self.manager.current = "gecmis"

    def makbuz_olustur(
        self,
        instance
    ):

        isler = oku(
            ISLER_DOSYASI
        )

        if not (
            0 <= self.is_index < len(isler)
        ):
            return

        is_ = isler[self.is_index]

        try:

            dosya_yolu, ozet = makbuz_pdf_olustur(
                is_
            )

        except Exception as e:

            self._makbuz_hata_goster(
                str(e)
            )

            return

        self._makbuz_hazir_popup(
            dosya_yolu,
            ozet
        )

    def _makbuz_hata_goster(self, mesaj):

        kutu = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(10)
        )

        kutu.add_widget(
            Label(
                text=(
                    "Makbuz oluşturulamadı:\n"
                    + mesaj
                ),
                font_size=15,
                color=BUTON_METIN
            )
        )

        kapat = buton(
            "KAPAT",
            yukseklik=52,
            font=16
        )

        kutu.add_widget(kapat)

        popup = Popup(
            title="Hata",
            content=kutu,
            size_hint=(.88, .45)
        )

        kapat.bind(
            on_press=lambda *_:
            popup.dismiss()
        )

        popup.open()

    def _makbuz_onizleme_karti(self, ozet):

        # PDF'in aynı bilgilerini gösteren, gerçek bir
        # makbuz gibi görünen beyaz bir önizleme kartı.
        # Kullanıcı paylaşmadan önce içeriği kontrol
        # edebilsin diye eklendi.

        kart = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(14), dp(12)],
            spacing=dp(4)
        )

        kart.bind(
            minimum_height=kart.setter("height")
        )

        with kart.canvas.before:

            Color(0.97, 0.97, 0.98, 1)

            kart._zemin = RoundedRectangle(
                pos=kart.pos,
                size=kart.size,
                radius=[dp(10)]
            )

        kart.bind(
            pos=lambda o, v: setattr(
                o._zemin, "pos", v
            ),
            size=lambda o, v: setattr(
                o._zemin, "size", v
            )
        )

        def satir_ekle(
            metin,
            font_size=13,
            bold=False,
            renk=(0.15, 0.15, 0.17, 1),
            ust_bosluk=0
        ):

            lbl = Label(
                text=metin,
                font_size=font_size,
                bold=bold,
                color=renk,
                halign="left",
                valign="middle",
                size_hint_y=None,
                height=dp(20 + ust_bosluk)
            )

            lbl.bind(
                size=lambda o, v:
                setattr(o, "text_size", v)
            )

            kart.add_widget(lbl)

        satir_ekle(
            ozet["firma_adi"],
            font_size=16,
            bold=True
        )

        if ozet["firma_telefon"]:
            satir_ekle(
                "Tel: " + ozet["firma_telefon"],
                renk=(0.4, 0.4, 0.45, 1)
            )

        satir_ekle(
            f"Makbuz No: {ozet['makbuz_no']}    "
            f"{ozet['tarih']}",
            font_size=12,
            renk=(0.4, 0.4, 0.45, 1),
            ust_bosluk=4
        )

        satir_ekle(
            "Müşteri: " + ozet["musteri"],
            ust_bosluk=6
        )

        satir_ekle(
            "Telefon: " + ozet["telefon"]
        )

        for etiket, tutar in ozet["satirlar"]:
            satir_ekle(
                f"{etiket}: {tutar:,.2f} TL",
                ust_bosluk=4
            )

        satir_ekle(
            f"TOPLAM: {ozet['toplam']:,.2f} TL",
            font_size=15,
            bold=True,
            ust_bosluk=6
        )

        satir_ekle(
            f"Ödenen: {ozet['alinan']:,.2f} TL"
        )

        satir_ekle(
            f"Kalan: {ozet['kalan']:,.2f} TL"
        )

        durum_lbl = Label(
            text=ozet["odeme_durumu"],
            font_size=13,
            bold=True,
            color=BEYAZ,
            size_hint_y=None,
            height=dp(30)
        )

        with durum_lbl.canvas.before:

            Color(*ozet["durum_renk"])

            durum_lbl._zemin = RoundedRectangle(
                pos=durum_lbl.pos,
                size=durum_lbl.size,
                radius=[dp(8)]
            )

        durum_lbl.bind(
            pos=lambda o, v: setattr(
                o._zemin, "pos", v
            ),
            size=lambda o, v: setattr(
                o._zemin, "size", v
            )
        )

        kart.add_widget(Widget(
            size_hint_y=None, height=dp(4)
        ))

        kart.add_widget(durum_lbl)

        return kart

    def _makbuz_hazir_popup(
        self,
        dosya_yolu,
        ozet
    ):

        kutu = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(10)
        )

        kutu.add_widget(
            Label(
                text="✅ Makbuz oluşturuldu",
                font_size=16,
                bold=True,
                color=BUTON_METIN,
                halign="center",
                size_hint_y=None,
                height=dp(26)
            )
        )

        onizleme_scroll = ScrollView(
            size_hint=(1, 1)
        )

        onizleme_scroll.add_widget(
            self._makbuz_onizleme_karti(ozet)
        )

        kutu.add_widget(onizleme_scroll)

        paylas = buton(
            "📤 PAYLAŞ",
            renk=YESIL,
            yukseklik=58,
            font=18
        )

        kapat = buton(
            "KAPAT",
            yukseklik=52,
            font=16
        )

        kutu.add_widget(paylas)
        kutu.add_widget(kapat)

        popup = Popup(
            title="Makbuz Önizleme",
            content=kutu,
            size_hint=(.92, .86)
        )

        def paylas_yap(*_):

            basarili, hata = makbuz_paylas(
                dosya_yolu
            )

            if not basarili:

                paylasim_hata_label = Label(
                    text=(
                        "Paylaşım açılamadı: "
                        + (hata or "bilinmeyen hata")
                        + "\nDosya kaydedildi:\n"
                        + dosya_yolu
                    ),
                    font_size=13,
                    color=SOLUK,
                    size_hint_y=None,
                    halign="center",
                    valign="middle",
                    text_size=(
                        kutu.width - dp(28), None
                    )
                )

                paylasim_hata_label.bind(
                    texture_size=lambda obj, val:
                    setattr(obj, "height", val[1])
                )

                kutu.add_widget(paylasim_hata_label)

        paylas.bind(
            on_press=paylas_yap
        )

        kapat.bind(
            on_press=lambda *_:
            popup.dismiss()
        )

        popup.open()


# =========================================================
# GELİR / GİDER
# =========================================================

class GelirGider(Screen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        simdi = datetime.now()

        self.secili_yil = simdi.year
        self.secili_ay = simdi.month

        ana = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )

        ana.add_widget(
            ust_baslik(
                self,
                "₺ GELİR / GİDER",
                "ana"
            )
        )

        ay_satir = BoxLayout(
            size_hint_y=None,
            height=dp(58),
            spacing=dp(7)
        )

        onceki = buton(
            "‹",
            yukseklik=56,
            font=30
        )

        onceki.size_hint_x = .18

        onceki.bind(
            on_press=self.onceki_ay
        )

        self.ay_baslik = Label(
            text="",
            font_size=20,
            bold=True,
            color=BEYAZ
        )

        sonraki = buton(
            "›",
            yukseklik=56,
            font=30
        )

        sonraki.size_hint_x = .18

        sonraki.bind(
            on_press=self.sonraki_ay
        )

        ay_satir.add_widget(onceki)
        ay_satir.add_widget(self.ay_baslik)
        ay_satir.add_widget(sonraki)

        ana.add_widget(ay_satir)

        scroll = ScrollView()

        icerik = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
            padding=[0, dp(2), 0, dp(10)]
        )

        icerik.bind(
            minimum_height=
            icerik.setter("height")
        )

        self._icerik = icerik

        # ---- 2x2 İSTATİSTİK IZGARASI (ana sayfa gibi
        # renkli / yuvarlak kartlar) ----
        izgara = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(204)
        )

        self.tahsilat_karti = IstatistikKarti(
            (0.20, 0.48, 0.40, 1),
            "✅",
            "Yapılan Tahsilat"
        )

        izgara.add_widget(
            self.tahsilat_karti
        )

        self.gider_karti = IstatistikKarti(
            (0.55, 0.24, 0.26, 1),
            "💸",
            "Diğer Gider"
        )

        izgara.add_widget(
            self.gider_karti
        )

        self.malzeme_karti = IstatistikKarti(
            (0.28, 0.42, 0.62, 1),
            "📦",
            "Malzeme"
        )

        izgara.add_widget(
            self.malzeme_karti
        )

        self.iscilik_karti = IstatistikKarti(
            (0.44, 0.38, 0.56, 1),
            "👷",
            "İşçilik"
        )

        izgara.add_widget(
            self.iscilik_karti
        )

        icerik.add_widget(izgara)

        # ---- YEŞİL KÂR KARTI (GRADYAN, ana sayfadaki
        # kazanç kartıyla aynı görsel dil) ----
        self.kar_kart = GradyanKart(
            renk_koyu=KAR_KART_KOYU,
            renk_acik=KAR_KART_ACIK,
            orientation="vertical",
            size_hint_y=None,
            height=dp(108),
            padding=[dp(18), dp(14)],
            spacing=dp(2)
        )

        kar_baslik_lbl = Label(
            text="✅ Bu Ayın Kârı",
            font_size=16,
            bold=True,
            color=BEYAZ,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(24)
        )

        kar_baslik_lbl.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )

        self.kar_kart.add_widget(kar_baslik_lbl)

        self.kar_tutar_lbl = Label(
            text="0 TL",
            font_size=32,
            bold=True,
            color=KAR_YAZI,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(44)
        )

        self.kar_tutar_lbl.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )

        self.kar_kart.add_widget(self.kar_tutar_lbl)

        icerik.add_widget(self.kar_kart)

        # ---- KIRMIZI "KALAN TAHSİLAT" KARTI (GRADYAN) ----
        # Sadece bitmiş ama parası tam alınmamış iş
        # varsa görünür; altında hangi işten ne kadar
        # kaldığı listelenir. Yoksa listeden tamamen
        # kaldırılır.
        self.kalan_kart = GradyanKart(
            renk_koyu=ALACAK_KART_KOYU,
            renk_acik=ALACAK_KART_ACIK,
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(18), dp(14)],
            spacing=dp(6)
        )

        self.kalan_kart.bind(
            minimum_height=
            self.kalan_kart.setter("height")
        )

        kalan_baslik_lbl = Label(
            text="🔴 Kalan Tahsilat",
            font_size=16,
            bold=True,
            color=BEYAZ,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(24)
        )

        kalan_baslik_lbl.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )

        self.kalan_kart.add_widget(kalan_baslik_lbl)

        self.kalan_tutar_lbl = Label(
            text="0 TL",
            font_size=28,
            bold=True,
            color=ALACAK_YAZI,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(38)
        )

        self.kalan_tutar_lbl.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )

        self.kalan_kart.add_widget(self.kalan_tutar_lbl)

        self.kalan_liste_lbl = Label(
            text="",
            font_size=15,
            bold=True,
            color=BEYAZ,
            halign="left",
            valign="top",
            size_hint_y=None
        )

        self.kalan_liste_lbl.bind(
            width=lambda obj, val:
            setattr(
                obj,
                "text_size",
                (val, None)
            ),
            texture_size=lambda obj, val:
            setattr(
                obj,
                "height",
                val[1]
            )
        )

        self.kalan_kart.add_widget(
            self.kalan_liste_lbl
        )

        # Başlangıçta gizli - sadece kalan tahsilat
        # varsa icerik'e eklenir (yenile() içinde).
        self._kalan_kart_gorunur = False

        scroll.add_widget(icerik)

        ana.add_widget(scroll)

        self.add_widget(ana)

    def onceki_ay(
        self,
        instance
    ):

        self.secili_ay -= 1

        if self.secili_ay == 0:
            self.secili_ay = 12
            self.secili_yil -= 1

        self.yenile()

    def sonraki_ay(
        self,
        instance
    ):

        self.secili_ay += 1

        if self.secili_ay == 13:
            self.secili_ay = 1
            self.secili_yil += 1

        self.yenile()

    def on_enter(self):

        self.yenile()

    def yenile(self):

        h = hesaplar(
            self.secili_yil,
            self.secili_ay
        )

        self.ay_baslik.text = (
            f"{TakvimPopup.AY_ISIMLERI[self.secili_ay - 1]} "
            f"{self.secili_yil}"
        )

        def tl_bicimle(deger):

            return "{:,.2f}".format(
                deger
            ).replace(",", ".")

        # ---- 2x2 İSTATİSTİK IZGARASI ----
        # Not: Bu 4 kart, işin "Bitti" olup olmadığına
        # bakmaksızın o ay içinde fiilen alınan/harcanan
        # gerçek tutarları gösterir (ör. iş bitmemiş olsa
        # bile alınan 3000 TL burada "Yapılan Tahsilat"
        # olarak görünür). Ana ekrandaki kazanç kartları ve
        # aşağıdaki "Bu Ayın Kârı" / "Kalan Tahsilat"
        # kartları bundan etkilenmez, eskisi gibi sadece
        # bitmiş işlerden hesaplanmaya devam eder.
        self.tahsilat_karti.tutar_ayarla(
            f"{tl_bicimle(h['ay_gelir_gercek'])} TL"
        )

        self.gider_karti.tutar_ayarla(
            f"{tl_bicimle(h['ay_gider_gercek'])} TL"
        )

        self.malzeme_karti.tutar_ayarla(
            f"{tl_bicimle(h['ay_malzeme_gercek'])} TL"
        )

        self.iscilik_karti.tutar_ayarla(
            f"{tl_bicimle(h['ay_iscilik_gercek'])} TL"
        )

        # ---- YEŞİL KÂR KARTI - her zaman gösterilir,
        # sadece bitmiş işlerden hesaplanır. ----
        self.kar_tutar_lbl.text = (
            f"{tl_bicimle(h['ay_net'])} TL"
        )

        # ---- KIRMIZI "KALAN TAHSİLAT" KARTI - sadece
        # bitmiş ama parası eksik alınan iş varsa
        # içeriğe eklenir. ----
        kalan_tahsilat = h["ay_alinacak"]
        kalan_isler = h["ay_kalan_isler"]

        if kalan_tahsilat > 0:

            self.kalan_tutar_lbl.text = (
                f"{tl_bicimle(kalan_tahsilat)} TL"
            )

            self.kalan_liste_lbl.text = "\n".join(
                f"• {is_kaydi['is_adi']}: "
                f"{tl_bicimle(is_kaydi['tutar'])} TL"
                for is_kaydi in kalan_isler
            )

            if not self._kalan_kart_gorunur:

                self._icerik.add_widget(
                    self.kalan_kart
                )

                self._kalan_kart_gorunur = True

        elif self._kalan_kart_gorunur:

            self._icerik.remove_widget(
                self.kalan_kart
            )

            self._kalan_kart_gorunur = False


# =========================================================
# MALZEME / ÖDEMELER
# =========================================================

class Malzemeler(Screen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        ana = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )

        ana.add_widget(
            ust_baslik(
                self,
                "📦 MALZEME / ÖDEMELER",
                "ana"
            )
        )

        ozet_satir = BoxLayout(
            spacing=dp(10),
            size_hint_y=None,
            height=dp(96)
        )

        self.toplam_karti = IstatistikKarti(
            (0.28, 0.42, 0.62, 1),
            "📦",
            "Toplam"
        )

        ozet_satir.add_widget(
            self.toplam_karti
        )

        self.odenecek_karti = IstatistikKarti(
            (0.58, 0.32, 0.34, 1),
            "⏳",
            "Ödenecek"
        )

        ozet_satir.add_widget(
            self.odenecek_karti
        )

        ana.add_widget(ozet_satir)

        scroll = ScrollView()

        self.liste = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None
        )

        self.liste.bind(
            minimum_height=
            self.liste.setter("height")
        )

        scroll.add_widget(
            self.liste
        )

        ana.add_widget(scroll)

        self.add_widget(ana)

    def on_enter(self):

        self.yenile()

    def yenile(self):

        self.liste.clear_widgets()

        isler = oku(
            ISLER_DOSYASI
        )

        toplam = 0
        odenecek = 0

        for is_ in isler:

            for m in is_.get(
                "malzemeler",
                []
            ):

                fiyat = para(
                    m.get(
                        "fiyat",
                        0
                    )
                )

                toplam += fiyat

                if not m.get(
                    "odendi",
                    False
                ):

                    odenecek += fiyat

        self.toplam_karti.tutar_ayarla(
            f"{toplam:.2f} TL"
        )

        self.odenecek_karti.tutar_ayarla(
            f"{odenecek:.2f} TL"
        )

        for i, is_ in enumerate(
            isler
        ):

            malzemeler = is_.get(
                "malzemeler",
                []
            )

            if not malzemeler:
                continue

            bekleyen_malzemeler = [

                m for m in malzemeler

                if not m.get(
                    "odendi",
                    False
                )
            ]

            if not bekleyen_malzemeler:
                continue

            self.liste.add_widget(
                Label(
                    text=(
                        f"🔨 "
                        f"{is_.get('is_adi', '')}"
                    ),
                    bold=True,
                    font_size=20,
                    color=BEYAZ,
                    size_hint_y=None,
                    height=dp(42)
                )
            )

            for j, m in enumerate(
                malzemeler
            ):

                # ÖDENENLER ARTIK
                # BU EKRANDA GÖSTERİLMEYECEK

                if m.get(
                    "odendi",
                    False
                ):
                    continue

                durum = (
                    "⏳ ÖDENECEK"
                )

                birim = m.get(
                    "birim",
                    "Adet"
                )

                b = buton(

                    f"{m.get('ad', '')} "
                    f"{m.get('adet', 1)} "
                    f"{birim} • "

                    f"{para(m.get('fiyat', 0)):.2f} TL • "

                    f"{durum}",

                    yukseklik=58,
                    font=16
                )

                b.bind(
                    on_press=lambda _, a=i, bidx=j:
                    self.odeme_degistir(
                        a,
                        bidx
                    )
                )

                self.liste.add_widget(b)

        if not self.liste.children:

            self.liste.add_widget(
                Label(
                    text=(
                        "Bekleyen malzeme "
                        "ödemesi yok."
                    ),
                    font_size=19,
                    color=SOLUK,
                    size_hint_y=None,
                    height=dp(70)
                )
            )

    def odeme_degistir(
        self,
        is_index,
        malzeme_index
    ):

        isler = oku(
            ISLER_DOSYASI
        )

        try:

            malzeme = (
                isler[is_index]
                ["malzemeler"]
                [malzeme_index]
            )

            malzeme["odendi"] = not (
                malzeme.get(
                    "odendi",
                    False
                )
            )

            kaydet(
                ISLER_DOSYASI,
                isler
            )

            self.yenile()

        except Exception:
            pass


# =========================================================
# RAPORLAR
# =========================================================

class Raporlar(Screen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        simdi = datetime.now()

        self.secili_yil = simdi.year
        self.secili_ay = simdi.month
        self.hepsi_mi = True

        ana = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )

        ana.add_widget(
            ust_baslik(
                self,
                "📊 RAPORLAR / GRAFİKLER",
                "ana"
            )
        )

        filtre_satir = BoxLayout(
            size_hint_y=None,
            height=dp(58),
            spacing=dp(7)
        )

        onceki = buton(
            "‹",
            yukseklik=56,
            font=30
        )

        onceki.size_hint_x = .16

        onceki.bind(
            on_press=self.onceki_ay
        )

        self.filtre_baslik = Label(
            text="TÜMÜ",
            font_size=19,
            bold=True,
            color=BEYAZ
        )

        sonraki = buton(
            "›",
            yukseklik=56,
            font=30
        )

        sonraki.size_hint_x = .16

        sonraki.bind(
            on_press=self.sonraki_ay
        )

        self.hepsi_buton = buton(
            "TÜMÜ",
            yukseklik=56,
            font=15
        )

        self.hepsi_buton.size_hint_x = .30

        self.hepsi_buton.bind(
            on_press=self.hepsini_goster
        )

        filtre_satir.add_widget(onceki)
        filtre_satir.add_widget(self.filtre_baslik)
        filtre_satir.add_widget(sonraki)
        filtre_satir.add_widget(self.hepsi_buton)

        ana.add_widget(filtre_satir)

        # ---- İŞ DURUMLARI (renkli / yuvarlak kartlar,
        # Gelir-Gider ekranındaki istatistik kartlarıyla
        # aynı görsel dil) ----
        durum_baslik = Label(
            text="📋 İŞ DURUMLARI",
            font_size=20,
            bold=True,
            color=BEYAZ,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(32)
        )

        durum_baslik.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )

        ana.add_widget(durum_baslik)

        durum_izgara = BoxLayout(
            spacing=dp(10),
            size_hint_y=None,
            height=dp(92)
        )

        self.devam_karti = IstatistikKarti(
            (0.24, 0.48, 0.42, 1),
            "🟢",
            "Devam eden"
        )

        durum_izgara.add_widget(
            self.devam_karti
        )

        self.bitti_karti = IstatistikKarti(
            (0.20, 0.48, 0.40, 1),
            "✅",
            "Biten"
        )

        durum_izgara.add_widget(
            self.bitti_karti
        )

        self.beklemede_karti = IstatistikKarti(
            (0.58, 0.32, 0.34, 1),
            "⏳",
            "Beklemede"
        )

        durum_izgara.add_widget(
            self.beklemede_karti
        )

        ana.add_widget(durum_izgara)

        scroll = ScrollView()

        self.icerik = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None
        )

        self.icerik.bind(
            minimum_height=
            self.icerik.setter("height")
        )

        scroll.add_widget(
            self.icerik
        )

        ana.add_widget(scroll)

        self.add_widget(ana)

    def onceki_ay(
        self,
        instance
    ):

        self.hepsi_mi = False

        self.secili_ay -= 1

        if self.secili_ay == 0:
            self.secili_ay = 12
            self.secili_yil -= 1

        self.yenile()

    def sonraki_ay(
        self,
        instance
    ):

        self.hepsi_mi = False

        self.secili_ay += 1

        if self.secili_ay == 13:
            self.secili_ay = 1
            self.secili_yil += 1

        self.yenile()

    def hepsini_goster(
        self,
        instance
    ):

        self.hepsi_mi = True

        self.yenile()

    def on_enter(self):

        self.yenile()

    def yenile(self):

        self.icerik.clear_widgets()

        if self.hepsi_mi:

            self.filtre_baslik.text = "TÜMÜ"

        else:

            self.filtre_baslik.text = (
                f"{TakvimPopup.AY_ISIMLERI[self.secili_ay - 1]} "
                f"{self.secili_yil}"
            )

        tum_isler = oku(
            ISLER_DOSYASI
        )

        if self.hepsi_mi:

            isler_indeksli = list(
                enumerate(tum_isler)
            )

        else:

            isler_indeksli = [
                (i, is_)
                for i, is_ in enumerate(tum_isler)
                if bu_ay_mi(
                    is_.get("tarih", ""),
                    self.secili_yil,
                    self.secili_ay
                )
            ]

        isler = [
            is_
            for _, is_ in isler_indeksli
        ]

        devam = 0
        bitti = 0
        beklemede = 0

        for is_ in isler:

            durum = is_durumu(
                is_
            )

            if durum == "Bitti":
                bitti += 1

            elif durum == "Beklemede":
                beklemede += 1

            else:
                devam += 1

        self.devam_karti.tutar_ayarla(
            str(devam)
        )

        self.bitti_karti.tutar_ayarla(
            str(bitti)
        )

        self.beklemede_karti.tutar_ayarla(
            str(beklemede)
        )

        self.icerik.add_widget(
            Label(
                text="📑 İŞ BAZLI DÖKÜM",
                font_size=22,
                bold=True,
                color=BEYAZ,
                size_hint_y=None,
                height=dp(42)
            )
        )

        if not isler:

            self.icerik.add_widget(
                Label(
                    text="Henüz iş kaydı yok.",
                    font_size=18,
                    color=SOLUK,
                    size_hint_y=None,
                    height=dp(50)
                )
            )

        for sira in range(
            len(isler_indeksli) - 1,
            -1,
            -1
        ):

            index, is_ = isler_indeksli[sira]

            is_adi = is_.get(
                "is_adi",
                "İsimsiz İş"
            )

            tarih = is_.get(
                "tarih",
                "Tarih yok"
            )

            iscilik = para(
                is_.get("iscilik", 0)
            )

            alinan = para(
                is_.get("gelir", 0)
            )

            malzeme_toplami = toplam_malzeme(
                is_
            )

            alinacak = alinacak_hesapla(
                is_.get("malzemeli", True),
                iscilik,
                malzeme_toplami,
                alinan
            )

            satirlar = [
                f"[b]🔨 {is_adi}[/b]",
                f"📅 {tarih}",
                f"👷 İşçilik: {iscilik:.2f} TL",
                f"💰 Alınan: {alinan:.2f} TL",
                f"📦 Malzeme: {malzeme_toplami:.2f} TL"
            ]

            diger_giderler = is_.get(
                "diger_giderler",
                []
            )

            if diger_giderler:

                for dg in diger_giderler:

                    kategori = dg.get(
                        "kategori",
                        "Diğer"
                    )

                    ikon = GIDER_IKONLARI.get(
                        kategori,
                        "💸"
                    )

                    satirlar.append(
                        f"{ikon} {kategori}: "
                        f"{para(dg.get('tutar', 0)):.2f} TL"
                    )

            elif para(is_.get("gider", 0)) > 0:

                satirlar.append(
                    f"💸 Diğer gider: "
                    f"{para(is_.get('gider', 0)):.2f} TL"
                )

            if alinacak > 0:

                satirlar.append(
                    "[color=D93333][b]🔴 Alınacak: "
                    f"{alinacak:.2f} TL[/b][/color]"
                )

            else:

                kar_is = (
                    alinan
                    - para(is_.get("gider", 0))
                )

                if is_.get("malzemeli", True):

                    kar_is -= malzeme_toplami

                satirlar.append(
                    "[color=33A64D][b]✅ Kâr: "
                    f"{kar_is:.2f} TL[/b][/color]"
                )

            metin = "\n".join(satirlar)

            kart_btn = buton(
                metin,
                yukseklik=40,
                font=17
            )

            kart_btn.markup = True
            kart_btn.halign = "left"
            kart_btn.valign = "top"
            kart_btn.padding = (
                dp(16),
                dp(16)
            )

            kart_btn.bind(
                width=lambda obj, val:
                setattr(
                    obj,
                    "text_size",
                    (val - dp(32), None)
                )
            )

            kart_btn.bind(
                texture_size=lambda obj, val:
                setattr(
                    obj,
                    "height",
                    val[1] + dp(32)
                )
            )

            kart_btn.bind(
                on_press=lambda _, i=index:
                self.detay_ac(i)
            )

            self.icerik.add_widget(
                kart_btn
            )

    def detay_ac(
        self,
        index
    ):

        detay = self.manager.get_screen(
            "detay"
        )

        detay.is_index = index

        detay.yukle()

        self.manager.current = "detay"


# =========================================================
# İŞ / FİRMA BİLGİLERİ DÜZENLEME (POPUP)
# =========================================================
# Makbuzlarda görünen Firma/Kişi Adı ve Telefon
# numarasını sonradan düzenlemek için kullanılır.
# İlk kurulumda (IlkKurulum) girilen bilgiler
# buradan güncellenebilir.

class IsBilgileriPopup(Popup):

    def __init__(self, ayarlar_ekrani, **kwargs):

        self.ayarlar_ekrani = ayarlar_ekrani

        super().__init__(
            title="İş / Firma Bilgilerini Düzenle",
            size_hint=(0.92, 0.62),
            auto_dismiss=True,
            **kwargs
        )

        mevcut = ayarlari_oku()

        govde = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(10)
        )

        self.firma_adi = giris(
            "Firma Adı / Kişi Adı"
        )

        self.firma_adi.text = mevcut.get(
            "firma_adi", ""
        )

        self.telefon = telefon_girisi(
            "Telefon Numarası"
        )

        self.telefon.text = mevcut.get(
            "telefon", ""
        )

        govde.add_widget(
            etiketli_alan(
                "Firma Adı / Kişi Adı",
                self.firma_adi
            )
        )

        govde.add_widget(
            etiketli_alan(
                "Telefon Numarası",
                self.telefon
            )
        )

        self.uyari = Label(
            text="",
            font_size=14,
            color=KIRMIZI,
            size_hint_y=None,
            height=dp(24)
        )

        govde.add_widget(self.uyari)

        govde.add_widget(Widget())

        alt_satir = BoxLayout(
            size_hint_y=None,
            height=dp(58),
            spacing=dp(8)
        )

        vazgec = buton(
            "VAZGEÇ",
            renk=KIRMIZI,
            yukseklik=58,
            font=18
        )

        vazgec.bind(
            on_press=lambda *_: self.dismiss()
        )

        kaydet = buton(
            "KAYDET",
            renk=YESIL,
            yukseklik=58,
            font=18
        )

        kaydet.bind(
            on_press=self.kaydet_et
        )

        alt_satir.add_widget(vazgec)
        alt_satir.add_widget(kaydet)

        govde.add_widget(alt_satir)

        # Telefonun alt kenarına / gezinme çubuğuna çok
        # yakın kalmasın diye butonların altına küçük,
        # görünmez bir boşluk bırakılıyor.
        govde.add_widget(
            Widget(
                size_hint_y=None,
                height=dp(20)
            )
        )

        self.content = govde

    def kaydet_et(self, instance):

        firma_adi = self.firma_adi.text.strip()
        telefon = self.telefon.text.strip()

        if not firma_adi:
            self.uyari.text = (
                "Lütfen Firma Adı / Kişi Adı girin."
            )
            return

        if not telefon:
            self.uyari.text = (
                "Lütfen Telefon Numarası girin."
            )
            return

        mevcut = ayarlari_oku()
        mevcut["firma_adi"] = firma_adi
        mevcut["telefon"] = telefon

        ayarlari_kaydet(mevcut)

        self.ayarlar_ekrani.durum.text = (
            "✅ İş bilgileri güncellendi."
        )

        self.dismiss()


# =========================================================
# AYARLAR / YEDEKLEME
# =========================================================

class Ayarlar(Screen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        ana = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(9)
        )

        ana.add_widget(
            ust_baslik(
                self,
                "⚙ YEDEKLEME / AYARLAR",
                "ana"
            )
        )

        ana.add_widget(
            Label(
                text=(
                    "Veriler telefon veya "
                    "bilgisayarda JSON olarak "
                    "saklanır."
                ),
                font_size=18,
                color=BEYAZ,
                size_hint_y=None,
                height=dp(90)
            )
        )

        is_bilgileri = buton(
            "🏢 İŞ DETAYLARINI DÜZENLE",
            yukseklik=62,
            font=19
        )

        is_bilgileri.bind(
            on_press=self.is_bilgilerini_duzenle
        )

        ana.add_widget(is_bilgileri)

        yedek = buton(
            "💾 YEDEK OLUŞTUR",
            yukseklik=62,
            font=19
        )

        yedek.bind(
            on_press=self.yedek_olustur
        )

        ana.add_widget(yedek)

        yerler = buton(
            "📍 YERLERİ YÖNET",
            yukseklik=62,
            font=19
        )

        yerler.bind(
            on_press=self.yerleri_goster
        )

        ana.add_widget(yerler)

        test_bildirim = buton(
            "🔔 TEST BİLDİRİMİ GÖNDER",
            yukseklik=62,
            font=17
        )

        test_bildirim.bind(
            on_press=self.test_bildirimi_gonder
        )

        ana.add_widget(test_bildirim)

        self.durum = Label(
            text="",
            font_size=15,
            color=SOLUK,
            size_hint_y=None,
            height=dp(120),
            halign="left",
            valign="top"
        )

        self.durum.bind(
            width=lambda obj, val: setattr(
                obj, "text_size", (val, None)
            ),
            texture_size=lambda obj, val: setattr(
                obj, "height", max(dp(40), val[1])
            )
        )

        ana.add_widget(
            self.durum
        )

        self.add_widget(ana)

    def is_bilgilerini_duzenle(
        self,
        instance
    ):

        IsBilgileriPopup(self).open()

    def yedek_olustur(
        self,
        instance
    ):

        try:

            os.makedirs(
                YEDEK_KLASORU,
                exist_ok=True
            )

            zaman = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            kaynak = ISLER_DOSYASI

            if os.path.exists(kaynak):

                hedef = os.path.join(
                    YEDEK_KLASORU,
                    f"isler_{zaman}.json"
                )

                shutil.copy2(
                    kaynak,
                    hedef
                )

            kaynak_yer = YERLER_DOSYASI

            if os.path.exists(
                kaynak_yer
            ):

                hedef_yer = os.path.join(
                    YEDEK_KLASORU,
                    f"yerler_{zaman}.json"
                )

                shutil.copy2(
                    kaynak_yer,
                    hedef_yer
                )

            self.durum.text = (
                "✅ Yedek oluşturuldu."
            )

        except Exception as e:

            self.durum.text = (
                f"Yedekleme hatası: {e}"
            )

    def test_bildirimi_gonder(
        self,
        instance
    ):

        try:
            self.durum.text = (
                bildirimler.test_bildirimi_gonder()
            )
        except Exception as e:
            self.durum.text = (
                f"Bildirim hatası: {e}"
            )

    def yerleri_goster(
        self,
        instance
    ):

        yerler = oku(
            YERLER_DOSYASI,
            [
                "Mavikent",
                "Karaöz",
                "Kumluca",
                "Hasyurt",
                "Finike"
            ]
        )

        kutu = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(7)
        )

        scroll = ScrollView()

        liste = BoxLayout(
            orientation="vertical",
            spacing=dp(7),
            size_hint_y=None
        )

        liste.bind(
            minimum_height=
            liste.setter("height")
        )

        for i, yer in enumerate(
            yerler
        ):

            satir = BoxLayout(
                size_hint_y=None,
                height=dp(55),
                spacing=dp(5)
            )

            satir.add_widget(
                Label(
                    text="📍 " + yer,
                    font_size=17,
                    color=BUTON_METIN
                )
            )

            sil = buton(
                "SİL",
                yukseklik=50,
                font=14
            )

            sil.size_hint_x = .25

            sil.bind(
                on_press=lambda _, x=i:
                self.yer_sil(
                    x,
                    popup
                )
            )

            satir.add_widget(sil)

            liste.add_widget(satir)

        scroll.add_widget(liste)

        kutu.add_widget(scroll)

        kapat = buton(
            "KAPAT",
            yukseklik=54,
            font=17
        )

        kutu.add_widget(kapat)

        popup = Popup(
            title="Kayıtlı Yerler",
            content=kutu,
            size_hint=(.90, .80)
        )

        kapat.bind(
            on_press=lambda *_:
            popup.dismiss()
        )

        popup.open()

    def yer_sil(
        self,
        index,
        popup
    ):

        yerler = oku(
            YERLER_DOSYASI
        )

        if 0 <= index < len(
            yerler
        ):

            del yerler[index]

            kaydet(
                YERLER_DOSYASI,
                yerler
            )

            popup.dismiss()

            self.yerleri_goster(
                None
            )


# =========================================================
# UYGULAMA
# =========================================================

class IsTakipApp(App):

    title = "Bi Tıkla Hesap"

    def build(self):

        Window.clearcolor = ARKA

        # NOT (hata düzeltmesi): İzin isteği, uygulama
        # penceresi/activity'si tam olarak hazır olmadan
        # çağrılırsa Android'de sistem izin penceresi hiç
        # açılmayabilir; bu durumda kullanıcı izni onaylama
        # şansı bile bulamadan RECORD_AUDIO / depolama
        # erişimi reddedilmiş sayılır ve "bu cihazda
        # desteklenmiyor" gibi hatalara yol açar. Çağrıyı bir
        # sonraki karesine (Clock.schedule_once) erteleyerek
        # bu yarış durumunu (race condition) önlüyoruz.
        Clock.schedule_once(
            lambda dt: self._android_izinlerini_iste(),
            0.5
        )

        try:

            Window.softinput_mode = (
                "below_target"
            )

        except Exception:
            pass

        ekranlar = ScreenManager()

        ekranlar.add_widget(
            AcilisEkrani(
                name="acilis"
            )
        )

        ekranlar.add_widget(
            IlkKurulum(
                name="kurulum"
            )
        )

        ekranlar.add_widget(
            AnaSayfa(
                name="ana"
            )
        )

        ekranlar.add_widget(
            YeniIs(
                name="yeni"
            )
        )

        ekranlar.add_widget(
            Gecmis(
                name="gecmis"
            )
        )

        ekranlar.add_widget(
            IsDetay(
                name="detay"
            )
        )

        ekranlar.add_widget(
            GelirGider(
                name="gelir"
            )
        )

        ekranlar.add_widget(
            Malzemeler(
                name="malzeme"
            )
        )

        ekranlar.add_widget(
            Raporlar(
                name="rapor"
            )
        )

        ekranlar.add_widget(
            Ayarlar(
                name="ayar"
            )
        )

        ekranlar.current = "acilis"

        try:
            bildirimler.tum_hatirlatmalari_planla()
        except Exception as e:
            print(f"[bildirim] planlama başlatılamadı: {e}")

        return ekranlar

    def _android_izinlerini_iste(self):

        # Android 6+ (API 23+) 'tehlikeli' izinleri sadece
        # buildozer.spec -> android.permissions listesine
        # yazmak YETMEZ; kullanıcıya sistem izin penceresinin
        # açılıp onaylanması gerekir. Bu çağrı olmadan
        # bildirimler ve kamera sessizce çalışmaz.

        try:

            from kivy.utils import platform

            if platform != "android":
                return

            from android.permissions import (
                request_permissions,
                Permission
            )

            istenecekler = [
                Permission.CAMERA,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
                # HATA DÜZELTMESİ: RECORD_AUDIO eksikti.
                # buildozer.spec içinde bu izin tanımlı
                # olsa bile, Android 6+ (API 23+) çalışma
                # anında (runtime) ayrıca onaylanmasını
                # ister. Bu satır olmadan mikrofon her
                # zaman izinsiz sayılıyor ve uygulama
                # ses kaydını "bu cihazda desteklenmiyor"
                # diye gösteriyordu (ses.py -> basla()).
                Permission.RECORD_AUDIO
            ]

            # POST_NOTIFICATIONS sadece Android 13+ (API 33+)
            # içinde var; eski sürümlerde bu isim bulunmaz.
            if hasattr(
                Permission, "POST_NOTIFICATIONS"
            ):

                istenecekler.append(
                    Permission.POST_NOTIFICATIONS
                )

            # READ_MEDIA_IMAGES Android 13+'ta galeri
            # erişimi için READ_EXTERNAL_STORAGE'ın yerini
            # aldı.
            if hasattr(
                Permission, "READ_MEDIA_IMAGES"
            ):

                istenecekler.append(
                    Permission.READ_MEDIA_IMAGES
                )

            request_permissions(istenecekler)

        except Exception as e:

            print(
                f"[izin] istenemedi: {e}"
            )


# =========================================================
# BAŞLAT
# =========================================================

if __name__ == "__main__":

    IsTakipApp().run()
