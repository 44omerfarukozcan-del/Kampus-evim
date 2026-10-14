from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Kullanici, KullaniciProfili, Ilan, SicilBelgesi, IlanSoru, Mesaj


# Modellerdeki alan adlarını otomatik tespit etme (FieldError hatasını tamamen önler)
_sicil_fields = [
    f.name for f in SicilBelgesi._meta.fields
    if f.name not in ('id', 'kullanici', 'onay_durumu', 'onaylandi', 'yuklenme_tarihi', 'olusturulma_tarihi')
]
SICIL_DOSYA_ALANI = _sicil_fields[0] if _sicil_fields else 'belge'

_soru_fields = [f.name for f in IlanSoru._meta.fields if f.name in ('soru_metni', 'soru', 'icerik')]
SORU_METNI_ALANI = _soru_fields[0] if _soru_fields else 'soru_metni'

_mesaj_fields = [f.name for f in Mesaj._meta.fields if f.name in ('icerik', 'mesaj_metni', 'mesaj')]
MESAJ_ICERIK_ALANI = _mesaj_fields[0] if _mesaj_fields else 'icerik'


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
            mevcut_tel = getattr(self.instance, 'telefon_no', None) or getattr(self.instance.kullanici, 'telefon', '')
            self.fields['telefon'].initial = mevcut_tel

    def clean_telefon(self):
        telefon = self.cleaned_data.get('telefon')
        if telefon:
            telefon = telefon.strip()
            if hasattr(Kullanici, 'telefon'):
                mevcut = Kullanici.objects.filter(telefon=telefon).exclude(pk=self.instance.kullanici.pk)
                if mevcut.exists():
                    raise forms.ValidationError("Bu telefon numarası başka bir kullanıcı tarafından kullanılıyor!")
            if hasattr(KullaniciProfili, 'telefon_no'):
                mevcut_p = KullaniciProfili.objects.filter(telefon_no=telefon).exclude(pk=self.instance.pk)
                if mevcut_p.exists():
                    raise forms.ValidationError("Bu telefon numarası başka bir kullanıcı tarafından kullanılıyor!")
        return telefon

    def save(self, commit=True):
        profil = super().save(commit=False)
        telefon = self.cleaned_data.get('telefon', '')
        if hasattr(profil, 'telefon_no'):
            profil.telefon_no = telefon
        if hasattr(profil, 'kullanici') and hasattr(profil.kullanici, 'telefon'):
            profil.kullanici.telefon = telefon
            if commit:
                profil.kullanici.save()
        if commit:
            profil.save()
        return profil


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
        fields = [SICIL_DOSYA_ALANI]
        labels = {
            SICIL_DOSYA_ALANI: 'Adli Sicil Belgesi (Sadece PDF)',
        }
        widgets = {
            SICIL_DOSYA_ALANI: forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }


# 5. İLAN ALTI SORU SORMA FORMU
class IlanSoruForm(forms.ModelForm):
    class Meta:
        model = IlanSoru
        fields = [SORU_METNI_ALANI]
        labels = {
            SORU_METNI_ALANI: 'Sorunuz',
        }
        widgets = {
            SORU_METNI_ALANI: forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ev hakkında merak ettiklerinizi ilan sahibine sorun...'
            }),
        }


# 6. ÖZEL MESAJ (DM) GÖNDERME FORMU
class MesajForm(forms.ModelForm):
    class Meta:
        model = Mesaj
        fields = [MESAJ_ICERIK_ALANI]
        labels = {
            MESAJ_ICERIK_ALANI: 'Mesajınız',
        }
        widgets = {
            MESAJ_ICERIK_ALANI: forms.Textarea(attrs={
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