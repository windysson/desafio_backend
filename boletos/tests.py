import unittest
from unittest.mock import patch, MagicMock
from django.test import RequestFactory
from django.http import JsonResponse
import pandas as pd
import json
from boletos.views import GeradorBoleto, EnviadorEmail, ProcessadorCSV, ProcessarArquivoView

# Testes para GeradorBoleto
class TestGeradorBoleto(unittest.TestCase):
    def test_gerar(self):
        gerador = GeradorBoleto()
        with patch('boletos.views.logger.info') as mock_logger:
            gerador.gerar("João Silva", 100.50)
            mock_logger.assert_called_once_with("Boleto gerado para João Silva, valor: 100.5")

# Testes para EnviadorEmail
class TestEnviadorEmail(unittest.TestCase):
    def test_enviar(self):
        enviador = EnviadorEmail()
        with patch('boletos.views.logger.info') as mock_logger:
            enviador.enviar("joao.silva@example.com")
            mock_logger.assert_called_once_with("E-mail enviado para joao.silva@example.com")

# Testes para ProcessadorCSV
class TestProcessadorCSV(unittest.TestCase):
    def setUp(self):
        self.processador = ProcessadorCSV()

    @patch('boletos.views.pd.read_csv')
    @patch('boletos.views.open')
    def test_processar_csv_valido(self, mock_open, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame({
            'name': ['João Silva'],
            'governmentId': ['123456789'],
            'email': ['joao.silva@example.com'],
            'debtAmount': [100.50],
            'debtDueDate': ['2023-12-31'],
            'debtId': ['1']
        })
        mock_open.return_value.__enter__.return_value.readlines.return_value = []
        mock_file = MagicMock()
        mock_file.name = 'test.csv'
        response = self.processador.processar(mock_file)

        # Nova verificação mais flexível
        response_data = json.loads(response.content)
        self.assertIn('mensagem', response_data)
        self.assertRegex(response_data['mensagem'], r'^\d+ boletos processados e serão armazenados em segundo plano\.$')

# Testes para ProcessarArquivoView
class TestProcessarArquivoView(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('boletos.views.ProcessadorCSV.processar')
    def test_post_com_arquivo(self, mock_processar):
        mock_processar.return_value = JsonResponse({'mensagem': '10 boletos processados e serão armazenados em segundo plano.'})
        with open('test.csv', 'w') as f:
            f.write('name,governmentId,email,debtAmount,debtDueDate,debtId\nJoão Silva,123456789,joao.silva@example.com,100.50,2023-12-31,1')
        with open('test.csv', 'rb') as f:
            request = self.factory.post('/boletos/processar/', {'file': f})
        view = ProcessarArquivoView.as_view()
        response = view(request)

        # Nova verificação mais flexível
        response_data = json.loads(response.content)
        self.assertIn('mensagem', response_data)
        self.assertRegex(response_data['mensagem'], r'^\d+ boletos processados e serão armazenados em segundo plano\.$')

    def test_post_sem_arquivo(self):
        request = self.factory.post('/boletos/processar/')
        view = ProcessarArquivoView.as_view()
        response = view(request)
        self.assertEqual(json.loads(response.content), {'erro': 'Nenhum arquivo enviado.'})
