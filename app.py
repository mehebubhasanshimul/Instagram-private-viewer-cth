import os
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

def fetch_instagram_data(username):
    # আপনার দেওয়া RapidAPI এন্ডপয়েন্ট
    url = "https://instagram-scraper-stable-api.p.rapidapi.com/get_ig_user_followers_v2.php"
    
    # আপনার দেওয়া API Key ও প্যারামিটারস
    headers = {
        "x-rapidapi-key": "b3ad11e41cmshb18121f061df58ep1b5c61jsnd7a63dda9d56",
        "x-rapidapi-host": "instagram-scraper-stable-api.p.rapidapi.com",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # বডি ডাটা ফরম্যাট (ইউজারনেম ডাইনামিক করা হয়েছে)
    payload = {
        "username_or_url": username,
        "data": "following",
        "amount": "12",
        "pagination_token": ""
    }
    
    try:
        # POST রিকোয়েস্ট পাঠানো হচ্ছে
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        
        if response.status_code != 200:
            return {"error": f"API Error. Status code: {response.status_code}"}
            
        data = response.json()
        
        # এপিআই রেসপন্স থেকে মূল ইউজার অবজেক্ট বা ডেটা এক্সট্রাক্ট করা
        # নোট: এই এপিআই-এর রেসপন্স স্ট্রাকচার অনুযায়ী ডেটা পার্সিং কিছুটা পরিবর্তন হতে পারে
        user_info = data.get("data", {})
        if not user_info:
            # যদি এপিআই সরাসরি অবজেক্ট রিটার্ন করে
            user_info = data
            
        # প্রোফাইল স্ট্যাটাস এবং বেসিক ইনফো ফিল্টার
        is_private = user_info.get("is_private", False)
        
        # ফলোয়ার বা ফলোইং লিস্ট থেকে কিছু ডেটা ডাইনামিকালি দেখানোর জন্য
        edges = user_info.get("items", []) or user_info.get("data", [])
        posts = []
        
        # যদি এপিআই রেসপন্সে কোন লিস্ট বা লিংক থাকে তা ফিল্টার করা
        if isinstance(edges, list):
            for item in edges:
                shortcode = item.get("shortcode")
                if shortcode:
                    posts.append(f"https://www.instagram.com/p/{shortcode}")
                elif item.get("username"):
                    # যদি ফলোয়ারদের ইউজারনেম আসে, তবে তাদের প্রোফাইল লিংক অ্যাড হবে
                    posts.append(f"https://www.instagram.com/{item.get('username')}")
                
        return {
            "username": username,
            "full_name": user_info.get("full_name") or user_info.get("username", username),
            "is_private": is_private,
            "profile_pic": user_info.get("profile_pic_url") or "https://via.placeholder.com/150",
            "followers": user_info.get("follower_count") or user_info.get("followers", 0),
            "following": user_info.get("following_count") or user_info.get("following", 0),
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

if __name__ == '__main__':
    app.run(debug=True)
