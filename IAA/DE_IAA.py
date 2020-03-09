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



with open("/Users/sina/My_GitHub/SeneAnnotation/0Experiments/DE_MWSA_A1.json") as json_file:
	annotator1 = json.load(json_file)

with open("/Users/sina/My_GitHub/SeneAnnotation/0Experiments/DE_MWSA_A2.json") as json_file:
	annotator2 = json.load(json_file)

# merge entries with identitcal headwords and pos tags
lemma_index_one = {i : j["lemma"] + "|||" + j["part-of-speech_tag"] for i, j in enumerate(annotator1["body"])}
lemma_index_two = {i : j["lemma"] + "|||" + j["part-of-speech_tag"] for i, j in enumerate(annotator1["body"])}

# count number of senses for which no alignment is provided
common = list()
num_all_senses, unique_aligned_senses = 0, 0
for i, j in enumerate(annotator1["body"]):
	sense_combinations = list()
	for m in j["resource_1_senses"]:
		for n in j["resource_2_senses"]:
			if n["#text"] != m["#text"]:
				sense_combinations.append( m["#text"] + "\t" + n["#text"])

	num_all_senses += len(sense_combinations)
	unique_aligned_senses += len(list(set([match["sense_source"] + "\t" + match["sense_target"] for match in j["alignment"]] +
		[match["sense_source"] + "\t" + match["sense_target"] for match in annotator2["body"][i]["alignment"]])))

	common.append({"one": j["alignment"], "two": annotator2["body"][i]["alignment"]})


commons = list()
for entry in common:
	annotators = {"one": {}, "two": {}}
	# print( [False if a not in entry else '' for a in annotators] )
	# print(entry["lemma"])
	for a in annotators:
		for match in entry[a]:
			annotators[a].update({match["sense_source"] + "\t" + match["sense_target"]: match["semantic_relationship"]})

	commons.append(annotators)
print(len(commons))
# print(commons[0])
# exit()
kkk = ["exact", "narrower", "broader", "related", "NONE"]
kkk_map = {"exact": "Yes", "narrower": "Yes", "broader": "Yes", "related": "Yes", "NONE": "No"}
kkk_two_map = {"exact": 1, "narrower": 1, "broader": 1, "related": 1, "NONE": 0}

num_annotator = 2
iaa_case = [5, 2]
print(num_all_senses - unique_aligned_senses)
for case in iaa_case:
	MATRIX = list()
	for i in commons:
		sense_pairs = list(set(list(i["one"].keys()) + list(i["two"].keys())))
		# print(i)
		for sense in sense_pairs:
			row = [0, 0, 0, 0, 0]
			two_case_row = [0, 0] 

			if case == 5:
				row[kkk.index(i["one"].get(sense, "NONE"))] += 1
				row[kkk.index(i["two"].get(sense, "NONE"))] += 1
				# print(", ".join([str(j) for j in row]))
				MATRIX.append(row)

			else:
				# two_case_row[0] = kkk_map[i["David"].get(sense, "NONE")]
				# two_case_row[1] = kkk_map[i["John"].get(sense, "NONE")]
				# two_case_row[2] = kkk_map[i["Dorus"].get(sense, "NONE")]

				two_case_row[kkk_two_map[i["one"].get(sense, "NONE")]] += 1
				two_case_row[kkk_two_map[i["two"].get(sense, "NONE")]] += 1
				# print(", ".join([str(j) for j in two_case_row]))
				MATRIX.append(two_case_row)

	
	print(str(case))
	print("="*30)
	# add senses without any alignment from all annotators
	if case == 5:
		for x in range(num_all_senses - unique_aligned_senses):
			MATRIX.append([0, 0, 0, 0, num_annotator])
	else:
		for x in range(num_all_senses - unique_aligned_senses):
			MATRIX.append([0, num_annotator])

	arr = np.vstack(MATRIX)
	kappa = fleiss_kappa(arr)
	alpha = krippendorff.alpha(arr)

	print("kappa:", kappa)
	print("alpha:", alpha)
	print()
	with open("DE_"+str(case)+".txt", "w") as f:
		f.write("\n".join([", ".join(map(str, ii)) for ii in MATRIX]))
