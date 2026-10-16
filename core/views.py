import os
import json
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse  # <--- CANLI MESAJLAŞMA İÇİN EKLENDİ
from .models import Kullanici, Ilan, SicilBelgesi, KullaniciProfili, IlanSoru, Mesaj
from .forms import KullaniciKayitFormu, SicilBelgesiForm, ProfilGuncellemeFormu, IlanForm, IlanSoruForm, MesajForm

# --- TELEFON NUMARASI İÇİN YARDIMCI FONKSİYONLAR ---
TELEFON_DOSYASI = os.path.join(settings.BASE_DIR, 'telefon_kayitlari.json')

def _telefon_sozlugu_yukle():
    if os.path.exists(TELEFON_DOSYASI):
        try:
            with open(TELEFON_DOSYASI, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _telefon_oku(user, profil=None):
    for obj in (profil, user):
        if obj:
            for alan in ('telefon', 'telefon_no', 'telefon_numarasi'):
                deger = getattr(obj, alan, None)
                if deger:
                    return str(deger)
    sozluk = _telefon_sozlugu_yukle()
    return sozluk.get(str(user.id), '')

def _telefon_baskasinda_var_mi(user, telefon):
    if not telefon:
        return False
    sozluk = _telefon_sozlugu_yukle()
    for uid, tel in sozluk.items():
        if uid != str(user.id) and tel == telefon:
            return True
    if hasattr(Kullanici, 'telefon'):
        if Kullanici.objects.filter(telefon=telefon).exclude(pk=user.pk).exists():
            return True
    return False

def _telefon_kaydet(user, profil, telefon):
    sozluk = _telefon_sozlugu_yukle()
    sozluk[str(user.id)] = telefon
    try:
        with open(TELEFON_DOSYASI, 'w', encoding='utf-8') as f:
            json.dump(sozluk, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    for alan in ('telefon', 'telefon_no', 'telefon_numarasi'):
        if hasattr(user, alan):
            setattr(user, alan, telefon)
            user.save(update_fields=[alan])
        if profil and hasattr(profil, alan):
            setattr(profil, alan, telefon)
            profil.save(update_fields=[alan])

# --- ANA SAYFA VE İLANLAR ---
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

    if request.user.is_authenticated:
        kullanici_profili, _ = KullaniciProfili.objects.get_or_create(kullanici=request.user)
        for ilan in aktif_ilanlar:
            ilan_sahibi_profili, _ = KullaniciProfili.objects.get_or_create(kullanici=ilan.kullanici)
            if ilan.kullanici != request.user:
                ilan.eslesme_puani = kullanici_profili.eslesme_puani_hesapla(ilan_sahibi_profili)
            else:
                ilan.eslesme_puani = 100

    return render(request, 'core/ilanlar.html', {'ilanlar': aktif_ilanlar})

# --- KAYIT VE DOĞRULAMA ---
def kayit_ol(request):
    if request.method == 'POST':
        form = KullaniciKayitFormu(request.POST)
        if form.is_valid():
            kullanici = form.save(commit=False)
            kullanici.is_active = True
            kod = str(random.randint(100000, 999999))
            kullanici.dogrulama_kodu = kod
            kullanici.save()
            
            KullaniciProfili.objects.get_or_create(kullanici=kullanici)

            mail_gitti = False
            try:
                send_mail(
                    subject='KampüsEvim - E-Posta Doğrulama Kodunuz',
                    message=f'Merhaba {kullanici.username},\n\nKampüsEvim hesabınızı aktifleştirmek için doğrulama kodunuz: {kod}',
                    from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None,
                    recipient_list=[kullanici.email],
                    fail_silently=False,
                )
                mail_gitti = True
            except Exception:
                pass

            if mail_gitti:
                request.session['dogrulanacak_kullanici_id'] = kullanici.id
                messages.info(request, "📧 Üniversite e-postanıza doğrulama kodu gönderildi.")
                return redirect('eposta_dogrula')
            else:
                kullanici.eposta_dogrulandi = True
                kullanici.save()
                login(request, kullanici, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, "🎉 Kaydınız başarıyla tamamlandı!")
                return redirect('ana_sayfa')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"⚠️ {error}")
    else:
        form = KullaniciKayitFormu()
    return render(request, 'core/kayit_ol.html', {'form': form})

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
            login(request, kullanici, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "🎉 E-postanız başarıyla doğrulandı!")
            return redirect('ana_sayfa')
        else:
            messages.error(request, "⚠️ Hatalı kod girdiniz!")

    return render(request, 'core/eposta_dogrula.html', {'email': kullanici.email})

# --- GİRİŞ VE ÇIKIŞ (TAMAMEN ESNEK SİSTEM) ---
def giris_yap(request):
    Kullanici.objects.filter(is_active=False).update(is_active=True)

    if request.method == 'POST':
        girilen_bilgi = request.POST.get('username', '').strip()
        sifre = request.POST.get('password', '').strip()

        kullanici = Kullanici.objects.filter(
            Q(username__iexact=girilen_bilgi) | Q(email__iexact=girilen_bilgi)
        ).first()

        if kullanici:
            sifre_dogru = kullanici.check_password(sifre)

            if not sifre_dogru and kullanici.password == sifre:
                kullanici.set_password(sifre)
                kullanici.save()
                sifre_dogru = True

            if sifre_dogru:
                kullanici.is_active = True
                kullanici.save(update_fields=['is_active'])
                login(request, kullanici, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('ana_sayfa')
            else:
                messages.error(request, "⚠️ Girdiğiniz şifre hatalı! Lütfen kontrol edip tekrar deneyin.")
        else:
            messages.error(request, "⚠️ Bu kullanıcı adı veya e-posta ile kayıtlı bir hesap bulunamadı!")

    form = AuthenticationForm()
    return render(request, 'core/giris_yap.html', {'form': form})

def cikis_yap(request):
    logout(request)
    return redirect('ana_sayfa')

# --- PROFİL VE BELGE YÜKLEME ---
@login_required(login_url='/giris/')
def belge_yukle(request):
    mevcut_belge = SicilBelgesi.objects.filter(kullanici=request.user).first()
    if request.method == 'POST':
        form = SicilBelgesiForm(request.POST, request.FILES, instance=mevcut_belge)
        if form.is_valid():
            belge = form.save(commit=False)
            belge.kullanici = request.user
            belge.save()
            messages.success(request, "✅ Adli sicil belgeniz yüklendi.")
            return redirect('profil')
    else:
        form = SicilBelgesiForm(instance=mevcut_belge)
    return render(request, 'core/belge_yukle.html', {'form': form})

@login_required(login_url='/giris/')
def profil_sayfasi(request):
    profil, created = KullaniciProfili.objects.get_or_create(kullanici=request.user)
    kullanici_ilanlari = Ilan.objects.filter(kullanici=request.user).order_by('-olusturulma_tarihi')

    if request.method == 'POST':
        telefon = request.POST.get('telefon_numarasi', '').strip()

        if _telefon_baskasinda_var_mi(request.user, telefon):
            messages.error(request, "⚠️ Bu telefon numarası başka bir kullanıcı tarafından kullanılıyor!")
            form = ProfilGuncellemeFormu(request.POST, request.FILES, instance=profil)
        else:
            bolum = request.POST.get('bolum', '').strip()
            sigara = request.POST.get('sigara_kullanimi', profil.sigara_kullanimi)
            uyku = request.POST.get('uyku_duzeni', profil.uyku_duzeni)
            evcil = request.POST.get('evcil_hayvan', profil.evcil_hayvan)
            temizlik = request.POST.get('temizlik_aliskanligi', profil.temizlik_aliskanligi)

            profil.bolum = bolum
            if sigara: profil.sigara_kullanimi = sigara
            if uyku: profil.uyku_duzeni = uyku
            if evcil: profil.evcil_hayvan = evcil
            if temizlik: profil.temizlik_aliskanligi = temizlik

            if 'profil_resmi' in request.FILES:
                profil.profil_resmi = request.FILES['profil_resmi']

            profil.save()

            KullaniciProfili.objects.filter(pk=profil.pk).update(
                bolum=profil.bolum,
                sigara_kullanimi=profil.sigara_kullanimi,
                uyku_duzeni=profil.uyku_duzeni,
                evcil_hayvan=profil.evcil_hayvan,
                temizlik_aliskanligi=profil.temizlik_aliskanligi,
            )

            _telefon_kaydet(request.user, profil, telefon)

            messages.success(request, "✅ Profil bilgileriniz kalıcı olarak güncellendi!")
            return redirect('profil')
    else:
        profil.refresh_from_db()
        baslangic_verileri = {
            'telefon_numarasi': _telefon_oku(request.user, profil),
            'bolum': profil.bolum,
            'sigara_kullanimi': profil.sigara_kullanimi,
            'uyku_duzeni': profil.uyku_duzeni,
            'evcil_hayvan': profil.evcil_hayvan,
            'temizlik_aliskanligi': profil.temizlik_aliskanligi,
        }
        form = ProfilGuncellemeFormu(instance=profil, initial=baslangic_verileri)

    return render(request, 'core/profil.html', {'form': form, 'profil': profil, 'ilanlar': kullanici_ilanlari})

# --- İLAN YÖNETİMİ ---
@login_required(login_url='/giris/')
def ilan_ekle(request):
    try:
        if not request.user.sicilbelgesi.onay_durumu:
            messages.error(request, "⚠️ Adli Sicil Belgeniz henüz onaylanmamış!")
            return redirect('profil')
    except Exception:
        messages.error(request, "⚠️ İlan verebilmek için önce Adli Sicil Belgesi yüklemelisiniz!")
        return redirect('belge_yukle')

    if request.method == 'POST':
        form = IlanForm(request.POST, request.FILES)
        if form.is_valid():
            ilan = form.save(commit=False)
            ilan.kullanici = request.user
            ilan.save()
            messages.success(request, "✅ İlanınız yayınlandı!")
            return redirect('ilanlar')
    else:
        form = IlanForm()
    return render(request, 'core/ilan_ekle.html', {'form': form})

def ilan_detay(request, id):
    ilan = get_object_or_404(Ilan, id=id)
    sorular = ilan.sorular.all().order_by('-olusturulma_tarihi')
    ilan_sahibi_profili, _ = KullaniciProfili.objects.get_or_create(kullanici=ilan.kullanici)
    
    eslesme_puani = None
    if request.user.is_authenticated and request.user != ilan.kullanici:
        kullanici_profili, _ = KullaniciProfili.objects.get_or_create(kullanici=request.user)
        eslesme_puani = kullanici_profili.eslesme_puani_hesapla(ilan_sahibi_profili)

    if request.method == 'POST' and request.user.is_authenticated:
        if 'soru_gonder' in request.POST:
            soru_form = IlanSoruForm(request.POST)
            if soru_form.is_valid():
                yeni_soru = soru_form.save(commit=False)
                yeni_soru.ilan = ilan
                yeni_soru.soran = request.user
                yeni_soru.save()
                messages.success(request, "✅ Sorunuz iletildi.")
                return redirect('ilan_detay', id=ilan.id)
        
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

# --- ÖZEL MESAJLAŞMA (DM) ---
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

    return render(request, 'core/mesajlar.html', {
        'konusulan_kisiler': konusulan_kisiler,
        'kisiler': konusulan_kisiler
    })

# --- CANLI MESAJLAŞMA İÇİN GÜNCELLENEN FONKSİYON ---
@login_required(login_url='/giris/')
def sohbet_detay(request, kullanici_id):
    karsi_taraf = get_object_or_404(Kullanici, id=kullanici_id)
    if karsi_taraf == request.user:
        return redirect('mesajlar_kutusu')

    # AJAX ile mesaj gönderme
    if request.method == 'POST':
        form = MesajForm(request.POST)
        if form.is_valid():
            yeni_mesaj = form.save(commit=False)
            yeni_mesaj.gonderen = request.user
            yeni_mesaj.alici = karsi_taraf
            yeni_mesaj.save()
            
            # İstek AJAX'tan (JavaScript'ten) geldiyse sadece OK yanıtı dön
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok'})
                
            return redirect('sohbet_detay', kullanici_id=karsi_taraf.id)

    mesajlar = Mesaj.objects.filter(
        (Q(gonderen=request.user) & Q(alici=karsi_taraf)) |
        (Q(gonderen=karsi_taraf) & Q(alici=request.user))
    ).order_by('tarih')

    mesajlar.filter(alici=request.user, okundu=False).update(okundu=True)

    # AJAX ile mesajları 2 saniyede bir çekme
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'GET':
        mesaj_listesi = []
        for m in mesajlar:
            mesaj_listesi.append({
                'icerik': m.icerik,
                'benim_mesajim': m.gonderen == request.user,
                'tarih': m.tarih.strftime('%d %b %H:%M')
            })
        return JsonResponse({'mesajlar': mesaj_listesi})

    kendi_profilim, _ = KullaniciProfili.objects.get_or_create(kullanici=request.user)
    karsi_profil, _ = KullaniciProfili.objects.get_or_create(kullanici=karsi_taraf)
    eslesme_puani = kendi_profilim.eslesme_puani_hesapla(karsi_profil)

    form = MesajForm()

    return render(request, 'core/sohbet.html', {
        'karsi_taraf': karsi_taraf,
        'diger_kullanici': karsi_taraf,
        'mesajlar': mesajlar,
        'form': form,
        'eslesme_puani': eslesme_puani
    })