#! /usr/bin/env/ python3
#
#   A simple bot to poll the AlphaVenture API
#   for the price of an equity and post
#   it to Discord.
#
#   @author xlanor
#   License: MIT
#

from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
import pandas as pd
import discord
import asyncio
import arrow
import json
import os

# shows current dir.
print(os.getcwd())
# prepares an instance of the discord client.
client = discord.Client()

# Begin loading values from config.Json
with open("./config.json") as f:
    configDict = json.loads(f.read())

# API key for alphaVenture
AV_API_KEY = configDict.get("AV_API_KEY")
TICKER_TO_MONITOR = configDict.get("TICKER_TO_MONITOR")
TICKER_INTERVAL = configDict.get("TICKER_INTERVAL")
TICKER_OUTPUTSIZE = configDict.get("TICKER_OUTPUTSIZE")
CLIENT_TOKEN = configDict.get("CLIENT_TOKEN")
IPO_CH_ID = configDict.get("IPO_CH_ID")
TIMEOUT = configDict.get("TIMEOUT")
GAME_NAME = configDict.get("GAME_NAME")


def callApi():
    ts = TimeSeries(key=AV_API_KEY, output_format="pandas", retries=10)
    data, meta_data = ts.get_intraday(
        symbol=TICKER_TO_MONITOR, interval=TICKER_INTERVAL, outputsize=TICKER_OUTPUTSIZE
    )
    return data


def plotGraph(data):
    data.set_index(pd.to_datetime(data.index), inplace=True)
    data["4. close"].plot()
    plt.figtext(
        0.74, 0.84, f"Current: {data.loc[max(data.index.values)][3]}", fontsize=9
    )
    plt.figtext(0.74, 0.8, f"Volume: {data.loc[max(data.index.values)][4]}", fontsize=9)
    plt.title(f"{TICKER_TO_MONITOR}:({TICKER_INTERVAL})")
    utc = arrow.utcnow()
    local = utc.to("Asia/Singapore")
    curDt = local.format("YYYY-MM-DD-HH:mm:ss")
    filepath = f"./images/{curDt}.png"
    plt.savefig(filepath)
    return filepath


async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith("!hello"):
        msg = "Hello {0.author.mention}".format(message)
        await client.send_message(message.channel, msg)


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")
    await client.change_presence(game=discord.Game(name=GAME_NAME))


async def send_image():
    await client.wait_until_ready()
    while not client.is_closed:
        try:
            print("Sending image")
            channel = client.get_channel(IPO_CH_ID)
            data = callApi()
            print("Api called")
            fileName = plotGraph(data)
            print(f"{fileName} archived")
            await client.send_file(channel, fileName)
            await asyncio.sleep(TIMEOUT)
        except KeyError:
            pass


if __name__ == "__main__":
    client.loop.create_task(send_image())
    client.run(CLIENT_TOKEN)
    send_image()
