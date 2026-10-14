from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. KULLANICI MODELİ (.edu.tr ve E-posta Doğrulama Kodu)
class Kullanici(AbstractUser):
    dogrulama_kodu = models.CharField(max_length=6, blank=True, null=True)
    eposta_dogrulandi = models.BooleanField(default=False)

# 2. ADLİ SİCİL BELGESİ MODELİ
class SicilBelgesi(models.Model):
    kullanici = models.OneToOneField(Kullanici, on_delete=models.CASCADE)
    dosya = models.FileField(upload_to='sicil_belgeleri/')
    yuklenme_tarihi = models.DateTimeField(auto_now_add=True)
    onay_durumu = models.BooleanField(default=False, verbose_name="Belge Onaylandı mı?")

    def __str__(self):
        return f"{self.kullanici.username} Sicil Belgesi"

# 3. KULLANICI PROFİLİ MODELİ (Telefon, Resim, Güven Skoru ve Eşleşme Kriterleri)
class KullaniciProfili(models.Model):
    SIGARA_SECENEKLERI = (('Evet', 'Evet'), ('Hayır', 'Hayır'), ('Fark Etmez', 'Fark Etmez'))
    UYKU_SECENEKLERI = (('Erken Yatarım', 'Erken Yatarım'), ('Gece Kuşuyum', 'Gece Kuşuyum'), ('Esnek', 'Esnek'))
    EVCIL_SECENEKLERI = (('Var / Severim', 'Var / Severim'), ('İstemiyorum', 'İstemiyorum'), ('Fark Etmez', 'Fark Etmez'))
    TEMIZLIK_SECENEKLERI = (('Çok Titizim', 'Çok Titizim'), ('Orta / Normal', 'Orta / Normal'), ('Rahatım', 'Rahatım'))

    kullanici = models.OneToOneField(Kullanici, on_delete=models.CASCADE, related_name='profil')
    telefon_numarasi = models.CharField(max_length=15, blank=True, null=True)
    profil_resmi = models.ImageField(upload_to='profil_resimleri/', default='profil_resimleri/default.png', blank=True, null=True)
    
    # Eşleşme Kriterleri
    bolum = models.CharField(max_length=100, blank=True, null=True, verbose_name="Okuduğunuz Bölüm")
    sigara_kullanimi = models.CharField(max_length=20, choices=SIGARA_SECENEKLERI, default='Fark Etmez')
    uyku_duzeni = models.CharField(max_length=20, choices=UYKU_SECENEKLERI, default='Esnek')
    evcil_hayvan = models.CharField(max_length=20, choices=EVCIL_SECENEKLERI, default='Fark Etmez')
    temizlik_aliskanligi = models.CharField(max_length=20, choices=TEMIZLIK_SECENEKLERI, default='Orta / Normal')

    def __str__(self):
        return f"{self.kullanici.username} Profili"

    @property
    def guven_skoru(self):
        skor = 0
        if self.kullanici.email and self.kullanici.email.endswith('.edu.tr'):
            skor += 40
        try:
            if hasattr(self.kullanici, 'sicilbelgesi') and self.kullanici.sicilbelgesi.dosya:
                skor += 40
        except:
            pass
        if self.profil_resmi and 'default.png' not in self.profil_resmi.name:
            skor += 10
        if self.telefon_numarasi:
            skor += 10
        return skor

    # İki kullanıcı arasındaki uyumu % olarak hesaplayan fonksiyon
    def eslesme_puani_hesapla(self, diger_profil):
        if not diger_profil:
            return 0
        puan = 0
        if self.sigara_kullanimi == diger_profil.sigara_kullanimi:
            puan += 25
        elif 'Fark Etmez' in [self.sigara_kullanimi, diger_profil.sigara_kullanimi]:
            puan += 15

        if self.uyku_duzeni == diger_profil.uyku_duzeni:
            puan += 25
        elif 'Esnek' in [self.uyku_duzeni, diger_profil.uyku_duzeni]:
            puan += 15

        if self.evcil_hayvan == diger_profil.evcil_hayvan:
            puan += 25
        elif 'Fark Etmez' in [self.evcil_hayvan, diger_profil.evcil_hayvan]:
            puan += 15

        if self.temizlik_aliskanligi == diger_profil.temizlik_aliskanligi:
            puan += 25
        elif 'Orta / Normal' in [self.temizlik_aliskanligi, diger_profil.temizlik_aliskanligi]:
            puan += 15

        return puan

# 4. İLAN MODELİ (Görsel Eklendi)
class Ilan(models.Model):
    ILAN_TURLERI = (
        ('Oda Arayan', 'Oda Arayan'),
        ('Ev Arkadaşı Arayan', 'Ev Arkadaşı Arayan'),
    )
    kullanici = models.ForeignKey(Kullanici, on_delete=models.CASCADE)
    baslik = models.CharField(max_length=100)
    aciklama = models.TextField()
    ilan_turu = models.CharField(max_length=50, choices=ILAN_TURLERI)
    fiyat = models.DecimalField(max_digits=10, decimal_places=2)
    oda_sayisi = models.CharField(max_length=20)
    ilan_resmi = models.ImageField(upload_to='ilan_resimleri/', blank=True, null=True, verbose_name="İlan Görseli")
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.baslik

# 5. İLAN ALTI SORU - CEVAP MODELİ
class IlanSoru(models.Model):
    ilan = models.ForeignKey(Ilan, on_delete=models.CASCADE, related_name='sorular')
    soran = models.ForeignKey(Kullanici, on_delete=models.CASCADE)
    soru_metni = models.TextField(verbose_name="Sorunuz")
    cevap_metni = models.TextField(blank=True, null=True, verbose_name="İlan Sahibinin Cevabı")
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.soran.username} -> {self.ilan.baslik}"

# 6. DM (ÖZEL MESAJLAŞMA) MODELİ
class Mesaj(models.Model):
    gonderen = models.ForeignKey(Kullanici, on_delete=models.CASCADE, related_name='gonderilen_mesajlar')
    alici = models.ForeignKey(Kullanici, on_delete=models.CASCADE, related_name='alinan_mesajlar')
    ilan = models.ForeignKey(Ilan, on_delete=models.SET_NULL, null=True, blank=True)
    icerik = models.TextField(verbose_name="Mesajınız")
    tarih = models.DateTimeField(auto_now_add=True)
    okundu = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.gonderen.username} -> {self.alici.username}"