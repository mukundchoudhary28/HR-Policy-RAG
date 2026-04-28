from typing import Dict
from src.core.dependencies import get_chroma_collection


def build_chroma_filter(filter_dict: Dict) -> Dict:
    chroma_filter = {"$and": []}

    if filter_dict.get("doc_type"):
        chroma_filter["$and"].append({"Document Type": filter_dict["doc_type"]})

    if filter_dict.get("year"):
        chroma_filter["$and"].append({"Year": filter_dict["year"]})
    else:
        chroma_filter["$and"].append({"Is Latest": "Yes"})

    if filter_dict.get("region"):
        regions = [
            r.lower().strip() for r in filter_dict["region"]
        ]

        chroma_filter["$and"].append({
            "Applicable Region": {
                "$in": regions + ["global"]
            }})

    if not chroma_filter["$and"]:
        return {}
    elif len(chroma_filter["$and"]) == 1:
        return chroma_filter["$and"][0]

    return chroma_filter




def retrieve_relevant_chunks(query_embedding, filter, top_k=5):
    
    collection = get_chroma_collection()
    chroma_filter = build_chroma_filter(filter)

    results = collection.query(
        query_embeddings=[query_embedding], 
        n_results=top_k, 
        where=chroma_filter)
    return results