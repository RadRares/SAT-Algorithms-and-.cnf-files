import sys
import time
import tracemalloc

def parse_dimacs(filename):
    """
    Parse a DIMACS CNF file and return a list of clauses (as frozensets of ints).
    Ignores comment lines (starting with 'c') and the header line.
    """
    clauses = []
    seen = set()
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c'):
                continue
            if line.startswith('p'):
                parts = line.split()
                if parts[1] != 'cnf':
                    raise ValueError("File format error: expected 'p cnf'")
                continue
            nums = [int(x) for x in line.split()]
            if nums[-1] != 0:
                raise ValueError("Clause line missing terminating 0")
            nums = nums[:-1]
            clause = frozenset(nums)
            if any(l in clause and -l in clause for l in clause):
                continue
            if clause and clause not in seen:
                seen.add(clause)
                clauses.append(clause)
    return clauses

def resolution_sat(clauses):
    """
    Perform propositional resolution on a list of frozenset clauses.
    Returns (is_unsat, num_steps, num_new_clauses).
    """
    clause_list = list(clauses)
    clause_set = set(clauses)
    n = len(clause_list)
    resolution_steps = 0
    new_clause_total = 0
    unsat = False

    new_clauses = []
    for i in range(n):
        for j in range(i+1, n):
            C1 = clause_list[i]
            C2 = clause_list[j]
            for lit in C1:
                if -lit in C2:
                    resolution_steps += 1
                    print(resolution_steps)  # Show step number only
                    resolvent = (C1.union(C2)) - {lit, -lit}
                    if not resolvent:
                        unsat = True
                        break
                    if any(l in resolvent and -l in resolvent for l in resolvent):
                        continue
                    if resolvent not in clause_set:
                        clause_set.add(resolvent)
                        new_clauses.append(resolvent)
                        new_clause_total += 1
                if unsat:
                    break
            if unsat:
                break
        if unsat:
            break

    if unsat:
        return True, resolution_steps, new_clause_total

    if not new_clauses:
        return False, resolution_steps, new_clause_total

    clause_list.extend(new_clauses)

    while new_clauses:
        old_n = len(clause_list) - len(new_clauses)
        total_n = len(clause_list)
        current_new = new_clauses
        new_clauses = []

        for i in range(old_n):
            for j in range(old_n, total_n):
                C1 = clause_list[i]
                C2 = clause_list[j]
                for lit in C1:
                    if -lit in C2:
                        resolution_steps += 1
                        print(resolution_steps)
                        resolvent = (C1.union(C2)) - {lit, -lit}
                        if not resolvent:
                            unsat = True
                            break
                        if any(l in resolvent and -l in resolvent for l in resolvent):
                            continue
                        if resolvent not in clause_set:
                            clause_set.add(resolvent)
                            new_clauses.append(resolvent)
                            new_clause_total += 1
                    if unsat:
                        break
                if unsat:
                    break
            if unsat:
                break

        for i in range(old_n, old_n + len(current_new)):
            for j in range(i+1, old_n + len(current_new)):
                C1 = clause_list[i]
                C2 = clause_list[j]
                for lit in C1:
                    if -lit in C2:
                        resolution_steps += 1
                        print(resolution_steps)
                        resolvent = (C1.union(C2)) - {lit, -lit}
                        if not resolvent:
                            unsat = True
                            break
                        if any(l in resolvent and -l in resolvent for l in resolvent):
                            continue
                        if resolvent not in clause_set:
                            clause_set.add(resolvent)
                            new_clauses.append(resolvent)
                            new_clause_total += 1
                    if unsat:
                        break
                if unsat:
                    break
            if unsat:
                break

        if unsat or not new_clauses:
            break

        clause_list.extend(new_clauses)

    return unsat, resolution_steps, new_clause_total

def main():
    if len(sys.argv) != 2:
        print("Usage: python resolution_sat.py <filename.cnf>")
        return

    filename = sys.argv[1]  # Get filename from command line

    tracemalloc.start()
    start_time = time.time()

    try:
        clauses = parse_dimacs(filename)
    except Exception as e:
        print(f"Error parsing file: {e}")
        return

    unsat, steps, new_clauses = resolution_sat(clauses)

    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("---------- RESULT ----------")
    print(f"Result: {'UNSAT' if unsat else 'SAT'}")
    print(f"Resolution steps: {steps}")
    print(f"New clauses derived: {new_clauses}")
    print(f"Runtime: {end_time - start_time:.4f} seconds")
    print(f"Peak memory usage: {peak / 10**6:.3f} MB")

if __name__ == "__main__":
    main()