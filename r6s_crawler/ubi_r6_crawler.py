# @Time : 2020/10/24 11:38
# @Author: dan
# @File : ubi_r6_crawler.py

import requests
import os
from bs4 import BeautifulSoup

url = "https://www.ubisoft.com/"


def do_op_page(op_url, op_name):
    req = requests.get(op_url)
    soup = BeautifulSoup(req.text, 'lxml')
    loadout_imgs = soup.find("div", "operator__loadout").find_all("img")

    for img_tag in loadout_imgs:
        img_src = img_tag['src']
        img_name = img_src.split("/")[6]
        print("保存", img_name)
        with open("file/weapon/" + img_name, 'wb') as f:
            img = requests.get(img_src)
            f.write(img.content)

    # with open('file/ability/' + op_name + '.png', 'wb') as f:
    #     print("保存技能icon", loadout_imgs[len(loadout_imgs) - 1]['src'])
    #     img = requests.get(loadout_imgs[len(loadout_imgs) - 1]['src'])
    #     f.write(img.content)


if __name__ == '__main__':
    main_page = requests.get("https://www.ubisoft.com/zh-tw/game/rainbow-six/siege/game-info/operators")
    main_page_soup = BeautifulSoup(main_page.text, 'lxml')
    oplist_cards = main_page_soup.find("div", "oplist__cards__wrapper").find_all("a", "oplist__card")

    for card in oplist_cards:
        op_url = url + card['href']
        op_name = card.find("span").text
        op_img_src = card.find("img", "oplist__card__img")['src']
        op_icon_src = card.find("img", "oplist__card__icon")['src']

        # path = "file/" + op_name
        # if not os.path.exists(path):
        #     os.makedirs(path)
        # else:
        #     pass

        print(op_name.lower())
        with open("file/half_avatar/" + op_name.lower() + ".png", 'wb') as f:
            img = requests.get(op_img_src)
            f.write(img.content)

        with open("file/icon/" + op_name.lower() + ".png", 'wb') as f:
            img = requests.get(op_icon_src)
            f.write(img.content)

        do_op_page(op_url, op_name.lower())
