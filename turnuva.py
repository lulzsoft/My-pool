import json
import time
# Yeniden düzenlenmiş simülasyon modülünü içe aktar
import savas_simulasyonu

def turnuva_calistir(mac_sayisi=10):
    """
    Belirtilen sayıda maç yaparak iki AI modelini karşılaştırır ve sonuçları raporlar.
    """
    print("Turnuva Başladı!")
    print(f"Toplam Maç Sayısı: {mac_sayisi}")
    print("-" * 30)

    # ayarlar.json dosyasından mevcut yapılandırmayı yükle
    with open('ayarlar.json', 'r') as f:
        ayarlar = json.load(f)

    takim1_model = ayarlar['takim1']['model']
    takim2_model = ayarlar['takim2']['model']
    print(f"Takım 1 (Mavi) Modeli: {takim1_model}")
    print(f"Takım 2 (Kırmızı) Modeli: {takim2_model}")
    print("-" * 30)

    galibiyetler = {1: 0, 2: 0}
    baslangic_zamani = time.time()

    for i in range(mac_sayisi):
        print(f"Maç {i+1}/{mac_sayisi} başlıyor...")

        # Simülasyonu "başsız" (görsel olmayan) modda çalıştır
        kazanan = savas_simulasyonu.oyunu_oyna(ayarlar, gorsel_mod=False)

        if kazanan in galibiyetler:
            galibiyetler[kazanan] += 1
            print(f"Maç {i+1} bitti. Kazanan: Takım {kazanan}")
        else:
            print(f"Maç {i+1} bitti. Sonuç: Berabere veya Hata")

    bitis_zamani = time.time()
    gecen_sure = bitis_zamani - baslangic_zamani

    # Sonuçları Raporla
    print("\n" + "=" * 30)
    print("Turnuva Sonuçları")
    print("=" * 30)
    print(f"Takım 1 (Mavi) Galibiyet Sayısı: {galibiyetler[1]}")
    print(f"Takım 2 (Kırmızı) Galibiyet Sayısı: {galibiyetler[2]}")

    if mac_sayisi > 0:
        takim1_kazanma_orani = (galibiyetler[1] / mac_sayisi) * 100
        takim2_kazanma_orani = (galibiyetler[2] / mac_sayisi) * 100
        print(f"Takım 1 Kazanma Oranı: %{takim1_kazanma_orani:.2f}")
        print(f"Takım 2 Kazanma Oranı: %{takim2_kazanma_orani:.2f}")

    print("-" * 30)
    print(f"Turnuva Toplam Süre: {gecen_sure:.2f} saniye")
    print("=" * 30)

if __name__ == "__main__":
    # 5 maçlık kısa bir turnuva ile test et
    turnuva_calistir(mac_sayisi=5)
