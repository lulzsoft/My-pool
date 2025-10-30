import time
import numpy as np
import sys
from ogrenen_ai import OgrenenYapayZeka

class HayatOrtami:
    def __init__(self):
        self.sifirla()

    def sifirla(self):
        self.aclik = 50
        self.enerji = 50
        self.para = 20
        self.hayatta_kalan_gun = 0
        return self._durum_getir()

    def _durum_getir(self):
        # Durumu normalize ederek AI'ya veriyoruz
        return np.array([self.aclik / 100, self.enerji / 100, self.para / 100])

    def adim_at(self, eylem):
        odul = 0
        bitti = False

        # Eylemleri uygula
        if eylem == 0: # Yemek ye
            if self.para >= 10:
                self.para -= 10
                self.aclik -= 30
                odul = 5
            else:
                odul = -10 # Ceza
        elif eylem == 1: # Uyu
            self.enerji += 40
            odul = 2
        elif eylem == 2: # Çalış
            self.para += 20
            self.enerji -= 10
            self.aclik += 10
            odul = 1

        # Durumu güncelle
        self.aclik += 5
        self.enerji -= 2
        self.hayatta_kalan_gun += 1

        # Sınırları kontrol et
        if self.aclik > 100: self.aclik = 100
        if self.aclik < 0: self.aclik = 0
        if self.enerji > 100: self.enerji = 100
        if self.enerji < 0: self.enerji = 0

        # Ölüm kontrolü
        if self.aclik >= 100 or self.enerji <= 0:
            bitti = True
            odul = -100 # Büyük ceza

        yeni_durum = self._durum_getir()
        return yeni_durum, odul, bitti

def main():
    ortam = HayatOrtami()
    durum_boyutu = 3 # açlık, enerji, para
    eylem_sayisi = 3 # yemek ye, uyu, çalış
    ai = OgrenenYapayZeka(durum_boyutu, eylem_sayisi)

    bolum_sayisi = 1000
    en_uzun_hayatta_kalma = 0

    for bolum in range(bolum_sayisi):
        durum = ortam.sifirla()
        toplam_odul = 0
        bitti = False

        while not bitti:
            eylem = ai.eylem_sec(durum)
            yeni_durum, odul, bitti = ortam.adim_at(eylem)

            ai.ogren(durum, eylem, odul, yeni_durum, bitti)

            durum = yeni_durum
            toplam_odul += odul

            if ortam.hayatta_kalan_gun > en_uzun_hayatta_kalma:
                en_uzun_hayatta_kalma = ortam.hayatta_kalan_gun

            # Tek satırda anlık durum gösterimi
            yazi = f"Bölüm: {bolum + 1}/{bolum_sayisi} | Gün: {ortam.hayatta_kalan_gun} | En Uzun: {en_uzun_hayatta_kalma} | Ödül: {toplam_odul:.2f} | Açlık: {ortam.aclik:.2f} | Enerji: {ortam.enerji:.2f} | Para: {ortam.para:.2f} | Epsilon: {ai.epsilon:.2f}"
            sys.stdout.write("\r" + yazi.ljust(120))
            sys.stdout.flush()

    print("\nEğitim tamamlandı.")

if __name__ == "__main__":
    main()
