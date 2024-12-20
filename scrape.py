import json

import requests
from bs4 import BeautifulSoup


def product_details(content: str):
    result = {}
    soup = BeautifulSoup(content, 'html.parser')

    try:
        result["name"] = soup.select_one(".b-pdp__product-name").text.strip() if soup.select_one(".b-pdp__product-name") else None
        result["price"] = soup.select_one(".price__regular").text.strip() if soup.select_one(".price__regular") else None

        sale_price_element = soup.select_one(".price__sale .value")
        if sale_price_element:
            for sr_only in sale_price_element.select('span'):
                sr_only.decompose()
            result["sale_price"] = sale_price_element.get_text(strip=True)

        images_elements = soup.select(".carousel-indicators li img")
        images = []
        for image_element in images_elements:
            if "data-src" in image_element.attrs:
                images.append(image_element["data-src"].split('?')[0])
            elif "src" in image_element.attrs:
                images.append(image_element["src"].split('?')[0])

        result["images"] = images
        description_element = soup.find("div", class_="b-productinfo", attrs={"data-product-attr": "productDescription"})
        if description_element:
            result["description"] = description_element.text.strip()

        description_specification_elements = soup.select(".b-productinfo li")
        result["description_specification"] = [element.text.strip() for element in description_specification_elements]

        scripts = soup.find_all('script')
        specification_json = ""
        specification2_json = ""
        for script in scripts:
            if script.string and script.string.strip().startswith("pageDataLayer ="):
                specification_json = script.string.replace('pageDataLayer = ', '').rstrip(';')
            elif script.string and script.string.strip().startswith("{\"@context\":\"https://schema.org/\",\"@type\":\"Product"):
                specification2_json = script.string.strip()

        if specification2_json:
            specification_data = json.loads(specification2_json)
            result["brand"] = specification_data.get("brand", {}).get("name", None)

        if specification_json:
            specification_data = json.loads(specification_json)
            try:
                result["available_sizes"] = specification_data.get("availableSizes", [])
                result["unavailable_sizes"] = specification_data.get("unavailableSizes", [])

                result["available_sizes_eu"] = specification_data.get("availableSizesEU", [])
                result["unavailable_sizes_eu"] = specification_data.get("unavailableSizesEU", [])

                result["available_sizes_uk"] = specification_data.get("availableSizesUK", [])
                result["unavailable_sizes_uk"] = specification_data.get("unavailableSizesUK", [])

                result["available_sizes_us"] = specification_data.get("availableSizesUS", [])
                result["unavailable_sizes_us"] = specification_data.get("unavailableSizesUS", [])

                result["sku_id"] = specification_data.get('pageDataMoeEvents', [{}])[0].get('eventData', {}).get('sku_id', None)

                result["gender"] = specification_data.get('pageDataMoeEvents', [{}])[0].get('eventData', {}).get('prod_gender', None)
                result["kids_gender"] = specification_data.get('pageDataMoeEvents', [{}])[0].get('eventData', {}).get('kids_gender', None)

                result["primary_category_id"] = specification_data.get('pageDataMoeEvents', [{}])[0].get('eventData', {}).get('primary_categoryid', None)
                result["category"] = specification_data.get('pageDataMoeEvents', [{}])[0].get('eventData', {}).get('category', None)
                result["sub_category"] = specification_data.get('pageDataMoeEvents', [{}])[0].get('eventData', {}).get('sub_category', None)
                result["sub_category2"] = specification_data.get('pageDataMoeEvents', [{}])[0].get('eventData', {}).get('sub_category2', None)

                result["color"] = specification_data.get('pageDataMoeEvents', [{}])[0].get('eventData', {}).get('color', None)
            except Exception as e:
                print(f"Error while processing specification_data: {e}")

        return result
    except AttributeError:
        print("Failed to extract product details.")
        return None


def product_variation(content: str):
    result = {}
    specification_data = json.loads(content)

    result["name"] = specification_data.get("product", {}).get("productName", None)
    result["brand"] = specification_data.get("product", {}).get("brand", None)
    result["color"] = specification_data.get("product", {}).get("color", None)
    result["description"] = specification_data.get("product", {}).get("shortDescription", None)
    product_html = specification_data.get("product", {}).get("pdpProductHtml", None)

    product_detail_data = product_details(product_html)
    if product_detail_data:
        result.update(product_detail_data)

    result["available_sizes"] = specification_data.get("pageDataLayer", {}).get("availableSizes", [])
    result["unavailable_sizes"] = specification_data.get("pageDataLayer", {}).get("unavailableSizes", [])
    result["available_sizes_eu"] = specification_data.get("pageDataLayer", {}).get("availableSizesEU", [])
    result["unavailable_sizes_eu"] = specification_data.get("pageDataLayer", {}).get("unavailableSizesEU", [])
    result["available_sizes_uk"] = specification_data.get("pageDataLayer", {}).get("availableSizesUK", [])
    result["unavailable_sizes_uk"] = specification_data.get("pageDataLayer", {}).get("unavailableSizesUK", [])
    result["available_sizes_us"] = specification_data.get("pageDataLayer", {}).get("availableSizesUS", [])
    result["unavailable_sizes_us"] = specification_data.get("pageDataLayer", {}).get("unavailableSizesUS", [])

    result["sku_id"] = specification_data.get("pageDataLayer", {}).get('pageDataMoeEvents', [{}])[0].get('eventData', {}).get('sku_id', None)
    result["gender"] = specification_data.get("pageDataLayer", {}).get('pageDataMoeEvents', [{}])[0].get('eventData', {}).get('prod_gender', None)
    result["kids_gender"] = specification_data.get("pageDataLayer", {}).get('pageDataMoeEvents', [{}])[0].get('eventData', {}).get('kids_gender', None)
    result["primary_category_id"] = specification_data.get("pageDataLayer", {}).get('pageDataMoeEvents', [{}])[0].get('eventData', {}).get('primary_categoryid', None)
    result["category"] = specification_data.get("pageDataLayer", {}).get('pageDataMoeEvents', [{}])[0].get('eventData', {}).get('category', None)
    result["sub_category"] = specification_data.get("pageDataLayer", {}).get('pageDataMoeEvents', [{}])[0].get('eventData', {}).get('sub_category', None)
    result["sub_category2"] = specification_data.get("pageDataLayer", {}).get('pageDataMoeEvents', [{}])[0].get('eventData', {}).get('sub_category2', None)

    return result


if __name__ == "__main__":
    product_url = "https://www.nike.ae/en/al-ittihad-f.c.-2024-25-stadium-home-jersey/NKFQ5003-721IT25-C.html"
    product_url = "https://www.nike.ae/en/jordan-sport-dri-fit-mens-mesh-shorts/NKDH9077-010.html"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    response = requests.get(product_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve the product page. Status code: {response.status_code}")

    product_details = product_details(response.text)
    print(product_details)
