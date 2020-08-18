from jikanpy import Jikan
jikan = Jikan()

# json of all anime info specified by Jikan docs
mushishi = jikan.anime(id=457, page=2)
# mushishi = jikan._get(endpoint="anime",id=457, page=2, extension=None)

print(mushishi)


# # same as above, but with extra info
# # see Jikan docs for information about which endpoints have which extensions
# mushishi_with_eps = jikan.anime(457, extension='episodes')
# mushishi_with_eps_2 = jikan.anime(457, extension='episodes', page=2)
# mushishi_with_characters_and_staff = jikan.anime(457, extension='characters_staff')

# # you can also query characters
# ginko = jikan.character(425)

# # and manga
# mushishi_manga = jikan.manga(418)

# # search up people too
# kana_hanazawa = jikan.person(185)

# # search
# search_result = jikan.search('anime', 'Mushishi')
# # add a page number to the search request
# search_result = jikan.search('anime', 'Mushishi', page=2)
# # add a filter to the search (see Jikan docs about what filters are legal)
# search_result = jikan.search('anime', 'Mushishi', parameters={'type': 'tv'})
# search_result = jikan.search('anime', 'Mushishi', parameters={'genre': 37})
# # use multiple query parameters
# search_result = jikan.search('anime', 'Mushishi', parameters={'genre': 37, 'type': 'tv'})
# # use it all!
# search_result = jikan.search('anime', 'Mushishi', page=3, parameters={'genre': 37, 'type': 'tv'})

# # seasonal anime
# winter_2018 = jikan.season(year=2018, season='winter')
# spring_2016 = jikan.season(year=2016, season='spring')

# # all the years and seasons on MAL
# archive = jikan.season_archive()

# # anime in upcoming seasons
# later = jikan.season_later()

# # scheduled anime
# scheduled = jikan.schedule()
# # add a day of the week if you only want the day's schedule
# monday = jikan.schedule(day='monday')

# # top anime
# top_anime = jikan.top(type='anime')
# # add a page and subtype if you want
# top_anime = jikan.top(type='anime', page=2, subtype='upcoming')

# # action anime
# # See Jikan docs for mappings between genres and their IDs
# action = jikan.genre(type='anime', genre_id=1)
# # adventure manga
# adventure = jikan.genre(type='manga', genre_id=2)

# # anime made by Studio Deen (sasuga deen)
# studio_deen_anime = jikan.producer(producer_id=37)
# # add an optional page
# studio_deen_anime = jikan.producer(producer_id=37, page=2)

# # manga from Weekly Shounen Jump
# jump = jikan.magazine(magazine_id=83)
# # add an optional page
# jump = jikan.magazine(magazine_id=83, page=2)

# # user info
# nekomata1037 = jikan.user(username='Nekomata1037')
# # get profile info, same as above
# nekomata1037 = jikan.user(username='Nekomata1037', request='profile')
# # friends info
# nekomata1037 = jikan.user(username='Nekomata1037', request='friends')
# # history of anime/manga
# nekomata1037 = jikan.user(username='Nekomata1037', request='history')
# # anime list
# nekomata1037 = jikan.user(username='Nekomata1037', request='animelist')
# nekomata1037 = jikan.user(username='Nekomata1037', request='animelist', argument='completed', page=2)
# # manga list
# xinil = jikan.user(username='Xinil', request='mangalist')
# xinil = jikan.user(username='Xinil', request='mangalist', argument='all')
# # user info filters (see Jikan docs for valid filters)
# nekomata1037 = jikan.user(username='Nekomata1037', request='animelist', parameters={'year': 2019})

# # clubs
# fantasy_anime_league = jikan.club(379)

# # meta info about the Jikan REST API
# # meta info about what requests have been done
# requests = jikan.meta(request='requests', type='anime', period='today')
# # meta info about API's status
# status = jikan.meta(request='status', type='anime', period='today')
