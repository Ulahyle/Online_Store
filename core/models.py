from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class AbstractBaseModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager() # The default manager
    active_objects = SoftDeleteManager() # Your new manager

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False): # softdelete
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])
