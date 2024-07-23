import requests
from bs4 import BeautifulSoup
import json

# The URL for the Rightmove property listings
url = "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E924&maxBedrooms=3&maxPrice=270000&minPrice=175000&radius=30.0&index=72&propertyTypes=bungalow%2Cdetached&includeSSTC=false&mustHave=&dontShow=newHome%2Cretirement%2CsharedOwnership&furnishTypes=&keywords="

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# List of words to skip
skip_words = ["semi - detached","semi detached","semi-detached", "shared ownership", "new home", "retirement","Auction", "Lodge", "terraced","terrace", "Semi - Detached"]


# Send a GET request to the URL
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all the property listings
    listings = soup.find_all('div', class_='l-searchResult is-list')

    # Open a file for writing JSON data
    with open('properties.json', 'w', encoding='utf-8') as file:
        # Iterate through each listing and extract relevant information
        for listing in listings:
            # Extract property title
            title_tag = listing.find('h2', class_='propertyCard-title')
            title = title_tag.get_text(strip=True) if title_tag else 'No title'

            # Extract property description using more specific XPath-like structure
            description_tag = listing.select_one('div.propertyCard-description')
            if not description_tag:
                description_tag = listing.select_one('div.propertyCard-content span span')
            description = description_tag.get_text(strip=True) if description_tag else 'No description'

            # Check if the title or description contains any words to skip
            if any(skip_word.lower() in title.lower() for skip_word in skip_words) or any(skip_word.lower() in description.lower() for skip_word in skip_words):
                continue

            # Extract property price
            price_tag = listing.find('div', class_='propertyCard-priceValue')
            price_text = price_tag.get_text(strip=True) if price_tag else 'No price'
            try:
                price = int(price_text.replace('£', '').replace(',', '').strip())
            except ValueError:
                price = 0

            # Extract property address
            address_tag = listing.find('address', class_='propertyCard-address')
            address = address_tag.get_text(strip=True) if address_tag else 'No address'

            # Extract property link
            link_tag = listing.find('a', class_='propertyCard-link')
            link = link_tag['href'] if link_tag else ''
            full_link = f"https://www.rightmove.co.uk{link}" if link else 'No link'

            # Create a JSON object for the current property
            property_data = {
                'title': title,
                'price': price,
                'price_text': price_text,
                'address': address,
                'description': description,
                'link': full_link
            }

            # Write the JSON object to the file as a single line
            file.write(json.dumps(property_data, ensure_ascii=False) + '\n')

    print("Properties have been written to properties.json")
else:
    print(f'Failed to retrieve the webpage. Status code: {response.status_code}')

