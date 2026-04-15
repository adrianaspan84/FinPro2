# FinPro vieno puslapio špargalkė

## Kas tai?

FinPro yra `Django` pagrindu sukurta paslaugų ir užsakymų valdymo sistema. Ji skirta klientų užsakymams, paslaugų katalogui, vadybininkų darbui, PDF sąskaitoms, galerijai ir atsiliepimams.

## Ką sistema daro?

- Registruoja ir autentifikuoja vartotojus.
- Valdo roles: `client`, `manager`, `admin`, `staff`.
- Leidžia administruoti paslaugų kategorijas ir paslaugas.
- Leidžia klientui kurti užsakymus iš kelių paslaugų.
- Automatiškai priskiria vadybininką.
- Leidžia peržiūrėti, filtruoti, redaguoti ir soft-delete užsakymus.
- Generuoja PDF sąskaitas.
- Rodo galeriją ir klientų atsiliepimus.
- Turi dienos / nakties režimą ir vieningą `glass UI`.

## Naudotos technologijos

- `Python`
- `Django`
- `Bootstrap 5`
- `django-crispy-forms`
- `django-tinymce`
- `Pillow`
- `WeasyPrint`
- `HTML`, `CSS`, `JavaScript`

## Pagrindiniai modeliai

- `Profile` – vartotojo profilis ir rolė.
- `SiteSettings` – bendri svetainės nustatymai.
- `ServiceCategory` – paslaugų grupė.
- `Service` – konkreti paslauga.
- `Order` – užsakymas.
- `OrderItem` – užsakymo eilutė.
- `Review` – kliento atsiliepimas.
- `GalleryItem` – galerijos įrašas.

## Ryšiai tarp lentelių

- `User -> Profile` = `OneToOne`
- `ServiceCategory -> Service` = `OneToMany`
- `User -> Order (client)` = `OneToMany`
- `User -> Order (manager)` = `OneToMany`
- `Order -> OrderItem` = `OneToMany`
- `Service -> OrderItem` = `OneToMany`
- `User -> Review` = `OneToMany`
- `User -> GalleryItem` = `OneToMany`

## Kur naudojami One-to-Many / Many-to-One?

- Viena paslaugų kategorija turi daug paslaugų, o viena paslauga priklauso vienai kategorijai.
- Vienas klientas turi daug užsakymų, o vienas užsakymas priklauso vienam klientui.
- Vienas vadybininkas gali turėti daug užsakymų, o vienas užsakymas turi vieną vadybininką.
- Vienas užsakymas turi daug eilučių, o viena eilutė priklauso vienam užsakymui.
- Viena paslauga gali būti daugelyje užsakymo eilučių, o viena eilutė rodo vieną paslaugą.
- Vienas vartotojas gali parašyti daug atsiliepimų.
- Vienas vartotojas gali įkelti daug galerijos įrašų.

## Svarbiausios funkcijos

- `index()` – pagrindinis puslapis ir hero fonų rotacija.
- `services_home()` – paslaugos pagal grupes.
- `service_list()` / `category_list()` – paslaugų administravimas.
- `create_order()` – užsakymo kūrimas.
- `assign_manager()` – automatinis vadybininko priskyrimas.
- `order_list()` – užsakymų sąrašas ir filtrai.
- `download_invoice()` – PDF sąskaita.
- `review_list()` – atsiliepimų sąrašas ir statistika.
- `gallery_home()` – galerija su puslapiavimu.

## Dizainas / UI

- `Glassmorphism`
- `Blur` efektai
- Neon `navbar`
- Dienos / nakties režimas
- Animacinis fonas tik `index.html`

## Labai trumpas atsakymas, jei kas paklaustų

FinPro yra `Django` sistema, skirta paslaugų katalogui, klientų užsakymams ir vadybininkų administravimui. 
Joje naudojami modeliai `Profile`, `ServiceCategory`, `Service`, `Order`, `OrderItem`, `Review` ir `GalleryItem`. 
Pagrindiniai ryšiai yra `OneToOne` tarp `User` ir `Profile`, bei keli `OneToMany` ryšiai tarp kategorijų, paslaugų, užsakymų ir jų eilučių.
