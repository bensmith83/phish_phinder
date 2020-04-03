import urllib
import zipfile
import os
import csv
import math
from collections import Counter
import argparse


#TODO: add command line options for all global arguments
#TODO: standardize scoring mechanisms
#TODO: suggestion: pull images from sites and do md5 comparisons OR maybe fuzzy hashing OR image name matching OR color palette or something


# Defaults
DOMAIN_MIN_LEN = 5 + 4
#PHISHING_DOMAIN = "goggle.com"
PHISHING_DOMAIN = "microshaft.com"
PHISHING_DOMAIN_FILE = "bottom_1m_test"
#PHISHING_DOMAIN_FILE = "amazon_phishes.csv"
#PHISHING_DOMAIN_FILE = "kickstarter_phishes.csv"
DOWNLOAD_NEW = 0
SCORE_THRESHOLD = 18.4
NEw_SCORE_THRESHOLD = 0.4
L_SCORE_THRESHOLD = 2
COS_SCORE_THRESHOLD = 0.9

# Args
arg_verbose = 0
arg_file = 0
arg_dl = 0
arg_min_len = 0
arg_score = 0
arg_domain = 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", dest="verbose", help="be more verbose", action='count')
    parser.add_argument("-l", "--lengthofdomain", dest="lengthofdomain", help="minimum domain length to look at", default=DOMAIN_MIN_LEN)
    parser.add_argument("-a", "--alexa", dest="alexa", help="download new alexa top 1m vs use existing", default=DOWNLOAD_NEW)
    parser.add_argument("-d", "--domain", dest="domain", help="domain to check for phishing score", default=PHISHING_DOMAIN)
    parser.add_argument("-s", "--score", dest="score", help="report only above this score", default=SCORE_THRESHOLD)
    parser.add_argument("-f", "--file", dest="file", help="read URLs from a csv, second column", default=PHISHING_DOMAIN_FILE)
    args = parser.parse_args()

    # Args
    global arg_verbose
    global arg_file
    global arg_dl
    global arg_min_len
    global arg_score
    global arg_domain

    arg_verbose = args.verbose or 0
    arg_file = args.file
    arg_dl = args.alexa
    arg_min_len = args.lengthofdomain
    arg_score = args.score
    arg_domain = args.domain

    if (arg_domain != 0):
        phish_score(arg_domain)
    elif (args.file != 0):
        with open(arg_file) as phishes:
            phishlist = csv.reader(phishes)
            for row in phishlist:
                phish_score(row[1])

def phish_score(domain):
    truncate_to = 500  # downloading list but keeping only this many
    alexa_top_1mil_url = "http://s3.amazonaws.com/alexa-static/top-1m.csv.zip"
    alexa_zip_file = "alexa_top-1m.csv.zip"
    alexa_csv_file = "top-1m.csv"
    found_list = []
    if (process_alexa_list(alexa_top_1mil_url, alexa_zip_file, alexa_csv_file, truncate_to, arg_dl)):
        with open(alexa_csv_file) as alexafile:
            alexalist = csv.reader(alexafile)
            for row in alexalist:
                domlen = len(row[1])
                if (domlen > arg_min_len):
                    dist = minimumEditDistance(row[1], domain)
                    lper = dist / domlen
                    coss = get_cosine(Counter(row[1]), Counter(domain))
                    score = (10 - dist) + (10 * coss)
                    new_score = 1-coss + lper
                    if (dist == 0 or coss == 1):
                        # exact match.
                        if (arg_verbose > 1):
                            print("[*] exact match with {0}.".format(row[1]))
                        break;
                    #if (coss > 0.9 and dist <= 3): #if (dist <= 2):
                    #if (new_score < arg_score):
                    if (score > arg_score):
                        if (arg_verbose >= 1):
                            print("[*] observed domain {1} looks a lot like {0} and may be a phish. edit: {2}; cos: {3}; score: {4}; new_score: {5};  domlen: {6}".format(row[1],domain,dist,coss,score,new_score,domlen))
                        else:
                            print("{0}".format(row[1]))
                        found_list.append(score)
                    #print("[*] compared {0} and {1} edit: {2}; cos: {3}; score: {4}; new_score: {5}".format(row[1],PHISHING_DOMAIN,dist, coss,score,new_score))


def process_alexa_list(alexa_top_1mil_url, alexa_zip_file, alexa_csv_file, truncate_to, download_new):
    # https://support.alexa.com/hc/en-us/articles/200449834-Does-Alexa-have-a-list-of-its-top-ranked-websites-
    if download_new != 0:
        urllib.urlretrieve(alexa_top_1mil_url, "alexa_top-1m.csv.zip")
        with open(alexa_zip_file, 'rb') as fh:
            z = zipfile.ZipFile(fh)
            for name in z.namelist():
                outpath = "."
                if name == alexa_csv_file:
                    z.extract(name,outpath)
        os.remove(alexa_zip_file)
    with open(alexa_csv_file, "r+") as f:
        for x in xrange(truncate_to):
            f.readline()
        f.truncate()
    return 1


def add_www_sub(alexalist):
    wwwlist = {}
    for row in alexalist:
        order, site = row


def minimumEditDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    distances = range(len(s1) + 1)
    for index2, char2 in enumerate(s2):
        newDistances = [index2 + 1]
        for index1, char1 in enumerate(s1):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1],
                                             distances[index1 + 1],
                                             newDistances[-1])))
        distances = newDistances
    return distances[-1]


def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
    sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


if __name__ == "__main__":
    main()
