pip install -r requirements.txt
gunicorn -w 2 app:app --daemon