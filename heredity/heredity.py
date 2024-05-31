import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]

def offer_mutated_GJB2_prob(ori_gene, offer_mutated):
    """
    Compute the probability of a parent with "ori_gene" gene type
    giving or not giving (if offer_gene is True or False)
    a mutated GJB2 gene to his/her child
    """
    """
    当发现过多的if else 判断时，想办法抽象出一个函数出来来清晰地表达逻辑！在这里，我们抽象出来的函数就是根据parent
    的gene type计算给出mutated GJB2的概率，于是：根据parent基因型的大量if else 被以参数调用的形式简化掉了
    """
    if offer_mutated:
        if ori_gene == 0:
            return PROBS["mutation"]
        elif ori_gene == 1:
            return 0.5  # by symmetry
        else:
            return 1 - PROBS["mutation"]
    else:
        if ori_gene == 0:
            return 1 - PROBS["mutation"]
        elif ori_gene == 1:
            return 0.5
        else:
            return PROBS["mutation"]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    """
    *1.首先想想事件的分法，最终是要分成一个乘法公式的形式，那么事件单元就不是everyone而是certain one，是一个人的情况
    *2.计算Bayesian网络的思路：乘法公式，深度小的（父母要么None要么已经被放到条件中了）先抽出来，再加到条件里面去，继续算下去。
    *3.但是上一点还是一个很粗糙的想法，事实上，完全可以一次循环算完，这是来自于条件概率的性质，如果条件中给出了直接决定自身的parent
    那么其他的条件都可以忽略，易证直接循环一边算出来的结果和根据上述性质化简后的2的结果是一致的（条件有且仅有自己的parent）
    """
    # 字典condition存储由输入决定的每个人的gene和trait的具体值
    # dictionary comprehension
    conditions = {
        person: {
            "gene": 1 if person in one_gene else
                    2 if person in two_genes else 0,
            "trait": True if person in have_trait else False
        }
        for person in people
    }
    probability = 1
    for person in people:
        p = 1
        p_trait_condi_on_gene = PROBS["trait"][conditions[person]["gene"]][conditions[person]["trait"]]
        p *= p_trait_condi_on_gene
        if people[person]["mother"] == people[person]["father"] == None:
            p *= PROBS["gene"][conditions[person]["gene"]]
        else:
            gene_type = conditions[person]["gene"]
            mum = people[person]["mother"]
            dad = people[person]["father"]
            mum_gene = conditions[mum]["gene"]
            dad_gene = conditions[dad]["gene"]
            if gene_type == 0:
                p *= offer_mutated_GJB2_prob(mum_gene, False)
                p *= offer_mutated_GJB2_prob(dad_gene, False)
            elif gene_type == 1:
                p1 = offer_mutated_GJB2_prob(mum_gene, True) * offer_mutated_GJB2_prob(dad_gene, False)
                p2 = offer_mutated_GJB2_prob(mum_gene, False) * offer_mutated_GJB2_prob(dad_gene, True)
                p *= (p1 + p2)
            else:
                p *= offer_mutated_GJB2_prob(mum_gene, True) * offer_mutated_GJB2_prob(dad_gene, True)
        probability *= p
    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    conditions = {
        person: {
            "gene": 1 if person in one_gene else
                    2 if person in two_genes else 0,
            "trait": True if person in have_trait else False
        }
        for person in probabilities
    }
    for person in probabilities:
        probabilities[person]["gene"][conditions[person]["gene"]] += p
        probabilities[person]["trait"][conditions[person]["trait"]] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        norm_factor = sum(probabilities[person]["gene"].values())
        for gene_type in probabilities[person]["gene"]:
            probabilities[person]["gene"][gene_type] /= norm_factor

        norm_factor = sum(probabilities[person]["trait"].values())
        for trait in probabilities[person]["trait"]:
            probabilities[person]["trait"][trait] /=norm_factor


if __name__ == "__main__":
    main()
