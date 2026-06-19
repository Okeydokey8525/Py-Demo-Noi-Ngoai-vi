from unittest import result


def internal_fragment(block, process):
    n = len(block)
    m = len(process)
    allocated = [0]*n
    total_internal = 0
    result = []

    for i in range(m):
        found = False
        for j in range(n):
            if allocated[j] == 0 and block[j] >= process[i]:
                allocated[j] = 1
                internal = block[j] - process[i]
                total_internal += internal

                result.append({
                    "process": i+1,
                    "size": process[i],
                    "block": j+1,
                    "block_size": block[j],
                    "internal": internal
                    })
                found = True
                break
        if not found:
            result.append({
                "process": i+1,
                "size": process[i],
                "block": None,
                "block_size": None,
                "internal": None
                })
    return result, total_internal