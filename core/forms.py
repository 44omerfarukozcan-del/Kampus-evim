from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Kullanici, SicilBelgesi, KullaniciProfili, Ilan, IlanSoru, Mesaj

# 1. KULLANICI KAYIT FORMU (.edu.tr ve Tekil E-posta Korumalı)
class KullaniciKayitFormu(UserCreationForm):
    email = forms.EmailField(required=True, label="Üniversite E-postası (.edu.tr)")

    class Meta:
        model = Kullanici
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email.endswith('.edu.tr'):
            raise forms.ValidationError("Güvenlik ihlali! Sadece .edu.tr uzantılı üniversite e-postası ile kayıt olabilirsiniz.")
        if Kullanici.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu e-posta adresi zaten başka bir hesaba kayıtlı!")
        return email

# 2. ADLİ SİCİL BELGESİ YÜKLEME FORMU
class SicilBelgesiForm(forms.ModelForm):
    class Meta:
        model = SicilBelgesi
        fields = ['dosya']
        labels = {
            'dosya': 'Adli Sicil Belgesi (Sadece PDF)'
        }

# 3. KULLANICI PROFİL VE EŞLEŞME KRİTERLERİ FORMU (Tekil Telefon Korumalı)
class ProfilGuncellemeFormu(forms.ModelForm):
    class Meta:
        model = KullaniciProfili
        fields = [
            'telefon_numarasi', 'profil_resmi', 'bolum', 
            'sigara_kullanimi', 'uyku_duzeni', 'evcil_hayvan', 'temizlik_aliskanligi'
        ]
        labels = {
            'telefon_numarasi': 'Telefon Numarası',
            'profil_resmi': 'Profil Resmi Seç',
            'bolum': 'Bölümünüz',
            'sigara_kullanimi': 'Sigara Kullanımı',
            'uyku_duzeni': 'Uyku Düzeni',
            'evcil_hayvan': 'Evcil Hayvan Yaklaşımı',
            'temizlik_aliskanligi': 'Temizlik Alışkanlığı'
        }

    def clean_telefon_numarasi(self):
        telefon = self.cleaned_data.get('telefon_numarasi')
        if telefon:
            # Boşlukları ve tireleri temizle ki 0555 111 22 33 ile 05551112233 aynı sayılsın
            telefon = telefon.strip().replace(" ", "").replace("-", "")
            if KullaniciProfili.objects.exclude(pk=self.instance.pk).filter(telefon_numarasi=telefon).exists():
                raise forms.ValidationError("Bu telefon numarası zaten başka bir hesaba kayıtlı! Her numara tek bir hesapta kullanılabilir.")
        return telefon

# 4. İLAN EKLEME FORMU (Görsel Destekli)
class IlanForm(forms.ModelForm):
    class Meta:
        model = Ilan
        fields = ['baslik', 'aciklama', 'ilan_turu', 'fiyat', 'oda_sayisi', 'ilan_resmi']
        labels = {
            'baslik': 'İlan Başlığı',
            'aciklama': 'Detaylı Açıklama',
            'ilan_turu': 'İlan Türü',
            'fiyat': 'Aylık Fiyat (TL)',
            'oda_sayisi': 'Oda Sayısı (Örn: 3+1)',
            'ilan_resmi': 'İlan Fotoğrafı Yükle'
        }

# 5. İLAN SORU SORMA FORMU
class IlanSoruForm(forms.ModelForm):
    class Meta:
        model = IlanSoru
        fields = ['soru_metni']
        labels = {'soru_metni': 'İlan Sahibine Soru Sor'}
        widgets = {
            'soru_metni': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ev hakkında merak ettiklerinizi yazın...'})
        }

# 6. ÖZEL MESAJ (DM) FORMU
class MesajForm(forms.ModelForm):
    class Meta:
        model = Mesaj
        fields = ['icerik']
        labels = {'icerik': 'Mesajınız'}
        widgets = {
            'icerik': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Mesajınızı buraya yazın...'})
        }