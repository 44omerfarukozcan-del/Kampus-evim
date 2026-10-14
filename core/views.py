import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from .models import Kullanici, Ilan, SicilBelgesi, KullaniciProfili, IlanSoru, Mesaj
from .forms import KullaniciKayitFormu, SicilBelgesiForm, ProfilGuncellemeFormu, IlanForm, IlanSoruForm, MesajForm

def ana_sayfa(request):
    return render(request, 'core/ana_sayfa.html')

def ilanlar_listesi(request):
    aktif_ilanlar = Ilan.objects.filter(is_active=True).order_by('-olusturulma_tarihi')
    arama_kelimesi = request.GET.get('q')
    ilan_turu = request.GET.get('ilan_turu')
    max_fiyat = request.GET.get('max_fiyat')

    if arama_kelimesi:
        aktif_ilanlar = aktif_ilanlar.filter(baslik__icontains=arama_kelimesi) | aktif_ilanlar.filter(aciklama__icontains=arama_kelimesi)
    if ilan_turu:
        aktif_ilanlar = aktif_ilanlar.filter(ilan_turu=ilan_turu)
    if max_fiyat:
        aktif_ilanlar = aktif_ilanlar.filter(fiyat__lte=max_fiyat)

    # Giriş yapan kullanıcı için her ilanla olan Eşleşme Puanını hesapla
    if request.user.is_authenticated:
        kullanici_profili, _ = KullaniciProfili.objects.get_or_create(kullanici=request.user)
        for ilan in aktif_ilanlar:
            ilan_sahibi_profili, _ = KullaniciProfili.objects.get_or_create(kullanici=ilan.kullanici)
            if ilan.kullanici != request.user:
                ilan.eslesme_puani = kullanici_profili.eslesme_puani_hesapla(ilan_sahibi_profili)
            else:
                ilan.eslesme_puani = 100

    return render(request, 'core/ilanlar.html', {'ilanlar': aktif_ilanlar})

# ÜYE OLURKEN MAİLE DOĞRULAMA KODU GÖNDERME
def kayit_ol(request):
    if request.method == 'POST':
        form = KullaniciKayitFormu(request.POST)
        if form.is_valid():
            kullanici = form.save(commit=False)
            kullanici.is_active = False  # Kod doğrulanana kadar hesabı pasif tut
            kod = str(random.randint(100000, 999999))
            kullanici.dogrulama_kodu = kod
            kullanici.save()
            
            # Profilini otomatik oluştur
            KullaniciProfili.objects.get_or_create(kullanici=kullanici)

            # Doğrulama mailini gönder
            try:
                send_mail(
                    subject='KampüsEvim - E-Posta Doğrulama Kodunuz',
                    message=f'Merhaba {kullanici.username},\n\nKampüsEvim hesabınızı aktifleştirmek için doğrulama kodunuz: {kod}\n\nGüvenli günler dileriz!',
                    from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None,
                    recipient_list=[kullanici.email],
                    fail_silently=False,
                )
            except Exception as e:
                pass

            request.session['dogrulanacak_kullanici_id'] = kullanici.id
            messages.info(request, "📧 Üniversite e-postanıza 6 haneli bir doğrulama kodu gönderdik. Lütfen kodu girin.")
            return redirect('eposta_dogrula')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"⚠️ {error}")
    else:
        form = KullaniciKayitFormu()
    return render(request, 'core/kayit_ol.html', {'form': form})

# E-POSTA DOĞRULAMA EKRANI
def eposta_dogrula(request):
    kullanici_id = request.session.get('dogrulanacak_kullanici_id')
    if not kullanici_id:
        return redirect('kayit_ol')
    
    kullanici = get_object_or_404(Kullanici, id=kullanici_id)

    if request.method == 'POST':
        girilen_kod = request.POST.get('kod', '').strip()
        if girilen_kod == kullanici.dogrulama_kodu:
            kullanici.is_active = True
            kullanici.eposta_dogrulandi = True
            kullanici.dogrulama_kodu = ''
            kullanici.save()
            login(request, kullanici)
            messages.success(request, "🎉 E-postanız başarıyla doğrulandı! KampüsEvim'e hoş geldiniz.")
            return redirect('ana_sayfa')
        else:
            messages.error(request, "⚠️ Hatalı doğrulama kodu girdiniz! Lütfen tekrar kontrol edin.")

    return render(request, 'core/eposta_dogrula.html', {'email': kullanici.email})

def giris_yap(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            kullanici = form.get_user()
            login(request, kullanici)
            return redirect('ana_sayfa')
        else:
            messages.error(request, "⚠️ Kullanıcı adı/şifre hatalı veya e-posta adresiniz henüz doğrulanmamış!")
    else:
        form = AuthenticationForm()
    return render(request, 'core/giris_yap.html', {'form': form})

def cikis_yap(request):
    logout(request)
    return redirect('ana_sayfa')

@login_required(login_url='/giris/') 
def belge_yukle(request):
    if request.method == 'POST':
        form = SicilBelgesiForm(request.POST, request.FILES) 
        if form.is_valid():
            belge = form.save(commit=False)
            belge.kullanici = request.user 
            belge.save()
            messages.success(request, "✅ Adli sicil belgeniz başarıyla yüklendi. Yönetici onayı bekleniyor.")
            return redirect('profil')
    else:
        form = SicilBelgesiForm()
    return render(request, 'core/belge_yukle.html', {'form': form})

@login_required(login_url='/giris/')
def profil_sayfasi(request):
    profil, created = KullaniciProfili.objects.get_or_create(kullanici=request.user)
    kullanici_ilanlari = Ilan.objects.filter(kullanici=request.user).order_by('-olusturulma_tarihi')

    if request.method == 'POST':
        form = ProfilGuncellemeFormu(request.POST, request.FILES, instance=profil)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Profil bilgileriniz ve eşleşme kriterleriniz güncellendi!")
            return redirect('profil')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"⚠️ {error}")
    else:
        form = ProfilGuncellemeFormu(instance=profil)
    
    return render(request, 'core/profil.html', {'form': form, 'profil': profil, 'ilanlar': kullanici_ilanlari})

@login_required(login_url='/giris/')
def ilan_ekle(request):
    try:
        if not request.user.sicilbelgesi.onay_durumu:
            messages.error(request, "⚠️ Adli Sicil Belgeniz yönetici tarafından henüz onaylanmamış! Güvenlik gereği ilan veremezsiniz.")
            return redirect('profil')
    except:
        messages.error(request, "⚠️ İlan verebilmek için önce Adli Sicil Belgesi yüklemelisiniz!")
        return redirect('belge_yukle')

    if request.method == 'POST':
        form = IlanForm(request.POST, request.FILES) # Görsel yükleme için request.FILES eklendi
        if form.is_valid():
            ilan = form.save(commit=False)
            ilan.kullanici = request.user 
            ilan.save()
            messages.success(request, "✅ İlanınız görseliyle birlikte başarıyla yayınlandı!")
            return redirect('ilanlar')
    else:
        form = IlanForm()
    return render(request, 'core/ilan_ekle.html', {'form': form})

# İLAN DETAY, EŞLEŞME PUANI VE SORU-CEVAP SİSTEMİ
def ilan_detay(request, id):
    ilan = get_object_or_404(Ilan, id=id)
    sorular = ilan.sorular.all().order_by('-olusturulma_tarihi')
    ilan_sahibi_profili, _ = KullaniciProfili.objects.get_or_create(kullanici=ilan.kullanici)
    
    eslesme_puani = None
    if request.user.is_authenticated and request.user != ilan.kullanici:
        kullanici_profili, _ = KullaniciProfili.objects.get_or_create(kullanici=request.user)
        eslesme_puani = kullanici_profili.eslesme_puani_hesapla(ilan_sahibi_profili)

    if request.method == 'POST' and request.user.is_authenticated:
        # Yeni soru sorma işlemi
        if 'soru_gonder' in request.POST:
            soru_form = IlanSoruForm(request.POST)
            if soru_form.is_valid():
                yeni_soru = soru_form.save(commit=False)
                yeni_soru.ilan = ilan
                yeni_soru.soran = request.user
                yeni_soru.save()
                messages.success(request, "✅ Sorunuz ilan sahibine iletildi.")
                return redirect('ilan_detay', id=ilan.id)
        
        # İlan sahibinin soruya cevap vermesi
        elif 'cevap_gonder' in request.POST and request.user == ilan.kullanici:
            soru_id = request.POST.get('soru_id')
            cevap_metni = request.POST.get('cevap_metni')
            soru_obj = get_object_or_404(IlanSoru, id=soru_id, ilan=ilan)
            soru_obj.cevap_metni = cevap_metni
            soru_obj.save()
            messages.success(request, "✅ Cevabınız yayınlandı.")
            return redirect('ilan_detay', id=ilan.id)
    else:
        soru_form = IlanSoruForm()

    context = {
        'ilan': ilan,
        'sorular': sorular,
        'soru_form': soru_form,
        'eslesme_puani': eslesme_puani,
        'ilan_sahibi_profili': ilan_sahibi_profili
    }
    return render(request, 'core/ilan_detay.html', context)

@login_required(login_url='/giris/')
def ilan_duzenle(request, id):
    ilan = get_object_or_404(Ilan, id=id)
    if ilan.kullanici != request.user:
        return redirect('profil')

    if request.method == 'POST':
        form = IlanForm(request.POST, request.FILES, instance=ilan)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ İlanınız güncellendi.")
            return redirect('profil')
    else:
        form = IlanForm(instance=ilan)
    return render(request, 'core/ilan_duzenle.html', {'form': form, 'ilan': ilan})

@login_required(login_url='/giris/')
def ilan_sil(request, id):
    ilan = get_object_or_404(Ilan, id=id)
    if ilan.kullanici != request.user:
        return redirect('profil')

    if request.method == 'POST':
        ilan.delete()
        messages.success(request, "🗑️ İlanınız silindi.")
        return redirect('profil')
    return render(request, 'core/ilan_sil.html', {'ilan': ilan})

# DM (ÖZEL MESAJLAŞMA) KUTUSU VE SOHBET EKRANI
@login_required(login_url='/giris/')
def mesajlar_kutusu(request):
    mesajlar = Mesaj.objects.filter(Q(gonderen=request.user) | Q(alici=request.user)).order_by('-tarih')
    konusulan_kisiler = []
    kisi_idleri = set()
    
    for m in mesajlar:
        karsi_taraf = m.alici if m.gonderen == request.user else m.gonderen
        if karsi_taraf.id not in kisi_idleri:
            kisi_idleri.add(karsi_taraf.id)
            konusulan_kisiler.append(karsi_taraf)

    return render(request, 'core/mesajlar.html', {'konusulan_kisiler': konusulan_kisiler})

@login_required(login_url='/giris/')
def sohbet_detay(request, kullanici_id):
    karsi_taraf = get_object_or_404(Kullanici, id=kullanici_id)
    if karsi_taraf == request.user:
        return redirect('mesajlar_kutusu')

    mesajlar = Mesaj.objects.filter(
        (Q(gonderen=request.user) & Q(alici=karsi_taraf)) |
        (Q(gonderen=karsi_taraf) & Q(alici=request.user))
    ).order_by('tarih')

    # Okunmamış mesajları okundu olarak işaretle
    mesajlar.filter(alici=request.user, okundu=False).update(okundu=True)

    # İki kullanıcı arasındaki eşleşme puanını sohbet ekranında da göster
    kendi_profilim, _ = KullaniciProfili.objects.get_or_create(kullanici=request.user)
    karsi_profil, _ = KullaniciProfili.objects.get_or_create(kullanici=karsi_taraf)
    eslesme_puani = kendi_profilim.eslesme_puani_hesapla(karsi_profil)

    if request.method == 'POST':
        form = MesajForm(request.POST)
        if form.is_valid():
            yeni_mesaj = form.save(commit=False)
            yeni_mesaj.gonderen = request.user
            yeni_mesaj.alici = karsi_taraf
            yeni_mesaj.save()
            return redirect('sohbet_detay', kullanici_id=karsi_taraf.id)
    else:
        form = MesajForm()

    return render(request, 'core/sohbet.html', {
        'karsi_taraf': karsi_taraf,
        'mesajlar': mesajlar,
        'form': form,
        'eslesme_puani': eslesme_puani
    })