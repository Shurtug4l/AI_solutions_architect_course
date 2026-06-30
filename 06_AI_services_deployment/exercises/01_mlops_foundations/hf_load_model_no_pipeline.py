from transformers import AutoTokenizer, AutoModelForCausalLM

# specificare il modello
model_name = "LorenzoDeMattei/GePpeTto"

# caricare tokenizer e modello
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# testo di input (prompt)
prompt = "L'Italia è un paese"
inputs = tokenizer(prompt, return_tensors="pt")

# generare il testo
output = model.generate(
    inputs["input_ids"], 
    max_length=50, 
    num_return_sequences=1, 
    no_repeat_ngram_size=2, 
    early_stopping=True
)

# decodificare il risultato
generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
print(f"Prompt: {prompt}")
print(f"Testo generato: {generated_text}")