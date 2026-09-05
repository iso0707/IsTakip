# =========================================================
# MINI PDF - Sıfır bağımlılıklı, saf Python PDF yazıcı
# =========================================================
#
# fpdf / fpdf2 yerine geçer. Hiçbir dış pakete (Pillow dahil)
# ihtiyaç duymaz, bu yüzden Android (buildozer/python-for-
# android) derlemesinde hiçbir pip/recipe çakışması yaratmaz.
#
# Sadece makbuz.py'nin ihtiyaç duyduğu kadarını destekler:
# metin hücreleri (cell), çok satırlı metin (multi_cell),
# çizgi (line), dolu/boş dikdörtgen (rect), temel renkler,
# Helvetica / Helvetica-Bold standart PDF fontları.
#
# Görsel (logo) ekleme YOKTUR - kasıtlı olarak kaldırıldı,
# çünkü resim gömmek (JPEG/PNG çözümleme) ek karmaşıklık ve
# potansiyel bağımlılık getirir. Metin tabanlı makbuz için
# bu özellik gerekli değildir.
#
# Türkçe karakterler (ş, ğ, ı, ö, ü, ç) standart PDF
# fontlarında (WinAnsi kodlaması) düzgün gösterilemediği
# için main.py tarafındaki _TURKCE_CEVIRI ile ASCII
# karşılığına çevrilerek gönderilmelidir.

import os


# ---------------------------------------------------------
# Helvetica standart genişlik tablosu (1/1000 em birim).
# PDF spesifikasyonunun bir parçası olan herkese açık (kamu
# malı) AFM metrik değerleridir - telif hakkı içermez.
# ---------------------------------------------------------
_HELV_GENISLIK = {
    32: 278, 33: 278, 34: 355, 35: 556, 36: 556, 37: 889,
    38: 667, 39: 191, 40: 333, 41: 333, 42: 389, 43: 584,
    44: 278, 45: 333, 46: 278, 47: 278, 48: 556, 49: 556,
    50: 556, 51: 556, 52: 556, 53: 556, 54: 556, 55: 556,
    56: 556, 57: 556, 58: 278, 59: 278, 60: 584, 61: 584,
    62: 584, 63: 556, 64: 1015, 65: 667, 66: 667, 67: 722,
    68: 722, 69: 667, 70: 611, 71: 778, 72: 722, 73: 278,
    74: 500, 75: 667, 76: 556, 77: 833, 78: 722, 79: 778,
    80: 667, 81: 778, 82: 722, 83: 667, 84: 611, 85: 722,
    86: 667, 87: 944, 88: 667, 89: 667, 90: 611, 91: 278,
    92: 278, 93: 278, 94: 469, 95: 556, 96: 333, 97: 556,
    98: 556, 99: 500, 100: 556, 101: 556, 102: 278,
    103: 556, 104: 556, 105: 222, 106: 222, 107: 500,
    108: 222, 109: 833, 110: 556, 111: 556, 112: 556,
    113: 556, 114: 333, 115: 500, 116: 278, 117: 556,
    118: 500, 119: 722, 120: 500, 121: 500, 122: 500,
    123: 334, 124: 260, 125: 334, 126: 584,
}

_HELV_BOLD_GENISLIK = dict(_HELV_GENISLIK)
_HELV_BOLD_GENISLIK.update({
    32: 278, 65: 722, 66: 722, 67: 722, 68: 722, 69: 667,
    70: 611, 71: 778, 72: 722, 73: 278, 74: 556, 75: 722,
    76: 611, 77: 833, 78: 722, 79: 778, 80: 667, 81: 778,
    82: 722, 83: 667, 84: 611, 85: 722, 86: 667, 87: 944,
    88: 667, 89: 667, 90: 611, 97: 556, 98: 611, 99: 556,
    100: 611, 101: 556, 102: 333, 103: 611, 104: 611,
    105: 278, 106: 278, 107: 556, 108: 278, 109: 889,
    110: 611, 111: 611, 112: 611, 113: 611, 114: 389,
    115: 556, 116: 333, 117: 611, 118: 556, 119: 778,
    120: 556, 121: 556, 122: 500,
})

_VARSAYILAN_GENISLIK = 556


def _metin_genislik_mm(metin, boyut_pt, kalin=False):
    tablo = _HELV_BOLD_GENISLIK if kalin else _HELV_GENISLIK
    toplam_1000 = 0
    for ch in metin:
        kod = ord(ch)
        toplam_1000 += tablo.get(kod, _VARSAYILAN_GENISLIK)
    # 1000 birim = 1 em = boyut_pt punto.
    # pt -> mm: * 0.352778
    return (toplam_1000 / 1000.0) * boyut_pt * 0.352778


def _pdf_kacir(metin):
    # PDF string literal içinde kaçırılması gereken karakterler.
    return (
        metin.replace("\\", r"\\")
        .replace("(", r"\(")
        .replace(")", r"\)")
    )


def _latin1_guvenli(metin):
    # WinAnsi/Latin-1 dışındaki karakterleri '?' ile değiştir
    # (main.py zaten Türkçe karakterleri önceden çeviriyor,
    # bu sadece son bir güvenlik ağı).
    try:
        metin.encode("latin-1")
        return metin
    except UnicodeEncodeError:
        return metin.encode("latin-1", errors="replace").decode(
            "latin-1"
        )


class MiniPDF:

    def __init__(self, orientation="P", unit="mm", format="A4"):

        if format == "A4":
            self.page_w, self.page_h = 210.0, 297.0
        else:
            self.page_w, self.page_h = 210.0, 297.0

        if orientation == "L":
            self.page_w, self.page_h = self.page_h, self.page_w

        self.l_margin = 10.0
        self.r_margin = 10.0
        self.t_margin = 10.0

        self.auto_break = False
        self.break_margin = 18.0

        self.x = self.l_margin
        self.y = self.t_margin

        self.font_size = 12
        self.font_bold = False

        self.text_color = (0, 0, 0)
        self.draw_color = (0, 0, 0)
        self.fill_color = (0, 0, 0)

        self._pages = []
        self._current_ops = None

    # -----------------------------------------------------
    # Sayfa / imleç yönetimi
    # -----------------------------------------------------

    def set_auto_page_break(self, auto=True, margin=18):
        self.auto_break = auto
        self.break_margin = margin

    def add_page(self):
        self._current_ops = []
        self._pages.append(self._current_ops)
        self.x = self.l_margin
        self.y = self.t_margin

    def set_xy(self, x, y):
        self.set_x(x)
        self.set_y(y)

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        if y < 0:
            self.y = self.page_h + y
        else:
            self.y = y

    def get_y(self):
        return self.y

    def get_x(self):
        return self.x

    def _sayfa_sonu_kontrol(self, yukseklik):
        if not self.auto_break:
            return
        if self.y + yukseklik > (self.page_h - self.break_margin):
            self.add_page()

    # -----------------------------------------------------
    # Stil
    # -----------------------------------------------------

    def set_font(self, family=None, style="", size=12):
        self.font_bold = "B" in (style or "")
        self.font_size = size

    def set_text_color(self, r, g=None, b=None):
        if g is None:
            g = r
        if b is None:
            b = r
        self.text_color = (r, g, b)

    def set_draw_color(self, r, g=None, b=None):
        if g is None:
            g = r
        if b is None:
            b = r
        self.draw_color = (r, g, b)

    def set_fill_color(self, r, g=None, b=None):
        if g is None:
            g = r
        if b is None:
            b = r
        self.fill_color = (r, g, b)

    # -----------------------------------------------------
    # Çizim ilkelleri (dahili)
    # -----------------------------------------------------

    def _renk_str(self, renk, dolgu):
        r, g, b = (c / 255.0 for c in renk)
        op = "rg" if dolgu else "RG"
        return f"{r:.3f} {g:.3f} {b:.3f} {op}"

    def _y_pdf(self, y_mm):
        # PDF koordinat sistemi sol-alt köşe kaynaklı, mm -> pt.
        return (self.page_h - y_mm) * 2.834645669

    def _x_pdf(self, x_mm):
        return x_mm * 2.834645669

    def _ciz_dikdortgen(self, x, y, w, h, dolu, cizgili):
        if self._current_ops is None:
            self.add_page()

        x_pt = self._x_pdf(x)
        y_pt = self._y_pdf(y + h)
        w_pt = w * 2.834645669
        h_pt = h * 2.834645669

        ops = self._current_ops

        if dolu:
            ops.append(self._renk_str(self.fill_color, True))

        if cizgili:
            ops.append(self._renk_str(self.draw_color, False))

        ops.append(f"{x_pt:.2f} {y_pt:.2f} {w_pt:.2f} {h_pt:.2f} re")

        if dolu and cizgili:
            ops.append("B")
        elif dolu:
            ops.append("f")
        else:
            ops.append("S")

    def _metin_yaz(self, x, y, metin, boyut, kalin, renk):
        if self._current_ops is None:
            self.add_page()

        if not metin:
            return

        metin = _latin1_guvenli(metin)
        font_adi = "/F2" if kalin else "/F1"

        # Metin taban çizgisi, hücrenin dikeyde ortalanması
        # için yaklaşık bir düzeltme ile hesaplanır.
        taban_y = y + (boyut * 0.352778) * 0.72

        x_pt = self._x_pdf(x)
        y_pt = self._y_pdf(taban_y)

        ops = self._current_ops
        ops.append(self._renk_str(renk, True))
        ops.append("BT")
        ops.append(f"{font_adi} {boyut:.2f} Tf")
        ops.append(f"{x_pt:.2f} {y_pt:.2f} Td")
        ops.append(f"({_pdf_kacir(metin)}) Tj")
        ops.append("ET")

    def line(self, x1, y1, x2, y2):
        if self._current_ops is None:
            self.add_page()

        ops = self._current_ops
        ops.append(self._renk_str(self.draw_color, False))
        ops.append(
            f"{self._x_pdf(x1):.2f} {self._y_pdf(y1):.2f} m"
        )
        ops.append(
            f"{self._x_pdf(x2):.2f} {self._y_pdf(y2):.2f} l"
        )
        ops.append("S")

    def rect(self, x, y, w, h, style=""):
        style = (style or "").upper()
        dolu = "F" in style
        cizgili = "D" in style or style == "" or "S" in style
        if dolu and "D" not in style and "S" not in style:
            cizgili = False
        self._ciz_dikdortgen(x, y, w, h, dolu, cizgili)

    # -----------------------------------------------------
    # Metin hücreleri
    # -----------------------------------------------------

    def cell(
        self, w, h, txt="", border=0, ln=0,
        align="L", fill=False
    ):
        self._sayfa_sonu_kontrol(h)

        if w == 0:
            w = self.page_w - self.r_margin - self.x

        x0, y0 = self.x, self.y

        if fill:
            self._ciz_dikdortgen(x0, y0, w, h, True, False)

        border_str = str(border) if border else ""
        if border_str in ("1",):
            border_str = "TRBL"

        if "T" in border_str:
            self.line(x0, y0, x0 + w, y0)
        if "B" in border_str:
            self.line(x0, y0 + h, x0 + w, y0 + h)
        if "L" in border_str:
            self.line(x0, y0, x0, y0 + h)
        if "R" in border_str:
            self.line(x0 + w, y0, x0 + w, y0 + h)

        if txt:
            metin_gen = _metin_genislik_mm(
                txt, self.font_size, self.font_bold
            )

            if align == "R":
                tx = x0 + w - metin_gen - 1
            elif align == "C":
                tx = x0 + (w - metin_gen) / 2.0
            else:
                tx = x0 + 1

            ty = y0 + (h - self.font_size * 0.352778) / 2.0

            self._metin_yaz(
                tx, ty, txt, self.font_size,
                self.font_bold, self.text_color
            )

        if ln == 1:
            self.x = self.l_margin
            self.y = y0 + h
        elif ln == 2:
            self.y = y0 + h
        else:
            self.x = x0 + w
            self.y = y0

    def multi_cell(self, w, h, txt):

        if w == 0:
            w = self.page_w - self.r_margin - self.x

        for paragraf in (txt or "").split("\n"):

            kelimeler = paragraf.split(" ")
            satir = ""

            for kelime in kelimeler:

                aday = (satir + " " + kelime).strip()

                genislik = _metin_genislik_mm(
                    aday, self.font_size, self.font_bold
                )

                if genislik > (w - 2) and satir:
                    self.set_x(self.l_margin)
                    self.cell(w, h, satir, ln=1)
                    satir = kelime
                else:
                    satir = aday

            self.set_x(self.l_margin)
            self.cell(w, h, satir, ln=1)

    # -----------------------------------------------------
    # Çıktı üretimi
    # -----------------------------------------------------

    def output(self, dosya_yolu):

        if not self._pages:
            self.add_page()

        buf = bytearray()
        offsets = []

        def yaz(veri):
            if isinstance(veri, str):
                veri = veri.encode("latin-1", errors="replace")
            buf.extend(veri)

        def nesne_basla(no):
            offsets.append((no, len(buf)))
            yaz(f"{no} 0 obj\n")

        yaz("%PDF-1.4\n")

        n_sayfa = len(self._pages)
        # Nesne numaralandırma:
        # 1: Catalog, 2: Pages, 3..: her sayfa (2 nesne:
        # page + content), sonda: font F1, font F2

        page_obj_nolari = []
        content_obj_nolari = []

        sonraki_no = 3
        for _ in self._pages:
            page_obj_nolari.append(sonraki_no)
            sonraki_no += 1
            content_obj_nolari.append(sonraki_no)
            sonraki_no += 1

        font1_no = sonraki_no
        font2_no = sonraki_no + 1

        # 1) Catalog
        nesne_basla(1)
        yaz(f"<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

        # 2) Pages
        kids = " ".join(f"{n} 0 R" for n in page_obj_nolari)
        nesne_basla(2)
        yaz(
            f"<< /Type /Pages /Kids [{kids}] "
            f"/Count {n_sayfa} >>\nendobj\n"
        )

        w_pt = self.page_w * 2.834645669
        h_pt = self.page_h * 2.834645669

        for i, ops in enumerate(self._pages):

            page_no = page_obj_nolari[i]
            content_no = content_obj_nolari[i]

            nesne_basla(page_no)
            yaz(
                f"<< /Type /Page /Parent 2 0 R "
                f"/MediaBox [0 0 {w_pt:.2f} {h_pt:.2f}] "
                f"/Resources << /Font << "
                f"/F1 {font1_no} 0 R /F2 {font2_no} 0 R "
                f">> >> "
                f"/Contents {content_no} 0 R >>\nendobj\n"
            )

            akis = "\n".join(ops)
            akis_bytes = akis.encode("latin-1", errors="replace")

            nesne_basla(content_no)
            yaz(f"<< /Length {len(akis_bytes)} >>\nstream\n")
            yaz(akis_bytes)
            yaz("\nendstream\nendobj\n")

        nesne_basla(font1_no)
        yaz(
            "<< /Type /Font /Subtype /Type1 "
            "/BaseFont /Helvetica /Encoding /WinAnsiEncoding "
            ">>\nendobj\n"
        )

        nesne_basla(font2_no)
        yaz(
            "<< /Type /Font /Subtype /Type1 "
            "/BaseFont /Helvetica-Bold "
            "/Encoding /WinAnsiEncoding >>\nendobj\n"
        )

        xref_konumu = len(buf)
        toplam_nesne = len(offsets) + 1

        yaz(f"xref\n0 {toplam_nesne}\n")
        yaz("0000000000 65535 f \n")

        offsets.sort(key=lambda o: o[0])
        for _, konum in offsets:
            yaz(f"{konum:010d} 00000 n \n")

        yaz(
            f"trailer\n<< /Size {toplam_nesne} "
            f"/Root 1 0 R >>\nstartxref\n{xref_konumu}\n"
            f"%%EOF"
        )

        os.makedirs(
            os.path.dirname(os.path.abspath(dosya_yolu)),
            exist_ok=True
        )

        with open(dosya_yolu, "wb") as f:
            f.write(bytes(buf))

        return dosya_yolu
