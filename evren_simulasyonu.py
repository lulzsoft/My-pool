import random
import time

class Evren:
    def __init__(self, baslangic_enerjisi=50, hedef_enerji=100, dalgalanma_araligi=0.5):
        self.enerji = baslangic_enerjisi
        self.hedef_enerji = hedef_enerji
        self.dalgalanma_araligi = dalgalanma_araligi

    def guncelle(self):
        # Evrenin enerjisi zamanla hedefe doğru veya rastgele dalgalanır
        dalgalanma = random.uniform(-self.dalgalanma_araligi, self.dalgalanma_araligi)
        self.enerji += dalgalanma

class Bilinç:
    def __init__(self, etki_gucu=1.0, tolerans=2.0):
        self.etki_gucu = etki_gucu
        self.tolerans = tolerans

    def karar_ver(self, evren):
        fark = evren.hedef_enerji - evren.enerji

        if abs(fark) <= self.tolerans:
            return "Bekle"
        elif fark > 0:
            return "Enerji Ver"
        else:
            return "Enerji Çek"

    def eyleme_gec(self, evren, karar):
        if karar == "Enerji Ver":
            evren.enerji += self.etki_gucu
        elif karar == "Enerji Çek":
            evren.enerji -= self.etki_gucu

def ana_simulasyon():
    evren = Evren()
    bilinc = Bilinç()
    adim = 0

    try:
        while True:
            evren.guncelle()
            karar = bilinc.karar_ver(evren)
            bilinc.eyleme_gec(evren, karar)

            print(f"Adım: {adim} | Evren Enerjisi: {evren.enerji:.2f} | Hedef: {evren.hedef_enerji} | AI Kararı: {karar}", end='\r')

            adim += 1
            time.sleep(0.1) # Simülasyon hızını ayarlar
    except KeyboardInterrupt:
        print("\nSimülasyon sonlandırıldı.")

if __name__ == "__main__":
    ana_simulasyon()
