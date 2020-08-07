from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
from faunadb.client_logger import logger
import os
import pickle

def write_to_db(items, collection, index, unique_keys):
    def chunk(seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))
    client = FaunaClient(secret=os.environ["FAUNA_SECRET"], observer=logger(lambda x: print(x)))
    for items in chunk(items, 500):
        print(len(items))
    client.query(
    q.map_expr(
        lambda item:
       q.call(
    q.function('upsert'),
    [collection, index, [q.select(key, item) for key in unique_keys ], item],
  ),
      items
        )
    )
  

def fetch_all_from_db(collection):
    after = ""
    data = []
    while after is not None:
        client = FaunaClient(secret=os.environ["FAUNA_SECRET"])
        result = client.query(q.map_expr(lambda x: q.select("data",q.get(x)), q.paginate(q.documents(q.collection(collection)), size=10000, after=after)))
        data += result["data"]
        after = result.get("after", None)
    return data

def fetch_all_from_index(index, values = []):
    after = ""
    data = []
    while after is not None:
        client = FaunaClient(secret=os.environ["FAUNA_SECRET"])
        result = client.query(q.map_expr(lambda x: q.select("data",q.get(x)), q.paginate(q.match(q.index(index), values), size=100000, after=after)))
        data += result["data"]
        after = result.get("after", None)
    return data

#fetch_all_from_db("PowerSpot")


def cached(cachefile):
    """
    A function that creates a decorator which will use "cachefile" for caching the results of the decorated function "fn".
    """
    def decorator(fn):  # define a decorator for a function "fn"
        def wrapped(*args, **kwargs):   # define a wrapper that will finally call "fn" with all arguments            
            # if cache exists -> load it and return its content
            if os.path.exists(cachefile):
                    with open(cachefile, 'rb') as cachehandle:
                        print("using cached result from '%s'" % cachefile)
                        return pickle.load(cachehandle)

            # execute the function with all arguments passed
            res = fn(*args, **kwargs)

            # write to cache file
            with open(cachefile, 'wb') as cachehandle:
                print("saving result to cache '%s'" % cachefile)
                pickle.dump(res, cachehandle)

            return res

        return wrapped

    return decorator   # return this "customized" decorator that uses "cachefile"
