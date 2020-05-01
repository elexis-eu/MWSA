#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Converts JSON files to RDF suitable for training with NAISC (https://github.com/insight-centre/naisc)
"""
import sys
import os
from urllib.parse import quote
import json


BASE_URL = "https://github.com/elexis-eu/mwsa"

term2id = {}

def to_tsv(json_file):
    final_file = list()
    with open(json_file) as f:
        for i in json.load(f)["body"]:
            senses_1 = [j["#text"] for j in i["resource_1_senses"]]
            senses_2 = [j["#text"] for j in i["resource_2_senses"]]
            # convert the alignment dictionary into a dicitonary where {tupels (sense_1, sense_2): relationship}
            new_alignment = dict()
            for j in i["alignment"]:
                key = (j["sense_source"], j["sense_target"])
                if key not in new_alignment:
                    new_alignment[key] = [j["semantic_relationship"]]
                else:
                    new_alignment[key].append(j["semantic_relationship"])

            for s1 in senses_1:
                for s2 in senses_2:
                    if (s1, s2) not in new_alignment and len(new_alignment):
                        final_file.append("\t".join( [i["lemma"], i.get("part-of-speech_tag", "None"), s1, s2, "none"]) )
                    else:
                        if len(new_alignment):
                            final_file.append("\t".join( [i["lemma"], i.get("part-of-speech_tag", "None"), s1, s2, new_alignment[(s1, s2)][0]]) )

    return "\n".join(final_file)


def process_file(tsv_file):
    lterms = []
    rterms = []
    links = []
    for line in tsv_file.split("\n"):
        e = line.split("\t")
        assert(len(e) == 5)
        lterm = (e[0], e[1], e[2])
        rterm = (e[0], e[1], e[3])
        if lterm not in term2id:
            term2id[lterm] = len(term2id)
            lterms.append(lterm)
        if rterm not in term2id:
            term2id[rterm] = len(term2id)
            rterms.append(rterm)
        links.append((term2id[lterm], term2id[rterm], e[4]))
    return lterms, rterms, links

def to_skos(r):
    if r == "exact":
        return "exactMatch"
    elif r == "narrower":
        return "narrowMatch"
    elif r == "broader":
        return "broadMatch"
    elif r == "related":
        return "relatedMatch"
    else:
        print("bad relation "+ r)
        sys.exit(-1)

def to_lang(l):
    if "_" in l:
        return l.split("_")[0]
    else:
        return l

def escape_literal(l):
    return l.replace("\"","\\\"")

def write_dataset(file_id, name, language, lterms):
    with open("RDF/%s/%s_%s.nt" %(file_id, name, language), "w") as left:
        for (lemma, pos, defn) in lterms:
            entry_id = "<%s#%s_%s>" % (BASE_URL, quote(lemma), quote(pos))
            sense_id = "<%s#sense%d>" % (BASE_URL, term2id[(lemma, pos, defn)]) 
            left.write("%s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/lemon/ontolex#LexicalEntry> .\n" % entry_id)
            left.write("%s <http://www.w3.org/ns/lemon/ontolex#sense> %s .\n" % (entry_id, sense_id))
            left.write("%s <http://www.w3.org/2000/01/rdf-schema#label> \"%s\"@%s .\n" % (entry_id, escape_literal(lemma), to_lang(language)))
            left.write("%s <http://www.w3.org/2004/02/skos/core#definition> \"%s\"@%s .\n" % (sense_id, escape_literal(defn), to_lang(language)))
 

def write_align(file_id, name, language, links):
    with open("RDF/%s/%s_%s.nt" % (file_id, name, language), "w") as align:
        for (id1, id2, link_type) in links:
            if link_type.strip() != "none":
                align.write("<%s#sense%d> <http://www.w3.org/2004/02/skos/core#%s> <%s#sense%d> .\n" % (BASE_URL, id1, to_skos(link_type.strip()), BASE_URL, id2))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/json-to-rdf.py JSON/english.json en")
        sys.exit(-1)

    filename = sys.argv[1]
    language = sys.argv[2]

    filepath_head, filepath_tail = os.path.split(filename)
    file_id = filepath_tail.split(".")[0]
    file_tsv = to_tsv(filename)
    lterms, rterms, links_train = process_file(file_tsv)
    

    if not os.path.isdir("RDF/%s" %file_id): #language):
        os.mkdir("RDF/%s" % file_id)# sys.argv[3])
    write_dataset(file_id, "left", language, lterms)
    write_dataset(file_id, "right", language, rterms)
    write_align(file_id, "align-train", language, links_train)
