import json 
import requests

def Get_Data(url):
	resp = requests.get(url)
	data = json.loads(resp.text)
	return data
	
def Parse_Product(product):
	item_list = {}
	for item in product['variants']:
		item_name = product['title'] + ' --- ' + item['title']
		item_price = item['price']
		item_list[item_name] = item_price
	return item_list

def Parse_Item_List_per_page(data):
	item_list = {}
	for product in data['products']:
		if product['product_type'] == "Clock" or product['product_type'] == "Watch":
			item_list.update(Parse_Product(product))
	return item_list

def Formatter(max_item_title_len, title_len):
	offset = max_item_title_len - title_len
	offset_spaces = ""
	for x in xrange(offset):
		offset_spaces = offset_spaces + " "
	return offset_spaces

def Print_Checkout_List(total_item_list):
	total_price = 0
	max_item_title_len = 8 + max(len(item) for item in total_item_list.keys())
	print "======================= CHECK OUT ======================="
	for title in total_item_list.keys():
		print title ,
		print Formatter(max_item_title_len, len(title)),
		print "$",total_item_list[title]
		total_price = total_price + float(total_item_list[title])
	print "========================================================="
	print "Final price:",
	print Formatter(max_item_title_len, len("Final price:")),
	print "$",total_price

def main():
	url = "http://shopicruit.myshopify.com/products.json?page="
	page_number = 1
	total_item_list = {}
	while True:
		try:
			data = Get_Data(url=url+str(page_number))
		except:
			print "Url not found"
			break;
		try:
			if (len(data['products']) == 0):
				break;
		except:
			print "Sorry the product list is empty"
			break;
		total_item_list.update(Parse_Item_List_per_page(data))
		page_number = page_number + 1

	Print_Checkout_List(total_item_list)

if __name__ == '__main__':
	main()