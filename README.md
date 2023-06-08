# keywordsExtractions


### Requirements ###

`pip install nltk`


### How to use it ###

Calling the keyword extractor returns a list of words ranked by their importance scores.
Option to include the score or not using the flag `incl_scores`, the default value is `False`

```
  from KeywordExtractor import RakeKeywordExtractor
  rake = RakeKeywordExtractor()
  keywords = rake.extract(doc, incl_scores=False)
  print(keywords)
```


### Extracting keywords from Arabic documents using Farasa: ###

Calling extractor on Arabic content, use `rake.extractArabic()`, This requires an API_key for Farasa. 

```
  from KeywordExtractor import RakeKeywordExtractor
  rake = RakeKeywordExtractor()
  keywords = rake.extractArabic(doc, farasa_api_key, incl_scores=True)
  print(keywords)
```



