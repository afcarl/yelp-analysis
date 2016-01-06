#!/usr/bin/env python
# -*- coding: utf-8 -*-
from myconfig import *
import csv


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


def dump_attribute_stats(attribute_dict):
    print "There are " + str(len(attribute_dict)) + " attributes"

    csv_target = open(result_root + attribute_info_csv, 'w')
    csv_writer = csv.writer(csv_target, delimiter=',')

    for att_key, att_val in attribute_dict.iteritems():
        row = [att_key]
        row.extend(att_val)
        csv_writer.writerow(row)
    csv_target.close()


