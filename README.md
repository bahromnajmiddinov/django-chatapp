# Django ChatAPP

1. Clone this repository:

   ```bash
   git clone https://github.com/bahromnajmiddinov/taskly-app.git


2. Create a virtual environment (recommended for isolation):
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate.bat  # Windows

3. Install dependencies:

    ```bash
    pip install -r requirements.txt

4. Apply database migrations:
    ```bash
    python manage.py makemigrations
    python manage.py migrate

5. (Optional) Create a superuser for initial administration:
    ```bash
    python manage.py createsuperuser

Start the development server:

```bash
python manage.py runserver
