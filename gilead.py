import csv
import json
import traceback

# './authorizedgeneric_authorized_ads.csv'
# TODO: Make file selection better
csv_file = './{}'.format(input(
    "Step 1: Please tell me the name of your authorized_ads file -> "))
json_file = './generated_authorized.json'


def parse_csv():
    titles_rows_array = []
    copies_rows_array = []
    urls_rows_array = []

    with open(csv_file) as c:
        csv_map = csv.DictReader(c)

        for rows in csv_map:
            # TODO: Make csv header identification dynamic
            titles_rows_array.append(rows.get("Ad Title"))
            copies_rows_array.append(rows.get("Ad Copy"))
            urls_rows_array.append(rows.get("Display URL"))

    print("CSV_TITLES ARRAY: {}\n".format(titles_rows_array))
    print("CSV_COPIES ARRAY: {}\n".format(copies_rows_array))
    generate_json(titles_rows_array, copies_rows_array, urls_rows_array)


def compare(parents):
    jf = json_file
    # './authorizedgeneric_noncompliant_ads.csv'
    nocomply_file = './{}'.format(input(
        "Step 2: Please tell me the name of your noncompliant_ads file -> "))

    print("\nNO_COMPLY FILE: {}\n".format(nocomply_file))

    titles_to_review = []
    copies_to_review = []
    urls_to_review = []

    # TODO: Maybe don't need to re-write all this code?
    with open(nocomply_file) as n:
        review_map = csv.DictReader(n)

        for rows in review_map:
            titles_to_review.append(rows.get("Ad Title"))
            copies_to_review.append(rows.get("Ad Copy"))
            urls_to_review.append(rows.get("Display URL"))

        print("TITLES_TO_REVIEW ARRAY: {}\n".format(titles_to_review))
        print("COPIES_TO_REVIEW ARRAY: {}\n".format(copies_to_review))

        n.close()

    with open(jf, "r+", encoding="utf-8") as j:
        json_map = json.load(j)
        title_item_positions = []
        copy_item_position = []

        print("*** NON-COMPLIANT ADS: ***\n")
        print("Non-compliant Ad Titles:")
        # This is where the comparison happens:
        for index, item in enumerate(titles_to_review):
            title_item_positions.append(index)

            # If an item from the titles_to_review array is not
            # present as an "ad_titles" value, print the bad ad
            if item not in json_map['ad_titles']:
                print("     {} - {}".format(item, copies_to_review[index]))

        print("\nNon-compliant Ad Copies:")
        for index, item in enumerate(copies_to_review):
            # A parent is an ad_title with matching array index from csv_titles array
            parent = parents[index]
            copy_item_position.append(index)

            # If an item from the copies_to_review array is not
            # present as an "ad_copies" value, print the bad ad
            if item not in json_map['ad_titles'][parent]['ad_copies']:
                print("     {} - {}".format(titles_to_review[index], item))

        j.close()


def generate_json(titles_rows_array, copies_rows_array, urls_rows_array):
    jf = json_file
    print("JSON FILE: {}\n".format(jf))

    brand = 'Authorized Generic'  # TODO: generate from csv_file string
    json_template = {
        "brand": brand,
        "ad_titles": {
            # "Title": {
            #   "ad_copies" : []
            # },
        },
        "display_urls": [],
        "callouts": []
    }  # It's easier for me to read like this

    # Write the json template to a new or existing json file
    with open(jf, "w", encoding="utf-8") as j:
        json.dump(json_template, j, indent=4)
        # Gotta close the file here or else it'll start reading in write_json()
        # before the template is written, resulting in a blank file being loaded as
        # json_map and json_map['ad_titles'] won't be found
        j.close()
        write_json(titles_rows_array, copies_rows_array, urls_rows_array, jf)


def write_json(titles_rows_array, copies_rows_array, urls_rows_array, jf):
    csv_titles = titles_rows_array
    csv_copies = copies_rows_array
    csv_urls = urls_rows_array

    # Open and load the templated json file
    with open(jf, "r+", encoding="utf-8") as j:
        # This reads the json file
        # Using .load() instead of .loads() handles the j.read() for me
        json_map = json.load(j)
        # For my sanity
        print("JSON_MAP: {}\n".format(json_map))
        print("JSON_MAP KEYS: ")
        for i in json_map:
            print(i)

        # Moves cursor back to beginning of the json file
        j.seek(0)

        # Foreach ad_title from csv_titles array,
        # add a new key:value pair to the loaded json file,
        # inside the "ad_titles" obj,
        # where ad_title is the key and the value is another obj, containing a key:value pair,
        # where "ad_copies" is the key and the value is an empty array.
        for ad_title in csv_titles:
            json_map['ad_titles'].update({
                ad_title: {"ad_copies": []}
            })
        # Output:
        # {
        #   "brand": "Example"
        #   "ad_titles": {
        #       "this is where 'ad_title' from 'csv_titles' goes": {
        #           "ad_copies": []
        #       },
        #   },
        #   "display_urls": [],
        #   "callouts": []
        # }

        # Assigning ad_copies values to parent ad_titles:

        # Array of indexes of each title in csv_titles array
        titles_positions = []
        print("\nAD TITLES: ")
        # Foreach index of each ad_title in csv_titles dictionary,
        # store it as a value in the titles_positions array
        for index, ad_title in enumerate(csv_titles):
            titles_positions.append(index)
            print(titles_positions)
            print("{} -> {}".format(ad_title, index))

        # Array of indexes of each title in csv_copies array
        copies_positions = []
        print("\nAD COPIES: ")
        # Foreach index of each ad_copy in csv_copies dictionary,
        # store it as a value in the copies_positions array
        for index, ad_copy in enumerate(csv_copies):
            parent = csv_titles[index]
            copies_positions.append(index)
            print(copies_positions)
            print("{} -> {}".format(ad_copy, index))
            print("PARENT: {} - > {}\n".format(parent, titles_positions[index]))

            if ad_copy in json_map['ad_titles'][parent]['ad_copies']:
                continue
            else:
                # Add each ad_copy to the "ad_copies" key array
                json_map['ad_titles'][parent]['ad_copies'].append(ad_copy)
                # Should look like this inside of "ad_titles": {
                #   "Ad Title Example": {
                #       "ad_copies": [
                #           "Ad Copy Example 1.",
                #           "Ad Copy Example 2."
                #       ]
                #   }
                # }

        for url in csv_urls:
            # If the URL contains 'www.' or '/', strip them
            if ('www.' in url) or ('/' in url):
                url = url.strip('w/.')

            # Checks if the URL is already in the "display_urls" key array, else add it as new value
            if url in json_map['display_urls']:
                continue
            else:
                json_map['display_urls'].append(url)

        # Update json file
        try:
            json.dump(json_map, j, indent=4)
            print("HOLY SHIT IT WORKS!\n\n")
        except Exception as err:
            print(traceback.format_exc(err))

        j.close()
    compare(csv_titles)


parse_csv()
