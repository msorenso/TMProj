#!/usr/bin/env python3
import csv
import sys
from collections import defaultdict
max_depth = 75

#reads in the machine description and stores it in a dictionary
def load_machine(file_path):
    machine = {
        "trans": defaultdict(list),  # store transitions
        "name": None,
        "states": [],  # list of states (Q)
        "sigma": [],  # input symbols (Σ)
        "gamma": [],  # tape symbols (Γ)
        "start_state": None,  # start state
        "accept_state": None,  # accept state
        "reject_state": None,  # reject state
    }
    
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        lines = list(reader)

        #parse machine description
        machine["name"] = lines[0][0]
        machine["states"] = lines[1]
        machine["sigma"] = lines[2]
        machine["gamma"] = lines[3]
        machine["start_state"] = lines[4][0]
        machine["accept_state"] = lines[5][0]
        machine["reject_state"] = lines[6][0]
        
        #parse transitions
        for line in lines[7:]:
            if len(line) >= 5:
                state, read, next_state, write, move = line
                machine["trans"][(state, read)].append((next_state, write, move))
    
    return machine

#processes a given transition and returns the next state(s)
def process_trans(machine, left, state, tape, current_symbol):
    next_configs = []
    if (state, current_symbol) in machine["trans"]:
        for next_state, write, move in machine["trans"][(state, current_symbol)]:
            new_tape, next_left = update_tape_and_head(tape, write, move, left, current_symbol)
            next_config = (next_left, next_state, new_tape)
            next_configs.append(next_config)
    return next_configs

#updates the tape and position
def update_tape_and_head(tape, write, move, left, curr_symbol):
    new_tape = write + tape[1:] if tape else write
    if move == "R":
        next_left = left + (curr_symbol if tape else "_")
        next_tape = new_tape[1:] if len(new_tape) > 1 else ""
    elif move == "L":
        next_left = left[:-1] if left else "_"
        next_tape = (left[-1] if left else "_") + new_tape
    return next_tape, next_left

#bfs search to trace all possible paths machine could take
def trace_ntm(machine, input_string, max_depth=100):
    tree = [[("", machine["start_state"], input_string)]]  #configurations
    transitions = 0

    for depth in range(max_depth):
        curr_level = tree[-1]
        next_level = []

        for left, state, tape in curr_level:
            transitions += 1

            if state == machine["accept_state"]:
                tree.append(next_level)
                return "Accepted", depth + 1, transitions, tree
            if state == machine["reject_state"]:
                continue

            current_symbol = tape[0] if tape else "_"
            next_level.extend(process_trans(machine, left, state, tape, current_symbol))

        if not next_level:  #no more configs to explore
            tree.append(next_level)
            return "Rejected", depth + 1, transitions, tree

        tree.append(next_level)

    return "Terminated", max_depth, transitions, tree

#print output of simulation
def print_output(machine, result, depth, total_configurations, tree, input_string):
    print(f"[\"{machine['name']}\"]")
    print(f"Initial string: {input_string}")
    print(f"Depth of tree: {depth}")
    print(f"Total configurations: {total_configurations}")
    
    
    tree_output = [f"[{','.join([f'[\"{left}\",\"{state}\",\"{tape}\"]' for left, state, tape in level])}]" for level in tree]
    print("\n".join(tree_output))

    if result == "Accepted":
        print(f"String accepted in {depth} transitions")
    elif result == "Rejected":
        print(f"String rejected in {depth} transitions")
    else:
        print(f"Execution stopped after {max_depth} transitions")


#run simulation
def simulate(ntm_file, input_string):
    machine = load_machine(ntm_file)
    result, depth, total_transitions, tree = trace_ntm(machine, input_string, max_depth)
    output = print_output(machine, result, depth, total_transitions, tree, input_string)
    return output

def main():
    if len(sys.argv) < 3:
        print("Usage: python traceTM_roadie.py <ntm_file.csv> <input_string_or_file>")
        sys.exit(1)

    ntm_file = sys.argv[1]
    input_arg = sys.argv[2]

    input_string = input_arg

    result = simulate(ntm_file, input_string)
    print(result)

if __name__ == "__main__":
    main()
