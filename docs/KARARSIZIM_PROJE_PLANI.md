# kararsızım — Proje Planı (Claude Code için)

> Bu dosya projenin tek kaynağıdır. Claude Code her aşamada önce bu dosyayı okumalı, sadece istenen aşamayı yapmalı ve **bir sonraki aşamaya kendiliğinden geçmemelidir**.
> İpucu: Bu dosyayı repo köküne `CLAUDE.md` adıyla da kopyalayabilirsin; Claude Code her oturumda otomatik okur.

---

## 1. Proje Özeti

**Proje adı:** kararsızım

**Amaç:** Kullanıcıların kararsız kaldıkları konularda diğer kullanıcılara danışabildiği bir anket platformu. Örnek: "Bugün sinemaya mı gitsem, restorana mı?" sorusu sorulur, 2 ile 5 arası seçenek eklenir, diğer kullanıcılar oy verir.

**Önemli kararlar:**
- Takip (follow) sistemi YOK. Herkes platformdaki her anketi görür ve oylayabilir.
- Üye olmadan anketler **görüntülenebilir ve oylanabilir**.
- **Anket oluşturmak için üyelik zorunlu.**
- Kayıt: e-posta + parola + kullanıcı adı. Anketlerde **kullanıcı adı** görünür, **e-posta asla görünmez**.
- Hedef: **basit bir prototip**. Gereksiz karmaşık teknoloji kullanılmayacak. Sonra adım adım geliştirilecek.

---

## 2. Teknoloji Seçimleri

| Alan | Seçim |
|---|---|
| Dil / Framework | Python + Django (güncel kararlı sürüm) |
| Veritabanı | Supabase (yalnızca **PostgreSQL** olarak kullanılacak) |
| Deployment | Vercel |
| Frontend | Ayrı framework YOK. Django template (HTML) + CSS + vanilla JavaScript, aynı repo içinde |

**Basit tutma kuralları (prototip için):**
- Supabase Auth, Supabase JS client, REST/Realtime kullanılmayacak. Sadece Django'nun veritabanı bağlantısı Supabase Postgres'e yönlenecek.
- Kimlik doğrulama Django'nun kendi auth sistemiyle yapılacak (session tabanlı).
- Django REST Framework, React, Tailwind, Celery, Redis vb. EKLENMEYECEK.
- Oy verme gibi etkileşimlerde sayfa yenilemeden çalışması için küçük `fetch` çağrıları yeterli.

---

## 3. Özellikler

### 3.1 Ziyaretçi (üye olmayan)
- Ana sayfada tüm anketleri görür (en yeni en üstte, sayfalama ile).
- Anket detayını açar, oy verir.
- Oy verdikten sonra sonuçları görür.
- Anket oluşturmaya çalışırsa kayıt/giriş sayfasına yönlendirilir.

### 3.2 Üye
- Ziyaretçinin yapabildiği her şey.
- Anket oluşturur.
- Kendi anketlerini "Anketlerim" sayfasında görür.
- Kendi anketini silebilir.
- Çıkış yapabilir.

### 3.3 Anket kuralları
- Soru: zorunlu, 5–200 karakter.
- Seçenek sayısı: **en az 2, en fazla 5**.
- Her seçenek: zorunlu, 1–80 karakter, aynı ankette tekrar edemez (büyük/küçük harf farkı yok sayılır).
- Anket oluşturma formunda "Seçenek ekle" butonu (5'e ulaşınca devre dışı) ve "Kaldır" butonu (2'nin altına inemez) olacak. Bu JavaScript ile yapılacak, ama sunucu tarafında da aynı kurallar mutlaka doğrulanacak.
- Anketlerde yazar olarak **kullanıcı adı** gösterilir.

### 3.4 Oylama kuralları
- Bir kişi bir ankette **yalnızca bir kez** oy verebilir. Oy sonradan değiştirilemez (prototip için).
- Giriş yapmış kullanıcı: oy kullanıcıya bağlanır.
- Giriş yapmamış ziyaretçi: oy Django session anahtarına bağlanır (session yoksa oluşturulur).
- Anket sahibi kendi anketine de oy verebilir.
- **Sonuçlar oy verdikten sonra gösterilir** (oy verilmeden önce sonuç görünmez, böylece insanlar sonuçtan etkilenmez). Anket sahibi sonuçları her zaman görür.
- Sonuç gösterimi: her seçenek için oy sayısı + yüzde + ilerleme çubuğu, toplam oy sayısı.

### 3.5 Kayıt / Giriş
- Kayıt alanları: kullanıcı adı, e-posta, parola, parola tekrarı.
- Kullanıcı adı: benzersiz (büyük/küçük harf duyarsız), 3–20 karakter, sadece harf, rakam ve alt çizgi.
- E-posta: benzersiz, geçerli format. Hiçbir sayfada başkalarına gösterilmez.
- Parola: Django'nun varsayılan parola doğrulayıcıları kullanılır.
- Giriş: **e-posta + parola** ile.
- E-posta doğrulama ve parola sıfırlama prototipte YOK (sonraki aşamalarda eklenebilir).

### 3.6 Kapsam dışı (şimdilik YAPILMAYACAK)
Takip sistemi, yorumlar, beğeni, kategori/etiket, arama, raporlama/moderasyon, bildirimler, profil sayfası düzenleme, oy değiştirme, anket düzenleme, süreli anketler, e-posta doğrulama, parola sıfırlama, çoklu dil, admin dışında yönetim paneli.

---

## 4. Veri Modeli

Django modelleri (Supabase Postgres üzerinde):

**User** (`AbstractUser` genişletilir, proje başında oluşturulmalı)
- `username` (benzersiz, büyük/küçük harf duyarsız kontrol)
- `email` (benzersiz, giriş alanı: `USERNAME_FIELD = "email"`)
- `password`
- `date_joined`

**Poll**
- `author` → User (FK, CASCADE)
- `question` (CharField, max 200)
- `created_at` (auto)

**Option**
- `poll` → Poll (FK, CASCADE, related_name="options")
- `text` (CharField, max 80)
- `position` (sıralama için, 0'dan başlar)

**Vote**
- `poll` → Poll (FK, CASCADE)
- `option` → Option (FK, CASCADE)
- `user` → User (FK, null=True, blank=True)
- `session_key` (CharField, null=True, blank=True)
- `created_at` (auto)
- Kısıtlar (UniqueConstraint):
  - `(poll, user)` — `user` boş değilken benzersiz
  - `(poll, session_key)` — `session_key` boş değilken benzersiz
- Oy kaydedilirken `option.poll == poll` olduğu doğrulanmalı.

Aynı anda gelen çift oy isteklerine karşı veritabanı kısıtına güvenilir; `IntegrityError` yakalanıp "zaten oy verdin" cevabı döndürülür.

---

## 5. Sayfalar ve URL'ler

| URL | Sayfa | Giriş gerekli mi |
|---|---|---|
| `/` | Ana sayfa: anket listesi (sayfalı, 10'ar) | Hayır |
| `/anket/<id>/` | Anket detayı + oylama / sonuçlar | Hayır |
| `/anket/<id>/oyla/` | Oy verme (POST, JSON cevap) | Hayır |
| `/anket/olustur/` | Anket oluşturma formu | **Evet** |
| `/anket/<id>/sil/` | Anketi sil (POST, sadece sahibi) | **Evet** |
| `/anketlerim/` | Kendi anketlerim | **Evet** |
| `/kayit/` | Kayıt | Hayır |
| `/giris/` | Giriş | Hayır |
| `/cikis/` | Çıkış (POST) | Evet |

Giriş gerektiren sayfalara giriş yapmadan gidilirse `/giris/?next=...` ile yönlendirilir; giriş sonrası kaldığı yere döner.

Arayüz dili: **Türkçe**. Django ayarları: `LANGUAGE_CODE = "tr"`, `TIME_ZONE = "Europe/Istanbul"`.

---

## 6. Arayüz / Tasarım Yönergesi

**Hedef kitle:** Gençler. **His:** Açık, temiz, enerjik, eğlenceli ama okunaklı.

- Arka plan: açık (örn. `#FAFAFF` / çok açık lavanta).
- Metin: koyu lacivert/antrasit (`#1E1B3A`), asla saf siyah değil.
- Canlı vurgu renkleri (CSS değişkenleri olarak tanımlanmalı):
  - Ana: `#6C5CE7` (mor)
  - İkincil: `#FF6B9D` (pembe)
  - Yardımcı: `#00CEC9` (turkuaz), `#FFD93D` (sarı)
- Kartlar: beyaz, yumuşak köşeler (`border-radius: 16–20px`), hafif gölge, hover'da hafif yükselme.
- Butonlar: yuvarlak köşeli, canlı arka plan, hover/focus durumları net.
- Oylama seçenekleri: büyük, tıklaması kolay kartlar/butonlar. Sonuç çubukları canlı renkli ve animasyonlu dolsun (CSS transition).
- Her seçeneğe farklı bir canlı renk verilebilir (5 renk paleti).
- Tipografi: Google Fonts'tan yuvarlak hatlı bir font (örn. Poppins veya Nunito), yedek font olarak sistem fontu.
- **Mobil öncelikli (responsive)**. Gençler çoğunlukla telefondan girecek. Tek sütun, geniş dokunma alanları.
- Üst menü: logo "kararsızım" (başında küçük bir emoji olabilir, örn. 🤔), "Anket Oluştur" belirgin buton, giriş yapmışsa kullanıcı adı + Çıkış, değilse Giriş / Kayıt.
- Boş durumlar için dostça mesajlar (örn. "Henüz anket yok, ilk kararsızlığı sen paylaş!").
- Hata ve başarı mesajları Django `messages` çerçevesiyle gösterilecek.
- Erişilebilirlik: yeterli renk kontrastı, form alanlarında `label`, klavye ile kullanılabilirlik.

---

## 7. Önerilen Proje Yapısı

```
kararsizim/
├── CLAUDE.md                  # (bu dosyanın kopyası, opsiyonel)
├── KARARSIZIM_PROJE_PLANI.md
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── config/                    # Django proje ayarları
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                  # Kullanıcı modeli, kayıt, giriş
├── polls/                     # Poll, Option, Vote, görünümler
├── templates/
│   ├── base.html
│   ├── accounts/
│   └── polls/
└── static/
    ├── css/style.css
    └── js/
        ├── create_poll.js     # seçenek ekle/kaldır
        └── vote.js            # fetch ile oy verme + sonuç gösterme
```

---

## 8. Ortam ve Dağıtım Notları

### 8.1 Ortam değişkenleri (`.env`, Git'e EKLENMEZ)
- `SECRET_KEY`
- `DEBUG` (yerelde `True`, Vercel'de `False`)
- `DATABASE_URL` (Supabase Postgres bağlantı adresi)
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS` (Vercel alan adı, `https://...` ile)

`.env.example` dosyası gerçek değerler olmadan oluşturulur. Gerçek anahtarlar asla koda yazılmaz.

### 8.2 Supabase
- Sadece Postgres bağlantısı kullanılır (`psycopg` + `dj-database-url`).
- Vercel serverless olduğu için Supabase'in **connection pooler** (transaction modu) adresi kullanılmalı; `CONN_MAX_AGE = 0` ve gerekirse `DISABLE_SERVER_SIDE_CURSORS = True` ayarlanmalı.
- Migrasyonlar **yerel bilgisayardan** Supabase'e çalıştırılır (`python manage.py migrate`); Vercel build sırasında çalıştırılmaz.

### 8.3 Vercel
- Vercel, Django'yu **sıfır yapılandırmayla** destekler: depoda `manage.py` bulunca projeyi otomatik tanır, `WSGI_APPLICATION` (veya `ASGI_APPLICATION`) ayarından giriş noktasını okur. Bu yüzden `api/index.py` veya karmaşık bir `vercel.json` ile BAŞLAMA; önce otomatik algılamayı dene, sadece gerekirse yapılandırma ekle.
- Statik dosyalar: `settings.py` içinde `STATIC_ROOT` tanımlanırsa Vercel build sırasında `collectstatic` komutunu kendisi çalıştırır ve dosyaları CDN'den `STATIC_URL` altında sunar. Önce bu akışı kullan; çalışmazsa `whitenoise` ekle.
- Python sürümünü `pyproject.toml` veya `.python-version` ile belirt; bağımlılıkları `requirements.txt` veya `pyproject.toml` içinde tanımla.
- **Güncel dokümantasyon:** Vercel'in "Deploy a Django app on Vercel" sayfasını kontrol et (https://vercel.com/docs/frameworks/full-stack/django). Bu bölümle çelişki varsa güncel dokümantasyon geçerlidir.
- Production'da: `DEBUG=False`, `SECURE_*` çerez ayarları (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`) açık.
- SQLite KULLANILMAYACAK (Vercel dosya sistemi kalıcı değil). Yerel geliştirmede de doğrudan Supabase kullanılabilir ya da ayrı bir geliştirme veritabanı tercih edilebilir.

### 8.4 Güvenlik temelleri (prototipte bile şart)
- Tüm POST istekleri CSRF korumalı. `fetch` çağrıları `X-CSRFToken` başlığını göndermeli.
- Kullanıcı girdisi şablonlarda otomatik escape edilir; `|safe` kullanılmaz.
- Anket silme ve oluşturma için sahiplik/giriş kontrolleri sunucuda yapılır.
- E-posta adresi hiçbir şablonda, JSON cevabında veya URL'de başkalarına gösterilmez.
- Oy verme ve kayıt için temel sınırlandırma (rate limit) sonraki aşamada eklenebilir; şimdilik not olarak kalsın.

---

## 9. Çalışma Aşamaları

Her aşama ayrı bir Claude Code oturumunda/isteğinde yapılmalıdır. Bir aşama bitip test edilmeden diğerine geçilmez.

### Aşama 0 — Proje iskeleti
- Django projesini (`config`) ve `accounts`, `polls` uygulamalarını oluştur.
- `requirements.txt`, `.gitignore`, `.env.example` hazırla.
- `settings.py`: ortam değişkenleri, `DATABASE_URL` ile Supabase Postgres, `tr` dil ayarı, templates/static klasörleri, `STATIC_ROOT` tanımı.
- Özel User modelini (e-posta ile giriş, benzersiz kullanıcı adı) **ilk migrasyondan önce** tanımla.
- `base.html` ve boş bir ana sayfa ile sunucunun çalıştığını göster.
- **Bitiş kriteri:** `python manage.py runserver` çalışıyor, migrasyonlar Supabase'e uygulanmış.

### Aşama 1 — Üyelik
- Kayıt, giriş, çıkış sayfaları ve formları (kurallar: bölüm 3.5).
- Üst menünün giriş durumuna göre değişmesi.
- `next` yönlendirmesi.
- **Bitiş kriteri:** Kayıt ol → çıkış yap → e-posta ile giriş yap akışı çalışıyor; aynı e-posta/kullanıcı adı ikinci kez kullanılamıyor.

### Aşama 2 — Anket oluşturma
- `Poll`, `Option` modelleri ve migrasyon.
- Anket oluşturma formu (2–5 seçenek, dinamik ekle/kaldır JS'i, sunucu doğrulaması).
- Giriş yoksa `/giris/` yönlendirmesi.
- Django admin'de Poll/Option/Vote kayıtları görünsün.
- **Bitiş kriteri:** Üye 2–5 seçenekli anket oluşturabiliyor; 1 veya 6 seçenek reddediliyor.

### Aşama 3 — Listeleme ve oylama
- Ana sayfa listesi (sayfalama), anket detay sayfası.
- `Vote` modeli, benzersizlik kısıtları, oy verme endpoint'i (JSON), `vote.js` ile sayfa yenilemeden sonuç gösterimi.
- Ziyaretçi (session) ve üye oylaması; çift oy engeli.
- "Anketlerim" sayfası ve anket silme.
- **Bitiş kriteri:** Ziyaretçi ve üye oy verebiliyor; ikinci oy reddediliyor; sonuçlar doğru yüzdelerle görünüyor.

### Aşama 4 — Tasarım cilası
- Bölüm 6'daki tasarım yönergesini uygula: renkler, kartlar, animasyonlu sonuç çubukları, mobil uyum, boş durumlar.
- **Bitiş kriteri:** 375px (telefon) ve masaüstü genişlikte düzgün görünüyor.

### Aşama 5 — Vercel'e yayınlama
- Önce Vercel'in Django için otomatik algılamasını dene (`manage.py`, `WSGI_APPLICATION`, `STATIC_ROOT`); sadece gerekirse `vercel.json` veya ek yapılandırma ekle.
- Production ayarları (bölüm 8): `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, güvenli çerezler.
- README'ye yerel kurulum ve yayınlama adımlarını yaz.
- **Bitiş kriteri:** Vercel adresinde kayıt, anket oluşturma ve oylama çalışıyor.

### Sonraki fikirler (prototipten sonra)
E-posta doğrulama, parola sıfırlama, kategoriler, arama, en çok oy alanlar sıralaması, süreli anketler, rate limit, rapor/moderasyon.

---

## 10. Claude Code'a Verilecek Hazır Promptlar

Her prompt ayrı ayrı verilmelidir. Başlamadan önce: *"Önce KARARSIZIM_PROJE_PLANI.md dosyasını baştan sona oku."*

**Aşama 0:**
```
KARARSIZIM_PROJE_PLANI.md dosyasını baştan sona oku. Sadece "Aşama 0 — Proje iskeleti" bölümünü uygula, başka aşamaya geçme. Bitirince neleri yaptığını, nasıl çalıştıracağımı ve Supabase DATABASE_URL değerini .env dosyasına nasıl ekleyeceğimi adım adım Türkçe anlat.
```

**Aşama 1:**
```
KARARSIZIM_PROJE_PLANI.md dosyasını oku. Aşama 0 tamamlandı. Sadece "Aşama 1 — Üyelik" bölümünü uygula. Bitirince bitiş kriterini nasıl test edeceğimi söyle.
```

**Aşama 2:**
```
KARARSIZIM_PROJE_PLANI.md dosyasını oku. Aşama 0 ve 1 tamamlandı. Sadece "Aşama 2 — Anket oluşturma" bölümünü uygula. Bitirince bitiş kriterini nasıl test edeceğimi söyle.
```

**Aşama 3:**
```
KARARSIZIM_PROJE_PLANI.md dosyasını oku. Aşama 0, 1 ve 2 tamamlandı. Sadece "Aşama 3 — Listeleme ve oylama" bölümünü uygula. Çift oy engeli ve ziyaretçi/üye oylaması bölüm 3.4 ve 4'teki kurallara birebir uysun. Bitirince bitiş kriterini nasıl test edeceğimi söyle.
```

**Aşama 4:**
```
KARARSIZIM_PROJE_PLANI.md dosyasını oku. Aşama 0-3 tamamlandı. Sadece "Aşama 4 — Tasarım cilası" bölümünü ve bölüm 6'daki tasarım yönergesini uygula. Yeni bir kütüphane veya framework ekleme; sadece HTML, CSS ve vanilla JS kullan.
```

**Aşama 5:**
```
KARARSIZIM_PROJE_PLANI.md dosyasını oku. Aşama 0-4 tamamlandı. Sadece "Aşama 5 — Vercel'e yayınlama" bölümünü uygula. Vercel'in güncel Django/Python dokümantasyonunu kontrol edip ona göre yapılandır. Her adımı benim yapabileceğim şekilde Türkçe açıkla.
```

---

## 11. Claude Code İçin Genel Kurallar

1. Sadece istenen aşamayı yap; kapsam dışı özellikleri (bölüm 3.6) ekleme.
2. En basit çalışan çözümü seç. Yeni bağımlılık eklemeden önce gerekçesini söyle.
3. Kod yorumları ve kullanıcıya görünen tüm metinler **Türkçe** olsun (değişken/fonksiyon adları İngilizce olabilir).
4. Gizli bilgileri (anahtarlar, veritabanı şifresi) koda yazma, `.env` kullan.
5. Her aşama sonunda: ne yapıldı, nasıl test edilir, bilinen eksikler neler — kısaca özetle.
6. Emin olmadığın bir karar varsa varsayım yapıp ilerlemeden önce sor.
7. Ben bilgisayar programcılığı öğrenen biriyim: önemli kavramları (model, migrasyon, view, CSRF vb.) kısa ve sade şekilde açıkla.
