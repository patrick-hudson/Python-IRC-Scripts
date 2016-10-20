###
# Copyright (c) 2015, lunchdump
# All Rights Reserved
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.ircmsgs as ircmsgs
import supybot.callbacks as callbacks
import requests
from random import randrange
#from urllib import quote_plus
import json
import re
import random
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('NSFW')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

class NSFW(callbacks.Plugin):
    """This plugin related to a given phrase, and selects a result at
    random to return to the channel"""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(NSFW, self)
        self.__parent.__init__(irc)
    def GetImages(self, subreddit, count):
        nsfw_return = []
        if(count > 4):
            count = 4
        r = requests.get('http://pornbot.us/api/v1.0/nsfw/'+subreddit+'/'+str(count))
        response = r.json()
        nsfw_list = response['data']
        if('error' in nsfw_list):
            error_list = ['error', nsfw_list['error']]
            return error_list
        else:
            for item in nsfw_list:
                title = item['title']
                url = item['url']
                subreddit = item['subreddit']
                permalink = "https://www.reddit.com{0}".format(item['permlink'])
                message = "{0} - {1} - {2}".format(title, url, permalink)
                nsfw_return.append(message)
            return nsfw_return
    def AddSubreddit(self, subreddit):
        r = requests.post('http://pornbot.us/api/v1.0/nsfw/add', data = {'subreddit':subreddit})
        self.log.info(r.text)
        return r.json()
    def GetImagur(self, subreddit):
        url = 'https://api.imgur.com/3/gallery/r/'+subreddit+'/time/'
        headers = {'Authorization': 'Client-ID cefb2e6ae32f74f'}
        r = requests.get(url, headers=headers)
        response = r.json()
        response = response['data']
        image_list = {}
        for image in response:
            #print(image['id'])
            image_list[image['id']] = {}
            image_list[image['id']]['title'] = image['title']
            image_list[image['id']]['link'] = image['link']
        return image_list
    def GetPornHub(self, category):
        r = requests.get('http://www.pornhub.com/webmasters/search?id=44bc40f3bc04f65b7a35&category='+category+'&tags[]='+category+'&thumbsize=medium')
        response = r.json()
        response = response['videos']
        return response
    def GetYouPorn(self, category):
        r = requests.get('http://www.youporn.com/api/webmasters/search?id=44bc40f3bc04f65b7a35&category='+category+'&tags[]='+category+'&thumbsize=medium')
        response = r.json()
        #print(response)
        response = response['video']
        return response
    def GetRedTube(self, category):
        r = requests.get('http://api.redtube.com/?data=redtube.Videos.searchVideos&output=json&category='+category+'&tags[]='+category+'&thumbsize=medium')
        response = r.json()
        response = response['videos']
        return response
    def nsfw(self, irc, msg, args, query):
        """<phrase>

        Returns porn
        """
        #encoded_query = quote_plus(query)
        #nsfw_url = "http://api.giphy.com/v1/gifs/search?q=%s&api_key=%s&limit=%d&offset=0" % (encoded_query, self.GIPHY_API_KEY, self.CHOOSE_FROM + 1)
        channel = msg.args[0]
        arg_request = re.split('\s+', query)
        result = None
        headers = {
            "User-Agent": "limnoria-nsfw/v0.0.1",
            "Accept": "application/json"
        }
        if(arg_request[0] == "stats"):
            irc.sendMsg(ircmsgs.privmsg(channel, "stats"))
        elif(arg_request[0] == "help"):
            irc.sendMsg(ircmsgs.privmsg(channel, "help"))
        elif(arg_request[0] == "add"):
            add_response = self.AddSubreddit(arg_request[1])
            add_response = add_response['data']
            if 'error' in add_response:
                if '1062' in add_response['error']:
                    irc.sendMsg(ircmsgs.privmsg(channel, ircutils.bold("Error: Subreddit already exists.")+" Full Error: "+add_response['error']))
                else:
                    irc.sendMsg(ircmsgs.privmsg(channel, ircutils.bold(add_response['error'])))
            else:
                irc.sendMsg(ircmsgs.privmsg(channel, ircutils.bold(add_response['success'])))
        elif(arg_request[0] == "imgur"):
            image_list = self.GetImagur(arg_request[1])
            count = int(arg_request[2])
            if count > 4:
                count = 4
            final_list = random.sample(image_list.keys(), count)
            for id in final_list:
                message = ircutils.bold("NSFW Random ") + image_list[id]['title'] + " - " + image_list[id]['link']
                irc.sendMsg(ircmsgs.privmsg(channel, message))
        elif(arg_request[0] == "pornhub"):
            video_list = self.GetPornHub(arg_request[1])
            num = random.randint(0, len(video_list))
            final_list = video_list[num]
            categories = ""
            for category in final_list['categories']:
                categories += category['category'] + ", "
            message = ircutils.bold("Title: ") + final_list['title'] + ircutils.bold(" Categories: ") + categories + ircutils.bold(" Duration: ") + final_list['duration'] + ircutils.bold(" URL: ") + final_list['url']
            irc.sendMsg(ircmsgs.privmsg(channel, message))
        elif(arg_request[0] == "youporn"):
            video_list = self.GetYouPorn(arg_request[1])
            num = random.randint(0, len(video_list))
            final_list = video_list[num]
            tags = ""
            for tag in final_list['tags']:
                tags += tag['tag_name'] + ", "
            message = ircutils.bold("Title: ") + final_list['title'] + ircutils.bold(" Categories: ") + tags + ircutils.bold(" Duration: ") + final_list['duration'] + ircutils.bold(" URL: ") + final_list['url']
            irc.sendMsg(ircmsgs.privmsg(channel, message))
        elif(arg_request[0] == "redtube"):
            video_list = self.GetRedTube(arg_request[1])
            num = random.randint(0, len(video_list))
            final_list = video_list[num]['video']
            tags = ""
            for tag in final_list['tags']:
                tags += tag['tag_name'] + ", "
            message = ircutils.bold("Title: ") + final_list['title'] + ircutils.bold(" Tags: ") + tags + ircutils.bold(" Duration: ") + final_list['duration'] + ircutils.bold(" URL: ") + final_list['url']
            irc.sendMsg(ircmsgs.privmsg(channel, message))
        else:
            try:
                count = int(arg_request[1])
                subreddit = arg_request[0]
                nsfw_list = self.GetImages(subreddit, count)
                if 'error' in nsfw_list:
                    irc.sendMsg(ircmsgs.privmsg(channel, nsfw_list[1]))
                else:
                    for message in nsfw_list:
                        header = ircutils.bold("NSFW Random ") + message
                        irc.sendMsg(ircmsgs.privmsg(channel, header))
            except ValueError:
                irc.sendMsg(ircmsgs.privmsg(channel, "You fuck, you need to tell me how many images you want"))

    nsfw = wrap(nsfw, ['text'])
Class = NSFW


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
