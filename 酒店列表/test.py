def get_from_break():
    total_hotel_list = [item.split(";")[1].strip("\n") for item in
                        open("haoqiao_city_20180731.txt", "r", encoding="utf-8").readlines()]

    total_hotel_name_list = [item.split(";")[0].strip("\n") for item in
                             open("haoqiao_city_20180731.txt", "r", encoding="utf-8").readlines()]
    # for i in total_hotel_name_list:
    #     print(i.split(";")[0], i.split(";")[1])
    suc_hotel_list = [item.split(";")[1].strip("\n") for item in
                      open("已抓取酒店url_v1.txt", "r", encoding="utf-8").readlines()]
    suc_hotel_name_list = [item.split(";")[0].strip("\n") for item in
                           open("已抓取酒店url_v1.txt", "r", encoding="utf-8").readlines()]

    total = list(zip(total_hotel_list, total_hotel_name_list))
    suc = list(zip(suc_hotel_list, suc_hotel_name_list))

    for j in suc:
        total.remove(j)
    rest = total
    return rest


if __name__ == "__main__":
    start_flag = 0
    current = 1
    hotel_list = get_from_break()
    for i in hotel_list[:10]:
        print(i[0], i[1])
