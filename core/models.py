from django.db import models
from django.utils import timezone


class AbstractBaseModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False): # soft delete
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])
