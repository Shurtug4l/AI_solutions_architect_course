# Usa l'immagine ufficiale di Python come immagine di base
FROM python:3.9

# Imposta la directory di lavoro all'interno del container
WORKDIR /app

# Copia il file 'app.py' dal tuo sistema locale al container
COPY app.py /app

# Espone la porta 8080 per comunicare con il container
EXPOSE 8080

# Comando per avviare l'applicazione quando il container parte
CMD ["python", "app.py"]
