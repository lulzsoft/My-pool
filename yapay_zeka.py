# -*- coding: utf-8 -*-

import numpy as np

class YapayZeka:
    """
    Hayat simülasyonu için karakteri yöneten basit bir sinir ağı modeli.
    Bu model, numpy kullanılarak sıfırdan oluşturulmuştur ve harici
    kütüphanelere (TensorFlow, PyTorch vb.) bağımlılığı yoktur.
    """
    def __init__(self, girdi_boyutu=6, gizli_katman_boyutu=100, cikti_boyutu=6):
        """
        Sinir ağını başlatır ve katmanların ağırlıklarını rastgele değerlerle oluşturur.

        Args:
            girdi_boyutu (int): Girdi katmanındaki nöron sayısı.
            gizli_katman_boyutu (int): Gizli katmanlardaki nöron sayısı.
            cikti_boyutu (int): Çıktı katmanındaki nöron sayısı.
        """
        # Katman boyutları
        self.girdi_boyutu = girdi_boyutu
        self.gizli_boyutu_1 = gizli_katman_boyutu
        self.gizli_boyutu_2 = gizli_katman_boyutu
        self.gizli_boyutu_3 = gizli_katman_boyutu
        self.cikti_boyutu = cikti_boyutu

        # Ağırlıkların ve sapmaların (bias) rastgele başlatılması
        # Girdi -> Gizli Katman 1
        self.W1 = np.random.randn(self.girdi_boyutu, self.gizli_boyutu_1)
        self.b1 = np.zeros((1, self.gizli_boyutu_1))
        # Gizli Katman 1 -> Gizli Katman 2
        self.W2 = np.random.randn(self.gizli_boyutu_1, self.gizli_boyutu_2)
        self.b2 = np.zeros((1, self.gizli_boyutu_2))
        # Gizli Katman 2 -> Gizli Katman 3
        self.W3 = np.random.randn(self.gizli_boyutu_2, self.gizli_boyutu_3)
        self.b3 = np.zeros((1, self.gizli_boyutu_3))
        # Gizli Katman 3 -> Çıktı
        self.W4 = np.random.randn(self.gizli_boyutu_3, self.cikti_boyutu)
        self.b4 = np.zeros((1, self.cikti_boyutu))

        # Olası eylemlerin listesi (çıktı nöronlarına karşılık gelir)
        self.eylemler = ['Çalış', 'Yemek Ye', 'Uyu', 'Temizlen', 'Eğitim Al', 'Kitap Oku']


    def _sigmoid(self, x):
        """Sigmoid aktivasyon fonksiyonu."""
        # Sayısal kararlılık için taşmayı önle
        x = np.clip(x, -500, 500)
        return 1 / (1 + np.exp(-x))

    def _ileri_yayilim(self, girdiler):
        """
        Sinir ağının ileri yayılım hesaplamasını gerçekleştirir.

        Args:
            girdiler (np.array): Normalleştirilmiş girdi verisi.

        Returns:
            np.array: Çıktı katmanının sonuçları.
        """
        # Katman 1
        z1 = np.dot(girdiler, self.W1) + self.b1
        a1 = self._sigmoid(z1)
        # Katman 2
        z2 = np.dot(a1, self.W2) + self.b2
        a2 = self._sigmoid(z2)
        # Katman 3
        z3 = np.dot(a2, self.W3) + self.b3
        a3 = self._sigmoid(z3)
        # Çıktı Katmanı
        z4 = np.dot(a3, self.W4) + self.b4
        cikti = self._sigmoid(z4)
        return cikti

    def _normalize_state(self, oyuncu, zaman):
        """
        Oyuncu ve zaman durumunu sinir ağı için normalleştirir (0-1 arasına getirir).

        Args:
            oyuncu (Oyuncu): Oyuncu nesnesi.
            zaman (ZamanSistemi): Zaman nesnesi.

        Returns:
            np.array: Normalleştirilmiş durum vektörü.
        """
        # Konumları sayısal bir değere dönüştür
        konum_map = {"Ev": 0.0, "Şehir Merkezi": 0.5, "Sanayi Bölgesi": 1.0}
        konum_degeri = konum_map.get(oyuncu.mevcut_konum.ad, 0.0)

        # Para için bir üst sınır belirleyerek normalleştir
        max_para = 10000.0

        state = np.array([
            oyuncu.saglik / 100.0,
            oyuncu.enerji / 100.0,
            oyuncu.aclik / 100.0,
            min(oyuncu.para, max_para) / max_para,
            zaman.saat / 23.0,
            konum_degeri
        ])

        return state.reshape(1, self.girdi_boyutu)

    def karar_ver(self, oyuncu, zaman):
        """
        Oyuncunun mevcut durumuna göre en uygun eylemi seçer.

        Args:
            oyuncu (Oyuncu): Oyuncu nesnesi.
            zaman (ZamanSistemi): Zaman nesnesi.

        Returns:
            str: Seçilen eylemin adı.
        """
        # "Geleceğe yatırım" mantığı
        # Temel ihtiyaçlar belirli bir seviyenin üzerindeyse, yatırım eylemlerini önceliklendir.
        temel_ihtiyaclar_yerinde = (oyuncu.saglik > 80 and
                                    oyuncu.enerji > 80 and
                                    oyuncu.aclik < 20 and
                                    oyuncu.hijyen > 70)

        # Oyuncu durumunu normalize et
        norm_state = self._normalize_state(oyuncu, zaman)

        # Karar için ileri yayılımı çalıştır
        eylem_guven_skorlari = self._ileri_yayilim(norm_state)

        if temel_ihtiyaclar_yerinde:
            # Sadece yatırım eylemlerini (Eğitim Al, Kitap Oku) dikkate al
            yatirim_eylem_indexleri = [4, 5]
            # Diğer eylemlerin skorlarını sıfırla
            mask = np.zeros_like(eylem_guven_skorlari)
            mask[0, yatirim_eylem_indexleri] = 1
            eylem_guven_skorlari *= mask

        # En yüksek güven skoruna sahip eylemin index'ini bul
        secilen_eylem_index = np.argmax(eylem_guven_skorlari)

        return self.eylemler[secilen_eylem_index]
