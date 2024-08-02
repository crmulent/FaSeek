# FaSeek

## Description
This Python-based reverse imaging program is designed to facilitate Open Source Intelligence (OSINT) gathering and facial recognition by leveraging PimEyes. The tool sends the image to PimEyes for processing and returns links to pages where those matches were found. It provides an efficient way to perform reverse image searches and gather relevant information from the web. This tool can be useful for investigative purposes, security research, and finding more information about people from their photos.

## Features
- Perform reverse image searches using PimEyes’ API.
- Retrieve links to web pages where the image matches were found.
- Display a preview of the image and corresponding links in a web application.
- Support for both clipboard pasting and file uploads for image input.

## Requirements
- Python 3.x
- ScrapingBee API Key

## Installation

### Clone the Repository
Clone the repository to your local machine using:
```
$ git clone https://github.com/crmulent/FaSeek.git
$ cd FaSeek
```

### Install Dependencies
Install the required Python packages by running:
```
$ pip install -r requirements.txt
```

### Adding API Key
Make a **.env** file containing the following:
```
API_KEY=<API KEY>
```
**Note:** Make sure to change the value to your own API key.

## Usage

### Running the Web App Locally
To run the web application locally and open it in your browser:
```
$ python main.py
```
After running the above command, open the program by clicking [here](http://localhost:5000/).

## Web App Features
- **Image Preview**: Displays a preview of the uploaded or pasted image.
- **Search Results**: Shows the preview and when clicked, redirects to the unblurred image (the value).
- **Upload Support**: Allows uploading of image files in addition to clipboard pasting.

## Contribution
Contributions are welcome! If you have suggestions for improvements or encounter issues, please open an issue or submit a pull request. 
