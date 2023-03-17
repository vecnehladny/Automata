import tkinter as tk
from tkinter import scrolledtext, Label, Frame
import re
from automata.fa.dfa import DFA
from automata.base.exceptions import RejectionException


def norm(txt):
    return re.sub("[^\S\r\n]", "", txt)


def removeNLs(txt):
    return re.sub("[\r\n]", "", txt)


def parseSpeed(s):
    try:
        value = int(s)
        if value <= 0:
            value = 1000
    except ValueError:
        return 1000;
    return value


class MyDFA(DFA):

    def read_input_stepwise(self, input_str, ignore_rejection=False):
        """
        Check if the given string is accepted by this DFA.
        Yield the current configuration of the DFA at each step.
        """
        current_state = self.initial_state

        yield current_state
        for input_symbol in input_str:
            current_state = self._get_next_current_state(
                current_state, input_symbol)
            yield current_state

        if not ignore_rejection:
            self._check_for_input_rejection(current_state)


class Automaton:

    def __init__(self, parser):
        self.parser = parser
        self.npda = None
        self.steps = None
        self.canStep = True
        self.simulating = False
        return

    def stop(self, text_area_C=None):
        self.npda = None
        self.steps = None
        if text_area_C is not None:
            text_area_C.delete('1.0', 'end')
        self.canStep = True
        self.simulating = False
        return

    def initialize(self, txtAreaT, txtAreaF, txtAreaI):
        txtTrans = txtAreaT.get("1.0", "end")
        txtF = txtAreaF.get("1.0", "end")
        txtI = txtAreaI.get("1.0", "end")
        definition = self.parser.parse(txtTrans, txtF)
        print(definition)
        self.dfa = MyDFA(**definition)
        self.steps = self.dfa.read_input_stepwise(removeNLs(txtI))
        return

    def step(self, txtAreaT, txtAreaF, txtAreaI, text_area_C):
        if (self.canStep == False):
            return
        if self.steps is None:
            self.initialize(txtAreaT, txtAreaF, txtAreaI)
        try:
            confs = next(self.steps)
            items = {}
            # TODO: print states to Priebeh text area
            if confs:
                text_area_C.insert(tk.END, confs + "\n")
            print(confs)
        except StopIteration:
            print("ACCEPTED!!!")
            text_area_C.insert(tk.END, ("─" * 11 + "\n") + "ACCEPTED!!!")
            self.canStep = False
        except RejectionException:
            print("REJECTED!!!")
            text_area_C.insert(tk.END, ("─" * 11 + "\n") + "REJECTED!!!")
            self.canStep = False
        text_area_C.see(tk.END)
        return


class Parser:

    def __init__(self):
        return

    def parse(self, txtTrans, txtF):
        transitions = {}
        states = set()
        inputSymbols = set()

        normedTrans = norm(txtTrans)

        matches = re.finditer("d\(([a-z]\d*),([a-z]|\d|)\)=\(([a-z]\d*)\)", normedTrans)
        for match in matches:

            state = match.group(1)
            inputSymbol = match.group(2)
            newState = match.group(3)

            states.add(state)
            inputSymbols.add(inputSymbol)

            if state not in transitions:
                transitions[state] = {}
            if inputSymbol not in transitions[state]:
                transitions[state][inputSymbol] = {}
            transitions[state][inputSymbol] = newState

        inputSymbols.discard('')
        states.add('q0')

        normedF = norm(txtF)
        match = re.match("\{(([a-z]\d*)(,[a-z]\d*)*)\}", normedF)
        finalStates = set(match.group(1).split(',')) if match is not None else set()

        states.add('q0')
        states.update(finalStates)

        definition = {
            'states': states,
            'input_symbols': inputSymbols,
            'transitions': transitions,
            'initial_state': 'q0',
            'final_states': finalStates,
        }
        return definition


if __name__ == "__main__":
    # Creating tkinter main window
    win = tk.Tk()
    win.title("DFA Sim")

    parser = Parser()
    automaton = Automaton(parser)

    font = ("Consolas", 12)

    label = Label(text="Definícia", anchor="w", font=font)
    label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
    text_area = scrolledtext.ScrolledText(
        win,
        wrap=tk.WORD,
        width=40,
        height=9,
        font=font
    )
    text_area.grid(row=1, column=0, padx=10)
    text_area.insert(tk.INSERT, "\n".join((
        "M = (K, S, d, q0, F)\n",
        "K je konečná množina stavov",
        "S je vstupná abeceda",
        "d je prechodová funkcia",
        "q0 je počiatočný stav",
        "F je množina koncových stavov"
    )))
    text_area.config(state=tk.DISABLED)

    label = Label(text="F", anchor="w", font=font)
    label.grid(row=2, column=0, sticky="w", padx=10, pady=(10, 0))
    text_area_F = scrolledtext.ScrolledText(
        win,
        wrap=tk.WORD,
        width=40,
        height=1,
        font=font
    )
    text_area_F.grid(row=3, column=0, padx=10)
    text_area_F.insert(tk.INSERT, "{q6}")

    label = Label(text="Prechodové funkcie", anchor="w", font=font)
    label.grid(row=4, column=0, sticky="w", padx=10, pady=(10, 0))
    text_area_T = scrolledtext.ScrolledText(
        win,
        wrap=tk.WORD,
        width=40,
        height=10,
        font=font
    )
    text_area_T.grid(row=5, column=0, pady=(0, 10), padx=10)
    text_area_T.insert(tk.INSERT, "\n".join(("d(q0,a)=(q1)",
                                             "d(q0,b)=(q0)",
                                             "d(q1,a)=(q2)",
                                             "d(q1,b)=(q0)",
                                             "d(q2,a)=(q2)",
                                             "d(q2,b)=(q3)",
                                             "d(q3,a)=(q4)",
                                             "d(q3,b)=(q0)",
                                             "d(q4,a)=(q2)",
                                             "d(q4,b)=(q5)",
                                             "d(q5,a)=(q1)",
                                             "d(q5,b)=(q6)",
                                             "d(q6,a)=(q6)",
                                             "d(q6,b)=(q6)",)))

    label = Label(text="Priebeh", anchor="w", font=font)
    label.grid(row=0, column=1, sticky="w", padx=10, pady=(10, 0))

    cframe = Frame(win)
    vbar = tk.Scrollbar(cframe)
    vbar.pack(side=tk.RIGHT, fill="y")
    hbar = tk.Scrollbar(cframe, orient=tk.HORIZONTAL)
    hbar.pack(side=tk.BOTTOM, fill="x")
    text_area_C = tk.Text(
        cframe,
        width=110,
        yscrollcommand=vbar.set,
        xscrollcommand=hbar.set,
        wrap="none",
        font=("Consolas", 8)
    )
    text_area_C.pack(expand=1, fill=tk.BOTH)
    hbar.config(command=text_area_C.xview)
    vbar.config(command=text_area_C.yview)
    cframe.grid(row=1, column=1, rowspan=7, pady=(0, 10), padx=10, sticky="ns")

    label = Label(text="Vstup", anchor="w", font=font)
    label.grid(row=6, column=0, sticky="w", padx=10)
    text_area_I = scrolledtext.ScrolledText(
        win,
        wrap=tk.WORD,
        height=2,
        width=40,
        font=font
    )
    text_area_I.grid(row=7, column=0, pady=(0, 10), padx=10)
    text_area_I.insert(tk.INSERT, "babaababaababbababa")

    bframe = Frame(win)
    bframe.grid(row=8, column=0, columnspan=2, sticky="nsew")

    button1 = tk.Button(bframe, text="Stop", command=lambda: automaton.stop(text_area_C))
    button1.grid(row=0, column=0, pady=(0, 10), padx=(10, 0))

    def __simulate():
        if automaton.simulating == True and automaton.canStep == True:
            automaton.step(text_area_T, text_area_F, text_area_I, text_area_C);
            text_area_C.after(500, __simulate)


    def simulate():
        if automaton.simulating == False:
            automaton.simulating = True
            __simulate()

    simButton = tk.Button(bframe, text="Simuluj", command=simulate)
    simButton.grid(row=0, column=2, pady=(0, 10))

    button1 = tk.Button(bframe, text="Krok",
                        command=lambda: automaton.step(text_area_T, text_area_F, text_area_I, text_area_C))
    button1.grid(row=0, column=1, pady=(0, 10))

    # Placing cursor in the text area
    text_area_T.focus()
    win.resizable(False, False)
    win.mainloop()
