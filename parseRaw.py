#!/usr/bin/env python
# -*- coding: utf-8 -*-
from utils import *
from businessUtils import *
from categoryUtils import *
from reviewUtils import *
from myconfig import *
import json
import os
import re
import pickle as p


def construct_ontology(path):
    # return an ontology that each category is hash by alias with entry
    # alias title children[] parents[] country_whitelist[]
    # it also returns a inverse hash table for title -> alias lookup

    # check if we have the cache
    ontology_dict = {} # a mapping from alias to its title, business count, parent and children
    title_dict = {} # a mapping title to alias
    ontology_cache_path = cache_root+'ontology.p'
    title_cache_path = cache_root+'title.p'

    if os.path.exists(ontology_cache_path) and os.path.exists(title_cache_path):
        ontology_dict = p.load( open(ontology_cache_path, "rb"))
        title_dict = p.load( open(title_cache_path, "rb"))
    else:
        # create the ontology and construct on ontology
        with open(path, 'r') as f:
            data = f.read().replace('\n', '')
            categories = json.loads(data)
            # construct the ontology
            for category in categories:
                category[u'children'] = []
                ontology_dict[category.get(u'alias')] = category
                title_dict[category.get(u'title')] = category.get(u'alias')

            # adding children
            for category in categories:
                parents = category.get(u'parents')
                for parent in parents:
                    parent_entry = ontology_dict.get(parent)
                    children = parent_entry.get(u'children', [])
                    children.append(category.get(u'alias'))
                    parent_entry[u'children'] = children
        p.dump(ontology_dict,  open(ontology_cache_path, "wb"))
        p.dump(title_dict,  open(title_cache_path, "wb"))

    return ontology_dict, title_dict


def construct_business(path, ontology_dict, title_dict):
    business_dict = {}  # a mapping from business id to its {name, category list}
    category_dict = {}  # a mapping from category_alias to a a list of business in that category
    attribute_dict = {}  # a mapping from attribute name to possible values of it

    with open(path, 'r') as f:
        for line in f:
            business = json.loads(line)
            categories = business.get(u'categories')
            categories_aliases = set()

            # make category_dict
            for category in categories:
                # collect statistics about categories
                if category == u'Flowers':
                    category = u'Flowers & Gifts' # a bug in the yelp data.
                alias = title_dict.get(category, None)
                categories_aliases.add(alias)
                if alias is None:
                    print 'ignoring ' + category
                    continue
                # save the business in the category_dict
                bus_list = category_dict.get(alias, [])
                bus_list.append(business.get(u'business_id'))
                category_dict[alias] = bus_list

            # make attribute_dict
            attributes = business.get(u'attributes')
            update_tree_dict(attribute_dict, attributes)

            # make business dictionary
            business_dict[business.get(u'business_id')] = {u'name': business.get(u'name'),
                                                           u'stars': business.get(u'stars'),
                                                           u'categories': categories_aliases,
                                                           u'attributes': attributes}

    return business_dict, category_dict, attribute_dict


def construct_review(path, ontology_dict, title_dict, business_dict, category_dict):

    # check if we have the cache
    business_review_cache_path = cache_root+'business_review.p'
    review_cache_path = cache_root+'review.p'
    if os.path.exists(business_review_cache_path) and os.path.exists(review_cache_path):
        business_review_dict = p.load(open(business_review_cache_path, "rb"))
        review_dict = p.load(open(review_cache_path, "rb"))
    else:
        business_review_dict = {} # from category title -> a list of review id
        review_dict = {} # from review id to review text and star
        # populate category_review_dict
        with open(path, 'r') as f:
            line_cnt = 0
            for line in f:
                line_cnt += 1
                review = json.loads(line)
                review_text = review.get(u'text').replace('\n', '').strip()
                review_id = review.get(u'review_id')
                review_star = review.get(u'stars')
                # process the review_text
                re.sub(u' +',u' ', review_text)
                if review_text:
                    # review dict
                    review_dict[review_id] = {u'text':review_text, u'stars':review_star}
                    # business review
                    bus_id = review.get(u'business_id')
                    bus_reviews = business_review_dict.get(bus_id, [])
                    bus_reviews.append(review_id)
                    business_review_dict[bus_id] = bus_reviews
                if line_cnt % 50000 == 0:
                    print line_cnt
            print 'read ' + str(line_cnt) + ' in total'
        p.dump(business_review_dict,  open(business_review_cache_path, "wb"))
        p.dump(review_dict,  open(review_cache_path, "wb"))
    print 'Load ' + str(len(business_review_dict)) + ' business'

    return business_review_dict, review_dict


def main():

    business_path = data_root + business_data
    ontology_path = data_root + ontology_data
    review_path = data_root + review_data

    # construct ontology
    print 'reading ontology'
    [ontology_dict, title_dict]= construct_ontology(path=ontology_path)

    # construct the business data
    print 'reading business data'
    [business_dict, category_dict, attribute_dict] = construct_business(path=business_path, ontology_dict=ontology_dict, title_dict=title_dict)

    # gather statistics about ontology and business
    dump_ontology_stats(ontology_dict, category_dict, business_dict)
    dump_business_stats(business_dict, ontology_dict)
    dump_attribute_stats(attribute_dict)

    # construct the review data
    print 'reading review data'
    '''
    [business_review_dict, review_dict] = construct_review(path=review_path, ontology_dict=ontology_dict,
                                                           title_dict= title_dict, business_dict=business_dict,
                                                           category_dict=category_dict)
    # gather stats about review
    dump_review_stats(ontology_dict=ontology_dict, category_dict=category_dict,
                      business_review_dict=business_review_dict, review_dict=review_dict)
    '''

    print 'Done'

if __name__ == '__main__':

    main()