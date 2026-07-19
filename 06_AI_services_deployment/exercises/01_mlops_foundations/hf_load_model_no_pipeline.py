from transformers import AutoTokenizer, AutoModelForCausalLM

# pick the model (GePpeTto is an Italian GPT-2)
model_name = "LorenzoDeMattei/GePpeTto"

# load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# input text (Italian prompt by design)
prompt = "L'Italia è un paese"
inputs = tokenizer(prompt, return_tensors="pt")

# generate the text
output = model.generate(
    inputs["input_ids"],
    max_length=50,
    num_return_sequences=1,
    no_repeat_ngram_size=2,
    early_stopping=True
)

# decode the result
generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
print(f"Prompt: {prompt}")
print(f"Generated text: {generated_text}")