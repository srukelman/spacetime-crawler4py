import re
from urllib.parse import urlparse, urlunsplit
# import lxml
from bs4 import BeautifulSoup
import os
import json
# import nltk

def tokenize(input_str: str) -> int:
    # tokenize and count the words in the input
    # res is a dictionary with the words as keys and the number of times they appear in the input as values
    # curr is a list of characters that are part of the current word (reset to empty when a non-letter is found)
    length = 0
    res = {}
    if os.path.exists('tokens.json'):
        with open('tokens.json', 'r') as f:
            res = json.load(f)
    curr = []
    
    for char in input_str:
        if not char:
            break
        char = char.lower()
        # allow for letters, numbers, apostrophes, and hyphens
        if (ord(char) >= 97 and ord(char) <= 122) or (ord(char) >= 48 and ord(char) <= 57) or char == '-' or char == "'":
            curr.append(char)
        elif curr:
            curr_word = ''.join(curr)
            if curr_word in stop_words:
                curr = []
                continue
            res[curr_word] = 1 + res.get(curr_word, 0)
            length += 1
            curr = []
            
    if curr:
        curr_word = ''.join(curr)
        if curr_word not in stop_words:
            res[curr_word] = 1  + res.get(curr_word, 0)
            length += 1
    
    with open('tokens.json', 'w') as f:
        json.dump(res, f)
    
    return length

def scraper(url, resp):
    if resp.status != 200:
        print('not 200')
        return [], 0
    soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    # remove script and style task
    for script_and_style in soup(['script', 'style']):
        script_and_style.decompose()
    
    # aggregate the raw text from the page
    text = soup.get_text(separator=" ", strip=True)
    # if there are less than 100 words, we deem it as low value
    if len(text.split()) < 100:
        print('low text')
        return [], 0

    # if there is a low text to html ratio, we deem it as low value
    # if len(text) / len(resp.raw_response.content) < 0.1:
    #    print('low text2')
    #    return [], 0
    
    # skip very large files (over 1 MB)
    # if len(resp.raw_response.content) > 1000000:
    #    return [], 0
    
    # tokenize and count the text
    curr_length = tokenize(text)
    
    # curr_subdomain = urlparse(url).netloc
    # print(resp.raw_response.content)
    links = extract_next_links(url, resp)
    print(f'{len(links)} extracted')
    res = [link for link in links if is_valid(link)]
    print(f'{len(res)} valid')
    return (res, curr_length)

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    if resp.status != 200:
        return list()
    
    # get the page content via BeautifulSoup
    soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    # extract the links from the page content
    links = soup.find_all('a')
    print(f'{len(links)} links')
    res = set()
    # parse through links found on page
    for link in links:
        # add the link to the list if it is a valid link
        if link.has_attr('href') and type(link.get('href')) == str:
            res.add(defragment(link.get('href')))
    return list(res)

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)    
        domain = parsed.netloc.lower() 
        path = parsed.path.lower()    
        # get rid of pages that are not on the web (i.e. not http or https)
        if parsed.scheme not in set(["http", "https"]):
            print(f'{url} scheme failing')
            return False
        
        # *.ics.uci.edu/*
        # *.cs.uci.edu/*
        # *.informatics.uci.edu/*
        # *.stat.uci.edu/*
        # today.uci.edu/department/information_computer_sciences/*

        # check if domain is within one of the four accepted domains
        if domain.endswith(".ics.uci.edu") or \
            domain.endswith(".cs.uci.edu") or \
           domain.endswith(".informatics.uci.edu") or \
           domain.endswith(".stat.uci.edu"):
            pass

        # check if domain is today.uci.edu and is on the correct path        
        elif domain == "today.uci.edu" and path.startswith("/department/information_computer_sciences/"):
            pass
        else:
            print(f'{domain} failing domain check')
            return False
        
        # skip all calendar trips
        if 'calendar' in path:
            return False

        # filter out URLs that are not scrapable (e.g. images and videos and such)
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def defragment(url):
    # Remove the fragment from the URL (the part after the #)
    # Return the URL without the fragment
    url = str(url)
    url = url.split('#')
    if len(url) > 1:
        url.pop()
    return url[0]
    
stop_words = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "aren't",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can't",
    "cannot",
    "could",
    "couldn't",
    "did",
    "didn't",
    "do",
    "does",
    "doesn't",
    "doing",
    "don't",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "had't", 
    "has",
    "hasn't",
    "have",
    "haven't",
    "having",
    "he",
    "he'd",
    "he'll",
    "he's",
    "her",
    "here",
    "here's",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "how's",
    "i",
    "i'd",
    "i'll",
    "i'm",
    "i've",
    "if",
    "in",
    "into",
    "is",
    "isn't",
    "it",
    "it's",
    "its",
    "itself",
    "let's",
    "me",
    "more",
    "most",
    "mustn't",
    "my",
    "myself",
    "no",
    "nor",
    "not",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "ought",
    "our",
    "ours"
}
