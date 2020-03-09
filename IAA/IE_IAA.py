# -*- coding: utf-8 -*-
import json
import numpy as np
import krippendorff

def fleiss_kappa(M):
  N, k = M.shape  # N is # of items, k is # of categories
  n_annotators = float(np.sum(M[0, :]))  # # of annotators

  p = np.sum(M, axis=0) / (N * n_annotators)
  P = (np.sum(M * M, axis=1) - n_annotators) / (n_annotators * (n_annotators - 1))
  Pbar = np.sum(P) / N
  PbarE = np.sum(p * p)

  kappa = (Pbar - PbarE) / (1 - PbarE)

  return kappa

MATRIX = list()

# with open("/Users/sina/My_GitHub/SeneAnnotation/0Experiments/GA_MWSA_merged.json") as json_file:
# 	irish = json.load(json_file)["body"]

with open("GA_commons.json") as json_file:
	common = json.load(json_file)

#####
# counter number of senses for which no alignment is provided
num_all_senses, unique_aligned_senses = 0, list()
with open("/Users/sina/My_GitHub/SeneAnnotation/0Experiments/GA_MWSA_merged.json") as json_file:
	merged = json.load(json_file)

sense_combinations = list()
for c_entry in common:
	for i, j in enumerate(merged["body"]):
		if c_entry["lemma"] == j["lemma"] and  c_entry["part-of-speech_tag"] == j["part-of-speech_tag"]:
			for m in j["resource_1_senses"]:
				for n in j["resource_2_senses"]:
					if n["#text"] != m["#text"]:
						sense_combinations.append( m["#text"] + "\t" + n["#text"])

for c_i in common: 
	# print(c_i)
	if "John" in c_i and "Theodorus" in c_i and "Oksana" in c_i:
		unique_aligned_senses.append([match["sense_source"] + "\t" + match["sense_target"] for match in c_i["John"]])
		unique_aligned_senses.append([match["sense_source"] + "\t" + match["sense_target"] for match in c_i["Theodorus"]])
		unique_aligned_senses.append([match["sense_source"] + "\t" + match["sense_target"] for match in c_i["Oksana"]])

print(len(unique_aligned_senses)/3)
num_all_senses = len(list(set(sense_combinations)))
unique_aligned_senses = list(set([item for sublist in unique_aligned_senses for item in sublist]))
print("len of unique", len(unique_aligned_senses))
print("num of all", num_all_senses)
#####

# merge entries with identitcal headwords and pos tags
GA_commons = list()
John, Dorus, Okdana = dict(), dict(), dict()
for entry in common:
	annotators = {"John": {}, "Theodorus": {}, "Oksana": {}}
	# print( [False if a not in entry else '' for a in annotators] )
	if len(entry) == 5:
		# print(entry["lemma"])
		for a in annotators:
			for match in entry[a]:
				annotators[a].update({match["sense_source"] + "\t" + match["sense_target"]: match["semantic_relationship"]})

		GA_commons.append(annotators)

# print(GA_commons[0])
# exit()
kkk = ["exact", "narrower", "broader", "related", "NONE"]
kkk_map = {"exact": "Yes", "narrower": "Yes", "broader": "Yes", "related": "Yes", "NONE": "No"}
kkk_two_map = {"exact": 1, "narrower": 1, "broader": 1, "related": 1, "NONE": 0}



num_annotator = 3
iaa_case = [5, 2]
for case in iaa_case:
	MATRIX = list()
	for i in GA_commons:
		sense_pairs = list(set(list(i["John"].keys()) + list(i["Theodorus"].keys()) + list(i["Oksana"].keys())))
		# print(i)
		for sense in sense_pairs:
			row = [0, 0, 0, 0, 0]
			two_case_row = [0, 0] # David, John, Dorus

			if case == 5:
				row[kkk.index(i["John"].get(sense, "NONE"))] += 1
				row[kkk.index(i["Theodorus"].get(sense, "NONE"))] += 1
				row[kkk.index(i["Oksana"].get(sense, "NONE"))] += 1
				# print(", ".join([str(j) for j in row]))
				MATRIX.append(row)

			else:
				# two_case_row[0] = kkk_map[i["David"].get(sense, "NONE")]
				# two_case_row[1] = kkk_map[i["John"].get(sense, "NONE")]
				# two_case_row[2] = kkk_map[i["Dorus"].get(sense, "NONE")]

				two_case_row[kkk_two_map[i["John"].get(sense, "NONE")]] += 1
				two_case_row[kkk_two_map[i["Theodorus"].get(sense, "NONE")]] += 1
				two_case_row[kkk_two_map[i["Oksana"].get(sense, "NONE")]] += 1
				# print(", ".join([str(j) for j in two_case_row]))
				MATRIX.append(two_case_row)

	print(str(case))
	print("="*30)
	# add senses without any alignment from all annotators
	if case == 5:
		for x in range(num_all_senses - len(unique_aligned_senses)):
			MATRIX.append([0, 0, 0, 0, num_annotator])
	else:
		for x in range(num_all_senses - len(unique_aligned_senses)):
			MATRIX.append([0, num_annotator])

	# print(MATRIX)
	arr = np.vstack(MATRIX)
	kappa = fleiss_kappa(arr)
	alpha = krippendorff.alpha(arr)

	print(kappa)
	print(alpha)
	with open("IE_"+str(case)+".txt", "w") as f:
		f.write("\n".join([", ".join(map(str, ii)) for ii in MATRIX]))
