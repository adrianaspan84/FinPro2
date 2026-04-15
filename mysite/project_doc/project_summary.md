# FinPro projekto santrauka

## Trumpas projekto aprašymas

FinPro yra `Django` pagrindu sukurta vidaus paslaugų ir užsakymų valdymo sistema. Projektas skirtas interjero, apdailos ir susijusių paslaugų administravimui: paslaugų katalogui, klientų užsakymams, vadybininkų paskyrimui, sąskaitų generavimui, galerijai ir atsiliepimams.

## Pagrindinis funkcionalumas

- Vartotojų registracija, prisijungimas, atsijungimas, profilio redagavimas.
- Rolės: `client`, `manager`, `admin`, `staff`.
- Paslaugų kategorijų ir paslaugų CRUD administravimas.
- Viešas puslapis `Paslaugos pagal grupes` su akordeonu.
- Užsakymų kūrimas klientui iš kelių paslaugų eilučių.
- Automatinis vadybininko priskyrimas pagal mažiausią aktyvių užsakymų skaičių.
- Užsakymų filtravimas, peržiūra, redagavimas, soft delete ir atkūrimas.
- PDF sąskaitų generavimas.
- Vieša galerija su nuotraukomis, YouTube/Vimeo/TikTok turiniu ir puslapiavimu.
- Klientų atsiliepimai su vertinimo statistika.
- Dienos / nakties režimas ir bendras `glass UI` dizainas.
- `index.html` hero fonų rotacija iš failų saugyklos.

## Naudotos technologijos ir bibliotekos

- `Python`
- `Django 6`
- `Bootstrap 5`
- `django-crispy-forms`
- `crispy-bootstrap5`
- `django-tinymce`
- `Pillow`
- `WeasyPrint`
- `HTML`, `CSS`, `JavaScript`

## Pagrindiniai modeliai

### `main`

- `Profile`
  - saugo vartotojo rolę, avatarą, kontaktus ir juridinio asmens rekvizitus.
- `SiteSettings`
  - saugo bendrus svetainės nustatymus, pvz. hero foną.

### `services`

- `ServiceCategory`
  - paslaugų grupė.
- `Service`
  - atskira paslauga su kaina, matavimo vienetu ir aprašymu.

### `orders`

- `Order`
  - pagrindinis užsakymas: klientas, vadybininkas, statusas, terminas, PDF sąskaita.
- `OrderItem`
  - užsakymo eilutė: paslauga, kiekis, pasirinktinė kaina.

### `reviews`

- `Review`
  - kliento atsiliepimas su įvertinimu, tekstu ir media.

### `gallery`

- `GalleryItem`
  - galerijos įrašas: nuotrauka, video nuoroda, video failas, aprašymas.

## Svarbiausios funkcijos / logika

- `main.views.index`
  - užkrauna `index` puslapį ir hero fonų rotaciją.
- `services.views.services_home`
  - parodo visas paslaugų kategorijas ir jų paslaugas.
- `services.views.service_list`, `category_list`
  - administravimo sąrašai ir paieška.
- `orders.views.create_order`
  - sukuria užsakymą ir jo eilutes.
- `orders.models.Order.assign_manager`
  - automatiškai priskiria vadybininką.
- `orders.views.order_list`
  - filtruoja ir puslapiuoja užsakymus.
- `orders.views.download_invoice`
  - generuoja ir grąžina PDF sąskaitą.
- `reviews.views.review_list`
  - rodo atsiliepimus ir suvestinę.
- `gallery.views.gallery_home`
  - rodo galeriją su puslapiavimu.

## Ryšiai tarp lentelių

### One-to-One

- `Profile.user -> User`
  - vienas vartotojas turi vieną profilį.

### One-to-Many / Many-to-One

- `ServiceCategory -> Service`
  - viena kategorija turi daug paslaugų.
  - daug paslaugų priklauso vienai kategorijai.

- `User -> Order` per `client`
  - vienas klientas gali turėti daug užsakymų.
  - vienas užsakymas priklauso vienam klientui.

- `User -> Order` per `manager`
  - vienas vadybininkas gali valdyti daug užsakymų.
  - vienas užsakymas gali būti priskirtas vienam vadybininkui.

- `Order -> OrderItem`
  - vienas užsakymas turi daug eilučių.
  - viena eilutė priklauso vienam užsakymui.

- `Service -> OrderItem`
  - viena paslauga gali būti naudojama daugelyje užsakymo eilučių.
  - viena užsakymo eilutė rodo vieną paslaugą.

- `User -> Review`
  - vienas vartotojas gali turėti daug atsiliepimų.
  - vienas atsiliepimas priklauso vienam vartotojui.

- `User -> GalleryItem`
  - vienas vartotojas gali įkelti daug galerijos įrašų.
  - vienas galerijos įrašas turi vieną įkėlusį vartotoją arba `NULL`.

## Trumpa duomenų struktūros logika

- `ServiceCategory` yra katalogo viršus.
- `Service` yra parduodamas vienetas.
- `Order` yra kliento užsakymas.
- `OrderItem` jungia užsakymą su paslauga ir saugo kiekį bei kainą.
- `Profile` išplečia standartinį `User`.
- `Review` ir `GalleryItem` yra viešo turinio moduliai.

## UI / efektai

- Vieningas `glassmorphism` stilius.
- `blur` efektai formoms, lentelėms, kortelėms.
- Dienos / nakties režimas.
- Animuotas hero fonas tik `index.html`.
- Neon efektas `navbar` ir `dropdown` tekstams.
- Puslapiavimas ir galerijos overlay per `JavaScript`.

## Trumpa pristatymo versija

FinPro yra `Django` sistema, skirta paslaugų katalogui, klientų užsakymams, vadybininkų darbui, PDF sąskaitoms, galerijai ir atsiliepimams. Pagrindiniai duomenų modeliai yra `Profile`, `ServiceCategory`, `Service`, `Order`, `OrderItem`, `Review` ir `GalleryItem`. Svarbiausi ryšiai yra `ServiceCategory -> Service`, `User -> Order`, `Order -> OrderItem`, `Service -> OrderItem`, `User -> Review`, `User -> GalleryItem`, o `Profile` su `User` susietas `OneToOne` ryšiu.
