import asyncio

from helloweb3 import *


class Challenge(PwnChallengeWithAnvil, ChallengeWithAnvilAndPow):
    pass


event_loop = asyncio.new_event_loop()
event_loop.run_until_complete(serve_challenge(Challenge))
