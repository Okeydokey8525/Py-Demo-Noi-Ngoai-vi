#Co che don dich - Compaction

def compaction(block, process):
    empty_space = block.copy()
    allocation = []

    #Ap dung first fit
    for i in range(len(process)):
        allocated = False
        for j in range(len(empty_space)):
            if empty_space[j] >= process[i]:
                allocation.append({
                    "process": i+1,
                    "size": process[i],
                    "block": j+1,
                    "remain":  empty_space[j] - process[i]
                    })
                empty_space[j] -= process[i]
                allocated = True
                break
        if not allocated:
            allocation.append({
                "process": i+1,
                "size": process[i],
                "block": None,
                "remain": None
                })

    #tong bo nho con trong
    total_empty = sum(empty_space)

    #don cac phan bo nho da dung sang 1 ben -> chi con 1 block trong
    compacted = [block for block in empty_space if block == 0] #block dung het
    if total_empty > 0:
        compacted.append(total_empty)

    return allocation, empty_space, compacted