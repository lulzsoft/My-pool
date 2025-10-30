# -*- coding: utf-8 -*-

# Bu dosya, oyun içindeki tüm statik ve yapılandırma verilerini barındırır.
# Bu veriler oyunun "bilgi tabanı" olarak işlev görür ve genellikle oyun
# çalışırken değişmezler.

# Bağımlılıkları önlemek için bu dosyaya class veya sistem importu yapılmamalıdır.
from varliklar import Kariyer

ISIM_LISTESI = ["Ali", "Ayşe", "Mehmet", "Fatma", "Hasan", "Zeynep", "Emre", "Elif"]
SOYISIM_LISTESI = ["Yılmaz", "Kaya", "Demir", "Çelik", "Arslan", "Doğan", "Kurt"]
DEPARTMANLAR = ["Uretim", "Pazarlama", "Tedarik", "Ar-Ge"]

KARİYERLER = {
    "Yazılım Geliştirici": Kariyer("Yazılım Geliştirici", True, {
        1: {"unvan": "Stajyer Yazılımcı", "maas": 250, "tecrube_gereksinimi": 0},
        2: {"unvan": "Junior Yazılımcı", "maas": 400, "tecrube_gereksinimi": 200},
        3: {"unvan": "Senior Yazılımcı", "maas": 700, "tecrube_gereksinimi": 500}
    }),
    "Doktor": Kariyer("Doktor", True, {
        1: {"unvan": "Asistan Doktor", "maas": 350, "tecrube_gereksinimi": 0},
        2: {"unvan": "Uzman Doktor", "maas": 600, "tecrube_gereksinimi": 300},
        3: {"unvan": "Operatör Doktor", "maas": 1000, "tecrube_gereksinimi": 700}
    }),
    "Vasıfsız İşçi": Kariyer("Vasıfsız İşçi", False, {
        1: {"unvan": "İşçi", "maas": 120, "tecrube_gereksinimi": 0},
        2: {"unvan": "Usta Başı", "maas": 180, "tecrube_gereksinimi": 400}
    })
}

EV_EKSİKLİKLERİ = {
    "Sızdıran Çatı": {"maliyet": 1500, "kategori": "genel"},
    "Bozuk Parke": {"maliyet": 800, "kategori": "oda"},
    "Eski Tesisat": {"maliyet": 2500, "kategori": "genel"},
    "Çatlak Duvarlar": {"maliyet": 600, "kategori": "oda"},
    "Bozuk Prizler": {"maliyet": 300, "kategori": "oda"},
    "Eski Mutfak Dolapları": {"maliyet": 1200, "kategori": "mutfak"},
    "Bozuk Musluklar": {"maliyet": 250, "kategori": "mutfak_banyo"},
    "Tıkalı Giderler": {"maliyet": 400, "kategori": "mutfak_banyo"},
    "Kırık Pencereler": {"maliyet": 700, "kategori": "genel"},
    "Boya İhtiyacı": {"maliyet": 900, "kategori": "genel"},
    "Zayıf İnternet Altyapısı": {"maliyet": 1000, "kategori": "genel"},
    "Yetersiz Isı Yalıtımı": {"maliyet": 1800, "kategori": "genel"},
    "Eski Banyo Fayansları": {"maliyet": 1100, "kategori": "banyo"},
    "Bozuk Kombi/Isıtma Sistemi": {"maliyet": 3000, "kategori": "genel"},
    "Güvenlik Sistemi Eksikliği": {"maliyet": 1300, "kategori": "genel"},
    "Bahçe Bakımsızlığı": {"maliyet": 500, "kategori": "bahce"},
    "Bozuk Bahçe Çiti": {"maliyet": 650, "kategori": "bahce"},
    "Havuz Bakım Sorunu": {"maliyet": 2200, "kategori": "havuz"},
    "Garaj Kapısı Arızası": {"maliyet": 950, "kategori": "garaj"},
    "Küf Sorunu": {"maliyet": 1600, "kategori": "genel"},
    "Haşere Sorunu": {"maliyet": 750, "kategori": "genel"}
}

EV_TİPLERİ = {
    "1+0 Stüdyo Daire": {"min_m2": 35, "max_m2": 50, "temel_fiyat": 60000, "kategoriler": ["genel", "oda", "mutfak_banyo", "banyo"]},
    "1+1 Apartman Dairesi": {"min_m2": 55, "max_m2": 75, "temel_fiyat": 90000, "kategoriler": ["genel", "oda", "mutfak_banyo", "mutfak", "banyo"]},
    "2+1 Apartman Dairesi": {"min_m2": 80, "max_m2": 110, "temel_fiyat": 150000, "kategoriler": ["genel", "oda", "mutfak_banyo", "mutfak", "banyo"]},
    "Bahçeli Müstakil Ev": {"min_m2": 120, "max_m2": 200, "temel_fiyat": 250000, "kategoriler": ["genel", "oda", "mutfak_banyo", "mutfak", "banyo", "bahce", "garaj"]},
    "Villa": {"min_m2": 250, "max_m2": 400, "temel_fiyat": 500000, "kategoriler": ["genel", "oda", "mutfak_banyo", "mutfak", "banyo", "bahce", "garaj", "havuz"]}
}

URUN_RECETELERI = {
    "elektronik cihaz": {"metal": 2, "silikon": 3, "plastik": 1},
    "kıyafet": {"tekstil": 5, "plastik": 1}
}

MAGAZA_ESYALARI = {
    "gazete": {"fiyat": 25},
    "kitap": {"fiyat": 75, "etki": "zeka", "deger": 5},
    "konsol oyunu": {"fiyat": 200, "etki": "mutluluk", "deger": 15},
    "abur cubur": {"fiyat": 15, "etki": "aclik", "deger": -40, "metabolizma_etkisi": 0.2},
    "ev yemeği": {"fiyat": 40, "etki": "aclik", "deger": -50, "metabolizma_etkisi": 0},
    "lüks restoran yemeği": {"fiyat": 150, "etki": "aclik", "deger": -70, "metabolizma_etkisi": -0.1},
    "sabun": {"fiyat": 10, "etki": "hijyen", "deger": 20}
}
