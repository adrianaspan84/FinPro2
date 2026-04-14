from django.db import migrations, models


def add_missing_order_fields(apps, schema_editor):
    connection = schema_editor.connection
    introspection = connection.introspection

    existing_columns = {
        column.name
        for column in introspection.get_table_description(connection.cursor(), 'orders_order')
    }
    order_sql = {
        'deleted_at': "ALTER TABLE orders_order ADD COLUMN deleted_at datetime NULL",
        'is_deleted': "ALTER TABLE orders_order ADD COLUMN is_deleted bool NOT NULL DEFAULT 0",
        'manager_comment': "ALTER TABLE orders_order ADD COLUMN manager_comment text NOT NULL DEFAULT ''",
    }

    for column_name, sql in order_sql.items():
        if column_name not in existing_columns:
            schema_editor.execute(sql)

    existing_item_columns = {
        column.name
        for column in introspection.get_table_description(connection.cursor(), 'orders_orderitem')
    }
    if 'custom_price' not in existing_item_columns:
        schema_editor.execute(
            "ALTER TABLE orders_orderitem ADD COLUMN custom_price decimal NULL"
        )


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_missing_order_fields, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='order',
                    name='deleted_at',
                    field=models.DateTimeField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='order',
                    name='is_deleted',
                    field=models.BooleanField(default=False),
                ),
                migrations.AddField(
                    model_name='order',
                    name='manager_comment',
                    field=models.TextField(blank=True),
                ),
                migrations.AddField(
                    model_name='orderitem',
                    name='custom_price',
                    field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
                ),
            ],
        ),
    ]
