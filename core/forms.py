from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Kullanici, KullaniciProfili, Ilan, SicilBelgesi, IlanSoru, Mesaj


# 1. ÖĞRENCİ KAYIT FORMU (.edu.tr ve Tekil E-posta Korumalı)
class KullaniciKayitFormu(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Üniversite E-postası (.edu.tr)",
        widget=forms.EmailInput(attrs={'placeholder': 'ornek@samsun.edu.tr', 'class': 'form-control'})
    )
    first_name = forms.CharField(
        required=True,
        label="Adı",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        required=True,
        label="Soyadı",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Kullanici
        fields = ("username", "first_name", "last_name", "email")

    def clean_email(self):
        email = self.cleaned_data.get('email').lower().strip()
        if not email.endswith('.edu.tr'):
            raise forms.ValidationError("Sadece .edu.tr uzantılı öğrenci e-posta adresleri ile kayıt olabilirsiniz!")
        if Kullanici.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta adresi zaten başka bir hesapta kullanılıyor!")
        return email


# 2. PROFİL VE EŞLEŞME KRİTERLERİ GÜNCELLEME FORMU
class ProfilGuncellemeFormu(forms.ModelForm):
    telefon = forms.CharField(
        max_length=20,
        required=False,
        label="Telefon Numarası",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '05XX XXX XX XX'})
    )

    class Meta:
        model = KullaniciProfili
        fields = [
            'profil_resmi', 'bolum',
            'sigara_kullanimi', 'uyku_duzeni', 'evcil_hayvan', 'temizlik_aliskanligi'
        ]
        field_order = [
            'telefon', 'profil_resmi', 'bolum',
            'sigara_kullanimi', 'uyku_duzeni', 'evcil_hayvan', 'temizlik_aliskanligi'
        ]
        labels = {
            'profil_resmi': 'Profil Resmi Seç',
            'bolum': 'Bölümünüz',
            'sigara_kullanimi': 'Sigara Kullanımı',
            'uyku_duzeni': 'Uyku Düzeni',
            'evcil_hayvan': 'Evcil Hayvan Yaklaşımı',
            'temizlik_aliskanligi': 'Temizlik Alışkanlığı',
        }
        widgets = {
            'profil_resmi': forms.FileInput(attrs={'class': 'form-control'}),
            'bolum': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Örn: Yazılım Geliştirme'}),
            'sigara_kullanimi': forms.Select(attrs={'class': 'form-select'}),
            'uyku_duzeni': forms.Select(attrs={'class': 'form-select'}),
            'evcil_hayvan': forms.Select(attrs={'class': 'form-select'}),
            'temizlik_aliskanligi': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'kullanici'):
            self.fields['telefon'].initial = getattr(self.instance.kullanici, 'telefon', '')

    def clean_telefon(self):
        telefon = self.cleaned_data.get('telefon')
        if telefon:
            telefon = telefon.strip()
            if hasattr(Kullanici, 'telefon'):
                mevcut = Kullanici.objects.filter(telefon=telefon).exclude(pk=self.instance.kullanici.pk)
                if mevcut.exists():
                    raise forms.ValidationError("Bu telefon numarası başka bir kullanıcı tarafından kullanılıyor! Lütfen kendi numaranızı girin.")
        return telefon


# 3. İLAN EKLEME VE DÜZENLEME FORMU
class IlanForm(forms.ModelForm):
    class Meta:
        model = Ilan
        fields = ['baslik', 'ilan_turu', 'oda_sayisi', 'fiyat', 'ilan_resmi', 'aciklama']
        labels = {
            'baslik': 'İlan Başlığı',
            'ilan_turu': 'İlan Türü',
            'oda_sayisi': 'Oda Sayısı',
            'fiyat': 'Aylık Kira / Bütçe (TL)',
            'ilan_resmi': 'Ev / Oda Fotoğrafı',
            'aciklama': 'İlan Açıklaması',
        }
        widgets = {
            'baslik': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Örn: Atakum sahile yakın 2+1 daireye ev arkadaşı'}),
            'ilan_turu': forms.Select(attrs={'class': 'form-select'}),
            'oda_sayisi': forms.Select(attrs={'class': 'form-select'}),
            'fiyat': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Örn: 6500'}),
            'ilan_resmi': forms.FileInput(attrs={'class': 'form-control'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Ev ve aradığınız kriterler hakkında detaylı bilgi yazın...'}),
        }


# 4. ADLİ SİCİL BELGESİ YÜKLEME FORMU
class SicilBelgesiForm(forms.ModelForm):
    class Meta:
        model = SicilBelgesi
        fields = ['belge_dosyasi']
        labels = {
            'belge_dosyasi': 'Adli Sicil Belgesi (Sadece PDF)',
        }
        widgets = {
            'belge_dosyasi': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }


# 5. İLAN ALTI SORU SORMA FORMU
class IlanSoruForm(forms.ModelForm):
    class Meta:
        model = IlanSoru
        fields = ['soru_metni']
        labels = {
            'soru_metni': 'Sorunuz',
        }
        widgets = {
            'soru_metni': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ev hakkında merak ettiklerinizi ilan sahibine sorun...'
            }),
        }


# 6. ÖZEL MESAJ (DM) GÖNDERME FORMU
class MesajForm(forms.ModelForm):
    class Meta:
        model = Mesaj
        fields = ['icerik']
        labels = {
            'icerik': 'Mesajınız',
        }
        widgets = {
            'icerik': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Mesajınızı buraya yazın...'
            }),
        }


# Yedek isimlendirmeler
OgrenciKayitFormu = KullaniciKayitFormu
IlanFormu = IlanForm
SicilBelgesiFormu = SicilBelgesiForm
IlanSoruFormu = IlanSoruForm
MesajFormu = MesajForm