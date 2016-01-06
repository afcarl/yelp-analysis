#!/usr/bin/env python
# -*- coding: utf-8 -*-
from myconfig import *
import csv


def dump_business_stats(business_dict, ontology_dict):
    # dump statistics about the business
    print "there are " + str(len(business_dict)) + " business"

    # number of category label without merging
    avg_category = 0.0
    for bus_id, business in business_dict.iteritems():
        avg_category += len(business.get('categories', []))

    print 'avg category number is ' + str(avg_category/len(business_dict))

    # number of category label with merging
    avg_category = 0.0
    multi_class_cnt = 0.0
    non_leaf_cnt = 0.0
    for bus_id, business in business_dict.iteritems():
        raw_categories = business.get('categories', [])
        reduce_categories = merge_upwards(categories=raw_categories, ontology_dict=ontology_dict)
        leaf_categories = only_leaf(categories=raw_categories, ontology_dict=ontology_dict)
        if len(reduce_categories) > 1:
            multi_class_cnt += 1.0
        if len(leaf_categories) == 0:
            non_leaf_cnt += 1.0
        avg_category += len(reduce_categories)

    print 'avg category number with merging is ' + str(avg_category/len(business_dict))
    print 'multi-class proportion is ' + str(multi_class_cnt/len(business_dict))
    print 'non-leaf label proportion is ' + str(non_leaf_cnt/len(business_dict))

    # dump to file
    #csv_target = open(result_root+business_summary_csv, 'w')
    #csv_writer = csv.writer(csv_target, delimiter=',')


def merge_upwards(categories, ontology_dict):
    # return a reduced set of categories s.t removing items that are children of other items
    result = set()
    for key in categories:
        is_top = True
        for test_key in categories:
            if key != test_key:
                if is_parent(key, test_key, ontology_dict):
                    is_top = False
                    break
        if is_top:
            result.add(key)
    return result


def only_leaf(categories, ontology_dict):
    # return a reduced set of categories s.t. all category is a leaf in the ontology
    result = set()
    for key in categories:
        if not ontology_dict.get(key).get(u'children'):
            # it is a leaf (no children)
            result.add(key)
    return result

def is_parent(child, test_parent, ontology_dict):
    # return true if child is indeed the child of parent
    if child == test_parent:
        return True

    parents = ontology_dict.get(child).get('parents', None)
    # if we cannot move up, they are not connected
    if parents is None:
        return False

    # try moving up from all parents
    for parent in parents:
        if is_parent(parent, test_parent, ontology_dict):
            return True
    # none of the parents can reach the test_parent, return false
    return False

