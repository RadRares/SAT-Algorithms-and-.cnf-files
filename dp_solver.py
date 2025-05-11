
import sys
import time
import tracemalloc
import gc

def read_cnf(file_path):
    clauses = []
    seen = set()
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c'):
                continue
            if line.startswith('p'):
                if line.split()[1] != 'cnf':
                    raise ValueError("Invalid CNF format")
                continue
            literals = list(map(int, line.split()))
            literals.pop()  # remove trailing 0
            clause = frozenset(literals)
            if not any(l in clause and -l in clause for l in clause):
                if clause not in seen:
                    seen.add(clause)
                    clauses.append(clause)
    return clauses

def resolve_dp(clauses):
    clause_set = set(clauses)
    clause_list = list(clauses)
    steps = 0
    new_clauses_count = 0

    while True:
        new = []
        len_list = len(clause_list)
        for i in range(len_list):
            for j in range(i + 1, len_list):
                c1, c2 = clause_list[i], clause_list[j]
                common_vars = c1 & {-l for l in c2}
                for l in common_vars:
                    resolvent = (c1 | c2) - {l, -l}
                    if not resolvent:
                        print(f"Derived empty clause at step {steps+1}")
                        return True, steps + 1, new_clauses_count
                    if any(x in resolvent and -x in resolvent for x in resolvent):
                        continue  # skip tautologies
                    if resolvent not in clause_set:
                        clause_set.add(resolvent)
                        new.append(resolvent)
                        new_clauses_count += 1
                        if new_clauses_count % 100 == 0:
                            print(f"Step {steps}: Added {new_clauses_count} clauses")
        if not new:
            return False, steps, new_clauses_count

        clause_list.extend(new)
        steps += 1
        new.clear()
        gc.collect()  # free memory

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <cnf_file>")
        return

    tracemalloc.start()
    start = time.time()

    try:
        clauses = read_cnf(sys.argv[1])
    except Exception as e:
        print(f"Error: {e}")
        return

    print(f"Loaded {len(clauses)} initial clauses")
    result, steps, new_clauses = resolve_dp(clauses)

    end = time.time()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Status: {'UNSAT' if result else 'SAT'}")
    print(f"Steps: {steps}")
    print(f"New clauses: {new_clauses}")
    print(f"Time: {end - start:.3f}s")
    print(f"Peak memory: {peak / 1e6:.2f} MB")

if __name__ == "__main__":
    main()
