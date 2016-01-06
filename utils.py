#!/usr/bin/env python
# -*- coding: utf-8 -*-

def update_tree_dict(tree_dict, tree):
    # update tree_dict given a new tree
    # tree_dict is a mapping from node -> possible values (non)terminal nodes
    for tree_key, tree_val in tree.iteritems():
        node_set = tree_dict.get(tree_key, set())
        if type(tree_val) is dict:
            keys = tree_val.keys()
            for key in keys:
                node_set.add(key)
            tree_dict[tree_key] = node_set
            update_tree_dict(tree_dict, tree_val)
        else:
            node_set.add(tree_val)
            tree_dict[tree_key] = node_set

