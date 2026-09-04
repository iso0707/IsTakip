import json
import os
import shutil
import calendar
from datetime import datetime

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
from kivy.graphics import Color, RoundedRectangle, Line


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


# =========================================================
# TEMA
# =========================================================

ARKA = (0.12, 0.13, 0.15, 1)
KART = (0.20, 0.21, 0.24, 1)

BUTON = (0.88, 0.89, 0.91, 1)
BUTON_BASILDI = (0.72, 0.74, 0.78, 1)
BUTON_METIN = (0.08, 0.09, 0.11, 1)

BEYAZ = (0.96, 0.97, 0.98, 1)
SOLUK = (0.70, 0.72, 0.76, 1)

GIRIS = (0.94, 0.95, 0.97, 1)
GIRIS_METIN = (0.08, 0.09, 0.11, 1)

YESIL = (0.20, 0.65, 0.30, 1)
KIRMIZI = (0.85, 0.20, 0.20, 1)

GIDER_IKONLARI = {
    "Yakıt": "⛽",
    "Malzeme Özel": "🧰",
    "Gıda": "🍔",
    "Yardımcı Eleman": "🧑‍🔧"
}


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

        self.bind(
            pos=self._guncelle,
            size=self._guncelle,
            state=self._durum
        )

    def _guncelle(self, *args):

        self._arka.pos = self.pos
        self._arka.size = self.size

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

    return YuvarlakButon(
        text=yazi,
        size_hint_y=None,
        height=dp(yukseklik),
        font_size=font,
        ozel_renk=renk
    )


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
    ay_malzeme_alinacak = 0
    ay_iscilik = 0

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

        # Malzemeli işlerde malzeme tutarı
        # zaten işçilik rakamına dahil
        # olduğundan alınacak tutara
        # tekrar eklenmez.
        malzeme_alinacak = (
            0
            if malzemeli
            else malzeme
        )

        iscilik = para(
            is_.get("iscilik", 0)
        )

        toplam_gelir += gelir
        toplam_gider += gider
        toplam_malzeme_para += malzeme
        toplam_malzeme_kar += malzeme_kar
        toplam_iscilik += iscilik

        if bu_ay_mi(
            is_.get("tarih", ""),
            yil,
            ay
        ):

            ay_gelir += gelir
            ay_gider += gider
            ay_malzeme += malzeme
            ay_malzeme_kar += malzeme_kar
            ay_malzeme_alinacak += malzeme_alinacak
            ay_iscilik += iscilik

    return {

        "ay_gelir": ay_gelir,

        "ay_gider": ay_gider,

        "ay_malzeme": ay_malzeme,

        "ay_iscilik": ay_iscilik,

        "ay_alinacak":
            ay_iscilik
            + ay_malzeme_alinacak
            - ay_gelir,

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


class TarihInput(TextInput):

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

        self.background_normal = ""

        self.background_color = GIRIS

        self.foreground_color = GIRIS_METIN

        self.hint_text_color = (
            0.42,
            0.44,
            0.48,
            1
        )

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


class AcilisEkrani(Screen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.kok = FloatLayout()

        with self.kok.canvas.before:

            Color(*ARKA)

            self._zemin = RoundedRectangle(
                pos=self.kok.pos,
                size=self.kok.size,
                radius=[0]
            )

        self.kok.bind(
            pos=self._zemin_guncelle,
            size=self._zemin_guncelle
        )

        merkez = {
            "center_x": .5,
            "center_y": .60
        }

        self.halka1 = NabizHalkasi(
            size_hint=(None, None),
            size=(0, 0),
            pos_hint=merkez
        )

        self.halka2 = NabizHalkasi(
            size_hint=(None, None),
            size=(0, 0),
            pos_hint=merkez
        )

        self.baslik_kutu = BoxLayout(
            orientation="horizontal",
            size_hint=(None, None),
            height=dp(46),
            pos_hint={
                "center_x": .5,
                "center_y": .43
            }
        )

        self.baslik_harfleri = []

        for harf_yazi in "İŞ TAKİP PRO":

            genislik = (
                dp(14)
                if harf_yazi == " "
                else dp(23)
            )

            harf = Label(
                text=harf_yazi,
                font_size=30,
                bold=True,
                color=BEYAZ,
                size_hint=(None, None),
                size=(genislik, dp(46)),
                opacity=0
            )

            self.baslik_harfleri.append(harf)

            self.baslik_kutu.add_widget(harf)

        self.baslik_kutu.bind(
            minimum_width=
            self.baslik_kutu.setter("width")
        )

        self.alt_yazi = Label(
            text="ŞANTİYE • İŞ • PARA • MALZEME",
            font_size=13,
            color=SOLUK,
            size_hint=(None, None),
            size=(dp(320), dp(24)),
            pos_hint={
                "center_x": .5,
                "center_y": .375
            },
            opacity=0
        )

        self.bar = ProgressBar(
            max=100,
            value=0,
            size_hint=(None, None),
            size=(dp(230), dp(8)),
            pos_hint={
                "center_x": .5,
                "center_y": .30
            },
            opacity=0
        )

        self.durum_yazi = Label(
            text="Yükleniyor",
            font_size=16,
            color=SOLUK,
            size_hint=(None, None),
            size=(dp(320), dp(28)),
            pos_hint={
                "center_x": .5,
                "center_y": .25
            },
            opacity=0
        )

        self.kok.add_widget(self.halka1)
        self.kok.add_widget(self.halka2)
        self.kok.add_widget(self.baslik_kutu)
        self.kok.add_widget(self.alt_yazi)
        self.kok.add_widget(self.bar)
        self.kok.add_widget(self.durum_yazi)

        self.add_widget(self.kok)

        self._nokta_sayaci = 0
        self._nokta_olay = None
        self._ses = None

    def _zemin_guncelle(self, *args):

        self._zemin.pos = self.kok.pos
        self._zemin.size = self.kok.size

    def on_enter(self):

        self._sesi_calmayi_dene()

        # Arkada yayılan radar
        # halkaları
        self.halka1.baslat(0)
        self.halka2.baslat(.85)

        # Başlık harfleri tek tek,
        # sırayla beliriyor
        for i, harf in enumerate(
            self.baslik_harfleri
        ):

            Clock.schedule_once(
                lambda dt, w=harf:
                Animation(
                    opacity=1,
                    duration=.35,
                    t="out_quad"
                ).start(w),
                .25 + i * .045
            )

        Animation(
            opacity=1,
            duration=.7,
            t="out_quad"
        ).start(self.alt_yazi)

        Animation(
            opacity=1,
            duration=.7,
            t="out_quad"
        ).start(self.bar)

        Animation(
            opacity=1,
            duration=.7,
            t="out_quad"
        ).start(self.durum_yazi)

        # İlerleme çubuğu doluşu
        Animation(
            value=100,
            duration=2.1,
            t="out_quad"
        ).start(self.bar)

        # "Yükleniyor..." noktalarının
        # akması
        self._nokta_olay = Clock.schedule_interval(
            self._noktalari_guncelle,
            .4
        )

        Clock.schedule_once(
            self._devam_et,
            2.4
        )

    def _noktalari_guncelle(self, dt):

        self._nokta_sayaci = (
            self._nokta_sayaci + 1
        ) % 4

        self.durum_yazi.text = (
            "Yükleniyor"
            + "." * self._nokta_sayaci
        )

    def _sesi_calmayi_dene(self):

        try:

            if os.path.exists(
                SES_DOSYASI
            ):

                self._ses = SoundLoader.load(
                    SES_DOSYASI
                )

                if self._ses:

                    self._ses.volume = 0.6
                    self._ses.play()

        except Exception:
            pass

    def _devam_et(self, dt):

        if self._nokta_olay:
            self._nokta_olay.cancel()

        self.halka1.durdur()
        self.halka2.durdur()

        if self.manager:

            self.manager.transition = (
                FadeTransition(
                    duration=.35
                )
            )

            self.manager.current = "ana"


# =========================================================
# ANA SAYFA
# =========================================================

class AnaSayfa(Screen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        ana = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(9)
        )

        ana.add_widget(
            Label(
                text="🔨 İŞ TAKİP PRO",
                font_size=32,
                bold=True,
                color=BEYAZ,
                size_hint_y=None,
                height=dp(62)
            )
        )

        ana.add_widget(
            Label(
                text="ŞANTİYE • İŞ • PARA • MALZEME",
                font_size=15,
                color=SOLUK,
                size_hint_y=None,
                height=dp(28)
            )
        )

        self.durum_kutu = KirmiziKutu(
            text="",
            font_size=19,
            bold=True,
            color=BEYAZ,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(90)
        )

        self.durum_kutu.bind(
            size=lambda obj, val:
            setattr(
                obj,
                "text_size",
                val
            )
        )

        ana.add_widget(
            self.durum_kutu
        )

        menuler = [

            (
                "＋ YENİ İŞ",
                "yeni",
                62
            ),

            (
                "▣ GEÇMİŞ İŞLER",
                "gecmis",
                60
            ),

            (
                "₺ GELİR / GİDER",
                "gelir",
                60
            ),

            (
                "📦 MALZEME / ÖDEMELER",
                "malzeme",
                60
            ),

            (
                "📊 RAPORLAR / GRAFİKLER",
                "rapor",
                60
            ),

            (
                "⚙ YEDEKLEME / AYARLAR",
                "ayar",
                58
            )
        ]

        for (
            yazi,
            ekran,
            yukseklik
        ) in menuler:

            b = buton(
                yazi,
                yukseklik=yukseklik,
                font=19
            )

            b.bind(
                on_press=lambda _, s=ekran:
                setattr(
                    self.manager,
                    "current",
                    s
                )
            )

            ana.add_widget(b)

        cikis_btn = buton(
            "💾 KAYDET VE ÇIK",
            renk=KIRMIZI,
            yukseklik=60,
            font=19
        )

        cikis_btn.bind(
            on_press=self.kaydet_ve_cik
        )

        ana.add_widget(cikis_btn)

        ana.add_widget(
            Label(
                text="Veriler otomatik olarak saklanır.",
                font_size=14,
                color=SOLUK
            )
        )

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

        if toplam_alinacak > 0:

            self.durum_kutu.renk_ayarla(
                KIRMIZI
            )

            self.durum_kutu.text = (
                "🔴 TOPLAM ALINACAK\n"
                f"{toplam_alinacak:.2f} TL"
            )

        else:

            self.durum_kutu.renk_ayarla(
                YESIL
            )

            self.durum_kutu.text = (
                "✅ KÂRIM (İşçilik - Diğer Gider)\n"
                f"{karim:.2f} TL"
            )


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
            spacing=dp(9),
            size_hint_y=None
        )

        form.bind(
            minimum_height=
            form.setter("height")
        )

        self.is_adi = giris(
            "İş / proje adı"
        )

        self.musteri = giris(
            "Müşteri / iş sahibi"
        )

        self.telefon = giris(
            "Telefon (isteğe bağlı)"
        )

        form.add_widget(self.is_adi)
        form.add_widget(self.musteri)
        form.add_widget(self.telefon)

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

        form.add_widget(yer_satir)

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
            background_color=GIRIS,
            color=GIRIS_METIN
        )

        durum_satir.add_widget(
            self.durum
        )

        form.add_widget(
            durum_satir
        )

        self.aciklama = giris(
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

        self.gelir = giris(
            "Alınan (TL)",
            input_filter="float"
        )

        self.iscilik = giris(
            "İşçilik (TL)",
            input_filter="float"
        )

        form.add_widget(self.aciklama)
        form.add_widget(self.baslangic)
        form.add_widget(self.bitis)

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

        form.add_widget(
            malzeme_secim_satir
        )

        form.add_widget(
            etiketli_alan(
                "Alınan",
                self.gelir
            )
        )

        form.add_widget(
            etiketli_alan(
                "İşçilik",
                self.iscilik
            )
        )

        form.add_widget(
            Label(
                text="💸 DİĞER GİDERLER",
                font_size=22,
                bold=True,
                color=BEYAZ,
                size_hint_y=None,
                height=dp(42)
            )
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

        form.add_widget(
            self.gider_kutusu
        )

        self.gider_satirlari = []

        self.gider_satiri_ekle()

        form.add_widget(
            Label(
                text="📦 MALZEMELER",
                font_size=22,
                bold=True,
                color=BEYAZ,
                size_hint_y=None,
                height=dp(42)
            )
        )

        malzeme_satir = BoxLayout(
            size_hint_y=None,
            height=dp(58),
            spacing=dp(5)
        )

        self.malzeme_adi = giris(
            "Malzeme"
        )

        self.malzeme_adet = giris(
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
            background_color=GIRIS,
            color=GIRIS_METIN
        )

        self.malzeme_fiyat = giris(
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

        form.add_widget(
            malzeme_satir
        )

        self.malzeme_listesi = Label(
            text="Henüz malzeme yok.",
            font_size=17,
            color=SOLUK,
            size_hint_y=None,
            height=dp(130)
        )

        form.add_widget(
            self.malzeme_listesi
        )

        self.alinacak_kutu = KirmiziKutu(
            text="ALINACAK TUTAR: 0.00 TL",
            font_size=20,
            bold=True,
            color=BEYAZ,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(64)
        )

        self.alinacak_kutu.bind(
            size=lambda obj, val:
            setattr(
                obj,
                "text_size",
                val
            )
        )

        form.add_widget(
            self.alinacak_kutu
        )

        kaydet_btn = buton(
            "💾 İŞİ KAYDET",
            renk=YESIL,
            yukseklik=66,
            font=20
        )

        kaydet_btn.bind(
            on_press=self.kaydet
        )

        form.add_widget(
            kaydet_btn
        )

        scroll.add_widget(form)

        ana.add_widget(scroll)

        self.add_widget(ana)

        for widget in (
            self.is_adi,
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

        isim = giris(
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
            text="Yakıt",
            values=self.GIDER_KATEGORILERI,
            size_hint_x=.42,
            size_hint_y=None,
            height=dp(58),
            font_size=16,
            background_normal="",
            background_color=GIRIS,
            color=GIRIS_METIN
        )

        tutar = giris(
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

                gider += tutar

                diger_giderler.append({
                    "kategori":
                        kayit["kategori"].text,
                    "tutar":
                        tutar
                })

        veri = {

            "is_adi":
                self.is_adi.text.strip()
                or "İsimsiz İş",

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
            self.is_adi,
            self.musteri,
            self.telefon,
            self.aciklama,
            self.baslangic,
            self.bitis,
            self.gelir,
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

            is_adi = is_.get(
                "is_adi",
                "İsimsiz İş"
            )

            musteri = is_.get(
                "musteri",
                "Belirtilmemiş"
            )

            yer = is_.get(
                "yer",
                "Yer belirtilmemiş"
            )

            kart = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(155),
                spacing=dp(7)
            )

            if durum == "Bitti":
                is_renk = KIRMIZI
            elif durum == "Beklemede":
                is_renk = YESIL
            else:
                is_renk = BEYAZ

            detay_btn = buton(
                f"🔨  {is_adi}\n\n"
                f"👤  {musteri}\n"
                f"📍  {yer}",
                renk=is_renk,
                yukseklik=110,
                font=20
            )

            detay_btn.halign = "left"
            detay_btn.valign = "middle"

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

            kart.add_widget(
                detay_btn
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

        scroll = ScrollView()

        self.scroll = scroll

        form = BoxLayout(
            orientation="vertical",
            spacing=dp(9),
            size_hint_y=None
        )

        form.bind(
            minimum_height=
            form.setter("height")
        )

        self.is_adi = giris(
            "İş / proje adı"
        )

        self.musteri = giris(
            "Müşteri / iş sahibi"
        )

        self.telefon = giris(
            "Telefon"
        )

        self.yer = giris(
            "Yer"
        )

        self.aciklama = giris(
            "Açıklama / notlar",
            multiline=True,
            height=125
        )

        self.baslangic = giris(
            "Başlangıç tarihi"
        )

        self.bitis = giris(
            "Bitiş tarihi"
        )

        self.gelir = giris(
            "Gelir",
            input_filter="float"
        )

        self.iscilik = giris(
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
            background_color=GIRIS,
            color=GIRIS_METIN
        )

        form.add_widget(self.is_adi)
        form.add_widget(self.musteri)
        form.add_widget(self.telefon)
        form.add_widget(self.yer)
        form.add_widget(self.durum)
        form.add_widget(self.aciklama)
        form.add_widget(self.baslangic)
        form.add_widget(self.bitis)

        form.add_widget(
            etiketli_alan(
                "Alınan",
                self.gelir
            )
        )

        form.add_widget(
            etiketli_alan(
                "İşçilik",
                self.iscilik
            )
        )

        form.add_widget(
            Label(
                text="💸 DİĞER GİDERLER",
                font_size=22,
                bold=True,
                color=BEYAZ,
                size_hint_y=None,
                height=dp(42)
            )
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

        form.add_widget(
            self.gider_kutusu
        )

        self.gider_satirlari = []

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

        form.add_widget(
            malzeme_secim_satir
        )

        form.add_widget(
            Label(
                text="📦 MALZEMELER",
                font_size=22,
                bold=True,
                color=BEYAZ,
                size_hint_y=None,
                height=dp(42)
            )
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

        form.add_widget(
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

        form.add_widget(
            yeni_malzeme
        )

        self.alinacak_kutu = KirmiziKutu(
            text="ALINACAK TUTAR: 0.00 TL",
            font_size=20,
            bold=True,
            color=BEYAZ,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(64)
        )

        self.alinacak_kutu.bind(
            size=lambda obj, val:
            setattr(
                obj,
                "text_size",
                val
            )
        )

        form.add_widget(
            self.alinacak_kutu
        )

        kaydet_btn = buton(
            "💾 DEĞİŞİKLİKLERİ KAYDET",
            renk=YESIL,
            yukseklik=66,
            font=20
        )

        kaydet_btn.bind(
            on_press=self.kaydet
        )

        form.add_widget(
            kaydet_btn
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

    GIDER_KATEGORILERI = (
        "Yakıt",
        "Gıda",
        "Malzeme Özel",
        "Yardımcı Eleman"
    )

    def gider_satiri_ekle(
        self,
        kategori_sec="Yakıt",
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
            background_color=GIRIS,
            color=GIRIS_METIN
        )

        tutar = giris(
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

        self.is_adi.text = is_.get(
            "is_adi",
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

        ad = giris(
            "Malzeme adı"
        )

        adet = giris(
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
            background_color=GIRIS,
            color=GIRIS_METIN
        )

        fiyat = giris(
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

        is_["is_adi"] = (
            self.is_adi.text.strip()
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

        self.ozet = Label(
            text="",
            font_size=21,
            bold=True,
            color=BEYAZ,
            size_hint_y=None,
            height=dp(260)
        )

        ana.add_widget(
            self.ozet
        )

        self.durum_kutu = KirmiziKutu(
            text="",
            font_size=20,
            bold=True,
            color=BEYAZ,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(90)
        )

        self.durum_kutu.bind(
            size=lambda obj, val:
            setattr(
                obj,
                "text_size",
                val
            )
        )

        ana.add_widget(
            self.durum_kutu
        )

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

        self.ozet.text = (

            f"💰 Alınan: "
            f"{h['ay_gelir']:.2f} TL\n"

            f"💸 Diğer gider: "
            f"{h['ay_gider']:.2f} TL\n"

            f"📦 Malzeme: "
            f"{h['ay_malzeme']:.2f} TL\n"

            f"👷 İŞÇİLİK: "
            f"{h['ay_iscilik']:.2f} TL"
        )

        ay_alinacak = h["ay_alinacak"]

        if ay_alinacak > 0:

            self.durum_kutu.renk_ayarla(
                KIRMIZI
            )

            self.durum_kutu.text = (
                f"👷 İşçilik: {h['ay_iscilik']:.2f} TL\n"
                f"📦 Malzeme: {h['ay_malzeme']:.2f} TL"
            )

        else:

            kar = h["ay_net"]

            self.durum_kutu.renk_ayarla(
                YESIL
            )

            self.durum_kutu.text = (
                "✅ KÂR: "
                f"{kar:.2f} TL"
            )


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

        self.ozet = Label(
            text="",
            font_size=21,
            bold=True,
            color=BEYAZ,
            size_hint_y=None,
            height=dp(100)
        )

        ana.add_widget(
            self.ozet
        )

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

        self.ozet.text = (
            f"📦 TOPLAM: "
            f"{toplam:.2f} TL\n"
            f"⏳ ÖDENECEK: "
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

        self.icerik.add_widget(
            Label(
                text=(
                    "📋 İŞ DURUMLARI\n\n"
                    f"🟢 Devam eden: "
                    f"{devam}\n\n"
                    f"✅ Biten: "
                    f"{bitti}\n\n"
                    f"⏳ Beklemede: "
                    f"{beklemede}"
                ),
                font_size=20,
                color=BEYAZ,
                size_hint_y=None,
                height=dp(230)
            )
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

        self.durum = Label(
            text="",
            font_size=16,
            color=SOLUK
        )

        ana.add_widget(
            self.durum
        )

        self.add_widget(ana)

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

    def build(self):

        Window.clearcolor = ARKA

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

        return ekranlar


# =========================================================
# BAŞLAT
# =========================================================

if __name__ == "__main__":

    IsTakipApp().run()
