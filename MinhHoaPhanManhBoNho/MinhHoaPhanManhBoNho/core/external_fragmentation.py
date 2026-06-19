#Phan manh ngoai vi - External Fragmentation

#FIRST FIT
def first_fit(block, process):
    empty_space = block.copy()
    result = []

    for i in range(len(process)):
        allocated = False
        for j in range(len(empty_space)):
            if empty_space[j] >= process[i]:
                result.append({
                    "process": i+1,
                    "size": process[i],
                    "block": j+1,
                    "remain": empty_space[j] - process[i]
                    })
                empty_space[j] -= process[i]
                allocated = True
                break
        if not allocated:
            result.append({
                "process": i+1,
                "size": process[i],
                "block": None,
                "remain": None
                })
    return result, empty_space

#BEST FIT
def best_fit(block, process):
    empty_space = block.copy()
    result = []

    for i in range(len(process)):
        best_index = -1
        for j in range(len(empty_space)):
            if empty_space[j] >= process[i]:
                if(best_index == -1 or empty_space[j] < empty_space[best_index]):
                    best_index = j
        if best_index != -1:
            result.append({
                "process": i + 1,
                "size": process[i],
                "block": best_index + 1,
                "remain": empty_space[best_index] - process[i]
            })
            empty_space[best_index] -= process[i]

        else:
            result.append({
                "process": i+1,
                "size": process[i],
                "block": None,
                "remain": None
            })
    return result, empty_space

#WORST FIT
def worst_fit(block, process):
    empty_space = block.copy()
    result = []

    for i in range(len(process)):
        worst_index = -1
        for j in range(len(empty_space)):
            if empty_space[j] >= process[i]:
                if(worst_index == -1 or empty_space[j] > empty_space[worst_index]):
                    worst_index = j
        if worst_index != -1:
            result.append({
                "process": i + 1,
                "size": process[i],
                "block": worst_index + 1,
                "remain": empty_space[worst_index] - process[i]
            })
            empty_space[worst_index] -= process[i]

        else:
            result.append({
                "process": i + 1,
                "size": process[i],
                "block": None,
                "remain": None
            })
    return result, empty_space

ALGORITHMS = {
    "First Fit":  first_fit,
    "Best Fit":   best_fit,
    "Worst Fit":  worst_fit,
}