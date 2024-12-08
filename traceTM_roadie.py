#!/usr/bin/env python3
import csv
import sys
from collections import defaultdict
max_depth = 75

def load_machine(file_path):
    """Reads the NTM configuration from a CSV file."""
    machine = {
        "transitions": defaultdict(list),  # Store transitions
        "name": None,
        "states": [],  # List of states
        "input_symbols": [],  # Input symbols (Σ)
        "tape_symbols": [],  # Tape symbols (Γ)
        "start_state": None,  # Start state
        "accept_state": None,  # Accept state
        "reject_state": None,  # Reject state
    }
    
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        lines = list(reader)

        # Parse machine header (first 7 lines)
        machine["name"] = lines[0][0]
        machine["states"] = lines[1]
        machine["input_symbols"] = lines[2]
        machine["tape_symbols"] = lines[3]
        machine["start_state"] = lines[4][0]
        machine["accept_state"] = lines[5][0]
        machine["reject_state"] = lines[6][0]
        
        # Parse transitions
        for line in lines[7:]:
            if len(line) >= 5:
                state, read, next_state, write, move = line
                machine["transitions"][(state, read)].append((next_state, write, move))
    
    return machine

def process_transitions(machine, left, state, tape, current_symbol):
    """Process the transitions for a given configuration."""
    next_configs = []
    if (state, current_symbol) in machine["transitions"]:
        for next_state, write, move in machine["transitions"][(state, current_symbol)]:
            new_tape, next_left = update_tape_and_head(tape, write, move, left, current_symbol)
            next_config = (next_left, next_state, new_tape)
            next_configs.append(next_config)
    return next_configs

def update_tape_and_head(tape, write, move, left, current_symbol):
    """Update the tape and head position based on the move."""
    new_tape = write + tape[1:] if tape else write
    if move == "R":
        next_left = left + (current_symbol if tape else "_")
        next_tape = new_tape[1:] if len(new_tape) > 1 else ""
    elif move == "L":
        next_left = left[:-1] if left else "_"
        next_tape = (left[-1] if left else "_") + new_tape
    return next_tape, next_left

def trace_ntm(machine, input_string, max_depth=100):
    """Traces all possible paths of the NTM using BFS."""
    tree = [[("", machine["start_state"], input_string)]]  # List of lists for configurations
    total_transitions = 0

    for depth in range(max_depth):
        current_level = tree[-1]
        next_level = []

        for left, state, tape in current_level:
            total_transitions += 1

            if state == machine["accept_state"]:
                tree.append(next_level)
                return "Accepted", depth + 1, total_transitions, tree
            if state == machine["reject_state"]:
                continue

            current_symbol = tape[0] if tape else "_"
            next_level.extend(process_transitions(machine, left, state, tape, current_symbol))

        if not next_level:  # No more configurations to explore
            tree.append(next_level)
            return "Rejected", depth + 1, total_transitions, tree

        tree.append(next_level)  # Add the next level to the tree

    return "Terminated", max_depth, total_transitions, tree

def generate_output(machine, result, depth, total_transitions, tree, input_string):
    """Generate formatted output based on simulation results."""
    print(f"[\"{machine['name']}\"]")
    print(f"Initial string: {input_string}")
    print(f"Depth of tree: {depth}")
    print(f"Total transitions: {total_transitions}")
    
    
    tree_output = [f"[{','.join([f'[\"{left}\",\"{state}\",\"{tape}\"]' for left, state, tape in level])}]" for level in tree]
    print("\n".join(tree_output))

    if result == "Accepted":
        print(f"String accepted in {depth} transitions")
    elif result == "Rejected":
        print(f"String rejected in {depth} transitions")
    else:
        print(f"Execution stopped after {max_depth} transitions")


def simulate(ntm_file, input_string, max_depth=100):
    """Simulate the NTM and return the result."""
    machine = load_machine(ntm_file)
    result, depth, total_transitions, tree = trace_ntm(machine, input_string, max_depth)
    output = generate_output(machine, result, depth, total_transitions, tree, input_string)
    return output

def main():
    """Main function to simulate the NTM."""
    if len(sys.argv) < 3:
        print("Usage: python ntm_machine.py <ntm_file.csv> <input_string_or_file>")
        sys.exit(1)

    ntm_file = sys.argv[1]
    input_arg = sys.argv[2]

    input_string = input_arg
    if input_arg.endswith('.txt'):
        with open(input_arg, 'r') as file:
            input_string = file.read().strip()

    result = simulate(ntm_file, input_string)
    print(result)

if __name__ == "__main__":
    main()
