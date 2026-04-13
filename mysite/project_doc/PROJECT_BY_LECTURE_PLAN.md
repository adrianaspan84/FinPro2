# FinPro - Baigiamojo projekto atitiktis paskaitų planui

> Projektas: **FinPro**  
> Įmonė: **UAB "HARLEMO PROJEKTAI" (H-Pro)**  
> Technologinė bazė: **Django 5, Python 3.14, SQLite, Bootstrap 5**

## 1. Dokumento paskirtis

Šis dokumentas pateikia aiškų atitikimą tarp paskaitų plano temų ir realiai įgyvendintų sprendimų projekte `FinPro`.

Tikslas:
- parodyti, kur kiekviena paskaitos tema panaudota projekte,
- įvardyti konkrečius failus, modelius ir funkcijas,
- pagrįsti praktinę kiekvieno sprendimo vertę.

---

## 2. Naudotos programos ir bibliotekos

- `Python 3.14` - pagrindinė programavimo kalba
- `Django 5.x` - MVT architektūra, ORM, autentifikacija, administravimo modulis, formos, i18n
- `SQLite` - duomenų bazė (development aplinkoje)
- `Bootstrap 5` - vartotojo sąsajos struktūra ir responsyvus dizainas
- `django-crispy-forms` + `crispy-bootstrap5` - patogus formų atvaizdavimas
- `django-tinymce` - HTML/WYSIWYG laukų palaikymas
- `WeasyPrint` - PDF sąskaitų generavimas
- `Pillow` - `ImageField` palaikymas
- `gettext` / Django i18n - daugiakalbystė (`lt`, `en`, `ru`)

---

## 3. Projekto modeliai ir ryšiai

### Pagrindiniai modeliai
- `main.Profile`
- `main.SiteSettings`
- `services.ServiceCategory`
- `services.Service`
- `orders.Order`
- `orders.OrderItem`
- `reviews.Review`
- `gallery.GalleryItem`

### Esminiai ryšiai
- `User (1:1) Profile`
- `User (1:N) Order` kaip klientas
- `User (1:N) Order` kaip vadybininkas
- `ServiceCategory (1:N) Service`
- `Order (1:N) OrderItem`
- `OrderItem (N:1) Service`
- `User (1:N) Review`

### Svarbiausia verslo logika modeliuose
- `Order.assign_manager()` - automatinis vadybininko priskyrimas
- `Order.soft_delete()` - loginis trynimas
- `Order.is_overdue`, `subtotal`, `vat_amount`, `total_with_vat`
- `OrderItem.unit_price`
- `Profile.billing_name`, `Profile.billing_address`

---

## 4. Atitikties matrica pagal paskaitas

| Paskaita | Kur realizuota projekte | Pagrindiniai pavadinimai / funkcijos | Praktinis rezultatas |
|---|---|---|---|
| 1. Įžanga | `main/views.py`, `main/templates/main/index.html` | `index`, hero sekcija, role-based CTA | Pradinis puslapis su aiškia projekto paskirtimi |
| 2. Modeliai | `main/models.py`, `orders/models.py`, `services/models.py`, `reviews/models.py`, `gallery/models.py` | `Profile`, `Order`, `OrderItem`, `Service`, `Review`, `GalleryItem` | Pilna duomenų schema su realiais ryšiais |
| 3. Administratoriaus svetainė | `main/admin.py`, `orders/admin.py`, `services/admin.py`, `orders/views.py` | `ProfileAdmin`, `OrderAdmin`, `admin_dashboard` | Administratorius valdo duomenis per Django admin ir custom panelę |
| 4. Šablonai | `main/templates/main/base.html`, `navbar.html`, app šablonai | `base`, `include`, role badge, status badge | Vieninga UI architektūra visame projekte |
| 5. Views | `main/views.py`, `orders/views.py`, `services/views.py`, `reviews/views.py` | `order_list`, `order_detail`, `create_order`, `admin_dashboard`, `ReviewCreateView` | Įgyvendintas pilnas vartotojo veiksmų ciklas |
| 6. Puslapiavimas, paieška, nuotraukos | `orders/views.py`, `gallery/views.py`, modelių `ImageField` | `Paginator`, `_apply_order_filters`, `avatar/photo/image` | Patogus didesnio duomenų kiekio valdymas |
| 7. Autorizacija | Django auth + role tikrinimai views | `@login_required`, `PermissionDenied`, role-based logika | Apsaugotos funkcijos pagal vartotojo teises |
| 8. Vartotojai II, HTML laukai | `main/signals.py`, `reviews/models.py`, `gallery/models.py` | `create_profile`, `save_profile`, TinyMCE `content` | Automatinis profilio valdymas ir rich text turinys |
| 9. Registracija, formos | `main/forms.py`, `orders/forms.py`, `reviews/forms.py` | `RegisterForm`, `ProfileEditForm`, `OrderCreateForm`, `OrderEditForm` | Kontroliuojamas duomenų įvedimas ir validacija |
| 10. Vartotojo profilis | `main/templates/main/accounts/profile*.html`, `main/views.py` | `profile_view`, `profile_edit_view` | Pilnas profilio peržiūros ir redagavimo scenarijus |
| 11. Create/Update/Delete rodinių klasės | `reviews/views.py`, papildomai FBV kituose app | `ReviewCreateView`, `ReviewUpdateView`, `ReviewDeleteView`; `edit_order`, `delete_order`, `restore_order` | Pritaikyti tiek CBV, tiek FBV CRUD principai |
| 12. Vertimai | `main/locale/*/LC_MESSAGES/django.po`, `_fill_translations.py` | `compilemessages`, `/set-language/`, gettext | Veikianti daugiakalbė sistema (`lt/en/ru`) |

---

## 5. Papildomi komponentai, stiprinantys projektą

### PDF sąskaitos
- Failai: `orders/utils/pdf.py`, `orders/templates/orders/invoice.html`
- Funkcija: `generate_invoice_pdf(order)`
- Vertė: automatizuota komercinių dokumentų generacija

### Dashboard analitika
- Failas: `orders/views.py` (`admin_dashboard`, `manager_dashboard`, `client_dashboard`)
- Rodikliai: nauji, aktyvūs, atlikti, vėluojantys, deleted

### Testavimas
- Failai: `main/tests.py`, `orders/tests.py`, `services/tests.py`, `reviews/tests.py`, `gallery/tests.py`
- Tikrinama: teisės, validacija, puslapiavimas, dashboard elgsena

---

## 6. Trumpa architektūrinė išvada

Projektas pilnai atitinka paskaitų planą ir parodo praktinį visų temų pritaikymą vienoje sistemoje:
- nuo modelių projektavimo ir ryšių,
- iki autentifikacijos, formų, CRUD, paieškos ir puslapiavimo,
- su administravimo valdymu, media ir PDF,
- bei pilna i18n integracija.

`FinPro` yra funkcionalus, testuojamas ir toliau plečiamas Django projektas, tinkamas baigiamajam atsiskaitymui.
