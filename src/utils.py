from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
import os

def write_to_db(items, collection, index, unique_keys):
    def chunk(seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))
    client = FaunaClient(secret=os.environ["FAUNA_SECRET"])
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
        result = client.query(q.map_expr(lambda x: q.select("data",q.get(x)), q.paginate(q.documents(q.collection(collection)), size=100000, after=after)))
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
