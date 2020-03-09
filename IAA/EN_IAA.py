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


if False: # convert the spreadsheet into a list of dictionaries
	with open("/EN-WN-Webster.tsv", "r") as f:
		left = f.read().split('\n')[1:-1]

	# Find the position of the entries
	sheet_left_dict = list()
	headword_positions = list()
	for i in range(len(left)):
		if left[i].split("\t")[0]:
			headword_positions.append(i)

	# Retrieve senses of each entry
	for i in range(len(headword_positions)):
		if i == len(headword_positions)-1: # last entry
			sheet_left_dict.append( "\n".join( left[headword_positions[i]:] ) )
		else:
			sheet_left_dict.append( "\n".join( left[headword_positions[i]:headword_positions[i+1]] ) )

	body = list()

	# Resource 1 at the left
	for entry in sheet_left_dict:
		david, john, dorus = dict(), dict(), dict()
		# Create a dictionary of {the sense match: real sense in the right}
		match_right_dictionary = list(set([i.split("\t")[9] for i in entry.split("\n")])) # entry senses in the right side
		sense_matches = list(set([i.split("\t")[4] for i in entry.split("\n")])) # sense matches
		sense_matches += list(set([i.split("\t")[6] for i in entry.split("\n")]))
		sense_matches += list(set([i.split("\t")[8] for i in entry.split("\n")]))
		left_senses = list()
		sense_match_dict = dict()

		for s in sense_matches:
			if s == "":
				sense_match_dict[""] = ""
			else:
				for sns in match_right_dictionary:
					if s in sns:
						sense_match_dict[s] = sns

		# Retrieve other elements
		for i in entry.split("\n"):
			# check if has the lemma
			if "\t\t\t\t\t" in i:
				headword = i.split("\t")[0]
			# i contains senses
			else:
				sense_row = i.split("\t")

				if not len(sense_row[2]):
					raise ValueError('Left sense empty.')
				
				# Check if the sense has been already added (in case of polysemy)
				# if sense_row[2] not in left_senses:
				# 	resource_1_senses.append(sense_row[2])

				# if len(sense_row[5]):
				# 	resource_2_senses.append(sense_row[9])

				if len(sense_row[4]) and len(sense_row[3]) and sense_row[3] != "NONE":
					david.update({sense_row[2] + "\t" + sense_match_dict[sense_row[4]]: sense_row[3]})

				if len(sense_row[6]) and len(sense_row[5]) and sense_row[5] != "NONE":
					john.update({sense_row[2] + "\t" +  sense_match_dict[sense_row[6]]: sense_row[5]})

				if len(sense_row[8]) and len(sense_row[7]) and sense_row[7] != "NONE":
					dorus.update({sense_row[2] + "\t" +  sense_match_dict[sense_row[8]]: sense_row[7]})
				

		body.append({
			"headword": headword,
			"David": david,
			"John": john,
			"Dorus": dorus
		})

	with open("EN_common.json", "w") as f:
	    json.dump(body, f, indent=4, ensure_ascii=False)		

######
with open("EN_common.json", "r") as f:
    english = json.load(f)

# Using the headword, find out how many senses in those headwords exist
with open("/Users/sina/My_GitHub/SeneAnnotation/0Experiments/EN_NUIG_MWSA_1.json", "r") as f:
	en_nuig = json.load(f)

num_all_senses, unique_aligned_senses = 0, 0
for entry_common in english:
	for entry in en_nuig["body"]:
		if entry_common["headword"] == entry["lemma"] + " (" + entry["part-of-speech_tag"] + ")":
			sense_combinations = list()
			for m in entry["resource_1_senses"]:
				for n in entry["resource_2_senses"]:
					if n["#text"] != m["#text"]:
						sense_combinations.append( m["#text"] + "\t" + n["#text"])
			num_all_senses += len(sense_combinations)
	unique_aligned_senses += len(list(set(list(entry_common["David"].keys()) + list(entry_common["John"].keys()) + list(entry_common["Dorus"].keys()))))

# print(num_all_senses)
# print(unique_aligned_senses)

kkk = ["exact", "narrower", "broader", "related", "NONE"]
kkk_map = {"exact": "Yes", "narrower": "Yes", "broader": "Yes", "related": "Yes", "NONE": "No"}
kkk_two_map = {"exact": 1, "narrower": 1, "broader": 1, "related": 1, "NONE": 0}

print(len(english))
num_annotator = 2
iaa_case = [5, 2]
print(num_all_senses - unique_aligned_senses)
for case in iaa_case:
	MATRIX = list()
	for i in english:
		sense_pairs = list(set(list(i["David"].keys()) + list(i["John"].keys()) + list(i["Dorus"].keys())))

		for sense in sense_pairs:
			row = [0, 0, 0, 0, 0]
			two_case_row = [0, 0] # David, John, Dorus

			if case == 5:
				row[kkk.index(i["David"].get(sense, "NONE"))] += 1
				row[kkk.index(i["John"].get(sense, "NONE"))] += 1
				row[kkk.index(i["Dorus"].get(sense, "NONE"))] += 1
				# print(", ".join([str(j) for j in row]))
				MATRIX.append(row)
			else:

				# two_case_row[0] = kkk_map[i["David"].get(sense, "NONE")]
				# two_case_row[1] = kkk_map[i["John"].get(sense, "NONE")]
				# two_case_row[2] = kkk_map[i["Dorus"].get(sense, "NONE")]

				two_case_row[kkk_two_map[i["David"].get(sense, "NONE")]] += 1
				two_case_row[kkk_two_map[i["John"].get(sense, "NONE")]] += 1
				two_case_row[kkk_two_map[i["Dorus"].get(sense, "NONE")]] += 1
				# print(", ".join([str(j) for j in two_case_row]))
				MATRIX.append(two_case_row)
				# MATRIX.append(row)

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
	with open("EN_"+str(case)+".txt", "w") as f:
		f.write("\n".join([", ".join(map(str, ii)) for ii in MATRIX]))