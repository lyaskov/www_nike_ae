import csv
from datetime import datetime

import requests
import threading
import time

from queue import Queue, Empty
from bs4 import BeautifulSoup
from scrape import product_details, product_variation

# Main page URL
start_url = "https://www.nike.ae/en/home/"
base_url = "https://www.nike.ae"

# Task queue
url_queue = Queue()

# Set to track processed links
visited_urls = set()

# Lock for synchronizing access to visited_urls
visited_lock = threading.Lock()

# Lock for writing to products_data
products_data_lock = threading.Lock()

products_data = []


def export_to_csv(data, csv_file):
    """
    Exports an array of dictionaries to a CSV file.

    :param data: list of dicts, an array of dictionaries with potentially varying keys
    :param csv_file: str, the name of the CSV file for saving
    """
    if not data:
        print("Empty data array. Nothing to export.")
        return

    # Retrieve all unique fields (columns)
    all_fields = set()
    for item in data:
        all_fields.update(item.keys())

    # Convert the set to a list and sort it
    # all_fields = sorted(all_fields)
    all_fields = list(all_fields)

    try:
        # Create and write to the CSV
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=all_fields, extrasaction='ignore', quoting=csv.QUOTE_MINIMAL)

            # Write headers
            writer.writeheader()

            # Write rows, joining lists with commas
            for item in data:
                formatted_item = {key: ", ".join(map(str, value)) if isinstance(value, list) else value for key, value in item.items()}
                writer.writerow(formatted_item)

        print(f"Data successfully exported to the file {csv_file}")

    except Exception as e:
        print(f"Error writing to CSV: {e}")


def scrape_page(url):
    """Function to fetch and process a webpage."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error: {http_err}")
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return None


def process_start_page(url):
    """Process the main page and add categories to the queue."""
    content = scrape_page(url)
    if not content:
        return
    soup = BeautifulSoup(content, 'html.parser')
    urls = list(
        set(
            [a['href'] for a in soup.select("a.b-megasubmenu__link, a.b-megamenu__link") if "href" in a.attrs]
        )
    )
    for url in urls:
        add_to_queue(url, "category")

    print("End process_start_page: ", url)


def process_category(url):
    """Process categories and add subcategories/products to the queue."""
    content = scrape_page(url)
    if not content:
        return

    soup = BeautifulSoup(content, 'html.parser')

    # Find subcategories
    urls = list(
        set(
            [a['href'] for a in soup.select(".b-linkslist a") if "href" in a.attrs]
        )
    )
    for url in urls:
        add_to_queue(url, "category")

    url_next_element = soup.select_one(".b-product-grid__footer-show-more button")
    if url_next_element:
        url_next = url_next_element["data-url"]
        if not url_next.startswith("http"):
            url_next = base_url + url_next
        add_to_queue(url_next, "category")

    # Find products
    product_links = soup.select(".b-product-tile a.b-product-tile__image-link")
    for link in product_links:
        product_url = link['href']
        if not product_url.startswith("http"):
            product_url = base_url + product_url
        add_to_queue(product_url, "product")

    print("End process_category: ", url)


def process_product(url):
    """Scrape a product page."""
    content = scrape_page(url)
    if not content:
        return

    try:
        product_details_data = product_details(content)
        if product_details_data:
            with products_data_lock:
                products_data.append(product_details_data)
    except AttributeError:
        print(f"Failed to extract data for product: {url}")
        return

    # Search for other product variations
    soup = BeautifulSoup(content, "html.parser")
    buttons_without_selected = soup.select("button.color-attribute:not(.m-selected)")
    if buttons_without_selected:
        product_variation_urls = [button["data-url"] for button in buttons_without_selected]
        for url in product_variation_urls:
            if not url.startswith("http"):
                url = base_url + url
            add_to_queue(url, "product_variation")

    print("End process_product: ", url)


def process_product_variation(url):
    """Scrape product variations."""
    content = scrape_page(url)

    variation_data = product_variation(content)
    if variation_data:
        with products_data_lock:
            products_data.append(variation_data)

    print("End process_product_variation: ", url)


def add_to_queue(url, task_type):
    """Add a link to the queue if it has not been processed yet."""
    with visited_lock:
        if url not in visited_urls:
            visited_urls.add(url)
            url_queue.put((task_type, url))
            print(f"Added to queue {task_type}: {url}")


def worker():
    """Thread function for processing the queue."""
    start_time = time.time()
    while True:
        try:
            # Get a task from the queue with a timeout
            task_type, url = url_queue.get(timeout=5)  # Timeout to prevent infinite waiting
        except Empty:
            break  # If the queue is empty and the timeout expires, terminate the thread

        try:
            if task_type == "category":
                process_category(url)
            elif task_type == "product":
                process_product(url)
            elif task_type == "product_variation":
                process_product_variation(url)
            elif task_type == "home":
                process_start_page(url)
        except Exception as e:
            print(f"Error processing {url}: {e}")
        finally:
            url_queue.task_done()

    # End timing
    end_time = time.time()

    # Execution time
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.5f} seconds")


# test_url = "https://www.nike.ae/en/one-womens-high-waisted-7-8-leggings/NKFN3232-C.html"
# add_to_queue(test_url, "product")
# add_to_queue("https://www.nike.ae/en/invincible-3-womens-road-running-shoes/NKDR2660-C.html", "product")
# add_to_queue("https://www.nike.ae/en/infinityrn-4-womens-road-running-shoes/NKDR2670-C.html", "product")
# add_to_queue("https://www.nike.ae/en/pro-womens-dri-fit-cropped-long-sleeve-top/NKFV5484-C.html", "product")
add_to_queue("https://www.nike.ae/en/jordan-womens-tank/NKDX4700-C.html", "product")


# Add the initial page to the queue
# add_to_queue(start_url, "home")

# Number of threads
num_threads = 5

# Create and start threads
threads = []
for _ in range(num_threads):
    thread = threading.Thread(target=worker)
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()

print("Scraping completed!")

# Get the current date and time
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"output_{timestamp}.csv"

# Export data to the CSV file with a timestamped filename
export_to_csv(products_data, filename)
