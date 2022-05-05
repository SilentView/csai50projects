import os
import random
import re
import sys
import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    pdisribution = {}
    linkcnt = len(corpus[page])
    corpus_length = len(corpus)
    for node in corpus:
        pdisribution[node] = (1-damping_factor)/corpus_length
        if node in corpus[page]:
            pdisribution[node] += damping_factor/linkcnt

    return pdisribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    sample_cnt = {}
    corpus_length = len(corpus)
    for page in corpus:
        sample_cnt[page] = 0
    start_page = random.sample(sorted(corpus), 1)[0]
    next_page = start_page
    for i in range(n):
        current_page = next_page
        sample_cnt[current_page] += 1
        # 加权随机选择算法（相当于运用几何概型）
        rv = random.random()
        weightsum = 0
        tran_model = transition_model(corpus, current_page, damping_factor)
        for page in tran_model:
            weightsum += tran_model[page]
            if weightsum > rv:
                next_page = page
                break
    for page in corpus:
        sample_cnt[page] /= n
    return sample_cnt


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    next_pdistribution = {}
    corpus_length = len(corpus)
    # initialization
    for page in corpus:
        next_pdistribution[page] = 1/corpus_length

    while 1:
        current_pdistribution = copy.deepcopy(next_pdistribution)
        # 迭代更新next分布
        for page in current_pdistribution:
            newp = (1-damping_factor)/corpus_length
            for node in corpus:
                if page in corpus[node]:
                    newp += damping_factor*current_pdistribution[node]/len(corpus[node])
            next_pdistribution[page] = newp

        # check if converge
        isconverge = True
        for page in current_pdistribution:
            if abs(current_pdistribution[page] - next_pdistribution[page]) >= 0.001:
                isconverge = False
                break
        if isconverge:
            current_pdistribution = copy.deepcopy(next_pdistribution)
            break
    return current_pdistribution


if __name__ == "__main__":
    main()
