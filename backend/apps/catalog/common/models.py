from django.db import models


class BaseModel(models.Model):
    active = models.BooleanField(default=True, verbose_name="activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="actualizado")

    class Meta:
        abstract = True

    def activate(self) -> None:
        self.active = True
        self.save(update_fields=["active"])

    def deactivate(self) -> None:
        self.active = False
        self.save(update_fields=["active"])
