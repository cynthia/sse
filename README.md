Semantic Similarity Evaluator (SSE)
===================================

Simple tool to allow an annotator to look at a source sentence and pick the most similar sentence out of a set of sentences.

This was written as a quick tool for a particular type of annotation for a machine translation paper and isn't expected to be ever made into something general purpose. If you host this on a server facing the internet and you end up getting your server compromised as a result, you shouldn't be surprised.

The name is intentionally confusing so that as few people use it as possible. This is not a well-written piece of software.

Preview
-------

![Screenshot in action](screenshot.png)

Requirements
------------

 - Python 3.8+
 - pip install -r requirements.txt

Running
-------

    flask run --host=0.0.0.0


Disclaimer
----------

This is not an official Google product.
