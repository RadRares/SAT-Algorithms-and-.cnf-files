
import sys
import time
import tracemalloc


def read_cnf(file_path):
    clauses = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c'):
                continue
            if line.startswith('p'):
                continue
            literals = list(map(int, line.split()))
            literals.pop()  # remove the trailing 0
            clauses.append(literals)
    return clauses


def is_unit_clause(clause):
    return len(clause) == 1


def simplify(clauses, literal):
    new_clauses = []
    for clause in clauses:
        if literal in clause:
            continue
        new_clause = [l for l in clause if l != -literal]
        if not new_clause:
            return None  # conflict
        new_clauses.append(new_clause)
    return new_clauses


def unit_propagate(clauses, assignment):
    while True:
        unit_clauses = [c for c in clauses if is_unit_clause(c)]
        if not unit_clauses:
            break
        for unit in unit_clauses:
            lit = unit[0]
            if -lit in assignment:
                return None
            assignment.add(lit)
            clauses = simplify(clauses, lit)
            if clauses is None:
                return None  # <-- Added check to stop on conflict
    return clauses


def choose_literal(clauses):
    for clause in clauses:
        for lit in clause:
            return abs(lit)
    return None


def dpll(clauses, assignment):
    clauses = unit_propagate(clauses, assignment)
    if clauses is None:
        return False
    if not clauses:
        return True

    var = choose_literal(clauses)
    for val in (var, -var):
        new_assignment = assignment.copy()
        new_assignment.add(val)
        new_clauses = simplify(clauses, val)
        if new_clauses is not None and dpll(new_clauses, new_assignment):
            return True

    return False


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <cnf_file>")
        return

    tracemalloc.start()
    start = time.time()

    try:
        clauses = read_cnf(sys.argv[1])
    except Exception as e:
        print(f"Error reading CNF: {e}")
        return

    print(f"Loaded {len(clauses)} clauses")

    result = dpll(clauses, set())

    end = time.time()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("\n=== Results ===")
    print(f"Status: {'SAT' if result else 'UNSAT'}")
    print(f"Time: {end - start:.3f}s")
    print(f"Peak memory: {peak / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
