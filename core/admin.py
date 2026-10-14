from django.contrib import admin
from .models import Kullanici, SicilBelgesi, KullaniciProfili, Ilan

admin.site.register(Kullanici)
admin.site.register(KullaniciProfili)

@admin.register(SicilBelgesi)
class SicilBelgesiAdmin(admin.ModelAdmin):
    list_display = ['kullanici', 'yuklenme_tarihi', 'onay_durumu']
    list_editable = ['onay_durumu']
    list_filter = ['onay_durumu']

@admin.register(Ilan)
class IlanAdmin(admin.ModelAdmin):
    list_display = ['baslik', 'kullanici', 'ilan_turu', 'fiyat', 'is_active']
    list_editable = ['is_active']
    list_filter = ['ilan_turu', 'is_active']