from flask import Flask, request, jsonify
from nltk.tree import Tree
from itertools import permutations

app = Flask(__name__)

def check_tree(tree: Tree):
    for subtree in tree:
        if not (subtree.label() == 'NP' or subtree[0] in [',', 'and']):
            return False
    return True

def get_subtrees(tree: Tree):
    nps = list(tree.subtrees(lambda t: t.label() == 'NP'))
    if nps[0].label() == 'NP':
        nps = nps[1:]

    perms = list(permutations(nps))

    permutated_subtrees = []
    for perm in perms:
        i = 0
        new_tree = tree.copy(deep=True)
        for subtree in new_tree:
            if subtree.label() == 'NP':
                subtree[:] = perm[i]
                i += 1
        permutated_subtrees.append(new_tree)

    return permutated_subtrees

def generate(tree: Tree, parent_tree: Tree):
    permutated_subtrees = get_subtrees(tree)

    result_trees = []
    for perm_tree in permutated_subtrees:
        new_tree = parent_tree.copy(deep=True)
        for subtree in new_tree.subtrees():
            if subtree == tree:
                subtree[:] = perm_tree
        result_trees.append(new_tree)

    return result_trees

def get_permutations(treestr: str):
    tree: Tree = Tree.fromstring(treestr)
    for subtree in list(tree.subtrees(lambda t: t.height() > 2)):
        if check_tree(subtree):
            return generate(subtree, tree)

@app.route('/paraphrase', methods=['GET'])
def paraphrase():
    tree = request.args.get('tree')
    limit = int(request.args.get('limit', 20))

    if not tree:
        return jsonify({"error": "tree parameter is required"}), 400

    paraphrases = get_permutations(tree)[:limit]
    paraphrases = [t.pformat() for t in paraphrases]

    return jsonify({"paraphrases": [{"tree": p} for p in paraphrases]})

if __name__ == '__main__':
    app.run(debug=True)
