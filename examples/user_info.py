# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
os.chdir(PROJECT_ROOT)

from pysna import TwitterAPI, TwitterAppAuthHandler

load_dotenv("local.env")

auth = TwitterAppAuthHandler(os.getenv("CONSUMER_KEY"), os.getenv("CONSUMER_SECRET"))
api = TwitterAPI(auth)

user = api.user_info(user="Twitter", attributes=["name", "description", "followers_count"])

print(user)
