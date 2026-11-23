from forms import form
from services import search

if __name__ == "__main__":
    form("Wikipedia search", [("Topic", "")], {"Search": search}, threaded=True)
