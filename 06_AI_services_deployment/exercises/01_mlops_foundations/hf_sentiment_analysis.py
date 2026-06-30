from transformers import pipeline

# creare un pipeline per l'analisi del sentimento
classifier = pipeline("sentiment-analysis", 
                     model="neuraly/bert-base-italian-cased-sentiment")

# esempio di utilizzo
testo = "Questo ristorante è fantastico, ci tornerò sicuramente!"
risultato = classifier(testo)

print(f"Testo: {testo}")
print(f"Sentimento: {risultato[0]['label']}")
print(f"Confidenza: {risultato[0]['score']:.2f}")