from transformers import pipeline

# build a sentiment-analysis pipeline (Italian model)
classifier = pipeline("sentiment-analysis",
                     model="neuraly/bert-base-italian-cased-sentiment")

# usage example (Italian input by design)
text = "Questo ristorante è fantastico, ci tornerò sicuramente!"
result = classifier(text)

print(f"Text: {text}")
print(f"Sentiment: {result[0]['label']}")
print(f"Confidence: {result[0]['score']:.2f}")