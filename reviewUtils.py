#!/usr/bin/env python
# -*- coding: utf-8 -*-
from myconfig import *
import csv
import os


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
            review_cnt = write_reviews(used_set=set(), writer=csv_writer, category_alias=key,
                                       category_dict=category_dict, review_dict=review_dict,
                                       business_review_dict=business_review_dict,
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