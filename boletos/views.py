from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import logging
import threading
from django.db import transaction
from .models import Boleto
from abc import ABC, abstractmethod

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IGeradorBoleto(ABC):
    @abstractmethod
    def gerar(self, nome, valor):
        pass

class IEnviadorEmail(ABC):
    @abstractmethod
    def enviar(self, email):
        pass

# Implementação concreta das classes de abstração
class GeradorBoleto(IGeradorBoleto):
    def gerar(self, nome, valor):
        logger.info(f"Boleto gerado para {nome}, valor: {valor}")

class EnviadorEmail(IEnviadorEmail):
    def enviar(self, email):
        logger.info(f"E-mail enviado para {email}")

# Classe para processamento do CSV
class ProcessadorCSV:
    def __init__(self):
        self.gerador_boleto = GeradorBoleto()
        self.enviador_email = EnviadorEmail()

    def processar(self, file):
        if not file:
            logger.warning("Nenhum arquivo enviado na requisição.")
            return JsonResponse({'erro': 'Nenhum arquivo enviado.'}, status=400)

        try:
            df = pd.read_csv(file)

            # Verificar colunas obrigatórias
            colunas_esperadas = {'name', 'governmentId', 'email', 'debtAmount', 'debtDueDate', 'debtId'}
            if not colunas_esperadas.issubset(df.columns):
                logger.error("Arquivo CSV com formato inválido.")
                return JsonResponse({'erro': 'Arquivo CSV com formato inválido.'}, status=400)

            # Remover duplicatas dentro do arquivo
            df = df.drop_duplicates(subset=['debtId'])

            # Filtrar registros já processados no banco de dados
            boletos_existentes = set(Boleto.objects.values_list('id', flat=True))
            df = df[~df['debtId'].isin(boletos_existentes)]

            # Processar boletos e enviar e-mails antes de salvar no banco de dados assíncrono
            boletos_para_salvar = []
            for _, row in df.iterrows():
                self.gerador_boleto.gerar(row['name'], row['debtAmount'])
                self.enviador_email.enviar(row['email'])
                
                boletos_para_salvar.append({
                    'id': row['debtId'],
                    'name': row['name'],
                    'government_id': row['governmentId'],
                    'email': row['email'],
                    'debt_amount': row['debtAmount'],
                    'debt_due_date': row['debtDueDate'],
                    'boleto_gerado': True,
                    'email_enviado': True
                })

            # Iniciar um thread para salvar os dados em lotes sem bloquear a API
            if boletos_para_salvar:
                threading.Thread(target=salvar_boletos_em_lotes, args=(boletos_para_salvar,)).start()

            logger.info(f"{len(boletos_para_salvar)} boletos processados e enviados para processamento assíncrono.")
            return JsonResponse({'mensagem': f'{len(boletos_para_salvar)} boletos processados e serão armazenados em segundo plano.'})

        except pd.errors.ParserError as e:
            logger.error(f"Erro ao ler o CSV: {e}")
            return JsonResponse({'erro': 'Erro ao ler o arquivo CSV.'}, status=400)

        except Exception as e:
            logger.critical(f"Erro inesperado no processamento do arquivo: {str(e)}")
            return JsonResponse({'erro': 'Erro interno do servidor.'}, status=500)

# Função para salvar boletos em lotes no banco de forma completamente assíncrona
def salvar_boletos_em_lotes(boletos):
    try:
        tamanho_lote = 50000
        for i in range(0, len(boletos), tamanho_lote):
            with transaction.atomic():
                boletos_objetos = [Boleto(**dados) for dados in boletos[i:i + tamanho_lote]]
                Boleto.objects.bulk_create(boletos_objetos)
                logger.info(f"{len(boletos_objetos)} boletos foram salvos no banco de dados com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao salvar boletos no banco: {e}")

@method_decorator(csrf_exempt, name='dispatch')
class ProcessarArquivoView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.processador_csv = ProcessadorCSV()

    def post(self, request):
        file = request.FILES.get('file')
        return self.processador_csv.processar(file)
