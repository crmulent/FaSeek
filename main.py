from flask import Flask, render_template, request, jsonify, redirect
import datetime, re, base64, requests, os, json, time
from urllib.parse import unquote, urlparse, parse_qs
from collections import Counter
from dotenv import load_dotenv
from FaSeek import FaSeek
from io import BytesIO
from PIL import Image

load_dotenv()
API_KEY = os.getenv('API_KEY')

image_counter = 1
results, links, tikwm_data = [], [], []
freqlist, tikwm_data, tikwm_freq = {}, [], {}
firstname, lastname, words, yt_links = [], [], [], []
base_path = os.path.dirname(os.path.abspath(__file__))
text_path = os.path.join(base_path, 'text_files')
app = Flask(__name__)

def process_tikwm(vid_ids):
    url = 'https://www.tikwm.com/api/'
    headers = {
        'Host': 'www.tikwm.com',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    data = f'url={vid_ids}&count=12&cursor=0&web=1&hd=1'
    r = requests.post(url, headers=headers, data=data)
    data = json.loads(r.text)
    return data

def extract_tikwm(links):
    results = []
    for link in links:
        if re.search(r"tikwm\.com", link):
            results.append(re.search(r'\d+', link))
    return results

def extract_and_create_youtube_links(urls):
    pattern = r'vi/([^/]+)'
    youtube_links = []
    for url in urls:
        match = re.search(pattern, url)
        
        if match:
            video_id = match.group(1)
            youtube_url = f'https://www.youtube.com/watch?v={video_id}'
            youtube_links.append(youtube_url)
    return youtube_links

def remove_keys_from_json(json_data, keys_to_remove):
    json_copy = json_data.copy()
    
    for key in keys_to_remove:
        if key in json_copy:
            del json_copy[key]
    
    keys_to_remove_based_on_length = [key for key in json_copy if len(key) < 4]
    for key in keys_to_remove_based_on_length:
        del json_copy[key]
    
    keys_to_remove_based_on_numbers = [key for key in json_copy if key.isdigit()]
    for key in keys_to_remove_based_on_numbers:
        del json_copy[key]
    
    keys_to_remove_based_on_pattern = [key for key in json_copy if 4 <= len(key) <= 5 and len(re.findall(r'\d', key)) >= 2]
    for key in keys_to_remove_based_on_pattern:
        del json_copy[key]
    
    return json_copy

def filter_json_by_keys(json_data, key_array):
    lower_json_data = {key.lower(): value for key, value in json_data.items()}
    lower_key_array = [key.lower() for key in key_array]
    filtered_data = {key: json_data[key] for key in lower_key_array if key in lower_json_data}
    return filtered_data

def word_freq(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[~`!@#$%^&*(){}\[\];:"<,.>?\/\\|_+=-]', ' ', text)
    words = text.lower().split()
    freqlist = {}
    for word in words:
        if word.strip():
            freqlist[word] = freqlist.get(word, 0) + 1
    tuples = list(freqlist.items())
    tuples.sort(key=lambda x: x[1], reverse=True)
    return {f'{key}': value for key, value in tuples}

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def download_image(url, save_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False

def is_image_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '')
        if 'image' not in content_type:
            return False
        
        try:
            img = Image.open(BytesIO(response.content))
            img.verify()
        except (IOError, SyntaxError):
            return False
        
        return True
    except Exception as e:
        print(f"Error checking image URL: {e}")
        return False

def get_image_name_from_url(url):
    if not is_image_url(url):
        print("URL does not point to a valid image")
        return None
    
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    path = parsed_url.path
    filename = path.split('/')[-1]
    
    basename, ext = os.path.splitext(filename)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    allowed_extensions = ['.png', '.jpg']
    if ext.lower() not in allowed_extensions:
        ext = '.jpg'
    
    if 'width' in query_params and 'quality' in query_params:
        width = query_params['width'][0]
        quality = query_params['quality'][0]
        basename = f"{basename}_w{width}_q{quality}_{timestamp}"
    else:
        basename = f"{basename}_{timestamp}"
    
    filename = f"{basename}{ext}"
    
    return sanitize_filename(filename)

@app.route('/')
def index():            
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    global results, links, freqlist, firstname, lastname, tikwm_data, tikwm_freq, yt_links

    [i.clear() for i in [results, links, freqlist, firstname, lastname, tikwm_data, tikwm_freq]]

    firstname, lastname = [], []

    data = request.form if request.form else request.json
    if 'image_data' not in data:
        return jsonify({'error': 'No image data received'}), 400
    
    base64_data = data['image_data']
    image_bytes = base64.b64decode(base64_data)
    
    with open('temp_image.png', 'wb') as f:
        f.write(image_bytes)
    
    api = FaSeek('temp_image.png', nsfw=False)
    api.process_search()
    results = api.results
    links = [unquote(link) for link in api.links]
    freqlist = word_freq(' '.join(links))
    print("Length:", len(results))

    with open(os.path.join(text_path, 'htmlWordList.txt'), 'r', encoding='utf-8') as file:
        for line in file:
            words.append(line.strip())
    with open(os.path.join(text_path, 'FirstNames.txt'), 'r', encoding='utf-8') as file:
        for line in file:
            firstname.append(line.strip())
    with open(os.path.join(text_path, 'LastNames.txt'), 'r', encoding='utf-8') as file:
        for line in file:
            lastname.append(line.strip())

    results = results if results else []
    freqlist = freqlist if freqlist else {}
    tikwm_links = extract_tikwm(links)
    for vid in tikwm_links:
        tikwm_data.append(process_tikwm(vid))
        print(vid)
        time.sleep(1)

    yt_links = extract_and_create_youtube_links(links)

    temp_data = []
    for i in tikwm_data:
        try:
            temp_data.append(i['data']['author']['unique_id'])
        except KeyError:
            pass
    tikwm_freq = dict(Counter(temp_data).most_common())
    freqlist = remove_keys_from_json(freqlist, words)
    firstname = filter_json_by_keys(freqlist, firstname)
    lastname = filter_json_by_keys(freqlist, lastname)

    return redirect('/display_results', code=302)

@app.route('/display_results')
def display_results():
    return render_template(
        'results.html',
        results=results,
        freqlist=freqlist,
        firstname=firstname,
        lastname=lastname,
        tikwm_freq=tikwm_freq,
        yt_links = yt_links
    )

@app.route('/download_all_images')
def download_all_images():
    global links, image_counter
   
    if not links:
        return jsonify({'error': 'No images to download'}), 400

    dl_path = os.path.join(base_path, 'downloads')
    
    folder_name = f'Images_{image_counter}'
    folder_path = os.path.join(dl_path, folder_name)
    
    while os.path.exists(folder_path):
        image_counter += 1
        folder_name = f'Images_{image_counter}'
        folder_path = os.path.join(dl_path, folder_name)

    try:
        os.makedirs(folder_path, exist_ok=True)
    except Exception as e:
        return jsonify({'error': f'Failed to create directory: {e}'}), 500

    for link in links:
        try:
            image_name = get_image_name_from_url(link)
            save_path = os.path.join(folder_path, image_name)
            if not download_image(link, save_path):
                print(f"Failed to download image from link: {link}")
        except Exception as e:
            print(f"{e}")

    return jsonify({'message': 'Images have been downloaded successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
