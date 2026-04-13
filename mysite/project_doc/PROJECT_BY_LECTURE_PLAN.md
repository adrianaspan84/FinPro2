# FinPro - Projekto suvestine pagal paskaitu plana

> Projektas: **FinPro** (Django)  
> Imone: **UAB "HARLEMO PROJEKTAI" (H-Pro)**  
> Tikslas: parodyti, kaip baigiamajame projekte pritaikytos paskaitu temos

## Naudotos programos ir bibliotekos

- **Python 3.14** - programavimo kalba
- **Django 5.x** - MVC/MVT karkasas (modeliai, views, autentifikacija, admin)
- **SQLite** - duomenu baze (development)
- **Bootstrap 5** - UI komponentai ir responsyvus dizainas
- **django-crispy-forms** + **crispy-bootstrap5** - formu atvaizdavimas
- **django-tinymce** - HTML/WYSIWYG laukai
- **WeasyPrint** - PDF saskaitu generavimas
- **Pillow** - paveiksliuku ikelimas (ImageField)
- **gettext / django i18n** - vertimai (lt/en/ru)

---

## 1) Izanga

**Projekto paskirtis:**
- Klientas kuria uzsakymus, mato statusus, atsisiuncia PDF saskaita.
- Vadybininkas administruoja priskirtus uzsakymus.
- Administratorius mato ir valdo visus uzsakymus, atkuria soft-delete irasus.
- Viesi dalis: paslaugos, galerija, atsiliepimai.

**Pagrindinis verslo srautas:**
`Klientas -> Uzsakymas -> Vadybininko administravimas -> Saskaita PDF -> Atsisiuntimas`

---

## 2) Modeliai

### Naudoti modeliai
- `main.Profile` - vartotojo profilis, role, kontaktai, imones rekvizitai
- `main.SiteSettings` - svetaines hero/fono nustatymai (singleton)
- `services.ServiceCategory` - paslaugu kategorijos
- `services.Service` - paslaugos (kaina, vienetas, aprasas)
- `orders.Order` - uzsakymas (client, manager, status, terminas, soft-delete)
- `orders.OrderItem` - uzsakymo eilute (service, kiekis, kaina)
- `reviews.Review` - atsiliepimai (reitingas, tekstas, foto)
- `gallery.GalleryItem` - galerijos turinys (foto/video/tiktok)

### Modeliu rysiai
- `User (1:1) Profile`
- `User (1:N) Order` kaip `client`
- `User (1:N) Order` kaip `manager`
- `ServiceCategory (1:N) Service`
- `Order (1:N) OrderItem`
- `OrderItem (N:1) Service`
- `User (1:N) Review`

### Svarbios modeliu funkcijos
- `Order.assign_manager()` - auto priskiria vadybininka
- `Order.soft_delete()` - logiskas trynimas
- `Order.is_overdue`, `subtotal`, `vat_amount`, `total_with_vat`
- `OrderItem.unit_price`
- `Profile.billing_name`, `Profile.billing_address`

---

## 3) Administratoriaus svetaine

**Django admin:**
- `main/admin.py` - `ProfileAdmin`, `SiteSettingsAdmin`
- `orders/admin.py` - `OrderAdmin`, `OrderItemInline`
- `services/admin.py` - `ServiceCategoryAdmin`, `ServiceAdmin`

**Custom administravimo paneles (ne tik /admin):**
- `orders/views.py -> admin_dashboard`
- `orders/templates/orders/admin_dashboard.html`
- Filtravimas, paieska, deleted rodymas, statistikos korteles

---

## 4) Sablonai

**Baziniai sablonai:**
- `main/templates/main/base.html`
- `main/templates/main/navbar.html`
- `main/templates/main/footer.html`

**App sablonai:**
- `orders/templates/orders/*.html`
- `services/templates/services/*.html`
- `reviews/templates/reviews/*.html`
- `gallery/templates/gallery/*.html`

**Naudojami include/templatetag sprendimai:**
- `orders/templates/orders/partials/order_table.html`
- `main/templatetags/role_badges.py`
- `orders/templatetags/status_badges.py`

---

## 5) Views

**Function-Based Views (FBV):**
- `main/views.py`: `index`, `contact_view`, `login_view`, `register_view`, `profile_view`
- `orders/views.py`: `create_order`, `order_list`, `order_detail`, `edit_order`, `delete_order`, `restore_order`, `admin_dashboard`, `manager_dashboard`, `client_dashboard`, `download_invoice`, `load_services`
- `services/views.py`: `services_home`, category/service CRUD

**Class-Based Views (CBV):**
- `reviews/views.py`: `ReviewCreateView`, `ReviewUpdateView`, `ReviewDeleteView`

---

## 6) Puslapiavimas, Paieska, Nuotraukos

**Puslapiavimas:**
- `orders/views.py -> order_list` (`Paginator`, 10 irasu)
- `gallery/views.py -> gallery_home` (9 irasai)

**Paieska / filtravimas:**
- `_apply_order_filters(queryset, status, q)` in `orders/views.py`
- Admin dashboard filtrai pagal statusa, q, include_deleted

**Nuotraukos / media:**
- `ImageField` modeliuose (`Profile.avatar`, `Review.photo`, `GalleryItem.image`)
- media katalogas: `mysite/media/`

---

## 7) Autorizacija

- Django auth (`login`, `logout`, `@login_required`)
- Teisiu kontrole pagal role (`client`, `manager`, `admin`, `staff`)
- `PermissionDenied` kai vartotojas neturi teisiu
- Role-based navigation `navbar.html`

---

## 8) Vartotojai II, HTML laukai

**Vartotoju role logika:**
- saugoma `Profile.role`
- signalai: `main/signals.py` (`create_profile`, `save_profile`)

**HTML laukai (rich text):**
- `reviews.models.Review.content` (TinyMCE)
- `gallery.models.GalleryItem.content` (TinyMCE)

---

## 9) Registracija, Formos

**Registracija:**
- `main/forms.py -> RegisterForm`
- `main/views.py -> register_view`

**Profilio formos:**
- `ProfileEditForm` su User + Profile atnaujinimu

**Uzsakymo formos:**
- `orders/forms.py -> OrderCreateForm`, `OrderEditForm`
- JSON eiluciu validacija (`items_json`)

**Atsiliepimu forma:**
- `reviews/forms.py -> ReviewForm`

---

## 10) Vartotojo profilis

- Profilio perziura: `main/templates/main/accounts/profile.html`
- Profilio redagavimas: `profile_edit.html`
- Avataras, kontaktai, juridinio asmens laukai, role badge
- Vartotojo verslo rekvizitai panaudojami saskaitose (`billing_name/address`)

---

## 11) Create, Update, Delete rodiniu klases

**CBV sukurimas/redagavimas/trynimas:**
- `reviews/views.py`: `ReviewCreateView`, `ReviewUpdateView`, `ReviewDeleteView`

**FBV CRUD principai kitose vietose:**
- `orders/views.py`: kurimas, redagavimas, soft-delete, restore
- `services/views.py`: category/service create-edit-delete

---

## 12) Vertimai

- Kalbos: `lt`, `en`, `ru`
- Failai: `main/locale/{lt,en,ru}/LC_MESSAGES/django.po`
- Kompiliavimas: `python manage.py compilemessages`
- Kalbos perjungimas per `navbar` ir `/set-language/`
- Pagalbinis skriptas: `_fill_translations.py`

---

## Papildomai: PDF, testai, kokybe

**PDF saskaita:**
- `orders/utils/pdf.py -> generate_invoice_pdf(order)`
- WeasyPrint + `orders/templates/orders/invoice.html`

**Testai:**
- `main/tests.py`, `orders/tests.py`, `services/tests.py`, `reviews/tests.py`, `gallery/tests.py`
- Testuojami: teises, puslapiavimas, validacija, dashboard elgsena

---

## Trumpa isvada pagal paskaitu plana

Visos 12 paskaitu temu projekte panaudotos praktiskai:
- nuo modeliu ir rysiu,
- iki autorizacijos, formu, CRUD, vertimu,
- su admin valdymu, paieska/puslapiavimu,
- ir papildomu realaus projekto komponentu (PDF, media, role-based dashboard).

Sis dokumentas gali buti naudojamas kaip baigiamojo projekto "atitikties paskaitoms" suvestine.

