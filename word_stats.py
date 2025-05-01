import heapq
import json
from scraper import stop_words
def fifty_most_common_words(tokens):
    heap = [(-tokens[token], token) for token in tokens]
    heapq.heapify(heap)
    res = []
    for _ in range(50):
        curr = heapq.heappop(heap)
        while curr[1] in stop_words:
            curr = heapq.heappop(heap)
        res.append(f'{curr[1]}, {-curr[0]}')
    
    with open("fifty_most_common.txt", 'w') as f:
        f.write('\n'.join(res))

def subdomain_stats(subdomains):
    subdomain_count = {}
    for subdomain in subdomains:
        if subdomain.startswith('www.'):
            edited_subdomain = subdomain[4:]
        else:
            edited_subdomain = subdomain
        subdomain_count[edited_subdomain] = subdomain_count.get(edited_subdomain, 0) + subdomains.get(subdomain, 0)

    with open("subdomain_stats.txt", 'w') as f:
        for subdomain, count in subdomain_count.items():
            f.write(f'{subdomain}, {count}\n')

def main():
    tokens = json.load(open('tokens.json'))
    subdomains = json.load(open('subdomains-test.json'))
    fifty_most_common_words(tokens)
    subdomain_stats(subdomains)


main()