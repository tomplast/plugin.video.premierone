# Module: addon
# Author: Tomas "tomplast" Gustavsson
# Created on: 30.12.2022
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""
Premier One video plugin
"""
import xbmcgui
import xbmcplugin
import requests
import uuid
import routing

plugin = routing.Plugin()
DEVICE_ID = str(uuid.uuid4())


@plugin.route("/list_search")
def list_search():
    search_term = xbmcgui.Dialog().input("Поиск")
    search_result = requests.get(
        f"https://premier.one/app/v1.2/search?query={search_term}&page=1&picture_type=card_group&system=hwi_vod_id%2Chwi_world&is_active=1&device=web",
        headers={"x-device-type": "browser", "x-device-id": DEVICE_ID},
    ).json()

    for card in search_result["results"]:
        list_item = xbmcgui.ListItem(label=card["name"])
        list_item.setArt({"thumb": card["picture"]})

        list_item.setInfo(
            "video",
            {
                "title": card["name"],
                "genre": ", ".join([x["name"] for x in card["genres"]]),
                "mediatype": "video",
            },
        )

        url = plugin.url_for(list_seasons, program=card["slug"])
        xbmcplugin.addDirectoryItem(plugin.handle, url, list_item, True)

    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route("/list_seasons/<program>")
def list_seasons(program):
    result = requests.get(
        f"https://premier.one/uma-api/metainfo/tv/{program}/season/?picture_type=banner"
    ).json()

    for season in result:
        list_item = xbmcgui.ListItem(label=f'сезон {season["number"]}')
        list_item.setArt({"thumb": season["picture"]})

        url = plugin.url_for(
            list_videos, program=program, season=int(season["number"]), page=1
        )
        xbmcplugin.addDirectoryItem(plugin.handle, url, list_item, True)

    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route("/")
def list_main_menu():
    xbmcplugin.addDirectoryItem(
        plugin.handle,
        plugin.url_for(list_free, page=1),
        xbmcgui.ListItem(label="Бесплатно"),
        True,
    )

    xbmcplugin.addDirectoryItem(
        plugin.handle,
        plugin.url_for(list_search),
        xbmcgui.ListItem(label="Поиск (Может работать)"),
        True,
    )

    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route("/list_programs")
def list_programs(page=1):
    card_group = requests.get(
        f"https://premier.one/uma-api/feeds/cardgroup/202?alias=all_premier&style=portrait&link=https%3A%2F%2Ftnt-premier.ru&title=&bg_url=https%3A%2F%2Ftnt-premier.ru%2Fimg%2Fdevices-4.1168fded.png&picture_type=card_group&quantity=6&sort=publication_d&origin__type=hwi,rtb&is_active=1&system=hwi_vod_id,hwi_world&page={page}"
    ).json()

    xbmcplugin.addDirectoryItem(
        plugin.handle,
        plugin.url_for(list_search),
        xbmcgui.ListItem(label="Поиск"),
        True,
    )

    for card in card_group["results"]:

        list_item = xbmcgui.ListItem(label=card["object"]["name"])
        list_item.setArt({"thumb": card["object"]["picture"]})

        list_item.setInfo(
            "video",
            {
                "title": card["object"]["name"],
                "genre": ", ".join([x["name"] for x in card["object"]["genres"]]),
                "mediatype": "video",
            },
        )
        url = plugin.url_for(list_seasons, program=card["object"]["slug"])
        xbmcplugin.addDirectoryItem(plugin.handle, url, list_item, True)

    if card_group["has_next"]:
        xbmcplugin.addDirectoryItem(
            plugin.handle,
            plugin.url_for(list_programs, page=int(page) + 1),
            xbmcgui.ListItem(label="следующий"),
            True,
        )

    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route("/list_videos/<program>/<season>/<page>")
def list_videos(program, season, page):
    xbmcplugin.setPluginCategory(plugin.handle, "N/A")
    xbmcplugin.setContent(plugin.handle, "videos")

    videos = requests.get(
        f"https://premier.one/uma-api/metainfo/tv/{program}/video/?show_all=1&season={season}&type=6%2C9&limit=18&origin__type=hwi%2Crtb&page={page}"
    ).json()

    for video in videos["results"]:
        list_item = xbmcgui.ListItem(label=f"{video['title']}")
        list_item.setArt({"thumb": video["thumbnail_url"]})
        list_item.setInfo(
            "video",
            {
                "title": video["title"],
                "plot": video["description"],
                "season": season,
                "episode": video["episode"],
                "mediatype": "video",
                "picture": video["thumbnail_url"],
            },
        )
        list_item.setProperty("IsPlayable", "true")

        url = plugin.url_for(play_video, media_id=video["id"])

        xbmcplugin.addDirectoryItem(plugin.handle, url, list_item, False)

    if videos["has_next"]:
        xbmcplugin.addDirectoryItem(
            plugin.handle,
            plugin.url_for(
                list_videos, season=season, program=program, page=int(page) + 1
            ),
            xbmcgui.ListItem(label="следующий"),
            True,
        )

    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route("/list_free/<page>")
def list_free(page):
    card_group = requests.get(
        f"https://premier.one/uma-api/feeds/cardgroup/250?alias=all_premier&style=portrait&link=https%3A%2F%2Ftnt-premier.ru&title=&bg_url=https%3A%2F%2Ftnt-premier.ru%2Fimg%2Fdevices-4.1168fded.png&picture_type=card_group&quantity=6&sort=publication_d&origin__type=hwi,rtb&is_active=1&system=hwi_vod_id,hwi_world&page={page}"
    ).json()

    for card in card_group["results"]:

        list_item = xbmcgui.ListItem(label=card["object"]["name"])
        list_item.setArt({"thumb": card["object"]["picture"]})

        list_item.setInfo(
            "video",
            {
                "title": card["object"]["name"],
                "genre": ", ".join([x["name"] for x in card["object"]["genres"]]),
                "mediatype": "video",
            },
        )
        url = plugin.url_for(list_seasons, program=card["object"]["slug"])
        xbmcplugin.addDirectoryItem(plugin.handle, url, list_item, True)

    if card_group["has_next"]:
        xbmcplugin.addDirectoryItem(
            plugin.handle,
            plugin.url_for(list_free, page=int(page) + 1),
            xbmcgui.ListItem(label="следующий"),
            True,
        )

    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route("/play_video/<media_id>")
def play_video(media_id):
    media = requests.get(
        f"https://premier.one/api/play/options/{media_id}/?format=json&no_404=true&referer=https://premier.one/show/istoriya-na-noch/season/1/episode/18?fullscreen=true"
    ).json()

    play_item = xbmcgui.ListItem(path=media["video_balancer"]["default"])
    xbmcplugin.setResolvedUrl(plugin.handle, True, listitem=play_item)


if __name__ == "__main__":
    xbmcplugin.setPluginCategory(plugin.handle, "")
    plugin.run()
