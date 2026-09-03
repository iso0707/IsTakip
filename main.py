import json
import os
import shutil
from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle


# =========================================================
# DOSYALAR
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ISLER_DOSYASI = os.path.join(BASE_DIR, "isler.json")
YERLER_DOSYASI = os.path.join(BASE_DIR, "yerler.json")
YEDEK_KLASORU = os.path.join(BASE_DIR, "yedekler")


# =========================================================
# RENKLER
# =========================================================

ARKA = (0.025, 0.035, 0.07, 1)
KART = (0.055, 0.075, 0.13, 1)

MAVI = (0.08, 0.35, 0.9, 1)
YESIL = (0.05, 0.65, 0.34, 1)
KIRMIZI = (0.82, 0.12, 0.16, 1)
TURUNCU = (0.95, 0.48, 0.08, 1)
MOR = (0.48, 0.25, 0.85, 1)
GRI = (0.16, 0.19, 0.27, 1)

BEYAZ = (0.95, 0.97, 1, 1)
SOLUK = (0.62, 0.67, 0.78, 1)


# =========================================================
# YARDIMCI FONKSİYONLAR
# =========================================================

def oku(dosya, varsayilan=None):

    if varsayilan is None:
        varsayilan = []

    if not os.path.exists(dosya):
        return varsayilan

    try:

        with open(dosya, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return varsayilan


def kaydet(dosya, veri):

    with open(dosya, "w", encoding="utf-8") as f:
        json.dump(
            veri,
            f,
            ensure_ascii=False,
            indent=4
        )


def para(deger):

    try:
        return float(deger or 0)

    except Exception:
        return 0.0


def buton(yazi, renk, yukseklik=55, font=17):

    return Button(
        text=yazi,
        font_size=font,
        size_hint_y=None,
        height=dp(yukseklik),
        background_normal="",
        background_color=renk,
        color=BEYAZ
    )


def baslik(yazi, boyut=28):

    return Label(
        text=yazi,
        font_size=boyut,
        bold=True,
        color=BEYAZ,
        size_hint_y=None,
        height=dp(50)
    )


def toplam_malzeme(is_):

    toplam = 0

    for malzeme in is_.get("malzemeler", []):

        toplam += para(
            malzeme.get("fiyat", 0)
        )

    return toplam


def is_durumu(is_):

    return is_.get(
        "durum",
        "Devam ediyor"
    )


def bu_ay_mi(tarih):

    try:

        tarih = datetime.strptime(
            tarih,
            "%d.%m.%Y %H:%M"
        )

        simdi = datetime.now()

        return (
            tarih.month == simdi.month
            and
            tarih.year == simdi.year
        )

    except Exception:
        return False


def hesaplar():

    isler = oku(ISLER_DOSYASI)

    ay_gelir = 0
    ay_gider = 0
    ay_malzeme = 0

    toplam_gelir = 0
    toplam_gider = 0
    toplam_malzeme_para = 0

    for is_ in isler:

        gelir = para(
            is_.get("gelir", 0)
        )

        gider = para(
            is_.get("gider", 0)
        )

        malzeme = toplam_malzeme(is_)

        toplam_gelir += gelir
        toplam_gider += gider
        toplam_malzeme_para += malzeme

        if bu_ay_mi(
            is_.get("tarih", "")
        ):

            ay_gelir += gelir
            ay_gider += gider
            ay_malzeme += malzeme

    return {

        "ay_gelir": ay_gelir,

        "ay_gider": ay_gider,

        "ay_malzeme": ay_malzeme,

        "ay_net":
            ay_gelir
            - ay_gider
            - ay_malzeme,

        "toplam_gelir":
            toplam_gelir,

        "toplam_gider":
            toplam_gider,

        "toplam_malzeme":
            toplam_malzeme_para,

        "toplam_net":
            toplam_gelir
            - toplam_gider
            - toplam_malzeme_para
    }


# =========================================================
# ANA SAYFA
# =========================================================

class AnaSayfa(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        ana = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(9)
        )

        ana.add_widget(
            Label(
                text="🔨 İŞ TAKİP PRO",
                font_size=35,
                bold=True,
                color=BEYAZ,
                size_hint_y=None,
                height=dp(58)
            )
        )

        ana.add_widget(
            Label(
                text="ŞANTİYE • İŞ • PARA • MALZEME",
                font_size=12,
                color=SOLUK,
                size_hint_y=None,
                height=dp(25)
            )
        )

        self.ozet = Label(
            text="",
            font_size=18,
            bold=True,
            color=BEYAZ,
            size_hint_y=None,
            height=dp(82)
        )

        ana.add_widget(self.ozet)

        menuler = [

            (
                "＋ YENİ İŞ",
                MAVI,
                "yeni",
                60
            ),

            (
                "▣ GEÇMİŞ İŞLER",
                GRI,
                "gecmis",
                55
            ),

            (
                "₺ GELİR / GİDER",
                YESIL,
                "gelir",
                55
            ),

            (
                "📦 MALZEME / ÖDEMELER",
                TURUNCU,
                "malzeme",
                55
            ),

            (
                "📊 RAPORLAR / GRAFİKLER",
                MOR,
                "rapor",
                55
            ),

            (
                "⚙ YEDEKLEME / AYARLAR",
                GRI,
                "ayar",
                50
            )
        ]

        for yazi, renk, ekran, yukseklik in menuler:

            b = buton(
                yazi,
                renk,
                yukseklik,
                18
            )

            b.bind(
                on_press=
                lambda x, s=ekran:
                setattr(
                    self.manager,
                    "current",
                    s
                )
            )

            ana.add_widget(b)

        ana.add_widget(
            Label(
                text="Veriler otomatik olarak saklanır.",
                font_size=12,
                color=SOLUK
            )
        )

        self.add_widget(ana)

    def on_enter(self):

        h = hesaplar()

        self.ozet.text = (

            f"BU AY\n"
            f"💰 Gelir: {h['ay_gelir']:.2f} TL\n"
            f"📊 Net: {h['ay_net']:.2f} TL"

        )


# =========================================================
# YENİ İŞ
# =========================================================

class YeniIs(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.malzemeler = []
        self.secili_yer = ""

        ana = BoxLayout(
            orientation="vertical",
            padding=dp(13),
            spacing=dp(6)
        )

        ana.add_widget(
            baslik("＋ YENİ İŞ")
        )

        scroll = ScrollView()

        form = BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None
        )

        form.bind(
            minimum_height=
            form.setter("height")
        )

        self.is_adi = TextInput(
            hint_text="İş / proje adı",
            multiline=False,
            size_hint_y=None,
            height=dp(46)
        )

        form.add_widget(self.is_adi)

        self.musteri = TextInput(
            hint_text="Müşteri / iş sahibi",
            multiline=False,
            size_hint_y=None,
            height=dp(46)
        )

        form.add_widget(self.musteri)

        self.telefon = TextInput(
            hint_text="Telefon (isteğe bağlı)",
            multiline=False,
            size_hint_y=None,
            height=dp(46)
        )

        form.add_widget(self.telefon)

        yer_satir = BoxLayout(
            size_hint_y=None,
            height=dp(46),
            spacing=dp(5)
        )

        yer_btn = buton(
            "📍 İŞ YERİ SEÇ",
            MAVI,
            46,
            15
        )

        yer_btn.bind(
            on_press=self.yer_sec
        )

        self.yer_label = Label(
            text="Yer: seçilmedi",
            color=SOLUK
        )

        yer_satir.add_widget(yer_btn)
        yer_satir.add_widget(self.yer_label)

        form.add_widget(yer_satir)

        durum_satir = BoxLayout(
            size_hint_y=None,
            height=dp(46),
            spacing=dp(5)
        )

        durum_satir.add_widget(
            Label(
                text="Durum:",
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
            height=dp(46)
        )

        durum_satir.add_widget(self.durum)
        form.add_widget(durum_satir)

        self.aciklama = TextInput(
            hint_text="İş açıklaması / notlar",
            multiline=True,
            size_hint_y=None,
            height=dp(100)
        )

        form.add_widget(self.aciklama)

        self.baslangic = TextInput(
            hint_text="Başlangıç tarihi",
            multiline=False,
            size_hint_y=None,
            height=dp(46)
        )

        form.add_widget(self.baslangic)

        self.bitis = TextInput(
            hint_text="Bitiş tarihi",
            multiline=False,
            size_hint_y=None,
            height=dp(46)
        )

        form.add_widget(self.bitis)

        self.gelir = TextInput(
            hint_text="Alınacak / alınan para (TL)",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(46)
        )

        form.add_widget(self.gelir)

        self.gider = TextInput(
            hint_text="Diğer gider (TL)",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(46)
        )

        form.add_widget(self.gider)

        form.add_widget(
            Label(
                text="📦 MALZEMELER",
                font_size=18,
                bold=True,
                color=BEYAZ,
                size_hint_y=None,
                height=dp(32)
            )
        )

        malzeme_satir = BoxLayout(
            size_hint_y=None,
            height=dp(46),
            spacing=dp(5)
        )

        self.malzeme_adi = TextInput(
            hint_text="Malzeme"
        )

        self.malzeme_adet = TextInput(
            hint_text="Adet",
            input_filter="int",
            size_hint_x=.18
        )

        self.malzeme_fiyat = TextInput(
            hint_text="Birim fiyat",
            input_filter="float",
            size_hint_x=.27
        )

        ekle = buton(
            "+",
            YESIL,
            46,
            22
        )

        ekle.size_hint_x = .18

        ekle.bind(
            on_press=self.malzeme_ekle
        )

        malzeme_satir.add_widget(self.malzeme_adi)
        malzeme_satir.add_widget(self.malzeme_adet)
        malzeme_satir.add_widget(self.malzeme_fiyat)
        malzeme_satir.add_widget(ekle)

        form.add_widget(malzeme_satir)

        self.malzeme_listesi = Label(
            text="Henüz malzeme yok.",
            font_size=14,
            color=SOLUK,
            size_hint_y=None,
            height=dp(110)
        )

        form.add_widget(self.malzeme_listesi)

        kaydet_btn = buton(
            "💾 İŞİ KAYDET",
            YESIL,
            58,
            19
        )

        kaydet_btn.bind(
            on_press=self.kaydet
        )

        form.add_widget(kaydet_btn)

        scroll.add_widget(form)
        ana.add_widget(scroll)

        geri = buton(
            "← ANA MENÜ",
            GRI,
            45,
            15
        )

        geri.bind(
            on_press=
            lambda x:
            setattr(
                self.manager,
                "current",
                "ana"
            )
        )

        ana.add_widget(geri)

        self.add_widget(ana)

    def yer_sec(self, instance):

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
            spacing=dp(5)
        )

        popup = Popup(
            title="İş Yeri Seç",
            content=kutu,
            size_hint=(.85, .8)
        )

        for yer in yerler:

            b = buton(
                "📍 " + yer,
                MAVI,
                45,
                15
            )

            b.bind(
                on_press=
                lambda x, y=yer:
                self.yer_secildi(
                    y,
                    popup
                )
            )

            kutu.add_widget(b)

        yeni = buton(
            "＋ YENİ YER EKLE",
            YESIL,
            48,
            15
        )

        yeni.bind(
            on_press=
            lambda x:
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
            spacing=dp(8)
        )

        isim = TextInput(
            hint_text="Yeni yer adı",
            multiline=False
        )

        ekle = buton(
            "EKLE",
            YESIL,
            48
        )

        kutu.add_widget(isim)
        kutu.add_widget(ekle)

        popup = Popup(
            title="Yeni İş Yeri",
            content=kutu,
            size_hint=(.8, .35)
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

    def malzeme_ekle(self, instance):

        ad = self.malzeme_adi.text.strip()

        if not ad:
            return

        try:
            adet = int(
                self.malzeme_adet.text or 1
            )
        except:
            adet = 1

        try:
            birim = float(
                self.malzeme_fiyat.text or 0
            )
        except:
            birim = 0

        self.malzemeler.append({

            "ad": ad,

            "adet": adet,

            "birim_fiyat": birim,

            "fiyat": adet * birim,

            "odendi": False

        })

        self.malzeme_adi.text = ""
        self.malzeme_adet.text = ""
        self.malzeme_fiyat.text = ""

        self.malzemeleri_goster()

    def malzemeleri_goster(self):

        if not self.malzemeler:

            self.malzeme_listesi.text = (
                "Henüz malzeme yok."
            )

            return

        toplam = 0
        metin = ""

        for i, m in enumerate(
            self.malzemeler,
            1
        ):

            toplam += para(
                m["fiyat"]
            )

            metin += (
                f"{i}. {m['ad']} "
                f"x{m['adet']} → "
                f"{m['fiyat']:.2f} TL\n"
            )

        metin += (
            f"\nTOPLAM: {toplam:.2f} TL"
        )

        self.malzeme_listesi.text = metin

    def kaydet(self, instance):

        try:
            gelir = float(
                self.gelir.text or 0
            )
        except:
            gelir = 0

        try:
            gider = float(
                self.gider.text or 0
            )
        except:
            gider = 0

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

            "gider":
                gider,

            "malzemeler":
                self.malzemeler,

            "tarih":
                datetime.now().strftime(
                    "%d.%m.%Y %H:%M"
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
            self.gider,
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

        self.malzemeler = []

        self.malzemeleri_goster()


# =========================================================
# GEÇMİŞ İŞLER
# =========================================================

class Gecmis(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        ana = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(6)
        )

        ana.add_widget(
            baslik("📚 GEÇMİŞ İŞLER")
        )

        filtre = BoxLayout(
            size_hint_y=None,
            height=dp(44),
            spacing=dp(5)
        )

        self.arama = TextInput(
            hint_text="🔎 İş / müşteri / yer ara",
            multiline=False
        )

        self.filtre_durum = Spinner(
            text="Tümü",
            values=(
                "Tümü",
                "Devam ediyor",
                "Bitti",
                "Beklemede"
            )
        )

        filtre.add_widget(self.arama)
        filtre.add_widget(self.filtre_durum)

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
            spacing=dp(8),
            size_hint_y=None
        )

        self.liste.bind(
            minimum_height=
            self.liste.setter("height")
        )

        scroll.add_widget(self.liste)

        ana.add_widget(scroll)

        geri = buton(
            "← ANA MENÜ",
            GRI,
            45,
            15
        )

        geri.bind(
            on_press=
            lambda x:
            setattr(
                self.manager,
                "current",
                "ana"
            )
        )

        ana.add_widget(geri)

        self.add_widget(ana)

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

            durum = is_durumu(is_)

            arama_metni = (

                f"{is_.get('is_adi','')} "
                f"{is_.get('musteri','')} "
                f"{is_.get('yer','')}"

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

            malz = toplam_malzeme(is_)

            net = (

                para(
                    is_.get(
                        "gelir",
                        0
                    )
                )

                -

                para(
                    is_.get(
                        "gider",
                        0
                    )
                )

                -

                malz
            )

            text = (

                f"🔨 {is_.get('is_adi','')}\n"

                f"📍 {is_.get('yer','Yok')}   "
                f"👤 {is_.get('musteri','')}\n"

                f"📅 {is_.get('tarih','')}   "
                f"📌 {durum}\n"

                f"💰 {para(is_.get('gelir',0)):.2f} TL   "
                f"💸 {para(is_.get('gider',0)):.2f} TL\n"

                f"📦 Malzeme: {malz:.2f} TL\n"

                f"📊 Net: {net:.2f} TL\n"

                f"📝 {is_.get('aciklama','')}\n\n"

                f"✏️ DETAYLARI GÖR / DÜZENLE"

            )

            kutu = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(205),
                spacing=dp(4)
            )

            detay_btn = Button(
                text=text,
                font_size=13,
                background_normal="",
                background_color=KART,
                color=BEYAZ,
                halign="left",
                valign="middle"
            )

            detay_btn.bind(
                on_press=
                lambda _, i=index:
                self.detay_ac(i)
            )

            kutu.add_widget(
                detay_btn
            )

            sil = buton(
                "🗑 BU İŞİ SİL",
                KIRMIZI,
                43,
                14
            )

            sil.bind(
                on_press=
                lambda _, i=index:
                self.sil(i)
            )

            kutu.add_widget(sil)

            self.liste.add_widget(kutu)

        if not self.liste.children:

            self.liste.add_widget(
                Label(
                    text="Kayıt bulunamadı.",
                    color=SOLUK,
                    size_hint_y=None,
                    height=dp(60)
                )
            )

    def detay_ac(self, index):

        detay = self.manager.get_screen(
            "detay"
        )

        detay.is_index = index

        detay.yukle()

        self.manager.current = "detay"

    def sil(self, index):

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
# İŞ DETAY / DÜZENLE
# =========================================================

class IsDetay(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.is_index = None
        self.malzemeler = []

        ana = BoxLayout(
            orientation="vertical",
            padding=dp(13),
            spacing=dp(6)
        )

        ana.add_widget(
            baslik("✏️ İŞ DETAY / DÜZENLE")
        )

        scroll = ScrollView()

        form = BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None
        )

        form.bind(
            minimum_height=
            form.setter("height")
        )

        # -------------------------------------------------
        # İŞ BİLGİLERİ
        # -------------------------------------------------

        self.is_adi = TextInput(
            hint_text="İş / proje adı",
            multiline=False,
            size_hint_y=None,
            height=dp(46)
        )

        self.musteri = TextInput(
            hint_text="Müşteri / iş sahibi",
            multiline=False,
            size_hint_y=None,
            height=dp(46)
        )

        self.telefon = TextInput(
            hint_text="Telefon",
            multiline=False,
            size_hint_y=None,
            height=dp(46)
        )

        self.yer = TextInput(
            hint_text="İş yeri",
            multiline=False,
            size_hint_y=None,
            height=dp(46)
        )

        form.add_widget(self.is_adi)
        form.add_widget(self.musteri)
        form.add_widget(self.telefon)
        form.add_widget(self.yer)

        # -------------------------------------------------
        # DURUM
        # -------------------------------------------------

        durum_satir = BoxLayout(
            size_hint_y=None,
            height=dp(46),
            spacing=dp(5)
        )

        durum_satir.add_widget(
            Label(
                text="Durum:",
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
            height=dp(46)
        )

        durum_satir.add_widget(
            self.durum
        )

        form.add_widget(
            durum_satir
        )

        # -------------------------------------------------
        # AÇIKLAMA
        # -------------------------------------------------

        self.aciklama = TextInput(
            hint_text="İş açıklaması / notlar",
            multiline=True,
            size_hint_y=None,
            height=dp(100)
        )

        form.add_widget(
            self.aciklama
        )

        # -------------------------------------------------
        # TARİHLER
        # -------------------------------------------------

        self.baslangic = TextInput(
            hint_text="Başlangıç tarihi",
            multiline=False,
            size_hint_y=None,
            height=dp(46)
        )

        self.bitis = TextInput(
            hint_text="Bitiş tarihi",
            multiline=False,
            size_hint_y=None,
            height=dp(46)
        )

        form.add_widget(self.baslangic)
        form.add_widget(self.bitis)

        # -------------------------------------------------
        # PARA
        # -------------------------------------------------

        self.gelir = TextInput(
            hint_text="Alınacak / alınan para (TL)",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(46)
        )

        self.gider = TextInput(
            hint_text="Diğer gider (TL)",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(46)
        )

        form.add_widget(self.gelir)
        form.add_widget(self.gider)

        # -------------------------------------------------
        # MALZEMELER
        # -------------------------------------------------

        form.add_widget(
            Label(
                text="📦 MALZEMELER",
                font_size=18,
                bold=True,
                color=BEYAZ,
                size_hint_y=None,
                height=dp(35)
            )
        )

        self.malzeme_listesi = BoxLayout(
            orientation="vertical",
            spacing=dp(5),
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

        # -------------------------------------------------
        # YENİ MALZEME
        # -------------------------------------------------

        form.add_widget(
            Label(
                text="＋ YENİ MALZEME",
                font_size=16,
                bold=True,
                color=BEYAZ,
                size_hint_y=None,
                height=dp(32)
            )
        )

        malzeme_satir = BoxLayout(
            size_hint_y=None,
            height=dp(46),
            spacing=dp(5)
        )

        self.yeni_malzeme_adi = TextInput(
            hint_text="Malzeme"
        )

        self.yeni_malzeme_adet = TextInput(
            hint_text="Adet",
            input_filter="int",
            size_hint_x=.18
        )

        self.yeni_malzeme_fiyat = TextInput(
            hint_text="Birim fiyat",
            input_filter="float",
            size_hint_x=.27
        )

        ekle = buton(
            "+",
            YESIL,
            46,
            20
        )

        ekle.size_hint_x = .18

        ekle.bind(
            on_press=self.yeni_malzeme_ekle
        )

        malzeme_satir.add_widget(
            self.yeni_malzeme_adi
        )

        malzeme_satir.add_widget(
            self.yeni_malzeme_adet
        )

        malzeme_satir.add_widget(
            self.yeni_malzeme_fiyat
        )

        malzeme_satir.add_widget(
            ekle
        )

        form.add_widget(
            malzeme_satir
        )

        # -------------------------------------------------
        # KAYDET
        # -------------------------------------------------

        kaydet_btn = buton(
            "💾 DEĞİŞİKLİKLERİ KAYDET",
            YESIL,
            58,
            18
        )

        kaydet_btn.bind(
            on_press=self.kaydet
        )

        form.add_widget(
            kaydet_btn
        )

        scroll.add_widget(form)

        ana.add_widget(scroll)

        geri = buton(
            "← GEÇMİŞ İŞLERE DÖN",
            GRI,
            45,
            15
        )

        geri.bind(
            on_press=
            lambda x:
            setattr(
                self.manager,
                "current",
                "gecmis"
            )
        )

        ana.add_widget(geri)

        self.add_widget(ana)

    # =====================================================
    # İŞİ YÜKLE
    # =====================================================

    def yukle(self):

        if self.is_index is None:
            return

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

        self.gider.text = str(
            is_.get(
                "gider",
                0
            )
        )

        self.malzemeler = [
            dict(m)
            for m in is_.get(
                "malzemeler",
                []
            )
        ]

        self.yeni_malzeme_adi.text = ""
        self.yeni_malzeme_adet.text = ""
        self.yeni_malzeme_fiyat.text = ""

        self.malzemeleri_goster()

    # =====================================================
    # MALZEMELERİ GÖSTER
    # =====================================================

    def malzemeleri_goster(self):

        self.malzeme_listesi.clear_widgets()

        if not self.malzemeler:

            self.malzeme_listesi.add_widget(
                Label(
                    text="Bu işte malzeme yok.",
                    color=SOLUK,
                    size_hint_y=None,
                    height=dp(40)
                )
            )

            return

        for i, m in enumerate(
            self.malzemeler
        ):

            fiyat = para(
                m.get(
                    "fiyat",
                    0
                )
            )

            odendi = m.get(
                "odendi",
                False
            )

            satir = BoxLayout(
                size_hint_y=None,
                height=dp(48),
                spacing=dp(4)
            )

            durum_yazi = (
                "✅ ÖDENDİ"
                if odendi
                else
                "⏳ ÖDENECEK"
            )

            durum_renk = (
                YESIL
                if odendi
                else TURUNCU
            )

            odeme = Button(
                text=(
                    f"{m.get('ad','')} "
                    f"x{m.get('adet',1)}\n"
                    f"{fiyat:.2f} TL • {durum_yazi}"
                ),
                font_size=12,
                background_normal="",
                background_color=durum_renk,
                color=BEYAZ
            )

            odeme.bind(
                on_press=
                lambda _, idx=i:
                self.odeme_degistir(idx)
            )

            sil = buton(
                "X",
                KIRMIZI,
                48,
                16
            )

            sil.size_hint_x = .16

            sil.bind(
                on_press=
                lambda _, idx=i:
                self.malzeme_sil(idx)
            )

            satir.add_widget(odeme)
            satir.add_widget(sil)

            self.malzeme_listesi.add_widget(
                satir
            )

    # =====================================================
    # ÖDEME DURUMU
    # =====================================================

    def odeme_degistir(self, index):

        if 0 <= index < len(
            self.malzemeler
        ):

            self.malzemeler[index]["odendi"] = not (
                self.malzemeler[index].get(
                    "odendi",
                    False
                )
            )

            self.malzemeleri_goster()

    # =====================================================
    # MALZEME SİL
    # =====================================================

    def malzeme_sil(self, index):

        if 0 <= index < len(
            self.malzemeler
        ):

            del self.malzemeler[index]

            self.malzemeleri_goster()

    # =====================================================
    # YENİ MALZEME EKLE
    # =====================================================

    def yeni_malzeme_ekle(
        self,
        instance
    ):

        ad = self.yeni_malzeme_adi.text.strip()

        if not ad:
            return

        try:

            adet = int(
                self.yeni_malzeme_adet.text
                or 1
            )

        except:

            adet = 1

        try:

            birim = float(
                self.yeni_malzeme_fiyat.text
                or 0
            )

        except:

            birim = 0

        self.malzemeler.append({

            "ad": ad,

            "adet": adet,

            "birim_fiyat": birim,

            "fiyat": adet * birim,

            "odendi": False

        })

        self.yeni_malzeme_adi.text = ""
        self.yeni_malzeme_adet.text = ""
        self.yeni_malzeme_fiyat.text = ""

        self.malzemeleri_goster()

    # =====================================================
    # DEĞİŞİKLİKLERİ KAYDET
    # =====================================================

    def kaydet(self, instance):

        if self.is_index is None:
            return

        isler = oku(
            ISLER_DOSYASI
        )

        if not (
            0 <= self.is_index < len(isler)
        ):
            return

        try:

            gelir = float(
                self.gelir.text or 0
            )

        except:

            gelir = 0

        try:

            gider = float(
                self.gider.text or 0
            )

        except:

            gider = 0

        # Eski işin kayıt tarihi korunuyor.
        eski_tarih = isler[
            self.is_index
        ].get(
            "tarih",
            datetime.now().strftime(
                "%d.%m.%Y %H:%M"
            )
        )

        isler[self.is_index] = {

            "is_adi":
                self.is_adi.text.strip()
                or "İsimsiz İş",

            "yer":
                self.yer.text.strip(),

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

            "gider":
                gider,

            "malzemeler":
                self.malzemeler,

            "tarih":
                eski_tarih
        }

        kaydet(
            ISLER_DOSYASI,
            isler
        )

        self.manager.current = "gecmis"


# =========================================================
# GELİR / GİDER
# =========================================================

class GelirGider(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        ana = BoxLayout(
            orientation="vertical",
            padding=dp(13),
            spacing=dp(6)
        )

        ana.add_widget(
            baslik("🏦 GELİR / GİDER")
        )

        self.ozet = Label(
            text="",
            font_size=18,
            bold=True,
            size_hint_y=None,
            height=dp(180)
        )

        ana.add_widget(self.ozet)

        scroll = ScrollView()

        self.detay = Label(
            text="",
            font_size=14,
            size_hint_y=None,
            halign="left",
            valign="top"
        )

        self.detay.bind(
            texture_size=
            lambda o, v:
            setattr(
                o,
                "height",
                v[1]
            )
        )

        scroll.add_widget(self.detay)

        ana.add_widget(scroll)

        geri = buton(
            "← ANA MENÜ",
            GRI,
            45,
            15
        )

        geri.bind(
            on_press=
            lambda x:
            setattr(
                self.manager,
                "current",
                "ana"
            )
        )

        ana.add_widget(geri)

        self.add_widget(ana)

    def on_enter(self):

        self.hesapla()

    def hesapla(self):

        h = hesaplar()

        durum = (
            "KÂR"
            if h["ay_net"] >= 0
            else
            "ZARAR"
        )

        isler = oku(
            ISLER_DOSYASI
        )

        self.ozet.text = (

            f"📅 BU AY\n"

            f"💰 Gelir: "
            f"{h['ay_gelir']:.2f} TL\n"

            f"💸 Diğer gider: "
            f"{h['ay_gider']:.2f} TL\n"

            f"📦 Malzeme: "
            f"{h['ay_malzeme']:.2f} TL\n"

            f"📊 {durum}: "
            f"{abs(h['ay_net']):.2f} TL\n\n"

            f"📚 TOPLAM NET: "
            f"{h['toplam_net']:.2f} TL"

        )

        text = "📋 İŞLER\n\n"

        for is_ in reversed(isler):

            net = (

                para(
                    is_.get(
                        "gelir",
                        0
                    )
                )

                -

                para(
                    is_.get(
                        "gider",
                        0
                    )
                )

                -

                toplam_malzeme(
                    is_
                )
            )

            text += (

                f"🔨 "
                f"{is_.get('is_adi','')}"
                f" → "
                f"{net:.2f} TL\n"

            )

        self.detay.text = text


# =========================================================
# MALZEME / ÖDEMELER
# =========================================================

class Malzemeler(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        ana = BoxLayout(
            orientation="vertical",
            padding=dp(13),
            spacing=dp(6)
        )

        ana.add_widget(
            baslik(
                "📦 MALZEME / ÖDEMELER"
            )
        )

        self.ozet = Label(
            text="",
            font_size=17,
            bold=True,
            size_hint_y=None,
            height=dp(90)
        )

        ana.add_widget(self.ozet)

        scroll = ScrollView()

        self.liste = BoxLayout(
            orientation="vertical",
            spacing=dp(7),
            size_hint_y=None
        )

        self.liste.bind(
            minimum_height=
            self.liste.setter("height")
        )

        scroll.add_widget(self.liste)

        ana.add_widget(scroll)

        geri = buton(
            "← ANA MENÜ",
            GRI,
            45,
            15
        )

        geri.bind(
            on_press=
            lambda x:
            setattr(
                self.manager,
                "current",
                "ana"
            )
        )

        ana.add_widget(geri)

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

        for i, is_ in enumerate(isler):

            malzemeler = is_.get(
                "malzemeler",
                []
            )

            if not malzemeler:
                continue

            self.liste.add_widget(
                Label(
                    text=(
                        f"🔨 "
                        f"{is_.get('is_adi','')}"
                    ),
                    bold=True,
                    font_size=16,
                    color=BEYAZ,
                    size_hint_y=None,
                    height=dp(32)
                )
            )

            for j, m in enumerate(
                malzemeler
            ):

                odendi = m.get(
                    "odendi",
                    False
                )

                durum = (
                    "✅ ÖDENDİ"
                    if odendi
                    else
                    "⏳ ÖDENECEK"
                )

                b = buton(

                    f"{m.get('ad','')} "
                    f"x{m.get('adet',1)}  • "
                    f"{para(m.get('fiyat',0)):.2f} TL  • "
                    f"{durum}",

                    YESIL
                    if odendi
                    else TURUNCU,

                    45,
                    13
                )

                b.bind(
                    on_press=
                    lambda _, a=i, bidx=j:
                    self.odeme_degistir(
                        a,
                        bidx
                    )
                )

                self.liste.add_widget(b)

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

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        ana = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(6)
        )

        ana.add_widget(
            baslik("📊 RAPORLAR")
        )

        scroll = ScrollView()

        self.liste = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None
        )

        self.liste.bind(
            minimum_height=
            self.liste.setter("height")
        )

        scroll.add_widget(self.liste)

        ana.add_widget(scroll)

        geri = buton(
            "← ANA MENÜ",
            GRI,
            45,
            15
        )

        geri.bind(
            on_press=
            lambda x:
            setattr(
                self.manager,
                "current",
                "ana"
            )
        )

        ana.add_widget(geri)

        self.add_widget(ana)

    def on_enter(self):

        self.yenile()

    def yenile(self):

        self.liste.clear_widgets()

        h = hesaplar()

        isler = oku(
            ISLER_DOSYASI
        )

        self.liste.add_widget(
            Label(
                text=(

                    f"💰 TOPLAM GELİR\n"
                    f"{h['toplam_gelir']:.2f} TL\n\n"

                    f"💸 TOPLAM GİDER\n"
                    f"{h['toplam_gider']:.2f} TL\n\n"

                    f"📦 TOPLAM MALZEME\n"
                    f"{h['toplam_malzeme']:.2f} TL\n\n"

                    f"📊 TOPLAM NET\n"
                    f"{h['toplam_net']:.2f} TL"

                ),
                font_size=19,
                bold=True,
                color=BEYAZ,
                size_hint_y=None,
                height=dp(220)
            )
        )

        devam = 0
        bitti = 0
        beklemede = 0

        for is_ in isler:

            durum = is_durumu(is_)

            if durum == "Devam ediyor":
                devam += 1

            elif durum == "Bitti":
                bitti += 1

            elif durum == "Beklemede":
                beklemede += 1

        self.liste.add_widget(
            Label(
                text=(

                    "📌 İŞ DURUMLARI\n\n"

                    f"🟢 Devam eden: {devam}\n"

                    f"🔵 Biten: {bitti}\n"

                    f"🟠 Beklemede: {beklemede}"

                ),
                font_size=18,
                color=BEYAZ,
                size_hint_y=None,
                height=dp(150)
            )
        )


# =========================================================
# YEDEKLEME / AYARLAR
# =========================================================

class Ayarlar(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        ana = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(10)
        )

        ana.add_widget(
            baslik(
                "⚙ YEDEKLEME / AYARLAR"
            )
        )

        ana.add_widget(
            Label(
                text=(
                    "Verilerini yedekleyebilir "
                    "ve daha sonra geri yükleyebilirsin.\n\n"
                    "Yedekler 'yedekler' klasörüne kaydedilir."
                ),
                font_size=15,
                color=SOLUK,
                size_hint_y=None,
                height=dp(100)
            )
        )

        yedek = buton(
            "💾 ŞİMDİ YEDEKLE",
            MAVI,
            55,
            18
        )

        yedek.bind(
            on_press=self.yedekle
        )

        ana.add_widget(yedek)

        geri_yukle = buton(
            "↩ SON YEDEĞİ GERİ YÜKLE",
            TURUNCU,
            55,
            18
        )

        geri_yukle.bind(
            on_press=self.geri_yukle
        )

        ana.add_widget(geri_yukle)

        konum = buton(
            "ℹ DOSYA KONUMUNU GÖSTER",
            GRI,
            55,
            17
        )

        konum.bind(
            on_press=self.konum
        )

        ana.add_widget(konum)

        ana.add_widget(
            Label(
                text=""
            )
        )

        geri = buton(
            "← ANA MENÜ",
            GRI,
            45,
            15
        )

        geri.bind(
            on_press=
            lambda x:
            setattr(
                self.manager,
                "current",
                "ana"
            )
        )

        ana.add_widget(geri)

        self.add_widget(ana)

    def mesaj(
        self,
        baslik_yazi,
        metin
    ):

        Popup(
            title=baslik_yazi,
            content=Label(
                text=metin
            ),
            size_hint=(.85, .4)
        ).open()

    def yedekle(self, instance):

        os.makedirs(
            YEDEK_KLASORU,
            exist_ok=True
        )

        tarih = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        dosyalar = [
            ISLER_DOSYASI,
            YERLER_DOSYASI
        ]

        sayac = 0

        for dosya in dosyalar:

            if os.path.exists(dosya):

                isim = os.path.basename(
                    dosya
                )

                hedef = os.path.join(
                    YEDEK_KLASORU,
                    f"{tarih}_{isim}"
                )

                shutil.copy2(
                    dosya,
                    hedef
                )

                sayac += 1

        self.mesaj(
            "YEDEK TAMAM",
            f"{sayac} dosya yedeklendi."
        )

    def geri_yukle(self, instance):

        if not os.path.exists(
            YEDEK_KLASORU
        ):

            self.mesaj(
                "YEDEK YOK",
                "Henüz yedek bulunamadı."
            )

            return

        dosyalar = sorted(
            os.listdir(
                YEDEK_KLASORU
            ),
            reverse=True
        )

        if not dosyalar:

            self.mesaj(
                "YEDEK YOK",
                "Henüz yedek bulunamadı."
            )

            return

        son_isler = None
        son_yerler = None

        for dosya in dosyalar:

            yol = os.path.join(
                YEDEK_KLASORU,
                dosya
            )

            if (
                son_isler is None
                and
                dosya.endswith(
                    "isler.json"
                )
            ):

                son_isler = yol

            if (
                son_yerler is None
                and
                dosya.endswith(
                    "yerler.json"
                )
            ):

                son_yerler = yol

        sayac = 0

        if son_isler:

            shutil.copy2(
                son_isler,
                ISLER_DOSYASI
            )

            sayac += 1

        if son_yerler:

            shutil.copy2(
                son_yerler,
                YERLER_DOSYASI
            )

            sayac += 1

        self.mesaj(
            "GERİ YÜKLENDİ",
            f"{sayac} dosya geri yüklendi."
        )

    def konum(self, instance):

        self.mesaj(
            "DOSYA KONUMU",
            BASE_DIR
        )


# =========================================================
# UYGULAMA
# =========================================================

class IsTakipApp(App):

    def build(self):

        Window.clearcolor = ARKA

        ekranlar = ScreenManager()

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

        # YENİ: İŞ DETAY EKRANI
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

        return ekranlar


# =========================================================
# BAŞLAT
# =========================================================

if __name__ == "__main__":
    IsTakipApp().run()
