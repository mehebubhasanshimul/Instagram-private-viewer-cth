import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def fetch_instagram_data(username):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "X-IG-App-ID": "936619743392459",
        "Referer": f"https://www.instagram.com/{username}/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"error": f"Failed to fetch data. Status code: {response.status_code}"}
        
        data = response.json()
        user_data = data.get("data", {}).get("user")
        
        if not user_data:
            return {"error": "User not found or API changed."}
            
        is_private = user_data.get("is_private", False)
        edges = user_data.get("edge_owner_to_timeline_media", {}).get("edges", [])
        
        posts = []
        for edge in edges:
            shortcode = edge.get("node", {}).get("shortcode")
            if shortcode:
                posts.append(f"https://www.instagram.com/p/{shortcode}")
                
        return {
            "username": username,
            "full_name": user_data.get("full_name"),
            "is_private": is_private,
            "profile_pic": user_data.get("profile_pic_url_hd"),
            "followers": user_data.get("edge_followed_by", {}).get("count", 0),
            "following": user_data.get("edge_follow", {}).get("count", 0),
            "posts": posts
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if username:
            result = fetch_instagram_data(username)
    return render_template('index.html', result=result)

# Vercel-এর জন্য প্রয়োজনীয়
if __name__ == '__main__':
    app.run(debug=True)
