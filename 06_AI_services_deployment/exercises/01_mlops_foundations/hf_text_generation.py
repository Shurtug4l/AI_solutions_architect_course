from transformers import pipeline

# build a text-generation pipeline (GePpeTto, Italian GPT-2)
generator = pipeline("text-generation",
                    model="LorenzoDeMattei/GePpeTto")

# text generation (Italian prompt by design)
prompt = "L'Italia è un paese"
result = generator(prompt, max_length=50, num_return_sequences=1)

print(f"Prompt: {prompt}")
print(f"Generated text: {result[0]['generated_text']}")