# FinPro – Išsamus projekto aprašymas

> **Sugeneruota:** 2026-04-13  
> **Projektas:** FinPro – UAB „HARLEMO PROJEKTAI" (H-Pro) verslo valdymo sistema  
> **Technologijos:** Django 5.x, Python 3.14, SQLite, Bootstrap 5, WeasyPrint, TinyMCE

---

## 1. Projekto apžvalga

**FinPro** – tai web-aplikacija, skirta interjero dizaino bei remonto paslaugų valdymui. Sistema leidžia:

- Klientams: kurti užsakymus, sekti jų statusą, atsisiųsti sąskaitas-faktūras (PDF).
- Vadybininkams: valdyti priskirtus užsakymus, keisti statusus, redaguoti eilutes.
- Administratoriams: matyti visus užsakymus, atkurti pašalintus, valdyti puslapio nustatymus.
- Lankytojams: peržiūrėti paslaugų sąrašą, galeriją, atsiliepimus.

**Kalba:** lietuvių (pagrindinė), anglų, rusų (i18n palaikymas su django gettext).

---

## 2. Projekto struktūra

```
FinPro/
├── _fill_translations.py        ← Pagalbinis skriptas vertimų .po failams pildyti
├── requirements.txt
└── mysite/                      ← Django projekto šaknis
    ├── manage.py
    ├── db.sqlite3
    ├── mysite/                  ← Django nustatymai (settings, urls, wsgi, asgi)
    ├── main/                    ← Pagrindinis app (vartotojai, profilis, pradžios puslapis)
    ├── orders/                  ← Užsakymų app
    ├── services/                ← Paslaugų app
    ├── reviews/                 ← Atsiliepimų app
    ├── gallery/                 ← Galerijos app
    ├── media/                   ← Įkelti failai (avatariai, galerija, sąskaitos)
    ├── static/                  ← Statiniai failai (CSS, JS, paveikslėliai)
    └── project_doc/             ← Projekto dokumentacija (šis katalogas)
```

---

## 3. Modeliai

### 3.1 `main` app

#### `Profile` (`main/models.py`)

Vartotojo profilio modelis. Kiekvienas `User` turi lygiai vieną `Profile` (OneToOne).

| Laukas | Tipas | Aprašymas |
|--------|-------|-----------|
| `user` | `OneToOneField(User)` | Django `auth.User` – pagrindinis vartotojas |
| `avatar` | `ImageField(upload_to='avatars/')` | Profilio nuotrauka |
| `bio` | `TextField` | Trumpas aprašymas |
| `phone` | `CharField(30)` | Telefono numeris |
| `city` | `CharField(100)` | Miestas |
| `address` | `CharField(255)` | Gatvės adresas |
| `role` | `CharField(20)` | Rolė: `client`, `manager`, `admin`, `staff` |
| `is_legal_entity` | `BooleanField` | Ar juridinis asmuo? |
| `company_name` | `CharField(255)` | Įmonės pavadinimas |
| `company_code` | `CharField(30)` | Įmonės kodas |
| `company_vat_code` | `CharField(30)` | PVM kodas |
| `company_address` | `CharField(255)` | Juridinis adresas |

**Properties:**
- `billing_name` → grąžina įmonės pavadinimą (juridinis) arba vardą/pavardę (fizinis)
- `billing_address` → grąžina juridinį arba fizinį adresą

---

#### `SiteSettings` (`main/models.py`)

Singleton modelis puslapio nustatymams. Visada egzistuoja tik vienas įrašas (pk=1).

| Laukas | Tipas | Aprašymas |
|--------|-------|-----------|
| `background_image` | `ImageField(upload_to='settings/')` | Pagrindinis hero fono paveikslėlis |
| `created_at` | `DateTimeField(auto_now_add)` | Sukūrimo laikas |
| `updated_at` | `DateTimeField(auto_now)` | Atnaujinimo laikas |

**Klasės metodai:**
- `SiteSettings.load()` → `get_or_create(pk=1)` – grąžina singleton objektą

---

#### Pagalbinės funkcijos (`main/models.py`)

```python
get_rotating_background_urls() -> list[str]
```
Ieško failų `media/settings/rotating/background_1.jpg` … `background_5.jpg` (su visais leistinais plėtiniais) ir grąžina URL sąrašą.

```python
save_rotating_background(slot: int, uploaded_file) -> None
```
Išsaugo įkeltą paveikslėlį atitinkamame slotyje (1–5), ištrina seną.

```python
get_hero_rotation_settings() -> dict
```
Nuskaito `media/settings/rotating/rotation_config.json` ir grąžina `{'enabled': bool, 'interval_seconds': int}`.

```python
save_hero_rotation_settings(enabled: bool, interval_seconds: int) -> None
```
Išsaugo rotacijos nustatymus į JSON failą.

---

### 3.2 `orders` app

#### `Order` (`orders/models.py`)

Pagrindinis užsakymo modelis.

| Laukas | Tipas | Aprašymas |
|--------|-------|-----------|
| `client` | `ForeignKey(User, related_name='client_orders')` | Užsakymą sukūręs klientas |
| `manager` | `ForeignKey(User, null=True, related_name='managed_orders')` | Priskirtas vadybininkas |
| `created_at` | `DateTimeField(auto_now_add)` | Sukūrimo data/laikas |
| `deadline` | `DateField(null=True)` | Atlikimo terminas |
| `status` | `CharField(20)` | `new`, `in_progress`, `done`, `cancelled` |
| `manager_comment` | `TextField` | Vadybininko komentaras klientui |
| `pdf_file` | `FileField(upload_to='invoices/')` | Sugeneruota PDF sąskaita |
| `is_deleted` | `BooleanField(default=False)` | Soft delete žymė |
| `deleted_at` | `DateTimeField(null=True)` | Pašalinimo laikas |

**Properties:**
- `is_overdue` → `True` jei `deadline < šiandien` ir status ≠ `done`
- `overdue_days` → kiek dienų vėluoja
- `subtotal` → suma be PVM (suma iš visų `OrderItem`)
- `vat_amount` → PVM suma (21%)
- `total_with_vat` → bendra suma su PVM
- `total_price` → alias į `total_with_vat` (suderinamumas)

**Metodai:**
- `assign_manager()` → automatiškai priskiria vadybininką, turintį mažiausiai aktyvių užsakymų
- `soft_delete()` → pažymi `is_deleted=True` ir įrašo `deleted_at`
- `_money(value)` → statinis metodas, suapvalina iki 2 decimal

---

#### `OrderItem` (`orders/models.py`)

Užsakymo eilutė (viena paslauga ir kiekis).

| Laukas | Tipas | Aprašymas |
|--------|-------|-----------|
| `order` | `ForeignKey(Order, related_name='items')` | Tėvinis užsakymas |
| `service` | `ForeignKey(Service)` | Pasirinkta paslauga |
| `quantity` | `DecimalField(10,2)` | Kiekis |
| `custom_price` | `DecimalField(10,2, null=True)` | Pasirinktinė kaina (perrašo paslaugos kainą) |

**Properties:**
- `unit_price` → `custom_price` arba `service.price`
- `total_price` → `unit_price × quantity`

---

### 3.3 `services` app

#### `ServiceCategory` (`services/models.py`)

Paslaugų kategorija (pvz. „Grindys", „Langai").

| Laukas | Tipas | Aprašymas |
|--------|-------|-----------|
| `name` | `CharField(100, unique)` | Kategorijos pavadinimas |

---

#### `Service` (`services/models.py`)

Viena paslauga kataloge.

| Laukas | Tipas | Aprašymas |
|--------|-------|-----------|
| `category` | `ForeignKey(ServiceCategory, related_name='services')` | Kategorija |
| `name` | `CharField(200)` | Paslaugos pavadinimas |
| `description` | `TextField(null=True)` | Aprašymas |
| `unit` | `CharField(10)` | Matavimo vnt: `m2`, `m`, `vnt`, `h`, `task` |
| `price` | `DecimalField(10,2)` | Vieneto kaina (EUR) |

---

### 3.4 `reviews` app

#### `Review` (`reviews/models.py`)

Kliento atsiliepimas apie paslaugas.

| Laukas | Tipas | Aprašymas |
|--------|-------|-----------|
| `user` | `ForeignKey(User, related_name='reviews')` | Atsiliepimo autorius |
| `rating` | `PositiveSmallIntegerField` | Įvertinimas 1–5 |
| `content` | `HTMLField` (TinyMCE) | Atsiliepimo tekstas (HTML) |
| `photo` | `ImageField(upload_to='reviews/')` | Nuotrauka (max 2 MB, JPG/PNG) |
| `video_url` | `URLField(null=True)` | YouTube nuoroda |
| `video_file` | `FileField(upload_to='reviews/videos/')` | Video failas (draudžiamas per `clean()`) |
| `created_at` | `DateTimeField(auto_now_add)` | Sukūrimo data |
| `is_approved` | `BooleanField(default=True)` | Patvirtinimas |

**Validacijos (`clean()`):**
- Nuotrauka ≤ 2 MB
- Tik JPG/PNG plėtiniai
- Video failai negalimi (tik YouTube URL)
- Tik YouTube domenai

---

### 3.5 `gallery` app

#### `GalleryItem` (`gallery/models.py`)

Galerijos įrašas (nuotrauka, YouTube/Vimeo, TikTok ar video failas).

| Laukas | Tipas | Aprašymas |
|--------|-------|-----------|
| `title` | `CharField(200)` | Pavadinimas |
| `media_type` | `CharField(20)` | `photo`, `video_url`, `tiktok_url`, `video_file` |
| `image` | `ImageField(upload_to='gallery/')` | Nuotrauka |
| `video_url` | `URLField(null=True)` | YouTube/Vimeo/TikTok nuoroda |
| `video_file` | `FileField(upload_to='gallery/videos/')` | Video failas |
| `content` | `HTMLField` (TinyMCE) | Aprašymas |
| `order` | `PositiveIntegerField(default=0)` | Rodymo eilės tvarka |
| `is_published` | `BooleanField(default=True)` | Ar rodomas viešai? |
| `created_at` | `DateTimeField(auto_now_add)` | Sukūrimo laikas |
| `uploaded_by` | `ForeignKey(User, null=True)` | Kas įkėlė |

**Validacijos (`clean()`):**
- `photo` tipo → būtina `image`
- `video_file` tipo → būtinas failas
- `video_url` tipo → URL iš YouTube arba Vimeo
- `tiktok_url` tipo → URL iš TikTok su `/video/` kelyje

**Properties:**
- `embed_video_url` → TikTok nuorodai konvertuoja į `embed/v3/{video_id}` formatą

---

## 4. Modelių ryšiai

```
User (django.contrib.auth)
 ├─── Profile (OneToOne)          ← main
 ├─── Review (FK, related='reviews')  ← reviews
 ├─── GalleryItem (FK, related_name nenurodyta)  ← gallery
 ├─── Order (FK, related='client_orders')  ← orders
 └─── Order (FK, related='managed_orders') ← orders (vadybininkas)

ServiceCategory
 └─── Service (FK, related='services')   ← services

Order
 └─── OrderItem (FK, related='items')    ← orders
      └─── Service (FK)                  ← services
```

---

## 5. Views (rodiniai) ir funkcijos

### 5.1 `main/views.py`

| Funkcija | URL | Aprašymas |
|----------|-----|-----------|
| `index(request)` | `/` | Pradžios puslapis su hero fonu ir rotacijos nustatymais |
| `contact_view(request)` | `/contact/` | Kontaktų puslapis |
| `login_view(request)` | `/login/` | Prisijungimo forma (POST: `authenticate` + `login`) |
| `logout_view(request)` | `/logout/` | Atsijungimas |
| `register_view(request)` | `/register/` | Registracijos forma |
| `profile_view(request)` | `/profile/` | Profilio peržiūra (reikia prisijungimo) |
| `profile_edit_view(request)` | `/profile/edit/` | Profilio redagavimas |

---

### 5.2 `orders/views.py`

| Funkcija | URL | Aprašymas |
|----------|-----|-----------|
| `create_order(request)` | `/orders/create/` | Naujo užsakymo kūrimas (tik klientui) |
| `order_list(request)` | `/orders/list/` | Užsakymų sąrašas (filtruojamas pagal rolę) |
| `order_detail(request, order_id)` | `/orders/<id>/` | Vieno užsakymo detalės |
| `edit_order(request, order_id)` | `/orders/<id>/edit/` | Užsakymo redagavimas (manager/admin) |
| `delete_order(request, order_id)` | `/orders/<id>/delete/` | Soft delete (POST only) |
| `restore_order(request, order_id)` | `/orders/<id>/restore/` | Atkurti pašalintą (tik admin) |
| `order_change_status(request, order_id, new_status)` | `/orders/<id>/status/<status>/` | Statuso keitimas |
| `client_dashboard(request)` | `/orders/client/` | Kliento cruscotto statistika |
| `manager_dashboard(request)` | `/orders/manager/` | Vadybininko cruscotto |
| `admin_dashboard(request)` | `/orders/admin/` | Administratoriaus cruscotto |
| `download_invoice(request, order_id)` | `/orders/invoice/<id>/` | PDF sąskaitos generavimas ir parsisiuntimas |
| `load_services(request)` | `/orders/load-services/` | AJAX: paslaugos pagal kategoriją (JSON) |

**Pagalbinė funkcija:**
```python
_apply_order_filters(queryset, status=None, q='') -> QuerySet
```
Filtruoja užsakymų queryset pagal statusą ir paieškos eilutę (klientas arba ID).

---

### 5.3 `services/views.py`

| Funkcija | URL | Aprašymas |
|----------|-----|-----------|
| `services_home(request)` | `/services/` | Paslaugų sąrašas su kategorijomis (accordion) |

---

### 5.4 `reviews/views.py`

| Funkcija / Klasė | URL | Aprašymas |
|------------------|-----|-----------|
| `review_list(request)` | `/reviews/` | Atsiliepimų sąrašas su statistika |
| `ReviewCreateView` (CBV) | `/reviews/create/` | Atsiliepimo kūrimas (tik klientas) |
| `ReviewUpdateView` (CBV) | `/reviews/<id>/edit/` | Atsiliepimo redagavimas (tik staff/superuser) |
| `ReviewDeleteView` (CBV) | `/reviews/<id>/delete/` | Atsiliepimo trynimas (tik staff/superuser) |

---

### 5.5 `gallery/views.py`

| Funkcija | URL | Aprašymas |
|----------|-----|-----------|
| `gallery_home(request)` | `/gallery/` | Galerija su puslapiavimo blokais (9 per puslapį) |

---

## 6. Formos

### `main/forms.py`

#### `RegisterForm`
- Laukai: `username`, `email`, `password`, `password2`
- Validacija: slaptažodžiai turi sutapti

#### `ProfileEditForm`
- Laukai: `avatar`, `bio`, `phone`, `city`, `address`, `is_legal_entity`, `company_name`, `company_code`, `company_vat_code`, `company_address` + `first_name`, `last_name`, `email` (iš User)
- `save()` išsaugo ir User, ir Profile
- Jei `is_legal_entity=False` → įmonės laukai išvalomi

---

### `orders/forms.py`

#### `OrderCreateForm`
- Laukai: `deadline`, `category` (neįrašomas), `items_json` (paslėptas)
- `clean_items_json()` → parsuoja JSON masyvą, validuoja kiekius ir ID

#### `OrderEditForm`
- Laukai: `deadline`, `status`, `manager`, `manager_comment`
- Naudoja Bootstrap 5 widget'us

---

### `reviews/forms.py`

#### `ReviewForm`
- Laukai: `rating` (1–5 select), `content` (textarea)
- `clean_content()` → tekstas negali būti tuščias

---

## 7. Admin konfigūracija

### `main/admin.py`

- **`ProfileAdmin`** – sąraše: user, role, phone, city; filtrai: role, city
- **`SiteSettingsAdmin`** – singleton; galima įkelti iki 5 rotacinių fonų, nustatyti intervalą ir įjungti/išjungti rotaciją; `rotating_background_preview` rodo miniatūras; išsaugojant iškviečia `save_rotating_background` ir `save_hero_rotation_settings`

### `orders/admin.py`

- **`OrderAdmin`** – inline: OrderItem; sąraše: id, client, manager, status, created_at, deadline, is_overdue
- **`OrderItemInline`** – tabular inline su extra=1

---

## 8. URL struktūra

```
/                        ← main/urls.py (home)
/contact/
/login/
/logout/
/register/
/profile/
/profile/edit/
/password-change/
/password-change/done/

/admin/                  ← Django admin
/i18n/                   ← Kalbos perjungimas
/set-language/           ← set_language view
/tinymce/                ← TinyMCE API

/gallery/                ← gallery/urls.py
/orders/...              ← orders/urls.py
/reviews/...             ← reviews/urls.py
/services/               ← services/urls.py
```

---

## 9. Šablonai (Templates)

### `main/templates/main/`

| Failas | Paskirtis |
|--------|-----------|
| `base.html` | Pagrindinis šablonas – `<html>`, `<head>`, navbar, footer, Bootstrap 5, dark mode |
| `navbar.html` | Navigacijos juosta (include) – rolė sąlyginiai meniu, kalbos keitimas |
| `footer.html` | Apatinė juosta (include) |
| `index.html` | Pradžios puslapis – hero sekcija su rotaciniu fonu, features sekcija |
| `contact.html` | Kontaktų puslapis su įmonės rekvizitais |
| `accounts/profile.html` | Profilio peržiūra |
| `accounts/profile_edit.html` | Profilio redagavimo forma |
| `registration/login.html` | Prisijungimo forma |
| `registration/register.html` | Registracijos forma |
| `registration/password_change_form.html` | Slaptažodžio keitimas |
| `registration/password_change_done.html` | Patvirtinimas |
| `admin/base_site.html` | Pasirinktinis Django admin stilius |

### `orders/templates/orders/`

| Failas | Paskirtis |
|--------|-----------|
| `order_form.html` | Naujo užsakymo kūrimo forma (JavaScript paslaugų eilutėms) |
| `order_edit.html` | Užsakymo redagavimas (JavaScript eilutėms) |
| `order_list.html` | Užsakymų sąrašas su filtravimas/paginacija |
| `order_detail.html` | Vieno užsakymo detalios informacijos rodinys |
| `invoice.html` | PDF sąskaitos-faktūros šablonas (WeasyPrint) |
| `client_dashboard.html` | Kliento cruscotto |
| `manager_dashboard.html` | Vadybininko cruscotto |
| `admin_dashboard.html` | Administratoriaus cruscotto |

### `services/templates/services/`
- `services_list.html` – paslaugų accordion sąrašas pagal kategorijas

### `reviews/templates/reviews/`
- `review_list.html` – atsiliepimų sąrašas su statistika ir forma
- `review_form.html` – atsiliepimo redagavimo forma

### `gallery/templates/gallery/`
- `gallery_list.html` – galerija su puslapiavimo blokais

---

## 10. Statiniai failai (Static)

### CSS

| Failas | Paskirtis |
|--------|-----------|
| `static/main/css/styles.css` | Pagrindinis CSS (dark mode, hero sekcija, navbar, kortelės, paginacija) |
| `static/main/css/invoice.css` | PDF sąskaitos stilius (WeasyPrint) |

### Paveikslėliai

| Failas | Paskirtis |
|--------|-----------|
| `static/main/img/logo.png` | H-Pro logotipas |
| `static/main/img/default-avatar.png` | Numatytasis avataro paveikslėlis |
| `static/main/img/flags/lt.svg` | Lietuvos vėliavėlė (kalbai) |
| `static/main/img/flags/en.svg` | Didžiosios Britanijos vėliavėlė |
| `static/main/img/flags/ru.svg` | Rusijos vėliavėlė |

### Admin CSS

- `static/main/admin/css/premium_admin.css` – pasirinktinis Django admin stilius (nurodyta `settings.ADMIN_CSS`)

---

## 11. JavaScript funkcionalumas

JavaScript kodas yra tiesiogiai šablonuose (`<script>` blokai), nenaudojami atskiri `.js` failai.

### `order_form.html` / `order_edit.html`

Dinamiškas paslaugų eilučių valdymas:

| Funkcija | Aprašymas |
|----------|-----------|
| `fetchServices(categoryId)` | AJAX GET `/orders/load-services/?category_id=X` → užpildo paslaugų `<select>` |
| `addRow()` | Prideda naują eilutę su paslauga, kiekiu, kaina |
| `removeRow(btn)` | Pašalina eilutę iš lentelės |
| `updatePrice(select)` | Atnaujina kainos lauką pagal pasirinktą paslaugą |
| `recalcTotal()` | Perskaičiuoja bendrą sumą be PVM realiuoju laiku |
| `serializeItems()` | Serializuoja eilutes į JSON ir įrašo į `items_json` paslėptą lauką prieš submit |

### `index.html`

Hero fono rotacija:

| Funkcija | Aprašymas |
|----------|-----------|
| Hero slider JS | Cikliškai keičia `background-image` iš `hero_background_urls` sąrašo kas `hero_rotation_interval_ms` ms (jei `hero_rotation_enabled=True`) |

### Bendra

- **Dark mode toggle**: perjungia CSS klasę ir saugo parinktį `localStorage` (`data-bs-theme`)
- **Bootstrap 5**: modalai, dropdown'ai, accordion, tooltips – naudojamas per CDN

---

## 12. Template Tags (Šablonų žymos)

### `main/templatetags/role_badges.py`

```python
{% load role_badges %}

{% get_or_create_profile user %}
# Grąžina Profile objektą (arba sukuria naują). Sinchronizuoja rolę superuser/staff vartotojams.

{% role_badge role %}
# Grąžina Bootstrap badge HTML: <span class="badge bg-{color}">{label}</span>
# Spalvos: client=success, manager=primary, admin=danger, staff=warning
```

---

## 13. Signals (Signalai)

### `main/signals.py`

```python
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    # Sukuria Profile automatiškai kuriant naują User.
    # Jei is_superuser arba is_staff → role='admin', kitaip role='client'

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    # Automatiškai išsaugo profilį išsaugant User.
    # Jei superuser/staff → priverstinai nustato role='admin'
```

Signal'ai registruojami `MainConfig.ready()` metode (`main/apps.py`).

---

## 14. Context Processors (Konteksto procesoriai)

### `main/context_processors.py`

```python
def company_info(request):
    return {'company_info': settings.COMPANY_INFO}
```

Visur šablonuose pasiekiamas `{{ company_info.name }}`, `{{ company_info.email }}` ir t.t.

---

## 15. Sąskaitos-faktūros (Invoice) generavimas

### Proceso aprašymas

1. **Vartotojas** spaudžia „Atsisiųsti sąskaitą" → `download_invoice(request, order_id)` view
2. **View** kviečia `generate_invoice_pdf(order)` iš `orders/utils/pdf.py`
3. **PDF generavimas:**
   ```
   generate_invoice_pdf(order):
     a. Sugeneruoja sąskaitos numerį: "h-pro-online Nr.{order.id:06d}"
     b. Renderia HTML iš šablono: orders/invoice.html
        - kontekstas: order, items, company (iš settings.COMPANY_INFO), invoice_number
     c. Patikrina ar egzistuoja static/css/invoice.css (CSS stilius)
     d. WeasyPrint HTML(string=html).write_pdf(target=media/invoices/invoice_{id}.pdf)
     e. Grąžina santykinį kelią "invoices/invoice_{id}.pdf"
   ```
4. **View** grąžina `FileResponse` su PDF failu (`application/pdf`)
5. **Sąskaitos numeris:** `h-pro-online Nr.000001` (6 skaitmenys su nuliais)

### Sąskaitos turinys (`invoice.html`)

- **Pardavėjo rekvizitai:** iš `settings.COMPANY_INFO` (pavadinimas, kodas, PVM, bankas, sąskaita, telefonas, el. paštas)
- **Pirkėjo rekvizitai:** iš `order.client.profile` (`billing_name`, `billing_address`, telefonas)
- **Paslaugų lentelė:** kiekvienas `OrderItem` – pavadinimas, kiekis, vieneto kaina, suma
- **Sumos:** be PVM (`subtotal`), PVM 21% (`vat_amount`), su PVM (`total_with_vat`)
- **Parašų laukai:** pardavėjas + pirkėjas
- Išrašymo data (šiandien), valiuta EUR

### Naudojama biblioteka: **WeasyPrint**

WeasyPrint konvertuoja HTML + CSS į PDF serverio pusėje. Konfigūracija:
```python
WEASYPRINT_BASEURL = BASE_DIR  # settings.py – bazinis URL CSS/media failams
```

---

## 16. Trečiųjų šalių bibliotekos

| Biblioteka | Versija | Paskirtis |
|------------|---------|-----------|
| `Django` | 5.x | Pagrindinis web framework |
| `django-crispy-forms` | 2.6 | Formos su Bootstrap 5 stiliumi |
| `crispy-bootstrap5` | 2026.3 | Crispy forms Bootstrap 5 template pack |
| `django-tinymce` | 5.0.0 | Rich text (WYSIWYG) redaktorius atsiliepimams ir galerijai |
| `Pillow` | 12.2.0 | Paveikslėlių apdorojimas (ImageField) |
| `WeasyPrint` | (ne requirements.txt) | PDF generavimas iš HTML (sąskaitos) |
| `asgiref` | 3.11.1 | ASGI suderinamumas (Django internals) |
| `sqlparse` | 0.5.5 | SQL užklausų formatavimas (Django debug) |
| `tzdata` | 2026.1 | Laiko zonų duomenys |
| `django-extensions` | 4.1 | Django development praplėtimai |
| Bootstrap 5 | 5.x | CSS/JS framework (CDN per šablonus) |

> **Pastaba:** `weasyprint` nenurodytas `requirements.txt`, tačiau naudojamas `orders/utils/pdf.py`. Reikia įdiegti atskirai: `pip install weasyprint`

---

## 17. Internacionalizacija (i18n)

Sistema palaiko 3 kalbas:

| Kodas | Kalba | Numatytoji? |
|-------|-------|-------------|
| `lt` | Lietuvių | ✅ Taip |
| `en` | English | Ne |
| `ru` | Русский | Ne |

**Konfigūracija (`settings.py`):**
```python
LANGUAGE_CODE = 'lt'
USE_I18N = True
LOCALE_PATHS = [BASE_DIR / 'main' / 'locale']
MIDDLEWARE += ['django.middleware.locale.LocaleMiddleware']
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 31536000  # 1 metai
```

**Vertimų failai:** `main/locale/{lt,en,ru}/LC_MESSAGES/django.po`

**Kalbos perjungimas:** `/set-language/` + `django.views.i18n.set_language` + vėliavėlių mygtukai navbar'e

**Vertimų pildymas:** `_fill_translations.py` (šaknyje) – pagalbinis skriptas, kuris automatiškai užpildo EN ir RU `.po` failus iš žodynų. Paleidimas: `python _fill_translations.py`, tada `cd mysite && python manage.py compilemessages`

---

## 18. Nustatymai (`settings.py`)

### Svarbiausios konstantos

```python
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']
DATABASES = {'default': {'ENGINE': 'sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
WEASYPRINT_BASEURL = BASE_DIR
```

### Įmonės rekvizitai (`COMPANY_INFO`)

```python
COMPANY_INFO = {
    "name": 'H-Pro',
    "full_name": 'UAB "HARLEMO PROJEKTAI"',
    "address": 'Kolektyvo g. 158-1, LT-08350 Vilnius',
    "seller_code": '306148489',
    "vat_code": 'LT100016122613',
    "account_number": 'LT337300010184042606',
    "bank_name": 'SWEDBANK AB',
    "phone": '068965681',
    "email": 'harlemoprojektai@gmail.com',
    "manager": 'Adrianas Panovas',
}
```

Pasiekiama iš visų šablonų per `{{ company_info }}` (konteksto procesorius).

---

## 19. Testavimas

Visi testai yra `tests.py` failuose kiekviename app'e:

| App | Testų klasė | Testuojama |
|-----|-------------|------------|
| `main` | `NavbarOrderLinkTests` | Navbar nuorodos pagal rolę |
| `orders` | `EditOrderLinesTests` | Eilučių redagavimas, teisių tikrinimas, soft delete, restore, filtravimas |
| `orders` | `OrderListPaginationTests` | Puslapiavimas (10 per puslapį) |
| `reviews` | `ReviewFormValidationTests` | Formos validacija |
| `reviews` | `ReviewCrudCbvTests` | CBV teisių tikrinimas |
| `services` | `ServicesAccordionTests` | Accordion HTML generavimas |
| `gallery` | `GalleryPaginationTests` | Puslapiavimas (9 per puslapį, 3-puslapių blokai) |
| `gallery` | `GalleryTikTokTests` | TikTok URL konvertavimas ir validacija |

Paleidimas: `cd mysite && python manage.py test`

---

## 20. Projekto valymas

Peržiūrėjus projektą, **nerasta laikinų ar nereikalingų failų**. Visų `tests.py` failai yra realūs unit testai. `_fill_translations.py` šaknyje yra aktyviai naudojama pagalbinė priemonė.

**Rekomendacija:** `_fill_translations.py` galima perkelti į `tools/` ar `scripts/` katalogą projekto šaknyje, kad projektas atrodytų tvarkingiau:
```
FinPro/
├── tools/
│   └── _fill_translations.py
```

---

## 21. Paleidimas

```bash
# 1. Sukurti virtualią aplinką
python -m venv .venv
.venv\Scripts\activate

# 2. Įdiegti priklausomybes
pip install -r requirements.txt
pip install weasyprint  # papildomai

# 3. Migracijos
cd mysite
python manage.py migrate

# 4. Sukompiliuoti vertimus
python manage.py compilemessages

# 5. Sukurti superuser
python manage.py createsuperuser

# 6. Paleisti serverį
python manage.py runserver
```

Administratoriaus sąsaja: `http://127.0.0.1:8000/admin/`

