import pymupdf as fitz
import gpt
import random
import json
import webbrowser
import subprocess

def extract_highlights(pdf_path):
    doc = fitz.open(pdf_path)
    highlights = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        annotations = page.annots()
        if annotations:
            for annot in annotations:
                if annot.type[0] == 8: 
                    highlight_info = {
                        "page_num": page_num+1,
                        "content": page.get_text("text", clip=annot.rect),
                        "rect": annot.rect,
                    }
                    highlights.append(highlight_info)
    return highlights

example = '/Users/pablo/Downloads/00_Designing_Data_Intensive_Applications.pdf'
highlights = extract_highlights(example)
highlight = random.sample(highlights, k=1)[0]
prompt = """Create an anki card from this text: {highlight} \n
Format the answer using the following format, make sure it's parseable with json.loads.\n
Begin your answer with the open bracelet, dont add ```json```

{{"front": str, "back": str}}
"""
highlight_str = highlight['content']
page = highlight["page_num"]
stuffed = prompt.format(highlight=highlight_str)
res = gpt.get_gpt_response(stuffed)
anki = json.loads(res)
front = anki['front']

print(f"Q: {front}\n========\n\n".format(front=front))
uinput = input("Your answer: ")
prompt = """Your task is to evaluate a user answer to an anki card\n
Anki front (shown to user): {front} \n
Anki back: {back}
User answer: {uinput}
Score the user response choosing between: ['complete', 'partial', 'misses']
Note that you should not be to nit picky, be generous but still factual.
Your score and one-line simple rationale. Be smart!: """.format(front=anki['front'], back=anki['back'], uinput=uinput)

res = gpt.get_gpt_response(prompt)
print(f"Score: {res} \nOriginal: {highlight_str}\n\nPage: {page}")
