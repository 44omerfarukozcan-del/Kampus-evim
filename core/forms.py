class ProfilGuncellemeFormu(forms.ModelForm):
    class Meta:
        model = KullaniciProfili
        fields = [
            'telefon', 'profil_resmi', 'bolum', 
            'sigara_kullanimi', 'uyku_duzeni', 'evcil_hayvan', 'temizlik_aliskanligi'
        ]
        labels = {
            'telefon': 'Telefon Numarası',
            'profil_resmi': 'Profil Resmi Seç',
            'bolum': 'Bölümünüz',
            'sigara_kullanimi': 'Sigara Kullanımı',
            'uyku_duzeni': 'Uyku Düzeni',
            'evcil_hayvan': 'Evcil Hayvan Yaklaşımı',
            'temizlik_aliskanligi': 'Temizlik Alışkanlığı',
        }
        widgets = {
            'profil_resmi': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_telefon(self):
        telefon = self.cleaned_data.get('telefon')
        if telefon:
            telefon = telefon.strip()
            mevcut = KullaniciProfili.objects.filter(telefon=telefon).exclude(kullanici=self.instance.kullanici)
            if mevcut.exists():
                raise forms.ValidationError("Bu telefon numarası başka bir kullanıcı tarafından kullanılıyor! Lütfen kendi numaranızı girin.")
        return telefon