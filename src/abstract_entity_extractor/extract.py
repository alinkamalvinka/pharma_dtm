# %%
import spacy
from collections import OrderedDict
from spacy import displacy
from typing import List
import en_core_web_sm
nlp = en_core_web_sm.load()

# %%
TEXT = """
Acknowledgments
This work was supported by Amgen Inc. The authors thank the following individuals for their 
invaluable assistance with manuscript preparation and review: Kim Carrillo, Rylan Hanks, 
Grace Jiang, Jocelyn McQueen, Linda Narhi, Michelle Pernice, Lorraine Sutherland, Hideo Yoshida, 
all employees of Amgen Inc., Charles Wright (PreScouter, Inc., Evanston, IL) and the PreScouter 
team, as well as Anne Johnson and James Balwit (both Complete Healthcare Communications, LLC, an
We would like to thank Dr. Simone Wengner for the helpful discussion. The German Academic Exchange 
Service (DAAD) is acknowledged for providing a stipend to J.A-G. This work was contributed to the 
OrBiTo project (http://www.imi.europa.eu/content/) as sideground.
"""

# %%
def org_entities(data: str) -> List[str]:
    entities = nlp(data).ents
    orgs = filter(lambda e: e.label_ == 'ORG', entities)
    orgs = map(lambda o: o.text, orgs)
    return list(dict.fromkeys(orgs))

# %%
print(org_entities(TEXT))
