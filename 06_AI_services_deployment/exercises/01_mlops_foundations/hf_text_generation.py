from transformers import pipeline

# creare un pipeline per la generazione di testo
generator = pipeline("text-generation", 
                    model="LorenzoDeMattei/GePpeTto")

# generazione del testo
prompt = "L'Italia è un paese"
risultato = generator(prompt, max_length=50, num_return_sequences=1)

print(f"Prompt: {prompt}")
print(f"Testo generato: {risultato[0]['generated_text']}")