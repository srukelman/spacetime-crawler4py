import heapq
import json
from scraper import stop_words

def has_vowel(word: str):
    vowels = {'a', 'e', 'i', 'o', 'u'}
    return bool(vowels & set(list(word)))

def fifty_most_common_words(tokens):
    heap = [(-tokens[token], token) for token in tokens]
    heapq.heapify(heap)
    res = []
    for _ in range(50):
        curr = heapq.heappop(heap)
        while curr[1] in stop_words or len(curr[1]) < 3 or (ord(curr[1][0]) >= 48 and ord(curr[1][0]) <= 57) or not has_vowel(curr[1]):
            curr = heapq.heappop(heap)
        res.append(f'{curr[1]}, {-curr[0]}')
    
    with open("fifty_most_common.txt", 'w') as f:
        f.write('\n'.join(res))

def subdomain_stats(subdomains):
    subdomain_count = {}
    for subdomain in subdomains:
        if subdomain.startswith('mailto:'):
            continue
        if subdomain.startswith('www.'):
            edited_subdomain = subdomain[4:]
        else:
            edited_subdomain = subdomain
        subdomain_count[edited_subdomain] = subdomain_count.get(edited_subdomain, 0) + subdomains.get(subdomain, 0)
    total = 0
    heap = [(subdomain, count) for subdomain,count in subdomain_count.items()]
    heapq.heapify(heap)
    with open("subdomain_stats.txt", 'w') as f:
        while heap:
            subdomain, count = heapq.heappop(heap)
            f.write(f'{subdomain}, {count}\n')
            total += count
    print(total)

def main():
    tokens = json.load(open('tokens.json'))
    subdomains = json.load(open('subdomains-test.json'))
    fifty_most_common_words(tokens)
    subdomain_stats(subdomains)


main()