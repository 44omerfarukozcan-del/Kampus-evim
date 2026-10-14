from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Kullanici, SicilBelgesi, KullaniciProfili, Ilan

# 1. KULLANICI KAYIT FORMU (.edu.tr korumalı)
class KullaniciKayitFormu(UserCreationForm):
    class Meta:
        model = Kullanici
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('.edu.tr'):
            raise forms.ValidationError("Güvenlik ihlali! Sadece .edu.tr uzantılı üniversite e-postası ile kayıt olabilirsiniz.")
        return email

# 2. ADLİ SİCİL BELGESİ YÜKLEME FORMU
class SicilBelgesiForm(forms.ModelForm):
    class Meta:
        model = SicilBelgesi
        fields = ['dosya']
        labels = {
            'dosya': 'Adli Sicil Belgesi (Sadece PDF)'
        }

# 3. KULLANICI PROFİL GÜNCELLEME FORMU (5. HAFTA)
class ProfilGuncellemeFormu(forms.ModelForm):
    class Meta:
        model = KullaniciProfili
        fields = ['telefon_numarasi', 'profil_resmi']
        labels = {
            'telefon_numarasi': 'Telefon Numarası',
            'profil_resmi': 'Profil Resmi Seç'
        }

# 4. İLAN EKLEME FORMU (5. HAFTA)
class IlanForm(forms.ModelForm):
    class Meta:
        model = Ilan
        fields = ['baslik', 'aciklama', 'ilan_turu', 'fiyat', 'oda_sayisi']
        labels = {
            'baslik': 'İlan Başlığı',
            'aciklama': 'Detaylı Açıklama',
            'ilan_turu': 'İlan Türü',
            'fiyat': 'Aylık Fiyat (TL)',
            'oda_sayisi': 'Oda Sayısı (Örn: 3+1)'
        }