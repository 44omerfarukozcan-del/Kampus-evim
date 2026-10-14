from django.urls import path
from django.contrib.auth import views as auth_views  # Şifre sıfırlama için gereken kütüphane
from . import views  # Kendi sayfalarımızı (ana sayfa, giriş vb.) çekmek için

urlpatterns = [
    # ---- SENİN MEVCUT SAYFALARIN ----
    # (Eğer ilanlar, profil vb. başka sayfaların varsa onları da bu araya eklemelisin)
    path('', views.ana_sayfa, name='ana_sayfa'),
    path('giris/', views.giris_yap, name='giris_yap'),
    path('kayit/', views.kayit_ol, name='kayit_ol'),
    path('cikis/', views.cikis_yap, name='cikis_yap'),
   
    from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ---- SENİN MEVCUT SAYFALARIN (Eski kodların burada aynı kalsın) ----
    path('', views.ana_sayfa, name='ana_sayfa'),
    path('giris/', views.giris_yap, name='giris_yap'),
    path('kayit/', views.kayit_ol, name='kayit_ol'),
    path('cikis/', views.cikis_yap, name='cikis_yap'),
   
    # ---- ŞİFRE SIFIRLAMA SAYFALARI (GÜNCELLENMİŞ HALİ) ----
   
    # 1. Şifre Sıfırlama Talep Sayfası ve MAİL TASARIMI Bağlantısı
    path('sifre-sifirla/', auth_views.PasswordResetView.as_view(
        template_name='core/sifre_sifirla.html',
        html_email_template_name='core/sifre_sifirla_mail.html'  # <-- Tasarım dosyamızı buraya bağladık
    ), name='password_reset'),
   
    # 2. Mail Gönderildi (Başarılı) Sayfası
    path('sifre-sifirla/basarili/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/sifre_sifirla_basarili.html'
    ), name='password_reset_done'),
   
    # 3. Maildeki Linke Tıklayınca Açılan Yeni Şifre Girme Sayfası
    path('sifre-sifirla-onay/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/sifre_sifirla_onay.html'
    ), name='password_reset_confirm'),
   
    # 4. Şifre Değiştirme Tamamlandı Sayfası
    path('sifre-sifirla-tamamlandi/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/sifre_sifirla_tamam.html'
    ), name='password_reset_complete'),
]from django.urls import path
from django.contrib.auth import views as auth_views  # Şifre sıfırlama için gereken kütüphane
from . import views  # Kendi sayfalarımızı (ana sayfa, giriş vb.) çekmek için

urlpatterns = [
    # ---- SENİN MEVCUT SAYFALARIN ----
    # (Eğer ilanlar, profil vb. başka sayfaların varsa onları da bu araya eklemelisin)
    path('', views.ana_sayfa, name='ana_sayfa'),
    path('giris/', views.giris_yap, name='giris_yap'),
    path('kayit/', views.kayit_ol, name='kayit_ol'),
    path('cikis/', views.cikis_yap, name='cikis_yap'),
   
    from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ---- SENİN MEVCUT SAYFALARIN (Eski kodların burada aynı kalsın) ----
    path('', views.ana_sayfa, name='ana_sayfa'),
    path('giris/', views.giris_yap, name='giris_yap'),
    path('kayit/', views.kayit_ol, name='kayit_ol'),
    path('cikis/', views.cikis_yap, name='cikis_yap'),
   
    # ---- ŞİFRE SIFIRLAMA SAYFALARI (GÜNCELLENMİŞ HALİ) ----
   
    # 1. Şifre Sıfırlama Talep Sayfası ve MAİL TASARIMI Bağlantısı
    path('sifre-sifirla/', auth_views.PasswordResetView.as_view(
        template_name='core/sifre_sifirla.html',
        html_email_template_name='core/sifre_sifirla_mail.html'  # <-- Tasarım dosyamızı buraya bağladık
    ), name='password_reset'),
   
    # 2. Mail Gönderildi (Başarılı) Sayfası
    path('sifre-sifirla/basarili/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/sifre_sifirla_basarili.html'
    ), name='password_reset_done'),
   
    # 3. Maildeki Linke Tıklayınca Açılan Yeni Şifre Girme Sayfası
    path('sifre-sifirla-onay/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/sifre_sifirla_onay.html'
    ), name='password_reset_confirm'),
   
    # 4. Şifre Değiştirme Tamamlandı Sayfası
    path('sifre-sifirla-tamamlandi/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/sifre_sifirla_tamam.html'
    ), name='password_reset_complete'),
] 