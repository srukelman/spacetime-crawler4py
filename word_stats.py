import heapq
import json
def fifty_most_common_words(tokens):
    heap = [(-tokens[token], token) for token in tokens]
    res = []
    for _ in range(50):
        res.append(heapq.heappop(heap)[1])
    
    with open("fifty_most_common.txt", 'w') as f:
        f.write('\n'.join(res))


def main():
    tokens = json.load(open('tokens.json'))
    fifty_most_common_words(tokens)