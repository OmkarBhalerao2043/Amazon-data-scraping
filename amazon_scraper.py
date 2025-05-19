import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def is_sponsored(product):
    # Amazon marks sponsored products with a 'Sponsored' label
    sponsored = product.find('span', string=lambda text: text and 'Sponsored' in text)
    return sponsored is not None

def extract_brand(product):
    # Try to find brand from the data-brand attribute or within the product title
    brand = product.get('data-brand')
    if brand:
        return brand.strip()
    # Some products have brand in the 'by' line
    byline = product.find('h5', class_='s-line-clamp-1')
    if byline:
        return byline.text.strip()
    # Fallback: Try to extract brand from title (first word)
    title = product.h2.text.strip() if product.h2 else ''
    if title:
        return title.split()[0]
    return 'N/A'

def scrape_amazon_products(keyword, num_pages):
    products = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    for page in range(1, num_pages + 1):
        url = f"https://www.amazon.in/s?k={keyword.replace(' ', '+')}&page={page}"
        print(f"Scraping page {page}: {url}")
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page {page}, status code: {response.status_code}")
            continue
        soup = BeautifulSoup(response.content, 'html.parser')

        for product in soup.find_all('div', {'data-component-type': 's-search-result'}):
            if is_sponsored(product):
                continue

            # Title
            title = product.h2.text.strip() if product.h2 else 'N/A'

            # Product URL
            product_url = ''
            link = product.h2.find('a', href=True) if product.h2 else None
            product_url = 'https://www.amazon.in' + link

            # Brand extraction
            brand = extract_brand(product)

            # Reviews and rating
            reviews = product.find('span', class_='a-size-base').text.strip() if product.find('span', class_='a-size-base') else '0'
            rating = product.find('span', class_='a-icon-alt').text.strip() if product.find('span', class_='a-icon-alt') else '0'

            # Price
            selling_price = product.find('span', class_='a-price-whole').text.strip() if product.find('span', class_='a-price-whole') else 'N/A'

            # Image
            image_url = product.find('img', class_='s-image')['src'] if product.find('img', class_='s-image') else 'N/A'

            products.append({
                'Title': title,
                'Brand': brand,
                'Reviews': reviews,
                'Rating': rating,
                'Selling Price': selling_price,
                'Image URL': image_url,
                'Product URL': product_url
            })

        time.sleep(3)  # Be polite to Amazon

    return products

def save_to_csv(products, filename):
    df = pd.DataFrame(products)
    df.to_csv(filename, index=False)
    print(f"Saved {len(products)} products to {filename}")

if __name__ == "__main__":
    keyword = "soft toys"
    num_pages = 3  # You can change this as needed
    products = scrape_amazon_products(keyword, num_pages)
    save_to_csv(products, 'Amazon_Soft_toys_Scrping_data.csv')