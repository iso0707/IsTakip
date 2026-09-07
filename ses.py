# =========================================================
# SES KAYDI (Uygulama İçinden Mikrofonla Kayıt)
# =========================================================
#
# İş eklerken veya iş detayında, telefonun mikrofonuyla doğrudan
# UYGULAMA İÇİNDEN sesli not kaydetmeyi sağlar. Fotoğraf ekleme
# özelliğinin tersine burada dosya SEÇİLMEZ (galeri/ses seçici
# yok); kayıt bu ekrandaki buton ile başlatılıp durdurulur.
#
# HATA DÜZELTMESİ: Kayıt artık plyer.audio ÜZERİNDEN DEĞİL,
# projenin diğer kısımlarında (bildirimler.py, main.py paylaşım)
# olduğu gibi doğrudan Android API'siyle (pyjnius ile
# android.media.MediaRecorder) yapılır. SEBEP: plyer'ın Android
# ses kaydı desteği güvenilir değildi ve gerçek cihazlarda
# sessizce başarısız olup "bu cihazda ses kaydı desteklenmiyor"
# hatasına yol açıyordu. Kaydedilen ses dosyası doğrudan
# uygulamanın kendi "ses_kayitlari" klasörüne yazılır; işe
# sadece dosya adı kaydedilir (isler.json içinde
# "ses_kayitlari": [...] listesi).
#
# Kayıt adedi SINIRSIZDIR. Sadece 15 ve üzeri kayıt birikince,
# çok sayıda ses dosyasının paylaşım/senkronizasyon sırasında
# aşırı veri kullanımına yol açabileceğine dair kullanıcıya tek
# seferlik bir uyarı gösterilir; kayıt engellenmez.
#
# ÖNEMLİ (buildozer.spec): android.permissions içine RECORD_AUDIO
# eklenmelidir.
#
# NOT: Masaüstünde (Windows/Linux/Mac) ses kaydı desteklenmez
# (bu özellik sadece Android'de çalışır); bu durumda hata
# sessizce yakalanır, kullanıcıya kısa bir bilgi mesajı
# gösterilir, uygulamanın diğer kısımları etkilenmez.

import os
import time

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.audio import SoundLoader
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SES_KLASORU = os.path.join(BASE_DIR, "ses_kayitlari")

# Yeni İş / İş Detayı ekranlarının koyu tasarımıyla uyumlu
# olması için buton rengi koyu zeminli; yazı bu yüzden açık.
_BUTON = (0.13, 0.15, 0.19, 1)
_BUTON_METIN = (0.96, 0.97, 0.98, 1)
_BEYAZ = (0.96, 0.97, 0.98, 1)
_SOLUK = (0.70, 0.72, 0.76, 1)
_KIRMIZI = (0.85, 0.20, 0.20, 1)
_YESIL = (0.20, 0.66, 0.46, 1)

# 15 ve üzeri ses kaydında aşırı veri uyarısı gösterilir.
ASIRI_KAYIT_ESIGI = 15


# ---------------------------------------------------------
# Dosya işlemleri
# ---------------------------------------------------------

def _klasoru_hazirla():
    os.makedirs(SES_KLASORU, exist_ok=True)


def yeni_dosya_adi(uzanti=".3gp"):
    _klasoru_hazirla()
    zaman = time.strftime("%Y%m%d_%H%M%S")
    milis = int((time.time() % 1) * 1000)
    return f"ses_{zaman}_{milis}{uzanti}"


def tam_yol(dosya_adi):
    return os.path.join(SES_KLASORU, dosya_adi)


class _MikrofonKaydedici:
    """
    HATA DÜZELTMESİ: Daha önce plyer.audio kullanılıyordu; ancak
    plyer'ın Android ses kaydı desteği güvenilir değil (birçok
    cihaz/derlemede sessizce başarısız olup "bu cihazda ses
    kaydı desteklenmiyor" hatasına yol açıyordu). Projenin diğer
    kısımlarında (bildirimler.py, main.py paylaşım) olduğu gibi
    burada da plyer YERİNE doğrudan Android API'si (pyjnius ile
    android.media.MediaRecorder) kullanılır; bu standart ve
    güvenilir bir yöntemdir.

    Kayıt, doğrudan uygulamanın kendi "ses_kayitlari" klasörüne
    (aynı zamanda uygulamanın özel/private depolama alanı) MP4/
    AAC (.m4a) olarak yazılır; bu yüzden ayrıca bir "kopyalama"
    adımına gerek kalmaz.

    Masaüstünde (Windows/Linux/Mac) bu sınıf kullanılmaz;
    basla() NotImplementedError fırlatır, ses.py bunu yakalayıp
    kullanıcıya bilgi mesajı gösterir.
    """

    def __init__(self):
        self._recorder = None
        self._dosya_yolu = None

    def basla(self):
        from kivy.utils import platform

        if platform != "android":
            raise NotImplementedError(
                "Ses kaydı sadece Android cihazlarda "
                "desteklenir."
            )

        from jnius import autoclass

        MediaRecorder = autoclass(
            "android.media.MediaRecorder"
        )
        AudioSource = autoclass(
            "android.media.MediaRecorder$AudioSource"
        )
        OutputFormat = autoclass(
            "android.media.MediaRecorder$OutputFormat"
        )
        AudioEncoder = autoclass(
            "android.media.MediaRecorder$AudioEncoder"
        )

        _klasoru_hazirla()

        dosya_yolu = tam_yol(
            yeni_dosya_adi(".m4a")
        )

        recorder = MediaRecorder()

        try:
            recorder.setAudioSource(AudioSource.MIC)
            recorder.setOutputFormat(
                OutputFormat.MPEG_4
            )
            recorder.setAudioEncoder(AudioEncoder.AAC)
            recorder.setOutputFile(dosya_yolu)
            recorder.prepare()
            recorder.start()
        except Exception:
            try:
                recorder.release()
            except Exception:
                pass
            raise

        self._recorder = recorder
        self._dosya_yolu = dosya_yolu

    def bitir(self):
        if self._recorder is None:
            return None

        dosya_yolu = self._dosya_yolu
        recorder = self._recorder

        self._recorder = None
        self._dosya_yolu = None

        try:
            recorder.stop()
        except Exception as e:
            print(f"[ses] MediaRecorder stop hatası: {e}")
            dosya_yolu = None
        finally:
            try:
                recorder.release()
            except Exception:
                pass

        return dosya_yolu


_kaydedici = _MikrofonKaydedici()


# ---------------------------------------------------------
# Yeniden kullanılabilir widget: kayıt başlat/bitir butonu +
# kaydedilen ses notları listesi (oynat / sil)
# ---------------------------------------------------------

class SesKaydedici(BoxLayout):

    def __init__(self, uyari_callback=None, **kwargs):

        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("spacing", dp(7))
        kwargs.setdefault("size_hint_y", None)

        super().__init__(**kwargs)

        self.dosyalar = []
        self._uyari_callback = uyari_callback
        self._kayit_yapiliyor = False
        self._baslama_zamani = None
        self._calan_ses = None
        self._calan_dosya = None
        self._calan_buton = None
        self._uyari_gosterildi = False

        self.bind(
            minimum_height=self.setter("height")
        )

        baslik = Label(
            text="🎙 Ses Kayıtları",
            font_size=14,
            bold=True,
            color=_SOLUK,
            size_hint_y=None,
            height=dp(20),
            halign="left",
            valign="middle"
        )

        baslik.bind(
            size=lambda o, v: setattr(o, "text_size", v)
        )

        self.add_widget(baslik)

        satir = BoxLayout(
            size_hint_y=None,
            height=dp(54),
            spacing=dp(7)
        )

        self.kayit_btn = Button(
            text="🔴 SES KAYDET",
            background_normal="",
            background_color=_BUTON,
            color=_BUTON_METIN,
            font_size=15
        )

        self.kayit_btn.bind(
            on_press=self._kayit_toggle
        )

        satir.add_widget(self.kayit_btn)

        self.sure_label = Label(
            text="",
            font_size=16,
            bold=True,
            color=_KIRMIZI,
            size_hint_x=None,
            width=dp(64)
        )

        satir.add_widget(self.sure_label)

        self.add_widget(satir)

        self.liste_kutu = BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None
        )

        self.liste_kutu.bind(
            minimum_height=
            self.liste_kutu.setter("height")
        )

        self.add_widget(self.liste_kutu)

        self.durum_label = Label(
            text="",
            font_size=13,
            color=_SOLUK,
            size_hint_y=None,
            height=dp(18)
        )

        self.add_widget(self.durum_label)

    # -- dışarıdan (iş yükleme/temizleme) --

    def yukle(self, dosyalar):
        self._kayit_yapiliyor_iptal()
        self.dosyalar = list(dosyalar or [])
        self._uyari_gosterildi = (
            len(self.dosyalar) >= ASIRI_KAYIT_ESIGI
        )
        self.durum_label.text = ""
        self._listeyi_yenile()

    def _kayit_yapiliyor_iptal(self):
        if self._kayit_yapiliyor:
            self._kaydi_bitir()
        if self._calan_ses:
            self._calan_ses.stop()
            self._calan_ses = None
            self._calan_dosya = None

    # -- kayıt başlat / bitir --

    def _kayit_toggle(self, *args):
        if self._kayit_yapiliyor:
            self._kaydi_bitir()
        else:
            self._kaydi_baslat()

    def _kaydi_baslat(self, *args):

        # HATA DÜZELTMESİ: Uygulama açılışında istenen
        # RECORD_AUDIO izni henüz onaylanmamışsa (kullanıcı
        # ilk seferde kapatmış/geç onaylamış olabilir),
        # kayda başlamadan hemen önce tekrar kontrol edip
        # gerekirse yeniden isteriz. Böylece kullanıcı,
        # "desteklenmiyor" mesajını görüp uygulamayı kapatıp
        # açmak zorunda kalmadan izni verip devam edebilir.
        try:
            from kivy.utils import platform

            if platform == "android":
                from android.permissions import (
                    check_permission,
                    request_permissions,
                    Permission
                )

                if not check_permission(
                    Permission.RECORD_AUDIO
                ):
                    request_permissions(
                        [Permission.RECORD_AUDIO]
                    )

                    self.durum_label.text = (
                        "Mikrofon izni isteniyor, "
                        "izin verdikten sonra tekrar "
                        "deneyin."
                    )
                    return
        except Exception as e:
            print(f"[ses] izin kontrolü yapılamadı: {e}")

        try:
            _kaydedici.basla()
        except Exception as e:
            print(f"[ses] kayıt başlatılamadı: {e}")
            self.durum_label.text = (
                "Bu cihazda ses kaydı desteklenmiyor."
            )
            return

        self._kayit_yapiliyor = True
        self._baslama_zamani = time.time()

        self.kayit_btn.text = "⏹ KAYDI BİTİR"
        self.kayit_btn.background_color = _KIRMIZI
        self.kayit_btn.color = _BEYAZ

        self.durum_label.text = "Kayıt yapılıyor..."

        Clock.schedule_interval(
            self._sure_guncelle, 0.5
        )

    def _sure_guncelle(self, dt):

        if not self._kayit_yapiliyor:
            return False

        gecen = int(
            time.time() - self._baslama_zamani
        )

        dakika, saniye = divmod(gecen, 60)

        self.sure_label.text = (
            f"{dakika:02d}:{saniye:02d}"
        )

    def _kaydi_bitir(self, *args):

        self._kayit_yapiliyor = False

        Clock.unschedule(self._sure_guncelle)

        self.kayit_btn.text = "🔴 SES KAYDET"
        self.kayit_btn.background_color = _BUTON
        self.kayit_btn.color = _BUTON_METIN
        self.sure_label.text = ""

        try:
            kaynak_yol = _kaydedici.bitir()
        except Exception as e:
            print(f"[ses] kayıt durdurulamadı: {e}")
            self.durum_label.text = "Kayıt tamamlanamadı."
            return

        if not kaynak_yol or not os.path.exists(kaynak_yol):
            self.durum_label.text = "Kayıt tamamlanamadı."
            return

        # NOT: MediaRecorder dosyayı artık doğrudan
        # SES_KLASORU içine, doğru adla yazıyor; bu yüzden
        # ayrıca bir kopyalama adımına gerek yok. kaynak_yol
        # zaten hedef konumdadır, sadece dosya adını alırız.
        _klasoru_hazirla()

        hedef_ad = os.path.basename(kaynak_yol)

        self.dosyalar.append(hedef_ad)
        self.durum_label.text = "✅ Ses kaydı eklendi."

        self._listeyi_yenile()
        self._asiri_kayit_kontrol()

    def _asiri_kayit_kontrol(self):

        if (
            len(self.dosyalar) >= ASIRI_KAYIT_ESIGI
            and not self._uyari_gosterildi
        ):
            self._uyari_gosterildi = True

            if callable(self._uyari_callback):

                self._uyari_callback(
                    f"Bu işe {ASIRI_KAYIT_ESIGI} ya da daha "
                    "fazla ses kaydı eklediniz. Çok sayıda ses "
                    "kaydı, makbuz/paylaşım sırasında aşırı "
                    "veri kullanımına yol açabilir."
                )

    # -- liste / oynatma / silme --

    def _dosya_adi_kisa(self, dosya_adi):

        try:
            parca = dosya_adi.split("_")
            tarih = parca[1]
            saat = parca[2]

            return (
                f"{tarih[6:8]}.{tarih[4:6]}.{tarih[0:4]} "
                f"{saat[0:2]}:{saat[2:4]}:{saat[4:6]}"
            )
        except Exception:
            return dosya_adi

    def _calma_toggle(self, dosya_adi, buton_widget, *args):

        if (
            self._calan_dosya == dosya_adi
            and self._calan_ses
        ):
            self._calan_ses.stop()
            return

        if self._calan_ses:
            self._calan_ses.stop()
            self._calan_ses = None
            self._calan_dosya = None

        ses = SoundLoader.load(
            tam_yol(dosya_adi)
        )

        if not ses:
            self.durum_label.text = (
                "Ses dosyası oynatılamadı."
            )
            return

        eski_buton = self._calan_buton

        def _bitince(*_):
            buton_widget.text = "▶"
            if self._calan_dosya == dosya_adi:
                self._calan_ses = None
                self._calan_dosya = None
                self._calan_buton = None

        ses.bind(on_stop=_bitince)
        ses.play()

        self._calan_ses = ses
        self._calan_dosya = dosya_adi
        self._calan_buton = buton_widget
        buton_widget.text = "⏸"

    def _sil(self, dosya_adi, *args):

        if self._calan_dosya == dosya_adi and self._calan_ses:
            self._calan_ses.stop()
            self._calan_ses = None
            self._calan_dosya = None

        if dosya_adi in self.dosyalar:
            self.dosyalar.remove(dosya_adi)

        self._listeyi_yenile()

    def _listeyi_yenile(self):

        self.liste_kutu.clear_widgets()

        for i, dosya_adi in enumerate(
            self.dosyalar, start=1
        ):

            satir = BoxLayout(
                size_hint_y=None,
                height=dp(44),
                spacing=dp(6)
            )

            oynat_btn = Button(
                text="▶",
                size_hint_x=None,
                width=dp(44),
                background_normal="",
                background_color=_YESIL,
                color=_BEYAZ,
                font_size=16
            )

            etiket = Label(
                text=(
                    f"🎙 Kayıt {i}  •  "
                    f"{self._dosya_adi_kisa(dosya_adi)}"
                ),
                font_size=13,
                color=_BEYAZ,
                halign="left",
                valign="middle"
            )

            etiket.bind(
                size=lambda o, v:
                setattr(o, "text_size", v)
            )

            sil_btn = Button(
                text="✕",
                size_hint_x=None,
                width=dp(36),
                background_normal="",
                background_color=_KIRMIZI,
                color=_BEYAZ,
                font_size=14
            )

            oynat_btn.bind(
                on_press=lambda inst, d=dosya_adi, b=oynat_btn:
                self._calma_toggle(d, b)
            )

            sil_btn.bind(
                on_press=lambda inst, d=dosya_adi:
                self._sil(d)
            )

            satir.add_widget(oynat_btn)
            satir.add_widget(etiket)
            satir.add_widget(sil_btn)

            self.liste_kutu.add_widget(satir)
