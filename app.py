import os
import requests
import re
from flask import Flask, render_template, request

app = Flask(__name__)

def extract_username(input_string):
    """ইউজার লিঙ্ক বা @সহ নাম দিলে সেখান থেকে শুধু ইউজারনেম ফিল্টার করার লজিক"""
    input_string = input_string.strip()
    # যদি পুরো ইউআরএল দেয় (যেমন: https://www.instagram.com/username/?igsh=...)
    if "instagram.com" in input_string:
        match = re.search(r"instagram\.com/([^/?#]+)", input_string)
        if match:
            return match.group(1)
    # যদি @ দিয়ে নাম দেয় (যেমন: @username)
    return input_string.replace("@", "")

def fetch_instagram_data(raw_input):
    username = extract_username(raw_input)
    
    # আপনার দেওয়া stable-api এন্ডপয়েন্ট
    url = "https://instagram-scraper-stable-api.p.rapidapi.com/get_ig_user_followers_v2.php"
    
    headers = {
        "x-rapidapi-key": "b3ad11e41cmshb18121f061df58ep1b5c61jsnd7a63dda9d56",
        "x-rapidapi-host": "instagram-scraper-stable-api.p.rapidapi.com",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    payload = {
        "username_or_url": username,
        "data": "following",
        "amount": "12",
        "pagination_token": ""
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        
        if response.status_code != 200:
            return {"error": f"API Error. Status code: {response.status_code}"}
            
        data = response.json()
        
        # এই নির্দিষ্ট এপিআই-এর সঠিক JSON পাথ চেক করা
        # সাধারণত এই এপিআই 'user' বা 'data' কি-এর ভেতরে প্রোফাইল অবজেক্ট দেয়
        user_info = data.get("data", {}).get("user", {}) or data.get("user", {}) or data.get("data", {})
        
        if not user_info or (isinstance(user_info, dict) and not user_info.get("username") and not user_info.get("id")):
            # যদি সরাসরি রুট লেভেলে ডেটা থাকে
            user_info = data

        is_private = user_info.get("is_private", False)
        
        # সঠিক প্রোফাইল পিকচার এবং ফলোয়ার তথ্য পার্সিং
        profile_pic = user_info.get("profile_pic_url") or user_info.get("profile_pic_url_hd") or "https://via.placeholder.com/150"
        followers = user_info.get("follower_count") or user_info.get("followers") or user_info.get("edge_followed_by", {}).get("count", 0)
        following = user_info.get("following_count") or user_info.get("following") or user_info.get("edge_follow", {}).get("count", 0)
        full_name = user_info.get("full_name") or user_info.get("username") or username
        
        # ফলোয়িং বা স্ক্র্যাপড লিস্ট হ্যান্ডেল করা
        items = data.get("data", {}).get("items", []) or data.get("items", [])
        posts = []
        
        if isinstance(items, list):
            for item in items:
                if item.get("username"):
                    posts.append(f"https://www.instagram.com/{item.get('username')}")
                elif item.get("shortcode"):
                    posts.append(f"https://www.instagram.com/p/{item.get('shortcode')}")
                
        return {
            "username": username,
            "full_name": full_name,
            "is_private": is_private,
            "profile_pic": profile_pic,
            "followers": followers,
            "following": following,
            "posts": posts
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        username_input = request.form.get('username', '').strip()
        if username_input:
            result = fetch_instagram_data(username_input)
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
