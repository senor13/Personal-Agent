from memory import add_memory
from pathlib import Path
import json
import os
from googleapiclient.discovery import build
#!pip install sentence-transformers

youtube = build("youtube","v3",developerKey = os.environ["YOUTUBE_API_KEY"])
#model = SentenceTransformer("all-MiniLM-L6-v2")
def save_memory(category,content):
    add_memory(category,content)
def update_memory(id,new_content):
    file = Path("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/memory/long_term.json")
    if file.exists():
        with open("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/memory/long_term.json", "r") as f:
            data =  json.load(f)
            for entry in data:
                if entry["id"] == id:
                    entry["content"] = new_content
            with open("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/memory/long_term.json", "w") as f:
                json.dump(data,f)

def youtube_search(query,channel_id = None, published_after = None,min_view_count = None, max_results = 5,sort_by_views= False):
    print("youtube_search called with:", query, channel_id, published_after, min_view_count, max_results, sort_by_views)
    params = {
        "q": query, 
        "type": "video",
        "part": "snippet",
        "maxResults": max_results                                                                                            
        }
    if channel_id:                                                                                                                                           
      params["channelId"] = channel_id
    if published_after:
      params["publishedAfter"] = published_after
    
    search_list = youtube.search().list(**params).execute()

    final_output = []

    if min_view_count or sort_by_views:
        video_ids = []
        for item in search_list["items"]:
            video_ids.append(item["id"]["videoId"])
        search_list_2 =  youtube.videos().list(part="statistics", id=",".join(video_ids)).execute()
        video_stats = {item["id"]:item["statistics"] for item in search_list_2["items"]}
        for item in search_list["items"]:
            video_id = item["id"]["videoId"]
            views = video_stats[video_id]["viewCount"]
            if min_view_count and int(views) < min_view_count:
                continue

            output = {"title":item["snippet"]["title"],
            "description":item["snippet"]["description"],
            "url":f"https://www.youtube.com/watch?v={video_id}",
            "viewCount": views}
            final_output.append(output)
        if sort_by_views:
            final_output = sorted(final_output,key=lambda x: int(x["viewCount"]),reverse = True)
    else:
        for item in search_list["items"]:
            output = {"title":item["snippet"]["title"],
            "description":item["snippet"]["description"],
            "url":f"https://www.youtube.com/watch?v={item["id"]["videoId"]}"}
            final_output.append(output)


    return final_output
                

    



                


            
    
