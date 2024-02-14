from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfReader
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import csv

app = Flask(__name__)

nlp = spacy.load('en_core_web_md')
skill_path = '../data/skills.jsonl'
ruler = nlp.add_pipe("entity_ruler")
ruler.from_disk(skill_path)

def preprocessing(sentence):
    stopwords    = list(STOP_WORDS)
    doc          = nlp(sentence)
    clean_tokens = []
    
    for token in doc:
        if token.text not in stopwords and token.pos_ != 'PUNCT' and token.pos_ != 'SYM' and \
            token.pos_ != 'SPACE':
                clean_tokens.append(token.lemma_.lower().strip())
                
    return " ".join(clean_tokens)

def get_skills(doc):    
    skills = []
    
    for ent in doc.ents:
        if ent.label_ == 'SKILL':
            skills.append(ent.text)
            
    return skills

def unique_skills(x):
    return list(set(x))

def get_experiences(doc):    
    skills = []
    
    for ent in doc.ents:
        if ent.label_ == 'EXPERIENCE':
            skills.append(ent.text)
            
    return skills

def unique_experiences(x):
    return list(set(x))

def unique_entities(x):
    return list(set(x))

def get_entities(resume):
    
    doc = nlp(resume)

    entities={}
    
    for entity in doc.ents:
        if entity.label_ in entities:
            entities[entity.label_].append(entity.text)
        else:
            entities[entity.label_] = [entity.text]
    for ent_type in entities.keys():
        entities[ent_type]=', '.join(unique_entities(entities[ent_type]))
    return entities


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']

        reader = PdfReader(file)
        page = reader.pages[0]
        text = page.extract_text()

        print(text)

        text = preprocessing(text)

        print('////////////////////////////////////')
        print(text)
        print('////////////////////////////////////')

        doc = nlp(text)

        print(doc.ents)

        details = {
            'email' : [token.text for token in doc if token.like_email],
            'contact' : [ent.text for ent in doc.ents if ent.label_ == "PHONE"],
            'skills': get_skills(doc),
            'experience': get_experiences(doc)
        }

        csv_path = "extracted_information.csv"
        with open(csv_path, "w", newline="") as file:
            writer = csv.writer(file)
            for label, values in details.items():
                writer.writerow([label] + values)

        return send_file(csv_path, as_attachment=True)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
