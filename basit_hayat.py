import random
import time

class YapayZeka:
    def __init__(self):
        self.aclik = 50
        self.enerji = 50
        self.para = 20
        self.hayatta_kalan_gun = 0

    def eylem_sec(self):
        if self.aclik > 70:
            return self.yemek_ye
        elif self.enerji < 30:
            return self.uyu
        else:
            return self.calis

    def yemek_ye(self):
        if self.para >= 10:
            self.para -= 10
            self.aclik -= 30
            print("Yemek yendi.")
        else:
            print("Yeterli para yok, yemek alınamadı.")

    def uyu(self):
        self.enerji += 40
        print("Uyunuyor...")

    def calis(self):
        self.para += 20
        self.enerji -= 10
        self.aclik += 10
        print("Çalışılıyor...")

    def durum_guncelle(self):
        self.aclik += 5
        self.enerji -= 2
        if self.aclik >= 100 or self.enerji <= 0:
            return False
        return True

    def durum_goster(self):
        print(f"Gün: {self.hayatta_kalan_gun} | Açlık: {self.aclik} | Enerji: {self.enerji} | Para: {self.para}")

def main():
    ai = YapayZeka()
    while ai.durum_guncelle():
        ai.hayatta_kalan_gun += 1
        ai.durum_goster()
        eylem = ai.eylem_sec()
        eylem()
        time.sleep(1)
    print("Yapay zeka öldü.")
    print(f"Hayatta kalınan gün: {ai.hayatta_kalan_gun}")

if __name__ == "__main__":
    main()
