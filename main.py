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


if __name__ == "__main__":
    collection = Collection("olin-slac-test-image-collection")

    cat_image_urls = get_image_urls("cat")
    dog_image_urls = get_image_urls("dog")

    cat_examples = attach_target(cat_image_urls, "cat")
    dog_examples = attach_target(dog_image_urls, "dog")

    collection.add_data(dog_examples)
    collection.add_data(cat_examples)
    collection.train()

     # a blocking call until the collection/model is ready
    collection.wait()

    test_cat_image = "https://s-media-cache-ak0.pinimg.com/originals/84/71/e2/8471e2efdd2d3164895748ee8673124d.jpg"
    print "Cat Test Result", collection.predict(test_cat_image)

    test_dog_image = "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcQgkJhtDW-n9qwGytWcYDYKq12AUPznwuQxWhgmxq0TFDLcYa95"
    print "Dog Test Result", collection.predict(test_dog_image)

    # Clear so we can use the same collection name during development
    collection.clear()
