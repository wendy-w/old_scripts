def get_location_name(city_url):
    index = city_urls.index(city_url)
    return city_locations[index]


f = open("country_cities_20180725.txt", "r", encoding="utf-8")
city_lists = [item.strip("\n") for item in f.readlines()]
f.close()
city_urls = ["https://www.tripadvisor.cn" + i.split(",")[2] for i in city_lists]
city_locations = [i.split(",")[0] for i in city_lists]
print(get_location_name("https://www.tripadvisor.cn/Hotels-g294066-Punta_del_Este_Maldonado_Department-Hotels.html"))
