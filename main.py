# Set indico API key either in your environment as "INDICO_API_KEY"
# Or set it here
"""
import indicoio
indicoio.config.api_key = "YOUR API KEY"
"""
import requests

from indicoio.custom import Collection
from bs4 import BeautifulSoup as BSoup

IMAGE_SEARCH_URL = "https://www.google.com/search?site=&tbm=isch&q={query}"

def get_image_urls(query, size=5):
    """
    Takes in an image search query and returns `size` image urls
    """
    url = IMAGE_SEARCH_URL.format(query=query)
    response = requests.get(url)
    soup = BSoup(response.text, "lxml")

    images = []
    for img in soup.find_all("img", alt="Image result for {query}".format(query=query)):
        if len(images) > size:
            return images
        images.append(img["src"])
    return images


def attach_target(urls, target):
    """
    Takes in a list of urls and creates example -> target tuple pairs
    expected by indicoio's custom collections API.
    """
    return zip(urls, [ target for _ in xrange(len(urls)) ])

def create_labeled_examples(labels, num_examples=5):
    """
    Creates labeled examples from a list of labels to be passed into the
    add_data method of a indicoio custom collection
    """
    labeled_examples = []
    for label in labels:
        urls = get_image_urls(label, size=num_examples)
        labeled_examples += attach_target(urls, label)

    return labeled_examples

if __name__ == "__main__":
    collection = Collection("olin-slac-test-image-collection")

    examples = create_labeled_examples(
        labels=[ "cat", "dog" ],
        num_examples=5
    )

    collection.add_data(examples)
    collection.train()

     # a blocking call until the collection/model is ready
    collection.wait()

    test_cat_image = "https://s-media-cache-ak0.pinimg.com/originals/84/71/e2/8471e2efdd2d3164895748ee8673124d.jpg"
    print "Cat Test Result", collection.predict(test_cat_image)

    test_dog_image = "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcQgkJhtDW-n9qwGytWcYDYKq12AUPznwuQxWhgmxq0TFDLcYa95"
    print "Dog Test Result", collection.predict(test_dog_image)

    # Clear so we can use the same collection name during development
    collection.clear()
