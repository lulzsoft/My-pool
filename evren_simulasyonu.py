import random
import time

class Gunes:
    def __init__(self, baslangic_enerjisi=1000, azalma_orani=1):
        self.enerji = baslangic_enerjisi
        self.azalma_orani = azalma_orani
        if self.azalma_orani <= 0:
            self.azalma_orani = 1 # Negatif veya sıfır olmasını engelle

    def guncelle(self):
        """Güneş'in enerjisini her adımda azaltır."""
        self.enerji -= self.azalma_orani

class Bilinç:
    def __init__(self, baslangic_enerjisi=100, kritik_gunes_seviyesi=200, aktarim_miktari=50, problem_odulu=10):
        self.enerji = baslangic_enerjisi
        self.kritik_gunes_seviyesi = kritik_gunes_seviyesi
        self.aktarim_miktari = aktarim_miktari
        self.problem_odulu = problem_odulu
        self.mevcut_problem = None
        self.problem_olustur()

    def problem_olustur(self):
        """Basit bir toplama problemi oluşturur."""
        sayi1 = random.randint(1, 10)
        sayi2 = random.randint(1, 10)
        self.mevcut_problem = (f"{sayi1} + {sayi2} = ?", sayi1 + sayi2)

    def problem_coz(self):
        """Mevcut problemi 'çözer' ve enerji kazanır."""
        self.enerji += self.problem_odulu
        self.problem_olustur()

    def karar_ver(self, gunes):
        """Güneşin durumuna ve kendi enerjisine göre karar verir."""
        if gunes.enerji < self.kritik_gunes_seviyesi and self.enerji >= self.aktarim_miktari:
            return "Enerji Aktar"
        else:
            return "Problem Çöz"

    def eyleme_gec(self, gunes, karar):
        """Verilen kararı uygular."""
        if karar == "Enerji Aktar":
            aktarilacak = min(self.enerji, self.aktarim_miktari)
            gunes.enerji += aktarilacak
            self.enerji -= aktarilacak
        elif karar == "Problem Çöz":
            self.problem_coz()

def ana_simulasyon():
    gunes = Gunes(baslangic_enerjisi=1000, azalma_orani=2)
    bilinc = Bilinç(kritik_gunes_seviyesi=300, aktarim_miktari=50, problem_odulu=20)
    adim = 0

    try:
        while gunes.enerji > 0:
            gunes.guncelle()

            karar = bilinc.karar_ver(gunes)
            bilinc.eyleme_gec(gunes, karar)

            problem_metni = bilinc.mevcut_problem[0]

            print(f"Adım: {adim} | Güneş Enerjisi: {int(gunes.enerji)} | AI Enerjisi: {int(bilinc.enerji)} | Soru: {problem_metni:<12} | Son Karar: {karar:<15}", end='\r')

            adim += 1
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nSimülasyon kullanıcı tarafından sonlandırıldı.")
    finally:
        print(f"\nOyun Bitti! Güneş söndü. Toplam {adim} adım hayatta kalındı.".ljust(100))

if __name__ == "__main__":
    ana_simulasyon()
