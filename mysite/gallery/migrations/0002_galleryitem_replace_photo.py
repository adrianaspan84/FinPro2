# Generated manually to align migration state with the current GalleryItem model.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import tinymce.models


CREATE_GALLERYITEM_SQL = """
CREATE TABLE IF NOT EXISTS gallery_galleryitem (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    title varchar(200) NOT NULL,
    media_type varchar(20) NOT NULL,
    image varchar(100) NULL,
    video_url varchar(200) NULL,
    video_file varchar(100) NULL,
    content TEXT NOT NULL,
    "order" integer unsigned NOT NULL,
    is_published bool NOT NULL,
    created_at datetime NOT NULL,
    uploaded_by_id INTEGER NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED
);
"""

CREATE_GALLERYITEM_UPLOADED_BY_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS gallery_galleryitem_uploaded_by_id_6ee187f9
ON gallery_galleryitem (uploaded_by_id);
"""

DROP_OLD_PHOTO_SQL = "DROP TABLE IF EXISTS gallery_photo;"
DROP_GALLERYITEM_SQL = "DROP TABLE IF EXISTS gallery_galleryitem;"
DROP_GALLERYITEM_INDEX_SQL = "DROP INDEX IF EXISTS gallery_galleryitem_uploaded_by_id_6ee187f9;"


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(CREATE_GALLERYITEM_SQL, DROP_GALLERYITEM_SQL),
                migrations.RunSQL(CREATE_GALLERYITEM_UPLOADED_BY_INDEX_SQL, DROP_GALLERYITEM_INDEX_SQL),
                migrations.RunSQL(DROP_OLD_PHOTO_SQL, migrations.RunSQL.noop),
            ],
            state_operations=[
                migrations.CreateModel(
                    name='GalleryItem',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('title', models.CharField(max_length=200, verbose_name='Pavadinimas')),
                        ('media_type', models.CharField(choices=[('photo', 'Nuotrauka'), ('video_url', 'Video nuoroda (YouTube/Vimeo)'), ('tiktok_url', 'TikTok video nuoroda'), ('video_file', 'Video failas')], default='photo', max_length=20, verbose_name='Medijos tipas')),
                        ('image', models.ImageField(blank=True, null=True, upload_to='gallery/', verbose_name='Nuotrauka')),
                        ('video_url', models.URLField(blank=True, help_text='YouTube, Vimeo arba TikTok nuoroda (pagal pasirinktą medijos tipą)', null=True, verbose_name='Video nuoroda')),
                        ('video_file', models.FileField(blank=True, null=True, upload_to='gallery/videos/', verbose_name='Video failas')),
                        ('content', tinymce.models.HTMLField(blank=True, verbose_name='Aprašymas / Turinys')),
                        ('order', models.PositiveIntegerField(default=0, verbose_name='Eilės tvarka')),
                        ('is_published', models.BooleanField(default=True, verbose_name='Viešas')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Įkėlė')),
                    ],
                    options={
                        'verbose_name': 'Galerijos įrašas',
                        'verbose_name_plural': 'Galerija',
                        'ordering': ['order', '-created_at'],
                    },
                ),
                migrations.DeleteModel(
                    name='Photo',
                ),
            ],
        ),
    ]

