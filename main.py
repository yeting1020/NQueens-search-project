import time
import matplotlib.pyplot as plt

class NQueensCSP:
    def __init__(self, n):
        self.n=n
        self.column=list(range(n))
        self.domains={col: list(range(n)) for col in self.column}
        self.assignment={}

    def is_complete(self):
        return len(self.assignment)==self.n

    def is_consistent(self,column,row):
        for other_column,other_row in self.assignment.items():
            if row==other_row:
                return False
            if abs(row-other_row)==abs(column-other_column):
                return False
        return True

    def assign(self,column,row):
        self.assignment[column]=row

    def unassign(self,column):
        if column in self.assignment:
            del self.assignment[column]

    def select_unassigned_column(self):
        for column in self.column:
            if column not in self.assignment:
                return column
        return None

    def get_legal_rows(self,column):
        legal_rows=[]
        for row in self.domains[column]:
            if self.is_consistent(column,row):
                legal_rows.append(row)
        return legal_rows

    def order_rows_lcv(self,column):
        legal_rows=self.get_legal_rows(column)
        row_scores=[]
        for row in legal_rows:
            self.assign(column,row)
            score=0
            for other_column in self.column:
                if other_column not in self.assignment:
                    score+=len(self.get_legal_rows(other_column))
            self.unassign(column)
            row_scores.append((row,score))
        row_scores.sort(key=lambda x: x[1],reverse=True)
        return [row for row, score in row_scores]

    def get_conflicting_column(self,column,row):
        conflicts=set()
        for other_column, other_row in self.assignment.items():
            if row==other_row:
                conflicts.add(other_column)
            if abs(row-other_row)==abs(column-other_column):
                conflicts.add(other_column)
        return conflicts

class BacktrackingSolver:
    def __init__(self):
        self.nodes_expanded=0
        self.backtracks=0

    def solve(self,csp,column_selector,use_lcv=False):
        self.nodes_expanded=0
        self.backtracks=0
        return self.backtrack(csp,column_selector,use_lcv)

    def backtrack(self,csp,column_selector,use_lcv):
        self.nodes_expanded+=1
        if csp.is_complete():
            return dict(csp.assignment)
        column=column_selector.select_column(csp)
        if use_lcv:
            rows=csp.order_rows_lcv(column)
        else:
            rows=csp.get_legal_rows(column)
        for row in rows:
            csp.assign(column,row)
            result=self.backtrack(csp,column_selector,use_lcv)
            if result is not None:
                return result
            csp.unassign(column)
        self.backtracks+=1
        return None

class ForwardCheckingSolver:
    def __init__(self):
        self.nodes_expanded=0
        self.backtracks=0

    def solve(self,csp,column_selector,use_lcv=False):
        self.nodes_expanded=0
        self.backtracks=0
        return self.backtrack(csp,column_selector,use_lcv)

    def order_rows(self,csp,column,use_lcv):
        if use_lcv:
            return csp.order_rows_lcv(column)
        return csp.get_legal_rows(column)

    def prune_domains(self,csp,column,row):
        removed={}
        for other_column in csp.column:
            if other_column in csp.assignment or other_column==column:
                continue
            invalid_rows=[]
            for other_row in list(csp.domains[other_column]):
                same_row=other_row==row
                same_diagonal=abs(other_row-row)==abs(other_column-column)
                if same_row or same_diagonal:
                    invalid_rows.append(other_row)
            if invalid_rows:
                removed[other_column]=invalid_rows
                for invalid_row in invalid_rows:
                    csp.domains[other_column].remove(invalid_row)
            if len(csp.domains[other_column])==0:
                return False,removed
        return True, removed

    def restore_domains(self,csp,removed):
        for column,rows in removed.items():
            csp.domains[column].extend(rows)
            csp.domains[column].sort()

    def backtrack(self,csp,column_selector,use_lcv):
        self.nodes_expanded+=1
        if csp.is_complete():
            return dict(csp.assignment)
        column=column_selector.select_column(csp)
        rows=self.order_rows(csp,column,use_lcv)
        for row in rows:
            csp.assign(column,row)
            consistent,removed=self.prune_domains(csp,column,row)
            if consistent:
                result=self.backtrack(csp,column_selector,use_lcv)
                if result is not None:
                    return result
            self.restore_domains(csp,removed)
            csp.unassign(column)
        self.backtracks+=1
        return None

def print_board(solution, n):
    if solution is None:
        print("No solution.")
        return
    for row in range(n):
        for column in range(n):
            if solution[column]==row:
                print("Q", end=" ")
            else:
                print(".", end=" ")
        print()

class FirstAvailable:
    def select_column(self,csp):
        for column in csp.column:
            if column not in csp.assignment:
                return column
        return None

class MRV:
    def select_column(self,csp):
        best_column=None
        best_size=float('inf')

        for column in csp.column:
            if column not in csp.assignment:
                legal_rows=csp.get_legal_rows(column)
                domain_size=len(legal_rows)
                if domain_size<best_size:
                    best_size=domain_size
                    best_column=column
        return best_column

class BackjumpingSolver:
    def __init__(self):
        self.nodes_expanded=0
        self.backtracks=0
        self.backjumps=0

    def solve(self,csp,column_selector,use_lcv=False):
        self.nodes_expanded=0
        self.backtracks=0
        self.backjumps=0
        result,_= self.backjump(csp,column_selector,use_lcv)
        return result

    def order_candidate_rows(self,csp,column,use_lcv):
        if not use_lcv:
            return list(csp.domains[column])
        ordered_legal=csp.order_rows_lcv(column)
        remaining_rows=[
            row for row in csp.domains[column]
            if row not in ordered_legal
        ]
        return ordered_legal+remaining_rows

    def backjump(self,csp,column_selector,use_lcv):
        self.nodes_expanded+=1
        if csp.is_complete():
            return dict(csp.assignment), set()
        column=column_selector.select_column(csp)
        rows=self.order_candidate_rows(csp,column,use_lcv)
        conflict_set = set()
        for row in rows:
            local_conflicts = csp.get_conflicting_column(column,row)
            if len(local_conflicts)!=0:
                conflict_set.update(local_conflicts)
                continue
            csp.assign(column,row)
            result,child_conflicts=self.backjump(csp,column_selector,use_lcv)
            if result is not None:
                return result, set()
            csp.unassign(column)
            if column in child_conflicts:
                conflict_set.update(child_conflicts-{column})
                continue
            self.backjumps+=1
            return None,child_conflicts
        self.backtracks+=1
        return None,conflict_set

def is_valid_solution(solution, n):
    if solution is None:
        return False
    if len(solution)!=n:
        return False
    for col1 in range(n):
        if col1 not in solution:
            return False
        row1=solution[col1]
        for col2 in range(col1+1, n):
            if col2 not in solution:
                return False
            row2=solution[col2]
            if row1==row2:
                return False
            if abs(row1-row2)==abs(col1-col2):
                return False
    return True

def plot_metric(sizes,data_dict,ylabel,title,filename,log_scale=False):
    plt.figure(figsize=(8,5))
    styles = {
        "FA": {"marker": "o", "linestyle": "-", "linewidth": 2},
        "MRV": {"marker": "s", "linestyle": "--", "linewidth": 2},
        "MRV+LCV": {"marker": "^", "linestyle": "-.", "linewidth": 2.5},
        "MRV+LCV+BJ": {"marker": "D", "linestyle": ":", "linewidth": 2},
        "MRV+LCV+FC": {"marker": "P", "linestyle": "-", "linewidth": 2},
    }
    for label,values in data_dict.items():
        if label in styles:
            plt.plot(sizes, values, label=label, **styles[label])
        else:
            plt.plot(sizes, values, marker='o', label=label)
    plt.xlabel("N")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    if log_scale:
        plt.yscale("log")
    plt.savefig(filename, bbox_inches="tight")
    plt.close()


def filter_results(results,excluded_labels):
    return {
        name: metrics
        for name, metrics in results.items()
        if name not in excluded_labels
    }
    
if __name__=="__main__":
    sizes=[4,8,10,12,14,16,18,20,22,24,26,28]
    configs=[
        ("FA",BacktrackingSolver(),FirstAvailable(),False),
        ("MRV",BacktrackingSolver(),MRV(),False),
        ("MRV+LCV",BacktrackingSolver(),MRV(),True),
        ("MRV+LCV+BJ",BackjumpingSolver(),MRV(),True),
        ("MRV+LCV+FC",ForwardCheckingSolver(),MRV(),True),
    ]
    results={
        "FA": {"time": [], "nodes": [], "backtracks": []},
        "MRV": {"time": [], "nodes": [], "backtracks": []},
        "MRV+LCV": {"time": [], "nodes": [], "backtracks": []},
        "MRV+LCV+BJ": {"time": [], "nodes": [], "backtracks": []},
        "MRV+LCV+FC": {"time": [], "nodes": [], "backtracks": []},
    }
    for n in sizes:
        print(f"===== N = {n} =====")
        for name,solver,selector,use_lcv in configs:
            csp=NQueensCSP(n)
            start=time.perf_counter()
            solution=solver.solve(csp,selector,use_lcv=use_lcv)
            end=time.perf_counter()
            elapsed=end-start
            print(f"Selector: {name}")
            print("Valid solution:",is_valid_solution(solution,n))
            print("Time:",elapsed)
            print("Nodes expanded:",solver.nodes_expanded)
            print("Backtracks:",solver.backtracks)
            if hasattr(solver,"backjumps"):
                print("Backjumps:",solver.backjumps)
            print()
            results[name]["time"].append(elapsed)
            results[name]["nodes"].append(solver.nodes_expanded)
            results[name]["backtracks"].append(solver.backtracks)

    plot_metric(
        sizes,
        {name: results[name]["nodes"] for name in results},
        ylabel="Nodes Expanded",
        title="Nodes Expanded vs N",
        filename="nodes_expanded.png",
        log_scale=True
    )

    plot_metric(
        sizes,
        {name: results[name]["time"] for name in results},
        ylabel="Time (seconds)",
        title="Running Time vs N",
        filename="running_time.png",
        log_scale=True
    )

    plot_metric(
        sizes,
        {name: results[name]["backtracks"] for name in results},
        ylabel="Backtracks",
        title="Backtracks vs N",
        filename="backtracks.png",
        log_scale=True
    )

    results_without_fa = filter_results(results, {"FA"})

    plot_metric(
        sizes,
        {name: results_without_fa[name]["nodes"] for name in results_without_fa},
        ylabel="Nodes Expanded",
        title="Nodes Expanded vs N (Without FA)",
        filename="nodes_expanded_no_fa.png",
        log_scale=True
    )

    plot_metric(
        sizes,
        {name: results_without_fa[name]["time"] for name in results_without_fa},
        ylabel="Time (seconds)",
        title="Running Time vs N (Without FA)",
        filename="running_time_no_fa.png",
        log_scale=True
    )

    plot_metric(
        sizes,
        {name: results_without_fa[name]["backtracks"] for name in results_without_fa},
        ylabel="Backtracks",
        title="Backtracks vs N (Without FA)",
        filename="backtracks_no_fa.png",
        log_scale=True
    )
