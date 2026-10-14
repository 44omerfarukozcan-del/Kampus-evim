from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 

urlpatterns = [
    # ---- MEVCUT SAYFALARIN ----
    path('', views.ana_sayfa, name='ana_sayfa'),
    path('giris/', views.giris_yap, name='giris_yap'),
    path('kayit/', views.kayit_ol, name='kayit_ol'),
    path('cikis/', views.cikis_yap, name='cikis_yap'),
   
    
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