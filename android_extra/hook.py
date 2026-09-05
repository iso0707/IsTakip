# =========================================================
# p4a HOOK - AndroidManifest.xml'e FileProvider ekler
# =========================================================
#
# NEDEN GEREKLI: Makbuz PDF'ini paylasma ozelligi (main.py ->
# makbuz_paylas / _android_paylas) androidx FileProvider
# kullaniyor. FileProvider'in calismasi icin AndroidManifest.xml
# icindeki <application> etiketinin ICINE bir <provider>
# ALT-ETIKETI eklenmesi gerekiyor.
#
# buildozer.spec'teki "android.extra_manifest_application_arguments"
# secenegi SADECE <application> etiketine ekstra ATTRIBUTE
# eklemek icindir, alt-etiket icin degildir - onu kullanmak
# AndroidManifest.xml'i bozup "processDebugMainManifest" /
# ManifestMerger2 parse hatasi veriyordu.
#
# Bu yuzden <provider> tanimi, p4a manifesti dosya olarak
# URETTIKTEN SONRA (gradle derlemesinden ONCE) bu hook ile
# metin olarak guvenli sekilde ekleniyor.
#
# buildozer.spec -> p4a.hook = android_extra/hook.py

from pathlib import Path


_PROVIDER_XML = """
    <provider
        android:name="androidx.core.content.FileProvider"
        android:authorities="${applicationId}.fileprovider"
        android:exported="false"
        android:grantUriPermissions="true">
        <meta-data
            android:name="android.support.FILE_PROVIDER_PATHS"
            android:resource="@xml/file_paths" />
    </provider>
"""


def _manifesti_yamala(dist_dir):

    manifest_yolu = Path(dist_dir) / "src" / "main" / "AndroidManifest.xml"

    if not manifest_yolu.exists():
        print(f"[hook] AndroidManifest.xml bulunamadi: {manifest_yolu}")
        return

    icerik = manifest_yolu.read_text(encoding="utf-8")

    if "FileProvider" in icerik:
        # Zaten eklenmis (ikinci bir derleme calistirilmis olabilir).
        return

    if "</application>" not in icerik:
        print("[hook] </application> etiketi bulunamadi, atlaniyor.")
        return

    yeni_icerik = icerik.replace(
        "</application>",
        _PROVIDER_XML + "    </application>"
    )

    manifest_yolu.write_text(yeni_icerik, encoding="utf-8")
    print(f"[hook] FileProvider AndroidManifest.xml'e eklendi: {manifest_yolu}")


def after_apk_build(toolchain):
    """
    p4a, dagitim (dist) dosyalarini (AndroidManifest.xml dahil)
    urettikten hemen sonra, gradle derlemesi baslamadan once
    cagrilir.
    """
    try:
        dist_dir = toolchain._dist.dist_dir
    except Exception as e:
        print(f"[hook] dist_dir alinamadi: {e}")
        return

    _manifesti_yamala(dist_dir)
