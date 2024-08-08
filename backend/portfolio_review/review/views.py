from django.shortcuts import render
from selenium import webdriver 
import cloudinary
import cloudinary.uploader
import requests
from django.views.decorators.http import require_http_methods
import json
from django.http import JsonResponse
from .models import Review
# Create your views here.

# configure cloudinary
cloudinary.config( 
    cloud_name = "djhcrdtsh", 
    api_key = "998433841281296", 
    api_secret = "<CLOUDINARY_API_KEY>", # Click 'View Credentials' below to copy your API secret
    secure=True
)

# ftn to take screenshot  of url website
def take_screenshot(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") # when you want chrome instance it does that in the backend
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usuage")
    browser = webdriver.Chrome(options=options)

    browser.get(url)

    # now take height of url - JS code
    total_height = browser.execute_script("return document.body.parentNode.scrollHeight")
    # resizing the window of browser
    browser.set_window_size(1200, total_height)
    # take screenshot as png
    screenshot = browser.get_screenshot_as_png()

    browser.quit()

    # define image returned by cloudinary
    # sanitize url to look as want
    sanitized_url = url.replace('http://', '').replace('https://', '').replace('/', '_').replace(':', '_')

    # upload screenshot cloudinary
    upload_response = cloudinary.uploader.upload(
        screenshot,
        folder="screenshots",
        public_id=f"{sanitized_url}.png" ,#to specify the name for the returned url
        resource_type='image'
    )
    # print(upload_response)
    return upload_response['url']
    
def get_review(screenshot_url):
    url = "https://general-runtime.voiceflow.com/state/user/testuser/interact?logs=off"

    payload = {
        "action": {
            "type": "intent",
            "payload": {
                "query": screenshot_url,
                "intent": { "name": "review_intent" },
                "entities": []
            }
        },
        "config": {
            "tts": False,
            "stripSSML": True,
            "stopAll": True,
            "excludeTypes": ["block", "debug", "flow"]
        },
        "state": { "variables": { "x_var": 1 } }
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "<VOICEFLOW_API_KEY>"
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    
    review_text = "" # review to return

    # to get to text
    for item in data:
        if item['type'] == 'text' and 'payload' in item and 'slate' in item['payload'] and 'content' in item['payload']['slate']:
            review_text = item['payload']['slate']['content'][0]['children'][1]['text']
            break


    #print(review_text)
    return review_text

# decorator to specify only POST access this method
@require_http_methods(["POST"])
def submit_url(request):
    data = json.loads(request.body) # load the body of request as json
    domain = data.get('domain')

    # take screenshot
    website_screenshot = take_screenshot(domain) # url of the uploaded screenshot
    website_review = get_review(website_screenshot) # get review of uploaded image url

    # craete a model object
    new_review_object = Review.objects.create(
        site_url = domain,
        site_image_url = website_screenshot,
        feedback = website_review,
    )

    # if user rating  then update the rating column in database
    review_id = new_review_object.id

    response_data = {
        'website_screenshot': website_screenshot,
        'website_review': website_review,
        'review_id': review_id,

    }
    return JsonResponse(response_data) # display that data in csrf response

# decorator to specify only POST access this method
@require_http_methods(["POST"])
# def ftn to call when user enter rating update in db
def feedback(request):
    data = json.loads(request.body)
    review_id = data.get('id')
    type = data.get('type')

    try:
        review = Review.objects.get(id=review_id) # get element from db whose id is
        review.user_rating = type
        review.save()

        return JsonResponse({"status": "success", "message": "Feedback Submitted"})
    except Review.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Review Not Found"})

# ftn called in urls.py to print index html
def index(request):
    # render the request by rendering the html file
    #take_screenshot("https://felix221123.github.io/my-portfolio-website/")
    #get_review("http://res.cloudinary.com/djhcrdtsh/image/upload/v1723034972/screenshots/felix221123.github.io_my-portfolio-website_.png.png")
    return render(request, 'index.html')
