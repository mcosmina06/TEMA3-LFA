import sys

class AF:
    def __init__(self, NumberOfStates, StartState, FinaleStates, TransitionTable, Alfabet):
        self.NumberOfStates = NumberOfStates
        self.StartState = StartState
        self.FinaleStates = FinaleStates
        self.TransitionTable = TransitionTable
        self.Alfabet = Alfabet
#functia returneaza multimea de stari in care putem ajunge
#dintr-o multime de stari data si un caracter
def compute_SetOfTans_from_SetOfTans(TransitionTable, M1, c): 
	M2 = set()

	for i in M1:
		if c in TransitionTable[i].keys():
			for i in TransitionTable[i][c]:
				M2.add(i)
	return M2
# generez multimea de epsilon inchidere ce este reprezentata
# printr - o lista de seturi corespunzatoare fiecarei stari
# a NFA ului
def compute_EpsilonClosure(TransitionTable):
	n = len(TransitionTable.keys())
	MofEpsilons = [set() for i in range(n)]
	# pentru fiecare dictionar corespunzator starilor din dictionarul 
	# principal verific daca exista sau nu tranzitie pe epsilon
	for i in TransitionTable.keys():
		# daca nu exista atunci o adaug doar pe ea insasi in set
		if 'eps' not in TransitionTable[i].keys():
			MofEpsilons[i] = set()
			MofEpsilons[i].add(i)
		# in caz contrar extrag lista de valori specifica nodului pe
		# calea epsilon, adaug si starea curent si apoi pentru fiecare
		# stare dinn EpsAux caut caile pe epsilon si adaug starile care
		# nu sunt deja prezente
		else:
			EpsAux = TransitionTable[i]['eps']
			EpsAux.append(i)
			for j in EpsAux:
				if 'eps' not in TransitionTable[j].keys():
					continue
				for k in TransitionTable[j]['eps']:
					if k not in EpsAux:
						EpsAux.append(k)
			MofEpsilons[i] = set(sorted(EpsAux))
	return MofEpsilons

def compute_EpsilonClosure2(TransitionTable):
	n = len(TransitionTable.keys())
	MofEpsilons = [set() for i in range(n)]
	for i in (TransitionTable.keys()):
		MofEpsilons[i] = set()
		MofEpsilons[i] = compute_SetOfTans_from_SetOfTans(TransitionTable, [i], 'eps')
		MofEpsilons[i].add(i)
	ok = 0
	while ok == 0:                                              
		ok = 1                                                  
		for i in range(n):
			ex = MofEpsilons[i]
			for j in MofEpsilons[i]:
				MofEpsilons[i] = MofEpsilons[i] | MofEpsilons[j]
				if ex != MofEpsilons[i]:
					ok = 0
	return MofEpsilons

# generez a doua matrice de tranzitii de forma: un dictionar care are drept
# chei caracterele din alfabet si ca valori rezultatele generate de compute_SetOfTans_from_SetOfTans
# pentru fiecare stare generata de compute_EpsilonClosure
def compute_TransitionTable2(NFA):
	n = len(NFA.Alfabet)
	m = len(NFA.TransitionTable.keys())
	EpsilonClosure = compute_EpsilonClosure2(NFA.TransitionTable)
	TransitionTable2 = {}
	queue = [EpsilonClosure[0]]
	for state in queue:
		TransitionTable2[queue.index(state)] = {}
		for i in NFA.Alfabet:
			if i == 'eps':
				continue
			aux = compute_SetOfTans_from_SetOfTans(NFA.TransitionTable, state, i)
			new_state = aux
			for j in aux:
				new_state = new_state | EpsilonClosure[j]
			TransitionTable2[queue.index(state)][i] = new_state
			if new_state not in queue:
				queue.append(new_state)
	
	NewFinalStates = []
	for i in queue:
		for k in NFA.FinaleStates:
			if k in i:
				NewFinalStates.append(queue.index(i))

	for i in TransitionTable2.keys():
		for j in TransitionTable2[i]:
			TransitionTable2[i][j] = queue.index(TransitionTable2[i][j])

	return AF(len(TransitionTable2.keys()), 0, NewFinalStates, TransitionTable2, NFA.Alfabet)

def read_input(filename):
    InputFile = open(filename, "r")
    data = InputFile.readlines()
    InputFile.close()
    alfabet = []

    #numarul de stari
    NumberOfStates = int(data[0])
    #print(NumberOfStates)
   
    #lista starilor finale
    FinaleStates = []
    for i in data[1].split(" "):
        FinaleStates.append(int(i))
    #print(FinaleStates)
    
    #matricea de tranzitii de forma TransitionTable{0:{a:0, b:2}, 1:{a:2}}
    TransitionTable = {}
    for i in range(0, NumberOfStates):
        TransitionTable[i] = {}
    
    for i in data[2:]:
        line = i.split(" ")
        TransitionTable[int(line[0])][line[1]] = []
        for j in line[2:]:
        	TransitionTable[int(line[0])][line[1]].append(int(j))
        	if line[1] not in alfabet:
        		alfabet.append(line[1])
    alfabet.sort()
    return AF(NumberOfStates, 0, FinaleStates, TransitionTable, alfabet)

def write_output(filename, DFA):
	OutputFile = open(filename, "w")

	OutputFile.write(str(DFA.NumberOfStates))
	OutputFile.write(str("\n"))
	
	for i in DFA.FinaleStates:
		OutputFile.write(str(i))
		if i != DFA.FinaleStates[len(DFA.FinaleStates) - 1]:
			OutputFile.write(str(" "))
	OutputFile.write(str("\n"))

	for i in DFA.TransitionTable.keys():
		for j in DFA.TransitionTable[i]:
			OutputFile.write(str(i) + str(" ") + str(j) + str(" ") + str(DFA.TransitionTable[i][j]))
			OutputFile.write(str("\n"))

	OutputFile.close()
	

def main(inputFile, outputFile):
	NFA = read_input(inputFile)
	DFA = compute_TransitionTable2(NFA)
	write_output(outputFile, DFA)
	