import tinymce.models
from django.db import migrations, models


def sync_review_columns(apps, schema_editor):
    connection = schema_editor.connection
    introspection = connection.introspection
    existing_columns = {
        column.name
        for column in introspection.get_table_description(connection.cursor(), 'reviews_review')
    }

    if 'content' not in existing_columns:
        schema_editor.execute(
            "ALTER TABLE reviews_review ADD COLUMN content text NOT NULL DEFAULT ''"
        )

    if 'video_file' not in existing_columns:
        schema_editor.execute(
            "ALTER TABLE reviews_review ADD COLUMN video_file varchar(100) NULL"
        )

    if 'video_url' not in existing_columns:
        schema_editor.execute(
            "ALTER TABLE reviews_review ADD COLUMN video_url varchar(200) NULL"
        )


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(sync_review_columns, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.RemoveField(
                    model_name='review',
                    name='comment',
                ),
                migrations.AddField(
                    model_name='review',
                    name='content',
                    field=tinymce.models.HTMLField(blank=True, verbose_name='Atsiliepimo tekstas'),
                ),
                migrations.AddField(
                    model_name='review',
                    name='video_file',
                    field=models.FileField(blank=True, null=True, upload_to='reviews/videos/', verbose_name='Video failas'),
                ),
                migrations.AddField(
                    model_name='review',
                    name='video_url',
                    field=models.URLField(blank=True, null=True, verbose_name='Video nuoroda'),
                ),
                migrations.AlterField(
                    model_name='review',
                    name='is_approved',
                    field=models.BooleanField(default=True),
                ),
            ],
        ),
    ]
