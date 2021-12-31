from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from ffmpeg_progress_yield import FfmpegProgress
from concurrent.futures import ThreadPoolExecutor
from statusLogger import StatusLogger
from bs4 import BeautifulSoup
import time
import json
import os
import argparse
from pathlib import Path


import requests

class panoptoDownloader:
    
    def __init__(self, base_url: str, directory: str):
        self.BASE_URL = base_url
        self.s = requests.Session()
        self.directory = directory

        # Make directory
        if not os.path.isdir(directory):
            os.makedirs(directory)


    # Get's all visible videos
    def get_visible_videos(self, driver: WebDriver) -> list[str]:
        soup = BeautifulSoup(str(driver.page_source), 'html.parser')

        # get all id's
        table = soup.find('table', attrs={'class':'details-table'})
        table_body = table.find('tbody')

        rows = table_body.find_all('tr')
        videos = []
        for row in rows:
            if row["id"] != "panePlaceholder":
                videos.append(self.get_video_data(row["id"]))

        return videos

    # Get's open videos from tabs
    def get_open_tabs(self, driver: WebDriver) -> list[str]:
        videos = []
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            curr_url = driver.current_url
            if "id=" in curr_url:
                id = curr_url.split("id=")[1]
                videos.append(self.get_video_data(id))

        return videos
   
    
    def get_video_data(self, id: str) -> dict[str, str]:
        data = {
        'deliveryId': id,
        'isEmbed': 'true',
        'responseType': 'json'
        }

        response = self.s.post(self.BASE_URL+'/Panopto/Pages/Viewer/DeliveryInfo.aspx',data=data)

        res = json.loads(response.text)

        name = res["Delivery"]["SessionName"]
        link = res["Delivery"]["PodcastStreams"][0]["StreamUrl"]
        return {"name":name, "link":link}
    

    def download(self, out: str, link:str, task_id: int, logger: StatusLogger):

        command = ['ffmpeg', '-f', 'hls', '-i', link, '-c', 'copy', out]

        ff = FfmpegProgress(command)
        
        for progress in ff.run_command_with_progress():
            logger.update_state(task_id, progress)

        logger.finished_task(task_id)

    def run(self, mode:str, chrome_path: str, num_threads: int):
        
        # Open Panopto
        options = webdriver.ChromeOptions() 
        if chrome_path is not None:
            c_path = Path(chrome_path)
            profile_dir = str(c_path.parent)
            profile_name = str(c_path.name)
                        
            options.add_argument("user-data-dir={}".format(profile_dir)) #Path to your chrome profile
            options.add_argument("profile-directory={}".format(profile_name))

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(self.BASE_URL)

        input("Press any key once loaded!")
        
        # Set Cookies
        cookies = driver.get_cookies()
        for cookie in cookies:
            self.s.cookies.set(cookie['name'], cookie['value'])

        # Get videos
        if mode == "visible_videos":
            videos = self.get_visible_videos(driver)
        elif mode == "open_tabs":
            videos = self.get_open_tabs(driver)
        else:
            videos = []

        driver.quit()

        # Download
        logger = StatusLogger()
        executor = ThreadPoolExecutor(max_workers=num_threads)
        task_id = 0

        for video in videos:
            logger.add_task(video["name"], task_id)
            
            out = "{}/{}.mp4".format(self.directory, video["name"])

            executor.submit(self.download, out, video["link"], task_id, logger)
            task_id += 1

        
        executor.shutdown(wait=False)

        while not logger.finished():
            logger.reprint()
            time.sleep(0.5)

        logger.reprint()
        print("Completed!")

        executor.shutdown(wait=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='-Panopto Downloader-')
    parser.add_argument('-url', metavar='url', type=str, help='[REQ] panopto url', required=True)
    parser.add_argument('-mode', metavar='mode', type=str, help='choode mode',
                        choices=["visible_videos", "open_tabs"], default="visible_videos")

    parser.add_argument('-outdir', dest='outdir', action='store',
                    default="out", help='output directory (default: out/)')

    parser.add_argument('--chrome-profile-path', dest='chrome_path', action='store', help='path of chrome user if wanting to use normal profile')
    parser.add_argument('--num-threads', type=int, dest='num_threads', action='store', default=None, help='number of threads, default to ThreadPoolExecutor max_workers')

    args = parser.parse_args()

    dl = panoptoDownloader(args.url, args.outdir)
    dl.run(args.mode, args.chrome_path, args.num_threads)