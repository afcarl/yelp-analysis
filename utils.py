#!/usr/bin/env python
# -*- coding: utf-8 -*-
from myconfig import *
import csv
import os


def get_business(business_set, category_alias, ontology_dict, category_dict, recursive):
    # return a set of business id for a given category alias. If recursive it will goes down to the leaf
    business_list = category_dict.get(category_alias, [])
    for bus in business_list:
        business_set.add(bus)
    if recursive:
        category_entry = ontology_dict.get(category_alias)
        children = category_entry.get(u'children', [])
        for child in children:
            get_business(business_set, child, ontology_dict, category_dict, recursive)
    return business_set


def dump_ontology_stats(ontology_dict, category_dict, business_dict):
    print "There are " + str(len(ontology_dict)) + " categories"
    field_row = ['alias', 'business count', 'children count', 'attribute count']

    csv_target = open(result_root + category_info_csv, 'w')
    csv_writer = csv.writer(csv_target, delimiter=',')

    # get the frequency over all categories
    csv_writer.writerow(field_row)
    for key in ontology_dict:
        csv_writer.writerow(get_category_info(key, category_dict, ontology_dict, business_dict))
    csv_target.close()

    # get the frequency over top 22 category
    csv_target = open(result_root + top_category_info_csv, 'w')
    csv_writer = csv.writer(csv_target, delimiter=',')
    csv_writer.writerow(field_row)

    for key, category_entry in ontology_dict.iteritems():
        if not category_entry.get(u'parents'):
            csv_writer.writerow(get_category_info(key, category_dict, ontology_dict, business_dict))

    csv_target.close()

    # get the frequency over sub-categories within each top 22 category
    for key, category_entry in ontology_dict.iteritems():
        if not category_entry.get(u'parents'):
            # a parent here, combine all the counts of children
            csv_target = open(result_root +'inside/' + key +'_' + inside_category_info_csv, 'w')
            csv_writer = csv.writer(csv_target, delimiter=',')

            csv_writer.writerow(field_row)
            for child in category_entry.get(u'children'):
                csv_writer.writerow(get_category_info(child, category_dict, ontology_dict, business_dict))

            csv_target.close()


def get_category_info(category_alias, category_dict, ontology_dict, business_dict):
    # return a standard list of key information about the given category_alias
    category_entry = ontology_dict.get(category_alias)
    businesses = get_business(business_set=set(),
                              category_alias=category_alias,
                              ontology_dict=ontology_dict,
                              category_dict=category_dict,
                              recursive=True)
    attributes = set()
    for bus in businesses:
        bus_entry = business_dict.get(bus, None)
        bus_attributes = bus_entry.get(u'attributes').keys()
        for att in bus_attributes:
            attributes.add(att)
    row = [category_alias, len(businesses), len(category_entry.get(u'children')), len(attributes)]
    row.extend(attributes)
    return row


def dump_attribute_stats(attribute_dict):
    print "There are " + str(len(attribute_dict)) + " attributes"

    csv_target = open(result_root + attribute_info_csv, 'w')
    csv_writer = csv.writer(csv_target, delimiter=',')

    for att_key, att_val in attribute_dict.iteritems():
        row = [att_key]
        row.extend(att_val)
        csv_writer.writerow(row)
    csv_target.close()


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
    for bus_id, business in business_dict.iteritems():
        reduce_categories = merge_upwards(categories=business.get('categories', []), ontology_dict=ontology_dict)
        if len(reduce_categories) > 1:
            multi_class_cnt += 1.0
        avg_category += len(reduce_categories)

    print 'avg category number with merging is ' + str(avg_category/len(business_dict))
    print 'multi-class proportion is ' + str(multi_class_cnt/len(business_dict))

    # dump to file
    #csv_target = open(result_root+business_summary_csv, 'w')
    #csv_writer = csv.writer(csv_target, delimiter=',')


def dump_review_stats(ontology_dict, category_dict, review_dict, business_review_dict):
    # write everything to the disk
    print 'begin saving '
    target_dir = result_root+'review/'
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    total_review_cnt = 0
    for key, category_entry in ontology_dict.iteritems():
        if not category_entry.get(u'parents'):
            # it's a parent
            target_path = target_dir + key + '_reviews.csv'
            csv_target = open(target_path, 'w')
            csv_writer = csv.writer(csv_target, delimiter=',')
            csv_writer.writerow(['text', 'stars'])
            review_cnt = write_reviews(used_set=set(), writer=csv_writer, category_alias=key, category_dict=category_dict,
                                       review_dict=review_dict, business_review_dict=business_review_dict,
                                       ontology_dict=ontology_dict, recursive=True)
            total_review_cnt = total_review_cnt + review_cnt
            print key + ' has ' + str(review_cnt) + ' reviews'
            csv_target.close()
    print 'total have ' + str(total_review_cnt) + ' reviews'


def write_reviews(used_set, writer, category_alias, category_dict, review_dict, business_review_dict,
                  ontology_dict, recursive):
    review_cnt = 0
    business_list = category_dict.get(category_alias, [])
    for bus in business_list:
        review_list = business_review_dict.get(bus, [])
        for review in review_list:
            if review not in used_set:
                used_set.add(review)
                review_entry = review_dict.get(review)
                writer.writerow([review_entry.get(u'text').encode('utf-8'), str(review_entry.get(u'stars'))])
                review_cnt += 1
    if recursive:
        category_entry = ontology_dict.get(category_alias)
        children = category_entry.get(u'children', [])
        for child in children:
            child_review_cnt = write_reviews(used_set, writer, child, category_dict, review_dict,
                                             business_review_dict, ontology_dict, recursive)
            review_cnt = review_cnt + child_review_cnt
    return review_cnt


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


def update_tree_dict(tree_dict, tree):
    # update tree_dict given a new tree
    # tree_dict is a mapping from node -> possible values (non)terminal nodes
    for tree_key, tree_val in tree.iteritems():
        if (type(tree_val) is dict):
            update_tree_dict(tree_dict, tree_val)
        else:
            node_set = tree_dict.get(tree_key, set())
            node_set.add(tree_val)
            tree_dict[tree_key] = node_set

