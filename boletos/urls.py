from django.urls import path
from .views import ProcessarArquivoView

urlpatterns = [
    path('processar-arquivo/', ProcessarArquivoView.as_view(), name='processar_arquivo'),
]
