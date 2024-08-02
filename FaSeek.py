import os, re, json, base64, requests
from dotenv import load_dotenv
from scrapingbee import ScrapingBeeClient

load_dotenv()
API_KEY = os.getenv('API_KEY')

class FaSeek:
    def __init__(self, image_path, nsfw=False):
        self.api_key = API_KEY
        self.client = ScrapingBeeClient(api_key=self.api_key)
        self.image_path = image_path
        self.url = 'https://pimeyes.com'
        self.headers = {
            'Content-Type': 'application/json',
            'Host': 'pimeyes.com',
        }
        self.nsfw = nsfw
        self.results = {}
        self.links = []

    def image_to_base64(self):
        with open(self.image_path, 'rb') as f:
            image_bytes = f.read()
            base64_bytes = base64.b64encode(image_bytes)
            base64_string = base64_bytes.decode('utf-8')
        return base64_string
    
    def post(self, custom_url, payload):
        response = self.client.post(
            self.url + custom_url,
            headers = self.headers,
            data = payload,
            params = {
                'render_js': 'False',
            }
        )
        return response

    def upload_image(self):
        payload = {
            "g-recaptcha-response": None,
            "image": "data:image/png;base64," + self.image_to_base64()
        }
        response = requests.post(self.url+'/api/upload/file', json=payload)
        response = json.loads(response.text)
        return response

    def premium_search(self, face_id):
        payload = {
            "faces": [face_id],
            "time": "any",
            "type": "PREMIUM_SEARCH",
            "g-recaptcha-response": None
        }
        json_payload = json.dumps(payload)
        response = json.loads(self.post('/api/search/new', json_payload).text)
        return response

    def get_api_url(self, collector_hash, search_hash, face_id):
        url = f'{self.url}/en/results/{collector_hash}_{search_hash}?query={face_id}'
        response = requests.get(url)
        api_url = re.findall(r"jsc\d+", response.text)[0]
        return api_url

    def get_results(self, api_url, search_hash):
        url = f"https://{api_url}.pimeyes.com/get_results"

        payload = {
            "hash": search_hash,
            "limit": 250,
            "offset": 0,
            "retryCount": 0
        }
        headers = {
            'Host': f'{api_url}.pimeyes.com',
            'Content-Type': 'application/json',
            'Content-Length': str(len(payload)),
        }
        response = requests.post(
            url=url,
            headers=headers,
            json=payload
        )
        results = json.loads(response.text)
        return results

    def process_search(self):
        print("Starting search process...")
        try:
            # Upload Image
            print("Uploading image...")
            image_result = self.upload_image()
            face_id = image_result['faces'][0]['id']
            print(f"Uploaded image successfully. Face ID: {face_id}")

            # Search Image
            print("Performing premium search...")
            search_result = self.premium_search(face_id)
            search_hash = search_result['searchHash']
            print(f"Premium search completed. Search hash: {search_hash}")

            # Fetch Results
            print("Fetching results...")
            collector_hash = search_result['searchCollectorHash']
            api_url = self.get_api_url(collector_hash, search_hash, face_id)
            results = self.get_results(api_url, search_hash)
            results = results['results']
            print("Results fetched successfully.")
        except (KeyError, IndexError, json.decoder.JSONDecodeError):
            return None
        
        if self.nsfw:
            print("Validating links (NSFW mode)...")
            for result in results:
                thumbnail_url = result['thumbnailUrl']
                decoded_url = json.loads(bytes.fromhex(
                    thumbnail_url.split('/')[-1]).decode("utf-8"))['url']
                self.results[thumbnail_url] = decoded_url
                self.links.append(decoded_url)
        else:
            print("Validating links (Non-NSFW mode)...")
            for result in results:
                if result['adultContent'] == 'true':
                    continue
                thumbnail_url = result['thumbnailUrl']
                decoded_url = json.loads(bytes.fromhex(
                    thumbnail_url.split('/')[-1]).decode("utf-8"))['url']
                self.results[thumbnail_url] = decoded_url
                self.links.append(decoded_url)
        print("Search process completed.")


if __name__ == '__main__':
    api = FaSeek('daniel.jpg', nsfw=True)
    api.process_search()
    for link in api.links:
        print(link)
