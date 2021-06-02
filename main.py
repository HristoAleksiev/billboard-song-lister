from bs4 import BeautifulSoup
import requests
import datetime

billboard_base_url = "https://www.billboard.com/charts/hot-100/"
billabord_user_selected_url = ""
formatted_date = ""

while type(formatted_date) == str:
    try:
        user_date = input("Please specify the date to get the top songs from (format must be YYYY-MM-DD): ")
        user_date = user_date.split("-")
        formatted_date = datetime.date(int(user_date[0]), int(user_date[1]), int(user_date[2]))
    except ValueError:
        print("The date you have entered is not in the right format!")
    else:
        billabord_user_selected_url = billboard_base_url + formatted_date.strftime("%Y-%m-%d")

response = requests.get(url=billabord_user_selected_url).text

soup = BeautifulSoup(response, "html.parser")
songs = [f"{artist.text} - {song_name.text}"
         for artist, song_name
         in zip(soup.find_all(class_="chart-element__information__artist text--truncate color--secondary"),
                soup.find_all(class_="chart-element__information__song text--truncate color--primary"))]

print(songs)
