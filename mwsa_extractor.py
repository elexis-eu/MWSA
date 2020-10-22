import json

reversed_relationship = {"narrower": "broader", "broader": "narrower", "related": "related", "none": "none", "exact": "exact"}
output_dir = "/Users/sina/My_GitHub/MWSA/TSV/"

languages= {
    "bg": "BG_MWSA.json",
    "da": "DA_MWSA.json",
    "de": "DE_MWSA_A1.json",
    "en": "EN_NUIG_MWSA_2.json",
    "es": "ES_MWSA.json",
    "et": "ET_MWSA.json",
    "eu": "EU_MWSA.json",
    "ga": "GA_MWSA_merged.json",
    "ha": "HA_MWSA.json",
    "it": "IT_MWSA.json",
    "nl": "NL_MWSA.json",
    "pt": "PT_MWSA.json",
    "ru": "RU_MWSA.json",
    "sl": "SL_ZRC_SAZU_MWSA.json",
    "sr": "SR_MWSA.json"
    }
for lang in languages:
	lang_output = list()
	json_file_directory = "classification_datasets/Data/" + languages[lang]
	with open(json_file_directory) as f:
		resource = json.load(f)["body"]
		all_senses = dict()
		for i in resource:
			senses_1 = [j["#text"].lower() for j in i["resource_1_senses"] if j["#text"] != None]
			senses_2 = [j["#text"].lower() for j in i["resource_2_senses"] if j["#text"] != None]

			new_alignment = {(j["sense_source"].lower(), j["sense_target"].lower()): j["semantic_relationship"] for j in i["alignment"]}

			if "part-of-speech_tag" not in i:
				pos = ""
			else:
				pos = i["part-of-speech_tag"]

			if "gender" not in i:
				gender = ""
			else:
				gender = i["gender"]

			for s_1 in senses_1:
				for s_2 in senses_2:
					if (s_1, s_2) in new_alignment and new_alignment[(s_1, s_2)] != '' and new_alignment[(s_1, s_2)] in reversed_relationship:
						all_senses[(s_1, s_2)] = new_alignment[(s_1, s_2)]
						# reverse the sense order and create a new sense match
						all_senses[(s_2, s_1)] = reversed_relationship[new_alignment[(s_1, s_2)]]
						lang_output.append("\t".join((i["lemma"], pos, gender, s_1, s_2, new_alignment[(s_1, s_2)])))
						lang_output.append("\t".join((i["lemma"], pos, gender, s_1, s_2, reversed_relationship[new_alignment[(s_1, s_2)]])))
					else:
						all_senses[(s_1, s_2)] = "none"
						lang_output.append("\t".join((i["lemma"], pos, gender, s_1, s_2, "none")))


	with open(output_dir+lang+"_MWSA.tsv", "w") as ff:
		ff.write("\n".join(lang_output))

