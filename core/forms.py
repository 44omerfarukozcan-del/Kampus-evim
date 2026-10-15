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


# 2. PROFİL VE EŞLEŞME KRİTERLERİ GÜNCELLEME FORMU (models.py ile %100 Uyumlu)
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
            'temizlik_aliskanligi': 'Temizlik Alışkanlığı',
        }
        widgets = {
            'telefon_numarasi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '05XX XXX XX XX'}),
            'profil_resmi': forms.FileInput(attrs={'class': 'form-control'}),
            'bolum': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Örn: Yazılım Geliştirme'}),
            'sigara_kullanimi': forms.Select(attrs={'class': 'form-select'}),
            'uyku_duzeni': forms.Select(attrs={'class': 'form-select'}),
            'evcil_hayvan': forms.Select(attrs={'class': 'form-select'}),
            'temizlik_aliskanligi': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_telefon_numarasi(self):
        telefon = self.cleaned_data.get('telefon_numarasi')
        if telefon:
            telefon = telefon.strip()
            mevcut = KullaniciProfili.objects.filter(telefon_numarasi=telefon).exclude(pk=self.instance.pk)
            if mevcut.exists():
                raise forms.ValidationError("Bu telefon numarası başka bir kullanıcı tarafından kullanılıyor! Lütfen kendi numaranızı girin.")
        return telefon


# 3. İLAN EKLEME VE DÜZENLEME FORMU (Oda Sayısı Seçenekli)
class IlanForm(forms.ModelForm):
    ILAN_TURU_SECENEKLERI = [
        ('Ev Arkadaşı Arayan', 'Ev Arkadaşı Arayan (Evim var, arkadaş arıyorum)'),
        ('Oda Arayan', 'Oda Arayan (Kalacak yer/oda arıyorum)'),
    ]
    ODA_SAYISI_SECENEKLERI = [
        ('1+0 (Stüdyo)', '1+0 (Stüdyo)'),
        ('1+1', '1+1'),
        ('2+1', '2+1'),
        ('3+1', '3+1'),
        ('4+1 ve üzeri', '4+1 ve üzeri'),
        ('Paylaşımlı Oda', 'Paylaşımlı Oda'),
    ]

    ilan_turu = forms.ChoiceField(
        choices=ILAN_TURU_SECENEKLERI,
        label='İlan Türü',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    oda_sayisi = forms.ChoiceField(
        choices=ODA_SAYISI_SECENEKLERI,
        label='Oda Sayısı',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Ilan
        fields = ['baslik', 'ilan_turu', 'oda_sayisi', 'fiyat', 'ilan_resmi', 'aciklama']
        labels = {
            'baslik': 'İlan Başlığı',
            'fiyat': 'Aylık Kira / Bütçe (TL)',
            'ilan_resmi': 'Ev / Oda Fotoğrafı',
            'aciklama': 'İlan Açıklaması',
        }
        widgets = {
            'baslik': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Örn: Atakum sahile yakın 2+1 daireye ev arkadaşı'}),
            'fiyat': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Örn: 6500'}),
            'ilan_resmi': forms.FileInput(attrs={'class': 'form-control'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Ev ve aradığınız kriterler hakkında detaylı bilgi yazın...'}),
        }


# 4. ADLİ SİCİL BELGESİ YÜKLEME FORMU
class SicilBelgesiForm(forms.ModelForm):
    class Meta:
        model = SicilBelgesi
        fields = ['dosya']
        labels = {
            'dosya': 'Adli Sicil Belgesi (Sadece PDF)',
        }
        widgets = {
            'dosya': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
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