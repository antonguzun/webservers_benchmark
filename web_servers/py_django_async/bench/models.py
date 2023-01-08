from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True
        app_label = "bench_db"


class User(BaseModel):
    user_id = models.IntegerField(db_index=True, primary_key=True)
    username = models.CharField(max_length=255, null=False)
    email = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(null=False)
    is_archived = models.BooleanField(null=False, default=False)

    class Meta:
        db_table = "users"
        managed = False
