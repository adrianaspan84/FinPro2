# FinPro – Trumpas projekto aprašymas

> Django projektas | UAB „HARLEMO PROJEKTAI" (H-Pro) | Python 3.14 | Bootstrap 5

---

## Modeliai

| Modelis | App | Ką saugo |
|---------|-----|----------|
| `Profile` | `main` | Vartotojo profilis (rolė, telefonas, adresas, įmonės rekvizitai) |
| `SiteSettings` | `main` | Singleton – hero fono paveikslėlis ir rotacijos nustatymai |
| `ServiceCategory` | `services` | Paslaugų kategorija (pvz. „Grindys") |
| `Service` | `services` | Viena paslauga (pavadinimas, kaina, matavimo vnt.) |
| `Order` | `orders` | Užsakymas (klientas, vadybininkas, statusas, terminas, PDF) |
| `OrderItem` | `orders` | Užsakymo eilutė (paslauga × kiekis × kaina) |
| `Review` | `reviews` | Kliento atsiliepimas (įvertinimas, tekstas, nuotrauka) |
| `GalleryItem` | `gallery` | Galerijos įrašas (nuotrauka / YouTube / Vimeo / TikTok) |

---

## Modelių ryšiai

```
User ──(1:1)──► Profile
User ──(1:N)──► Order (as client)
User ──(1:N)──► Order (as manager)
User ──(1:N)──► Review
ServiceCategory ──(1:N)──► Service
Order ──(1:N)──► OrderItem ──(N:1)──► Service
```

---

## Pagrindinės Python funkcijos

### `main/models.py`

| Funkcija | Paskirtis |
|----------|-----------|
| `get_rotating_background_urls()` | Grąžina fono paveikslėlių URL sąrašą (iki 5) |
| `save_rotating_background(slot, file)` | Išsaugo rotacinį foną į nurodyto sloto failą |
| `get_hero_rotation_settings()` | Nuskaito rotacijos nustatymus iš JSON failo |
| `save_hero_rotation_settings(enabled, interval)` | Išsaugo rotacijos nustatymus į JSON failą |
| `Profile.billing_name` (property) | Grąžina atsiskaitymo vardą (įmonė arba asmuo) |
| `Profile.billing_address` (property) | Grąžina atsiskaitymo adresą |
| `SiteSettings.load()` | Grąžina singleton SiteSettings objektą |

### `orders/models.py`

| Funkcija | Paskirtis |
|----------|-----------|
| `Order.assign_manager()` | Automatiškai priskiria vadybininką (mažiausiai aktyvių užsakymų) |
| `Order.soft_delete()` | Pažymi užsakymą kaip ištrintą (is_deleted=True) |
| `Order.is_overdue` (property) | True jei terminas praėjęs ir statusas ≠ done |
| `Order.subtotal` (property) | Suma be PVM |
| `Order.vat_amount` (property) | PVM suma (21%) |
| `Order.total_with_vat` (property) | Bendra suma su PVM |
| `OrderItem.unit_price` (property) | Kaina (custom_price arba service.price) |

### `orders/views.py`

| Funkcija | Paskirtis |
|----------|-----------|
| `create_order` | Naujas užsakymas (tik client rolė) |
| `order_list` | Sąrašas (filtruotas pagal rolę + paginacija) |
| `order_detail` | Detalės (tikrinamos teisės) |
| `edit_order` | Redagavimas su JSON eilutėmis (manager/admin) |
| `delete_order` | Soft delete (POST only) |
| `restore_order` | Atkūrimas (tik admin) |
| `admin_dashboard` | Visi užsakymai + statistika + paieška |
| `download_invoice` | PDF generavimas ir parsisiuntimas |
| `load_services` | AJAX – paslaugos pagal kategoriją (JSON) |

### `orders/utils/pdf.py`

| Funkcija | Paskirtis |
|----------|-----------|
| `generate_invoice_pdf(order)` | HTML → PDF per WeasyPrint; išsaugo į `media/invoices/` |

### `main/signals.py`

| Signalas | Paskirtis |
|----------|-----------|
| `create_profile` (post_save User) | Automatiškai sukuria Profile kuriant User |
| `save_profile` (post_save User) | Sinchronizuoja rolę (superuser → admin) |

---

## Views trumpai

| View | URL | Rolė |
|------|-----|------|
| `index` | `/` | visi |
| `login_view` | `/login/` | visi |
| `register_view` | `/register/` | visi |
| `profile_view` | `/profile/` | prisijungę |
| `services_home` | `/services/` | visi |
| `gallery_home` | `/gallery/` | visi |
| `review_list` | `/reviews/` | visi |
| `ReviewCreateView` | `/reviews/create/` | client |
| `create_order` | `/orders/create/` | client |
| `order_list` | `/orders/list/` | prisijungę |
| `client_dashboard` | `/orders/client/` | client |
| `manager_dashboard` | `/orders/manager/` | manager/admin |
| `admin_dashboard` | `/orders/admin/` | admin |
| `download_invoice` | `/orders/invoice/<id>/` | client/manager/admin |

---

## Naudojamos programos ir bibliotekos

| Programa | Paskirtis |
|----------|-----------|
| **Django 5** | Pagrindinis web framework (ORM, views, forms, admin, i18n) |
| **WeasyPrint** | PDF sąskaitų generavimas iš HTML šablono |
| **TinyMCE** (`django-tinymce`) | Rich text redaktorius atsiliepimams ir galerijai |
| **django-crispy-forms** + `crispy-bootstrap5` | Bootstrap 5 formos be rankinio CSS |
| **Pillow** | Paveikslėlių įkėlimas (ImageField) |
| **Bootstrap 5** (CDN) | Responsive UI – grid, modalai, accordion, badges |
| **SQLite** | Duomenų bazė (development) |

---

## Sąskaitos-faktūros kūrimas

```
Klientas → [Atsisiųsti PDF] → download_invoice() view
  └─► generate_invoice_pdf(order)
        1. Sugeneruoja numerį:  "h-pro-online Nr.000001"
        2. Renderia HTML:       orders/invoice.html
           (duomenys: order, items, COMPANY_INFO iš settings)
        3. Taiko CSS:           static/css/invoice.css  
        4. WeasyPrint → PDF:    media/invoices/invoice_{id}.pdf
        5. Grąžina FileResponse su PDF
```

**Sąskaitoje yra:**
- Pardavėjo rekvizitai (iš `settings.COMPANY_INFO`)
- Pirkėjo rekvizitai (iš `Profile.billing_name` / `billing_address`)
- Paslaugų lentelė su kiekiais ir kainomis
- Sumos: be PVM / PVM 21% / su PVM
- Parašų laukai

---

## Vartotojų rolės

| Rolė | Gali |
|------|------|
| `client` | Kurti užsakymus, žiūrėti savo, rašyti atsiliepimus, siųstis sąskaitas |
| `manager` | Valdyti priskirtus užsakymus (redaguoti, keisti statusą, soft delete) |
| `admin` | Visos teisės + atkurti ištrintus + admin panelė |
| `staff` | Redaguoti/trinti atsiliepimus |

---

## i18n (daugiakalbystė)

- **Kalbos:** `lt` (numatyta), `en`, `ru`
- **Vertimų failai:** `main/locale/{lt,en,ru}/LC_MESSAGES/django.po`
- **Kalbos keitimas:** vėliavėlių mygtukai navbar'e → `/set-language/`
- **Vertimų pildymas:** `python _fill_translations.py` → `python manage.py compilemessages`

