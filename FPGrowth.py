# Object for the header table
class Header:
    def __init__(self):
        self.items = []  # probably not needed
        self.support = {}  # key is the item, value is the support
        self.pointer = {}  # key is the item, value is the pointer

    # Load data into a header and populate the support dictionary as well as the sorted support list
    def load_data(self, transaction_data, threshold):
        for transaction in transaction_data:
            for item in transaction:
                self.add_item(item)  # iterate through each item to find support.
        # Find all instances where the support does not meet the threshold.
        temp_key_list = []
        for key in self.support:
            if not (self.support.get(key) >= threshold):
                temp_key_list.append(key)
        # Remove each item that does not meet the threshold.
        for key in temp_key_list:
            self.support.pop(key)

    # Adding a specific item to the support dictionary
    def add_item(self, item):
        if item in self.support:  # Check to see if item is already accounted for
            self.support[item] += 1  # if yes, increment support by 1
        else:
            self.support[item] = 1  # if no, then create item with value of 1

    # sort the headers support dictionary
    def order_items(self):
        self.sorted_list = self.sort_dictionary(self.support)

    # Sorts all items in a dictionary by its value
    def sort_dictionary(self, dictionary):
        # create sorted tuples in a list. The first value in the tuple is the item, and the second value is the support. These are ordered from greatest to least support.
        sorted_tuples = sorted(dictionary.items(), key=lambda kv: kv[1], reverse=True)
        # create sorted list
        sorted_list = []
        for tuple in sorted_tuples:
            sorted_list.append(tuple[0])
        return sorted_list

    # order a transaction by the current header support dictionary
    def order_transaction(self, transaction):
        temp_dict = {}
        for item in transaction:
            if item in self.support:  # if the item is not in the support list then it is not included in the transaction
                temp_dict[item] = self.support[
                    item]  # change transaction to a dictionary with the values as the support
        transaction = self.sort_dictionary(temp_dict)
        return transaction


# Object for individual nodes
class Node:
    def __init__(self, item, parent):
        self.item = item
        self.count = 1
        self.parent = parent
        self.children = {}
        self.node_pointer = None


# Object for the FP-Tree
class FPTree:
    def __init__(self):
        self.nodes = {}
        self.nodes['root'] = Node('root', None)

    # add a node to the tree
    def add_node(self, item, parent):
        if item in self.current_node.children:
            self.current_node.children[item].count += 1  # increment child node by one.
            self.current_node = self.current_node.children[item]  # set child node to be current node.
        else:
            new_node = Node(item, parent)  # create new node
            self.current_node.children[item] = new_node  # add new node to children of current node.
            self.current_node = new_node  # set new node to be current node.
            self.create_node_pointers(self.current_node)  # add node pointers to the new node.

    # creates node pointers for a given node. If the pointer is already in the header table, then it will go to the node to which it is pointing.
    def create_node_pointers(self, node):
        if node.item in self.header.pointer:
            pointer = self.header.pointer.get(node.item)
            if pointer.node_pointer:  # if the pointer node containes a node pointer
                self.recursive_create_node_pointer(node, pointer)  # go to the next node
            else:  # if not
                pointer.node_pointer = node  # then set the current node as the pointer node.
        else:
            self.header.pointer[node.item] = node  # add node to the pointer table.

    # recursive call for node pointer creation
    def recursive_create_node_pointer(self, node, pointer):
        if pointer.node_pointer:
            self.recursive_create_node_pointer(node, pointer.node_pointer)
        else:
            pointer.node_pointer = node

    # take in a transaction and use data to create nodes
    def add_transaction(self, transaction):
        self.current_node = self.nodes['root']
        for item in transaction:
            self.add_node(item, self.current_node)

    # build tree
    def build_tree(self, transaction_data, threshold):

        # Find support for each item and hold in the header table
        self.header = Header()
        self.header.load_data(transaction_data, threshold)
        self.header.order_items()

        for transaction in transaction_data:
            self.add_transaction(self.header.order_transaction(transaction))  # add the ordered transaction.
            # self.add_transaction(transaction) #  add un-ordered transaction


# Object to mine the FP-Tree
class DataMiner:
    def __init__(self):
        self.frequent_items = {}
        self.prefix_list = []

    # mine FP-Tree
    def mine(self, fp_tree, threshold, frequent_item_list):
        self.tree = fp_tree
        self.threshold = threshold

        # iterate through each item to get frequent item sets for that item
        for item in reversed(fp_tree.header.sorted_list):
            # get all branches for this item
            item_sets = self.get_branches(item)

            # build new tree
            conditional_data = self.convert_item_set_to_transactions(
                item_sets)  # transform items sets into a list of lists
            new_tree = self.conditional_tree(conditional_data, self.threshold)  # create conditional FP-Tree

            # Get frequent sets from this tree
            if new_tree.header.support:
                self.add_frequent_item_set(new_tree.header.support, frequent_item_list, item)

            # Check if conditional tree needs to be mined recursively
            root = new_tree.nodes['root']
            recursion = self.need_recursion(root)

            # if conditional tree has multiple branches, then mine the tree
            if recursion:
                # mine the tree
                dataMinier = DataMiner()
                new_prefix_list = self.prefix_list.copy()
                new_prefix_list.append(item)
                dataMinier.prefix_list = new_prefix_list
                dataMinier.mine(new_tree, self.threshold, frequent_item_list)

    def add_frequent_item_set(self, item_sets, frequent_item_list, item):
        for key in item_sets.keys():  # for each tuple in the dictionary of items
            item_set = self.prefix_list + [key] + [item]  # merge the prefix with the current items
            count = item_sets[key]  # get the count of that set
            dict = {tuple(item_set): count}
            frequent_item_list.append({tuple(item_set): count})  # add set to the complete list

    def need_recursion(self, node):
        i = 0
        if node.children:
            for key in node.children.keys():
                i += 1
                child = node.children[key]
            if i > 1:
                return True
            else:
                self.need_recursion(child)
        else:
            return False

    def convert_item_set_to_transactions(self, item_sets):
        conditional_data = []  # place to hold all data that needs to be reprocessed
        for item_set in item_sets.keys():
            i = 0
            while i < item_sets[item_set]:
                conditional_data.append(list(item_set))
                i += 1
        return conditional_data

    def conditional_tree(self, transactions, threshold):
        tree = FPTree()
        tree.build_tree(transactions, threshold)
        return tree

    # get all branches for this item
    def get_branches(self, item):
        branches = {}  # all branches for this item
        node = self.tree.header.pointer[item]  # get the node in the first pointer
        self.locate_branches(node,
                             branches)  # travers through each branch and add the branch to the dictionary of branches
        return branches

    # traverse branches
    def locate_branches(self, node, branches):
        branches[tuple(self.get_branch(
            node))] = node.count  # append the branch to the list of branches for this item ## change the list to a tuple. put the tuple as a key and the value as the count of that item.
        if node.node_pointer:  # if there is a node pointer
            self.locate_branches(node.node_pointer, branches)  # go to the next branch

    # get the branch of the passed in node
    def get_branch(self, node):
        branch = []
        self.find_branch(node, branch)
        branch.reverse()
        return branch

    # Recursive method used by get_branch to move up to to each parent.
    def find_branch(self, node, branch):
        if node.parent.item != 'root':
            branch.append(node.parent.item)
            node = node.parent
            self.find_branch(node, branch)


# The algorithm
def fp_growth(transaction_data, threshold):

    # Change threshold to support count
    total_count = len(transaction_data)
    threshold = threshold * total_count

    # Build the FP-Tree
    fp_tree = FPTree()
    fp_tree.build_tree(transaction_data, threshold)

    # Create frequent item list
    frequent_item_list = []

    # mine the tree
    dataMiner = DataMiner()
    dataMiner.mine(fp_tree, threshold, frequent_item_list)

    return frequent_item_list

