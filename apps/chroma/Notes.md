## RUN CHROMA
Chroma runs as a server and provides Python and JavaScript/TypeScript client SDKs

Python:
```
pip install chromadb-client
```
```
import chromadb
client = chromadb.HttpClient(host='localhost', port=9065)
collection = client.create_collection("sample2_collection")
# Add docs to the collection. Can also update and delete. Row-based API coming soon!
collection.add(
    documents=["This is document1", "This is document2"], # we embed for you, or bring your own
    metadatas=[{"source": "notion"}, {"source": "google-docs"}], # filter on arbitrary metadata!
    ids=["doc1", "doc2"], # must be unique for each doc
)
results = collection.query(
    query_texts=["This is a query document"],
    n_results=2,
    # where={"metadata_field": "is_equal_to_this"}, # optional filter
    # where_document={"$contains":"search_string"}  # optional filter
)
print(results)
```

JavaScript:
```
npm install chromadb-client
```
```
import { ChromaClient } from 'chromadb'
  async function chromaExample() {
    const client = new ChromaClient();
    const collection = await client.createCollection({name: "sample_collection"});
    await collection.add({
      documents: ["This is a document", "This is another document"], // we embed for you, or bring your own
      metadatas: [{ source: "my_source" }, { source: "my_source" }], // filter on arbitrary metadata!
      ids: ["id1", "id2"] // must be unique for each doc
    });
    const results = await collection.query({
      queryTexts: ["This is a query document"],
      nResults: 2,
      // where: {"metadata_field": "is_equal_to_this"}, // optional filter
      // whereDocument: {"$contains":"search_string"} // optional filter
    });
  }
  chromaExample();
```