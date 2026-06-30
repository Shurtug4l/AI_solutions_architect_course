# salvare il modello localmente
model.save_pretrained("./mio_modello")
tokenizer.save_pretrained("./mio_modello")

# ricaricare il modello dal disco
model_locale = AutoModel.from_pretrained("./mio_modello")
tokenizer_locale = AutoTokenizer.from_pretrained("./mio_modello")