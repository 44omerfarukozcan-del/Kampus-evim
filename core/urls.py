from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 

urlpatterns = [
    # ---- TEMEL SAYFALAR ----
    path('', views.ana_sayfa, name='ana_sayfa'),
    path('giris/', views.giris_yap, name='giris_yap'),
    path('kayit/', views.kayit_ol, name='kayit_ol'),
    path('eposta-dogrula/', views.eposta_dogrula, name='eposta_dogrula'),
    path('cikis/', views.cikis_yap, name='cikis_yap'),
    
    # ---- PROFİL VE BELGE YÜKLEME ----
    path('profil/', views.profil_sayfasi, name='profil'),
    path('belge-yukle/', views.belge_yukle, name='belge_yukle'),

    # ---- İLAN İŞLEMLERİ SAYFALARI ----
    path('ilanlar/', views.ilanlar_listesi, name='ilanlar'), 
    path('ilan-ekle/', views.ilan_ekle, name='ilan_ekle'),
    path('ilan-detay/<int:id>/', views.ilan_detay, name='ilan_detay'),
    path('ilan-duzenle/<int:id>/', views.ilan_duzenle, name='ilan_duzenle'),
    path('ilan-sil/<int:id>/', views.ilan_sil, name='ilan_sil'),
    
    # ---- DM (ÖZEL MESAJLAŞMA) SAYFALARI ----
    path('mesajlar/', views.mesajlar_kutusu, name='mesajlar_kutusu'),
    path('mesajlar/<int:kullanici_id>/', views.sohbet_detay, name='sohbet_detay'),

    # ---- ŞİFRE SIFIRLAMA SAYFALARI ----
    path('sifre-sifirla/', auth_views.PasswordResetView.as_view(
        template_name='core/sifre_sifirla.html',
        html_email_template_name='core/sifre_sifirla_mail.html'
    ), name='password_reset'),
    
    path('sifre-sifirla/basarili/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/sifre_sifirla_basarili.html'
    ), name='password_reset_done'),
    
    path('sifre-sifirla-onay/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/sifre_sifirla_onay.html'
    ), name='password_reset_confirm'),
    
    path('sifre-sifirla-tamamlandi/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/sifre_sifirla_tamam.html'
    ), name='password_reset_complete'),
]