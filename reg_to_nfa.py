## Visuals borrowed from Mr. Shlok Pandey's github account: b30wulffz
from graphviz import Digraph
import tempfile

EPSILON = 'e'
#EPSILON = "$"
###########################
"""
NFA is defined as a dictionary
{
   "states": [
       <state_ids>,
       ...
   ],
   "initial_state": <initial_state_id>,
   "final_states": [
       <state_ids>,
       ...
   ],
   "alphabet": [
      "$",
       <symbols>,
      ...
   ],
   "transition_function": {
       <state_id>: {
           <symbol>: [
               <state_ids>,
           ],
           ... # transition for all alphabet symbols shoud be present here
       },
       ...
   }
}
"""

"""
DFA is also defined similarly
{
   "states": [
       "phi",
       <state_ids>,
       ...
    ],
    "initial_state": <state_id>,
    "final_states":[
       <state_ids>,
       ...
    ],
    "alphabet": [
       <symbols>,
       ...
    ],
    "transition_function": {
        <state_id>: {
            <symbol>: <state_id>,
            ... # transition for all alphabet symbols shoud be present here. In case of no transition, symbol must point to phi
        },
        ...
    },
    "reachable_states": [
        <state_ids>,
        ...
    ],
    "final_reachable_states": [
        <state_ids>,
        ...
    ],
}
"""
################################
################################
################################
#REGEX TO NFA
#Input: string reg_exp
#Output: NFA nfa such that L(nfa) = L(reg_exp)
def regex_to_nfa(reg_exp):
    """
       S  -> U S1 
       S1 -> + S
       S1 -> eps
       U  -> C U1
       U1 -> U
       U1 -> eps
       C  -> F C1
       C1 -> * C1
       C1 -> eps
       F  -> character
       F  -> ( S )
    """
    ll1_table = {}
    ll1_table['@S']  = {'$': [], '(': ['@U', '@S1'], 'isalpha': ['@U', '@S1'] }
    ll1_table['@S1'] = {'$': [],  ')': [],  '+': ['+', '@S'] }
    ll1_table['@U']  = {'(': ['@C', '@U1'], 'isalpha': ['@C', '@U1'] }
    ll1_table['@U1'] = {'$': [],  ')': [],  '+': [], '(': ['@U'], 'isalpha': ['@U']  }
    ll1_table['@C']  = {'(': ['@F', '@C1'], 'isalpha': ['@F', '@C1'] }
    ll1_table['@C1'] = {'$': [], '(': [], ')': [], 'isalpha': [], '*': ['*', '@C1'], '+': []}
    ll1_table['@F'] =  {'(': ['(', '@S', ')'], 'isalpha': ['isalpha'] }

    input = reg_exp + '$'
    root  = ['@S', []]
    stack = [root]
    while stack:
        state, stack = stack[0], stack[1:]
        symbol = state[0]
        if symbol[0] != '@': # terminal
            if (symbol == 'isalpha' and input[0].isalpha()) or symbol == input[0]: 
                state[1].append(input[0])
                input = input[1:]
            else:
                print("invalid input 1: " + input)
                exit()
        else:            
            ch = 'isalpha' if input[0].isalpha() else input[0]
            trans  = ll1_table[symbol].get(ch, None)
            if trans is None:
                print(symbol, ch, stack)
                print("invalid input 2: " + input)
                exit()
            op = [ [sym, []] for sym in trans ]
            state[1] = op
            stack = op + stack
    
    if input != '$':
        print("invalid input 3: " + input)
        exit()

    statename = -1
    transfn = {}
    states = []
    alpha = set()
    def gen():
        nonlocal statename
        statename += 1
        newstate = f"q{statename}"
        states.append(newstate)
        return newstate

    def pair():
        return (gen(), gen())
        
    def t(From, To, char = EPSILON):
        if char != EPSILON:
            alpha.add(char)
        if not From in transfn:
            transfn[From] = {}
        if not char in transfn[From]:
            transfn[From][char] = []
        transfn[From][char].append(To)
    
    def nfa_character(ch):
        st, ed = pair()
        t(st, ed, ch)
        return (st, ed)
        
    def nfa_star(n):
        sst, sed = n
        st, ed = pair()
        t(st, sst)
        t(sed, ed)
        t(ed, st)
        t(st, ed)
        return (st, ed)
        
    def nfa_union(n1, n2):
        st1, ed1 = n1
        st2, ed2 = n2
        st, ed = pair()
        t(st, st1)
        t(st, st2)
        t(ed1, ed)
        t(ed2, ed)
        return (st, ed)
        
    def nfa_concat(n1, n2):
        st1, ed1 = n1
        st2, ed2 = n2
        t(ed1, st2)
        return (st1, ed2)
        
    def convert(ast):
        name, sub = ast
        if name == '@S':
            if len(sub):
                left = convert(sub[0])
                right = convert(sub[1])
                if right is None:
                    return left
                else:
                    return nfa_union(left, right)
            else:
                return nfa_character(EPSILON)
        elif name == '@S1':
            if not sub:
                return None
            else:
                return convert(sub[1])
        elif name == '@U':
            left = convert(sub[0])
            right = convert(sub[1])
            if right is None:
                return left
            else:
                return nfa_concat(left, right)
        elif name == '@U1':
            if not sub:
                return None
            else:
                return convert(sub[0])
        elif name == '@C':
            left = convert(sub[0])
            right = convert(sub[1])
            if right is None:
                return left
            else:
                return nfa_star(left)
        elif name == '@C1':
            if len(sub):
                return True
            else:
                return None
        elif name == '@F':
            if len(sub) == 1:
                return convert(sub[0])
            else:
                return convert(sub[1])
        elif name == 'isalpha':
            return nfa_character(sub[0])
        else:
            print(ast)
    # print(root)                
    st, ed = convert(root)
    nfa = {}
    nfa['states'] = list(states)
    nfa['initial_state'] = st
    nfa['final_states'] = [ed]
    nfa['alphabet'] = ['$'] + list(alpha)
    nfa['transition_function'] = transfn
    for st in states:
        if st not in transfn:
            transfn[st] = {}
        for ch in ['$', EPSILON] + list(alpha):
            if not ch in transfn[st]:
                transfn[st][ch] = []
    # print(nfa)
    return nfa

################################
################################
################################
#Input: NFA nfa, string s
#Output: 1 if s is accepted by nfa, 0 otherwise. 
def in_language(nfa, s):
    start = set([nfa['initial_state']])
    transfn = nfa['transition_function']
    update = True
    while update:
        update = False
        newst = set(start)
        for st in start:
            for nn in transfn[st][EPSILON]:
                if nn not in newst:
                    update = True
                    newst.add(nn)
        start = newst
    while s != '':
        a = s[0]
        if a not in nfa['alphabet']:
            return 0
        s = s[1:]
        newst = set()
        for st in start:
            for nn in transfn[st][a]:
                if nn not in newst:
                    update = True
                    newst.add(nn)
        start = newst
        update = True
        while update:
            update = False
            newst = set(start)
            for st in start:
                for nn in transfn[st][EPSILON]:
                    if nn not in newst:
                        update = True
                        newst.add(nn)
            start = newst    
    for ed in nfa['final_states']:
        if ed in start:
            return 1
    return 0

################################
################################
###############################
#DRAW NFA / DFA
def draw_nfa(nfa, title=""):
    state_name = {}
    i = 0
    for state in nfa["states"]:
        state_name[state] = "q{}".format(i)
        i+=1

    g = Digraph()
    g.attr(rankdir='LR')

    if title == "":
        title = r'\n\nNFA'
    else:
        title = r'\n\nNFA : '+title
    g.attr(label=title, fontsize='30')

    # mark goal states
    g.attr('node', shape='doublecircle')
    for state in nfa['final_states']:
        g.node(state_name[state])

    # add an initial edge
    g.attr('node', shape='none')
    g.node("")
    
    g.attr('node', shape='circle')
    g.edge("", state_name[nfa["initial_state"]])

    for state in nfa["states"]:
        for symbol in nfa["transition_function"][state]:
            for transition_state in nfa["transition_function"][state][symbol]:
                g.edge(state_name[state], state_name[transition_state], label= symbol if symbol != EPSILON else u'\u03F5')

    g.view(tempfile.mktemp('.gv'))

def draw_dfa(dfa, title=""):
    state_name = {}
    i = 0
    for state in dfa["reachable_states"]:
        if state == "phi":
            state_name[state] = u'\u03A6'
        else:
            state_name[state] = "q{}".format(i)
            i+=1

    g = Digraph()
    g.attr(rankdir='LR')

    if title == "":
        title = r'\n\nDFA'
    else:
        title = r'\n\nDFA : '+title
    g.attr(label=title, fontsize='30')

    # mark goal states
    g.attr('node', shape='doublecircle')
    for state in dfa["final_reachable_states"]:
        g.node(state_name[state])

    # add an initial edge
    g.attr('node', shape='none')
    g.node("")
    
    g.attr('node', shape='circle')
    g.edge("", state_name[dfa["initial_state"]])

    for state in dfa["reachable_states"]:
        for symbol in dfa["transition_function"][state].keys():
            transition_state = dfa["transition_function"][state][symbol]
            g.edge(state_name[state], state_name[transition_state], label= symbol)

    g.view(tempfile.mktemp('.gv'))

################################
################################
################################
#MAIN
if __name__ == "__main__":
    reg_exp = "a(a+b)*b"
    #reg_exp = "(a+ab)(a*+b)"
    #reg_exp = "(a+b)*"
    #reg_exp = ''
    #reg_exp = "abc"
    #reg_exp = "(e+f)*"

    nfa = regex_to_nfa(reg_exp)
    #print(nfa)
    print("1 if s is accepted by nfa, 0 otherwise.")
    print("Answers: ",in_language(nfa, 'ab'))
    draw_nfa(nfa, reg_exp)
    
    
