from django.db import models

class Boleto(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    government_id = models.CharField(max_length=20)
    email = models.EmailField()
    debt_amount = models.DecimalField(max_digits=10, decimal_places=2)
    debt_due_date = models.DateField()
    boleto_gerado = models.BooleanField(default=False)
    email_enviado = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.debt_amount}"
