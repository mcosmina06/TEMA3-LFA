from typing import Dict, Tuple, Optional, List
import sys
import re

import tema2 

# elementele atomice pe care le-am putea gasi intr-o expresie aritmetica
EPS = ""
CONCAT = "+"
UNION = "|"
STAR = "*"
OPEN = "("
CLOSE = ")"
ALPHABET = []

class NFA:

    def __init__(self, NumberOfStates, StartState, FinaleStates, TransitionTable, Alfabet):
        self.NumberOfStates = NumberOfStates
        self.StartState = StartState
        self.FinaleStates = FinaleStates
        self.TransitionTable = TransitionTable
        self.Alfabet = Alfabet

class Expr:

    def eval(self):
        return None

class Concat(Expr):

    def __init__(self, left: Expr, right: Expr):
        self.left: Expr = left
        self.right: Expr = right

    def eval(self):
        NFA_left = self.left.eval()
        NFA_right = self.right.eval()

        Alfabet = list(set(NFA_left.Alfabet + NFA_right.Alfabet))
        StartState = 0
        NumberOfStates = NFA_left.NumberOfStates + NFA_right.NumberOfStates - 1
        
        # la concatenare pastrez tranzitiile nfa-ului din stanga, la care adaug
        # tranzitiile nfa-ului din dreapta dar redenmite
        TransitionTable = NFA_left.TransitionTable

        TransitionTable[NFA_left.FinaleStates] = {}

        # starea finala a nfa-ului din stanga devine starea initiala a nfa-uli din
        # dreapta; pentru redenumirea starilor am incrementat starile curente cu
        # numarul starii finale din nfa stanga
        for i in NFA_right.TransitionTable[StartState].keys():
            TransitionTable[NFA_left.FinaleStates][i] = [x + NFA_left.FinaleStates for x in NFA_right.TransitionTable[StartState][i]]

        # deoarece am procesat deja tranzitiile din prima stare, sterg aceasta 
        # intrare din dictionar
        del NFA_right.TransitionTable[StartState]

        # repet procesl si cu restul starilor
        for i in NFA_right.TransitionTable.keys():
            TransitionTable[i + NFA_left.FinaleStates] = {}
            for j in NFA_right.TransitionTable[i].keys():
                TransitionTable[i + NFA_left.FinaleStates][j] = [x + NFA_left.FinaleStates for x in NFA_right.TransitionTable[i][j]]

        # la final actualizez noua stare finala si numarul total de stari finale
        # ale noului nfa
        FinaleStates = NFA_right.FinaleStates + NFA_left.FinaleStates

        return(NFA(NumberOfStates, StartState, FinaleStates, TransitionTable ,Alfabet))


class Union(Expr):

    def __init__(self, left: Expr, right: Expr):
        self.left: Expr = left
        self.right: Expr = right

    def eval(self):

        # adaug o noua stare initiala si o noua stare finala
        # si redenumite starile din cele doua NFA-uri
        NFA_left = self.left.eval()
        NFA_right = self.right.eval()

        Alfabet = list(set(NFA_left.Alfabet + NFA_right.Alfabet))

        # noul Tabel de tranzitii
        TransitionTable = {}

        # adaug o noua stare initiala si adaug o tranzitie pe eps
        # pe starea initiala a NFA-ului din stanga care devine stare 1
        StartState = 0
        TransitionTable[0] = {}
        TransitionTable[0]['eps'] = [1]

        # parcurg tabela de tranzitii a NFA-ului din stanga si le adaug
        # in noua tabela dar redenumite, acestea vor creste cu 1
        for i in NFA_left.TransitionTable.keys():
            if (i + 1) not in TransitionTable.keys():
                TransitionTable[i + 1] = {}
            for j in NFA_left.TransitionTable[i].keys():
                TransitionTable[i + 1][j] = [x + 1 for x in NFA_left.TransitionTable[i][j]]
       
        # numarul cu care creste fiecare tranzitie din nfa dreapta
        k = NFA_left.NumberOfStates + 1

        # adaug tranzitia din noua stare initiala pe starea initiala din NFA-ul
        # din dreapta dar redenumita
        TransitionTable[0]['eps'].append(k)

        # parcurg tabela de tranzitii a NFA-ului din dreapta si le adaug
        # in noua tabela dar redenumite
        for i in NFA_right.TransitionTable.keys():
            if (i + k) not in TransitionTable.keys():
                TransitionTable[i + k] = {}
            for j in NFA_right.TransitionTable[i].keys():
                TransitionTable[i + k][j] = [x + k for x in NFA_right.TransitionTable[i][j]]
       
        # noua stare finala este
        FinaleStates = 1 + NFA_left.NumberOfStates + NFA_right.NumberOfStates
        NumberOfStates = 2 + NFA_left.NumberOfStates + NFA_right.NumberOfStates
        
        #adaug tranzitile pentru aceatsa
        TransitionTable[NFA_left.FinaleStates + 1] = {}
        TransitionTable[NFA_left.FinaleStates + 1]['eps'] = [FinaleStates]

        TransitionTable[NFA_right.FinaleStates + k] = {}
        TransitionTable[NFA_right.FinaleStates + k]['eps'] = [FinaleStates]

        return(NFA(NumberOfStates, StartState, FinaleStates, TransitionTable, Alfabet))

class Star(Expr):

    def __init__(self, expr: Expr):
        self.expr: Expr = expr

    def eval(self):
        nfa = self.expr.eval()

        # noul Tabel de tranzitii
        TransitionTable = {}

        # adaug o noua stare initiala si adaug o tranzitie pe eps
        # pe starea initiala a NFA-ului anterior care devine stare 1
        StartState = 0
        TransitionTable[0] = {}
        TransitionTable[0]['eps'] = [1]

        # adaug tranzitie pe epsilon intre starea finala si starea initiala
        # a NFA ului
        nfa.TransitionTable[nfa.FinaleStates] = {}
        nfa.TransitionTable[nfa.FinaleStates]['eps'] = [nfa.StartState]

        # redenumesc tranzitiile din NFA si le adag in noua tabela
        for i in nfa.TransitionTable.keys():
            if (i + 1) not in TransitionTable.keys():
                TransitionTable[i + 1] = {}
            for j in nfa.TransitionTable[i].keys():
                TransitionTable[i + 1][j] = [x + 1 for x in nfa.TransitionTable[i][j]]
        
        # adaug o noua stare finala si tranzitie catre aceasta din vechea stare finala 
        FinaleStates = nfa.FinaleStates + 2
        TransitionTable[nfa.FinaleStates + 1]['eps'].append(FinaleStates)
        
        TransitionTable[0]['eps'].append(FinaleStates)

        return(NFA(nfa.NumberOfStates + 2, StartState, FinaleStates, TransitionTable, nfa.Alfabet))

class Par(Expr):
    def __init__(self, expr: Expr):
        self.expr: Expr = expr

    def eval(self):
        return self.expr.eval()

class Character(Expr):
    def __init__(self, letter: str):
        self.letter = letter

    def eval(self):
        #returnez AFN-ul literei rexpective care e format din 2 stari si o tranzitie
        TransitionTable = {}
        TransitionTable[0] = {}
        TransitionTable[0][self.letter] = [1]
        return (NFA(2, 0, 1, TransitionTable, [self.letter]))

class Parser:
    def __init__(self):
        self.states: List[int] = [0, 1]
        self.initialState = 0
        self.finalStates: List[int] = [1]
        self.transitions: Dict[Tuple[int, (str, str, str)], int] = {} 

        # adaug tranzitiile pentru pda format din 2 stari
        self.transitions[0, (OPEN, EPS, OPEN)] = 0
        for letter in ALPHABET:
            self.transitions[0, (letter, EPS, letter)] = 1
            self.transitions[1, (letter, EPS, letter)] = 0
        self.transitions[1, (CLOSE, EPS, CLOSE)] = 1
        self.transitions[1, (CONCAT, EPS, CONCAT)] = 0
        self.transitions[1, (UNION, EPS, UNION)] = 0
        self.transitions[1, (STAR, EPS, STAR)] = 1

        self.stack = []

    # intoarce elementele din varful stivei
    def peek(self, pos):
        if pos < len(self.stack):
            return self.stack[-(pos + 1)]
        return None

    # primeste starea curenta si intoarce starea urmatoare in functie de litera
    # ce trebuie consumata
    def nextState(self, currentState: int, word: str) -> Optional[int]:
        # se trece prin toate tranzitiile pda-ului si cautam perechea formata
        # din starea si litera data
        for (state, transition) in self.transitions.keys():
            if state == currentState:
                if word[0] == transition[0]:
                    # facem push pe stiva 
                    if transition[2] != EPS:
                        self.stack.append(transition[2])
                    # Returnam starea urmatoare
                    return self.transitions[(state, transition)]
        return None

    # scoate caracterul de pe stiva si il pune la loc dar sub forma Character
    def reduceCharacter(self):
        letter = self.stack.pop()
        self.stack.append(Character(letter))

    # scoate expresia dintre cele 2 paranteze, '(' si ')', de pe stiva si o
    # pune la loc sub forma de dar Par
    def reducePar(self):
        self.stack.pop()
        expr = self.stack.pop()
        self.stack.pop()
        self.stack.append(Par(expr))
    
    # scoate cele doua expresii de pe stiva si le pune la loc sub forma de Concat
    def reduceConcat(self):
        expr1 = self.stack.pop()
        self.stack.pop()
        expr2 = self.stack.pop()
        self.stack.append(Concat(expr2, expr1))

    # scoate cele doua expresii de pe stiva si le pune la loc sub forma de Union
    def reduceUnion(self):
        expr1 = self.stack.pop()
        self.stack.pop()
        expr2 = self.stack.pop()
        self.stack.append(Union(expr2, expr1))

    # scoate expresia de pe stiva si o pune la loc sub forma de Star
    def reduceStar(self):
        self.stack.pop()
        expr = self.stack.pop()
        self.stack.append(Star(expr))

    def reduce(self) -> bool:

        # daca in varful stivei se afla un caracter atunci apelam reduceCharacter
        if self.peek(0) in ALPHABET:
            self.reduceCharacter()
            return True

        # daca in varful stivei se afla o ')', inseamna ca trebuie 
        # apela reducePar => ca reducerile de tip Star sa Concat au fost deja executate
        # si daca exista reduceri de tipul Union le facem acum, fiind cea mai "slaba"
        if self.peek(0)  == ")":
            while(1):
                if self.peek(2) == "|":
                    aux = self.stack.pop()
                    self.reduceUnion()
                    self.stack.append(aux)
                else:
                    break;
            # dupa ce am executat toate reducerile de tip Union putem reduce Paranteza
            self.reducePar()
            return True

        # daca in varul stivei se afla deja ceva de tipul Expr verificam daca elementul
        # anterior este '+' inseamna ca trebuie redusa Concatenarea
        if self.peek(1) == "+" and isinstance(self.peek(0), Expr):
            self.reduceConcat()
            return True

        # daca in varful stivei se afla '*', apelem reduceStar
        if self.peek(0) == "*":
            self.reduceStar()
            return True    

        return False

    # parsarea se incepe din stare intiala, si cat timp nu am ajuns la finalul
    # cuvantului trec la starea urmatoare
    def parse(self, word: str) -> Optional[Expr]:
        
        currentState = self.initialState
        while word != EPS:

            currentState = self.nextState(currentState, word)
            if currentState is None:
                break
            word = word[1:]

            # cat timp citesc star apelez reduce, trec la starea urmatoare si 
            # consum si caracterul din cuvant
            while (1):
                if(word[:1] == "*"):
	                self.reduce()
	                currentState = self.nextState(currentState, word)
	                word = word[1:]
                else:
	                break
            # cat timp am pe stiva ce reduce, reduc
            while self.reduce():
                continue

        # daca am terminat de consumat inputul, au ramas, daca exista, de facut
        # doar redcerile de tip union ce nu s-au alfat in interiorul unor paranteze
        while len(self.stack) != 1:
        	self.reduceUnion()

        if word != EPS and len(self.stack) != 1:
            return None

        return self.stack.pop()

def read_input(filename):
    InputFile = open(filename, "r")
    data = InputFile.readlines()
    InputFile.close()
    return data[0]

# pentru usurinta am introdus caracterul '+' ce reprezinta concatenarea in input
def convertInput(word) -> str:
    new = word[:1]

    for i in range(1, len(word)):
        if (word[i] in ALPHABET):
            if (new[-1] in ALPHABET) or (new[-1] == ")") or (new[-1] == "*"):
                 new += "+"
        elif (word[i] == "(") and (new[-1] in ALPHABET):
            new += "+"
        elif (word[i] == "(") and (new[-1] == "*"):
            new += "+"
        elif (new[-1] == ")") and (word[i] == "("):
            new += "+"
        new += word[i]

    return new

def generateAlphabet(word):
    global ALPHABET 
    ALPHABET =  list(("".join(re.split("[^a-zA-Z]*", word))))

# scrierea outputului in fisier
def write_output(filename, nfa):
    OutputFile = open(filename, "w")

    OutputFile.write(str(nfa.NumberOfStates))
    OutputFile.write(str("\n"))
    
    OutputFile.write(str(nfa.FinaleStates))
    OutputFile.write(str("\n"))

    for i in nfa.TransitionTable.keys():
        for j in nfa.TransitionTable[i]:
            OutputFile.write(str(i) + str(" ") + str(j))
            for k in nfa.TransitionTable[i][j]:
                OutputFile.write(str(" ") + str(k))
            OutputFile.write(str("\n"))

    OutputFile.close()

if __name__ == '__main__':
    string = read_input(str(sys.argv[1]))
    generateAlphabet(string)
    regex = convertInput(string)
    parser = Parser()
    expr = parser.parse(regex)
    if expr is not None:
        nfa = expr.eval()
    else:
        print("Nu am putut parsa cuvantul")
    print(nfa.TransitionTable)
    write_output(str(sys.argv[2]), nfa)
    tema2.main(str(sys.argv[2]), str(sys.argv[3]))
