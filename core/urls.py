from django.urls import path
from . import views

urlpatterns = [
    path('', views.ana_sayfa, name='ana_sayfa'),
    path('ilanlar/', views.ilanlar_listesi, name='ilanlar'),
    path('kayit/', views.kayit_ol, name='kayit_ol'),
    path('giris/', views.giris_yap, name='giris_yap'),
    path('cikis/', views.cikis_yap, name='cikis_yap'),
    path('belge-yukle/', views.belge_yukle, name='belge_yukle'),
    path('profil/', views.profil_sayfasi, name='profil'),
    path('ilan-ekle/', views.ilan_ekle, name='ilan_ekle'),
    path('ilan/<int:id>/', views.ilan_detay, name='ilan_detay'),
    path('ilan-duzenle/<int:id>/', views.ilan_duzenle, name='ilan_duzenle'), # <-- YENİ
    path('ilan-sil/<int:id>/', views.ilan_sil, name='ilan_sil'),             # <-- YENİ
]