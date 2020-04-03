# phish_phinder
spell check the internet!
## About
Use levenshtein (edit) distance and cosine similarity to "spell check" domains against the top domains in order to find typosquatting and similar misspellings. I wrote this a long time ago and found it recently. Check out the slides at [Phish Phinder](Phish Phinder.pdf)
### How
1. pull alexa top n list
2. remove any of length less than x
3. check all new domains seen:
  1. does it have com/org at the end of the domain portion?
    * if yes, report as possible phish
    * maybe also do a length check
  2. is it longer than x-2?
    * if no, ignore, no sense doing expensive operations for short names
  3. calculate levenshtein distance of domain.TLD and each alexa top n
    * anything that is 1 or 2, report
  4. calculate cosine similarity of domain.TLD and each alexa top n
    * if greater than 9, report
## Usage
```
./phish_phinder.py -a
./phish_phinder.py -d goog1e.com
./phish_phonder.py -f amazon_phishes.csv
./phish_phonder.py -f kickstarter_phishes.csv
./phish_phonder.py -f reddit_phishes.csv
```
### Results
```
[*] observed domain twiter.com looks a lot like twitter.com and may be a phish. edit: 1; cos: 0.98019605882; score: 18.8019605882; new_score: 0.0198039411804;  domlen: 11
[*] observed domain iclud.com looks a lot like icloud.com and may be a phish. edit: 1; cos: 0.96698755683; score: 18.6698755683; new_score: 0.0330124431695;  domlen: 10
```
## Testing
I used dnstwist to generate some phishing domains and tested them to decent results. I don't have them right now, but I can look for them and post them when I do.
