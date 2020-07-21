from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
import os

os.environ["FAUNA_SECRET"] = "fnADwBbPWHACBcWfAJOyZUHjoJ5cMFuZu3k9B2NO"


def write_to_db(items, collection, index, unique_key):
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
    [collection,index, q.select(unique_key, item), item ],
  ),
      items
        )
    )
