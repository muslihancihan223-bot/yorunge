# Yörünge Web — QR'dan para kazanma altyapısı

## Para nasıl geliyor?

```
QR'ı okutur → tarayıcıda Yörünge açılır → oynar → oyun bitince reklam → reklam ağı sana öder
```

Oyunda üç reklam yeri var:

| Yer | Ne zaman | Kaynak |
|---|---|---|
| Geçiş reklamı | Her 2 oyunda bir, oyun bitince | Google AdSense H5 Games Ads |
| Ödüllü reklam | "Reklam izle, devam et" (oyuncu kendi seçer, en çok kazandıran) | Google AdSense H5 Games Ads |
| Banner (320x50) | Menüde ve oyun sonu ekranında | Adsterra (Google onayı beklenirken hemen çalışır) |

Her QR'ın ayrı kodu var (`?src=durak`, `?src=kafe` …). Sayaç, hangi afişin kaç oyun ve kaç reklam getirdiğini ayrı ayrı gösterir. İşe yaramayan noktayı bırakır, iyi olanı çoğaltırsın.

## Gerçekçi hesap

```
Aylık gelir ≈ aylık oyun sayısı × oyun başına gösterilen reklam × (eCPM ÷ 1000)
```

- eCPM: 1000 reklam gösteriminin getirdiği para. Türkiye trafiğinde düşüktür; gerçek rakamı ilk haftanın verisinden göreceğiz, tahminle hareket etmeyeceğiz.
- Kendi verinden bir örnek: Adsterra'da 21.073 gösterim 1,83 $ etmişti. QR ile tek başına büyük para çıkmaz.
- **Asıl büyütme yolu portallar:** Aynı oyunu Poki / CrazyGames / GameMonetize / GamePix gibi oyun portallarına da yükleriz. Onların milyonlarca oyuncusu var ve reklam gelirini paylaşıyorlar. QR afişleri bunun yanında yerel ek kanal olur.

## Kurulum sırası

### 1. Oyunu yayına al (ücretsiz, 5 dakika)
1. GitHub'da **public** bir repo aç, adı: `yorunge` (hesap: muslihancihan223-bot).
2. Bana "repo açıldı" de. Dosyaları ben yüklerim ve GitHub Pages'i açarım.
3. Adres şu olur: `https://muslihancihan223-bot.github.io/yorunge/`. QR'lar bu adrese göre hazır.

### 2. Sayaç (ücretsiz)
1. goatcounter.com → hesap aç → kod olarak `yorunge` seç.
2. `index.html` içindeki `CONFIG.goatcounterCode` alanına `yorunge` yazılır.

### 3. Hemen çalışan reklam: Adsterra banner
1. Adsterra'da **Publisher** hesabı (reklamveren hesabından ayrı) → siteyi ekle → **Banner 320x50** oluştur.
2. Verilen koddaki `key` değerini `CONFIG.adsterraBannerKey` alanına yaz. Koddaki script adresi farklıysa bana gönder, ona göre düzeltirim.

### 4. Asıl gelir: Google AdSense H5 Games Ads
1. AdSense'e başvur. Not: AdSense büyük ihtimalle `github.io` alt adresini kabul etmez. Kendi alan adın gerekebilir (ör. `yorunge.com.tr`, yıllık birkaç yüz TL). Başvuru ekranında teyit ederiz.
2. Onay gelince **H5 Games Ads beta** erişimi için ayrıca form doldurulur (Google onaylamayabilir).
3. `ca-pub-...` numarasını `CONFIG.adsenseClient` alanına yaz. Test bitene kadar `adsenseTestMode: true` kalsın.
4. `ads.txt` dosyasındaki `pub-XXXX` kısmını kendi numaranla değiştir.

### 5. Afişler
- `qr/afis-*.png`: A6 boyutunda (105x148 mm), 300 dpi baskıya hazır.
- `qr/qr-*.png`: Sade QR. Sticker için.
- Yeni konum eklemek için: `python3 tools/afis.py` (konum listesi dosyanın içinde).

## Önemli: nereye asılır?
- **İzin alarak:** Kafe, berber, otel lobisi, işletme tuvaleti. Sahibinden izin al. İstersen karşılığında "ilk ay ücretsiz", sonra küçük bir pay ver.
- **Durak, direk, duvar:** İzinsiz yapıştırmak belediye cezası (Kabahatler Kanunu) gerektirir. Durak reklamları belediyenin reklam şirketi üzerinden kiralanır.
- Reklam ağları sahte/teşvikli trafiği yasaklar. "Okut, para kazan" gibi vaatler veya kendi kendine tıklama yapılmaz, hesap kapanır.

## Dosyalar
- `index.html`: Oyun + reklam katmanı + QR kaynak takibi (tek dosya, ayarlar en üstte `CONFIG` içinde)
- `gizlilik.html`: Gizlilik politikası (AdSense için zorunlu)
- `ads.txt`: AdSense satıcı doğrulama dosyası
- `qr/`: Afişler ve sade QR'lar
- `tools/afis.py`, `tools/qr.py`: QR ve afiş üretici

## Oyun portalı: GameMonetize
- `python3 tools/portal.py <GAME_ID>` → `portal/index.html` + `yorunge-gamemonetize.zip`
- Portal sürümünde kendi reklamlarımız (Adsterra/AdSense), sayaç, paylaşım butonu ve dış linkler yok;
  reklamı GameMonetize SDK'sı gösterir (her 2 oyunda bir, oyun sonunda). Kapak görselleri: `portal/thumbs/`.
- Oyun, cihaz dili Türkçe değilse otomatik İngilizce açılır (portallar ve Odd Origins izleyicileri için).
