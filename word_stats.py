import heapq
import json
def fifty_most_common_words(tokens):
    heap = [(-tokens[token], token) for token in tokens]
    heapq.heapify(heap)
    res = []
    for _ in range(50):
        curr = heapq.heappop(heap)
        res.append(f'{curr[1]}, {-curr[0]}')
    
    with open("fifty_most_common.txt", 'w') as f:
        f.write('\n'.join(res))


def main():
    tokens = json.load(open('tokens.json'))
    fifty_most_common_words(tokens)


main()