from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages # YENİ: Hata mesajları için eklendi
from .models import Ilan, SicilBelgesi, KullaniciProfili
from .forms import KullaniciKayitFormu, SicilBelgesiForm, ProfilGuncellemeFormu, IlanForm

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

    return render(request, 'core/ilanlar.html', {'ilanlar': aktif_ilanlar})

def kayit_ol(request):
    if request.method == 'POST':
        form = KullaniciKayitFormu(request.POST)
        if form.is_valid():
            form.save()
            return redirect('giris_yap')
    else:
        form = KullaniciKayitFormu()
    return render(request, 'core/kayit_ol.html', {'form': form})

def giris_yap(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            kullanici = form.get_user()
            login(request, kullanici)
            return redirect('ana_sayfa')
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
            return redirect('ana_sayfa')
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
            return redirect('profil')
    else:
        form = ProfilGuncellemeFormu(instance=profil)
    
    return render(request, 'core/profil.html', {'form': form, 'profil': profil, 'ilanlar': kullanici_ilanlari})

# 9. HAFTA YETKİ KONTROLÜ
@login_required(login_url='/giris/')
def ilan_ekle(request):
    # GÜVENLİK DUVARI: Belge onayı yoksa ilana izin verme
    try:
        if not request.user.sicilbelgesi.onay_durumu:
            messages.error(request, "⚠️ Adli Sicil Belgeniz yönetici tarafından henüz onaylanmamış! Güvenlik gereği ilan veremezsiniz.")
            return redirect('profil')
    except:
        messages.error(request, "⚠️ İlan verebilmek için önce Adli Sicil Belgesi yüklemelisiniz!")
        return redirect('belge_yukle')

    if request.method == 'POST':
        form = IlanForm(request.POST)
        if form.is_valid():
            ilan = form.save(commit=False)
            ilan.kullanici = request.user 
            ilan.save()
            return redirect('ilanlar')
    else:
        form = IlanForm()
    return render(request, 'core/ilan_ekle.html', {'form': form})

def ilan_detay(request, id):
    ilan = get_object_or_404(Ilan, id=id)
    return render(request, 'core/ilan_detay.html', {'ilan': ilan})

@login_required(login_url='/giris/')
def ilan_duzenle(request, id):
    ilan = get_object_or_404(Ilan, id=id)
    if ilan.kullanici != request.user:
        return redirect('profil')

    if request.method == 'POST':
        form = IlanForm(request.POST, instance=ilan)
        if form.is_valid():
            form.save()
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
        return redirect('profil')
    return render(request, 'core/ilan_sil.html', {'ilan': ilan})