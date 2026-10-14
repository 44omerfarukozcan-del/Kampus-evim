from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. KULLANICI MODELİ (.edu.tr kayıtları için özelleştirilmiş)
class Kullanici(AbstractUser):
    pass

# 2. ADLİ SİCİL BELGESİ MODELİ (9. Hafta: Onay Durumu Eklendi)
class SicilBelgesi(models.Model):
    kullanici = models.OneToOneField(Kullanici, on_delete=models.CASCADE)
    dosya = models.FileField(upload_to='sicil_belgeleri/')
    yuklenme_tarihi = models.DateTimeField(auto_now_add=True)
    onay_durumu = models.BooleanField(default=False, verbose_name="Belge Onaylandı mı?")

    def __str__(self):
        return f"{self.kullanici.username} - Sicil Belgesi"

# 3. KULLANICI PROFİLİ MODELİ (Resim, Telefon ve GÜVEN SKORU)
class KullaniciProfili(models.Model):
    kullanici = models.OneToOneField(Kullanici, on_delete=models.CASCADE, related_name='profil')
    telefon_numarasi = models.CharField(max_length=15, blank=True, null=True)
    profil_resmi = models.ImageField(upload_to='profil_resimleri/', default='profil_resimleri/default.png', blank=True, null=True)

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

# 4. İLAN MODELİ
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
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.baslik