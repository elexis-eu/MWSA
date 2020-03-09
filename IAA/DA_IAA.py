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

with open("/Users/sina/My_GitHub/SeneAnnotation/0Experiments/DA_CST_MWSA.json") as json_file:
	dsl = json.load(json_file)["body"]

with open("/Users/sina/My_GitHub/SeneAnnotation/0Experiments/DA_CST_MWSA.json") as json_file:
	common = json.load(json_file)["body"]

print("number of annotated entries", len(common))

k = ["exact", "narrower", "broader", "related", "both"]

MATRIX = list()
MATRIX_two = list()

for sense in common:
	# print(sense)
	sense_alignments = dict()
	for m in sense["alignment"]:
		if (m["sense_source"], m["sense_target"]) not in sense_alignments:
			sense_alignments[(m["sense_source"], m["sense_target"])] = [m["semantic_relationship"]]
		else:
			sense_alignments[(m["sense_source"], m["sense_target"])].append( m["semantic_relationship"] )

	for dsl_index in range(len(dsl)):
		s = dsl[dsl_index]
		N = list()
		if sense["lemma"] == s["lemma"] and sense["part-of-speech_tag"] == s["part-of-speech_tag"]:
			for i in s["resource_1_senses"]:
				for j in s["resource_2_senses"]:
					N.append((i["#text"], j["#text"]))
			break

	N_mat = np.zeros((len(N),len(k)), dtype=int) # five 
	two_mat = np.zeros((len(N),2), dtype=int) # two case

	for key in N:

		row = [0, 0, 0, 0, 0]
		two_row = [0, 0] # yes no
		if key in sense_alignments:
			for n in sense_alignments[key]:
				row[k.index(n)] += 1
		else:
			row[k.index("both")] += 2
		
		if sum(row) <2:
			row[k.index("both")] += 1	

		N_mat[N.index(key)] = row

		# check if both have annotated
		two_row[1] = row[k.index("both")] 
		two_row[0] = 2 - two_row[1]
		two_mat[N.index(key)] = two_row

		# print(", ".join([str(j) for j in row]))
		# print(", ".join([str(j) for j in two_row]))
	
	MATRIX.append(N_mat)
	MATRIX_two.append(two_mat)
	# print(N_mat)
	# kappa = fleiss_kappa(N_mat)
	# print(kappa)
	# ave += kappa
	
	# print(row)
# print(MATRIX)

print("5")
arr = np.vstack(MATRIX)
kappa = fleiss_kappa(arr)
alpha = krippendorff.alpha(arr)
print(kappa)
print(alpha)
print()
print("2")
arr_two = np.vstack(MATRIX_two)
kappa = fleiss_kappa(arr_two)
alpha = krippendorff.alpha(arr_two)
print(kappa)
print(alpha)


with open("DA_2.txt", "w") as f:
	f.write("\n".join([", ".join(map(str, ii)) for ii in [item for sublist in MATRIX_two for item in sublist]]))
with open("DA_5.txt", "w") as f:
	f.write("\n".join([", ".join(map(str, ii)) for ii in [item for sublist in MATRIX for item in sublist]]))

	
			