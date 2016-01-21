#-*- codding: utf-8 -*-

import urllib.request
import sys
import os
import json
import shelve
import subprocess
from pyquery import PyQuery as pq

class PtVideoBin:
    """binary process"""
    def __init__(self):
        super(PtVideoBin, self).__init__()

    def get_configurations(self):
        main_folder = str(os.environ['HOME']) + "/pt_video_downloader"
        fl = shelve.open("%s/app_data/configs.dat" % main_folder)
        try:
            ret = fl['configs']
        except:
            os.makedirs("/home/%s/Videos/PtVideoDownloader" % os.getlogin(), exist_ok=True)
            fl['configs'] = {
                'download':{
                    'down_path': {
                        'title': 'Download Target Path',
                        'value': str.format('/home/{0}/Videos/PtVideoDownloader/', os.getlogin()),
                        'type': 'file'
                        },
                    'down_after_remove': {
                        'title': 'Remove Downloaded Videos',
                        'value': True,
                        'type': 'bool'
                        }
                },
                'search':{
                    'search_max_result_count': {
                        'title': 'Maximum Search Results',
                        'value': 10,
                        'type': 'int'
                    }
                }
            }
            ret = fl['configs']
        finally:
            fl.close()
        return ret

    def set_configurations(self, configs):
        main_folder = str(os.environ['HOME']) + "/pt_video_downloader"
        fl = shelve.open("%s/app_data/configs.dat" % main_folder)
        fl['configs'] = configs
        fl.close()

    def search_youtube_videos(self, q):
        qr = q.replace(' ', '+')
        url = "https://www.youtube.com/results?filters=video&lclk=video&search_query=" + qr
        pcontent = pq(url=url)
        ret = []
        for mdiv in pcontent('ol.section-list li'):
            vid = pq(mdiv)("div.yt-lockup.yt-lockup-tile.yt-lockup-video.clearfix.yt-uix-tile").attr['data-context-item-id']
            if vid is not None:
                dg = {}
                dg['id'] = vid
                dg['thumbnail'] = "https://i.ytimg.com/vi/%s/default.jpg" % vid
            if pq(mdiv)('h3.yt-lockup-title a').attr['title'] is not None:
                dg['title'] = pq(mdiv)('h3.yt-lockup-title a').attr['title'].strip()
                dg['url'] = "https://youtube.com" + pq(mdiv)('h3.yt-lockup-title a').attr['href'].strip()
                ret.append(dg.copy())
        return ret

    def get_youtube_video_info(self, url):
        process = subprocess.Popen(["youtube-dl", "--no-warnings", "-J", url], stdout = subprocess.PIPE, universal_newlines=True)
        jret = ""
        while process.poll() is None:
            try:
                result = process.stdout.readline()
                jret += result.strip()
                sys.stdout.flush()
            except Exception as ex:
                pass
        data = json.loads(jret)
        data['thumbnail'] = data['thumbnail'].replace('maxresdefault.jpg', 'default.jpg').replace('hqdefault.jpg', 'default.jpg')
        data['url'] = data['webpage_url']
        return data

    def get_youtube_video_formats(self, url):
        process = subprocess.Popen(["youtube-dl" ,"-F", url], stdout = subprocess.PIPE, universal_newlines=True)
        jret = ""
        bl = False
        data = []
        while process.poll() is None:
            try:
                result = process.stdout.readline()
                if bl:
                    rtt = []
                    for rt in result.strip().split(' '):
                        if rt.strip() != '':
                            rtt.append(rt)
                    if 'DASH' not in rtt:
                        data.append(("(%s), %s, %s" % (rtt[1], rtt[2], rtt[3]), rtt[0]))
                if "format code" in result:
                    bl = True
                sys.stdout.flush()
            except Exception as ex:
                pass
        return data
