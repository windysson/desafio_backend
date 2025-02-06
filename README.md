# Processamento de Boletos - Django + MySQL + Docker

Este projeto é uma API desenvolvida com **Django** e **Django REST Framework** para processamento de boletos. Ele utiliza um **banco de dados MySQL** e suporta execução em **Docker**.

## **Requisitos**

Antes de começar, certifique-se de ter instalado:

- **Docker**  [Instalar Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**  [Instalar Docker Compose](https://docs.docker.com/compose/install/)
- **Python 3.9+** [Instalar Python](https://www.python.org/downloads/)

---

## **1️ Clonar o Repositório**
```bash
git clone https://github.com/windysson/desafio_backend.git
cd desafio_backend/
```

---

## **2️ Rodar o Projeto **
Execute os seguintes comandos para construir e iniciar o ambiente:
Com docker:
```bash
docker-compose build
docker-compose up -d
```
Sem docker:
```bash
pip install -r requirements.txt
python manage.py runserver
```

Isso irá:

✔️ Subir o banco de dados MySQL.  
✔️ Criar e rodar a API Django.  
✔️ Aplicar migrações automaticamente.

A API estará disponível em **`http://localhost:8000/`** 🚀

---

## **43 Rodar as Migrações (se necessário)**
Se o banco de dados ainda não estiver migrado, execute:

```bash
docker-compose exec web python manage.py migrate
```

---

## **4 Rodar os Testes**
Os testes unitarios estão dentro do app `boletos/`. Para rodá-los:

```bash
docker-compose exec web python manage.py test boletos
```

Se estiver rodando fora do Docker:

```bash
python manage.py test boletos
```

Teste de integração e o arquivo test-integration.txt

```bash
python test-integration.py
```

---

## **Rotas da API**
| Método | Endpoint                    | Descrição |
|--------|-----------------------------|-----------|
| POST   | `/boletos/processar/`       | Enviar arquivo CSV para processar boletos |

---

## **Dicas de Debug**
- Para ver os logs do Django:
```bash
docker logs -f <ID_DO_CONTAINER_WEB>
```
- Para acessar o shell interativo dentro do container:
```bash
docker-compose exec web sh
```

---

## **Parando os Containers**
Para desligar os serviços:

```bash
docker-compose down
```
Para remover volumes (dados do banco):

```bash
docker-compose down -v
```

---

