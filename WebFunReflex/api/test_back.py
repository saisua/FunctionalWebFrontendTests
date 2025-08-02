import pickle as pkl
import os
import asyncio

import aiofiles

from .router import router


@router.get("/test2/data")
async def get_data():
	# await asyncio.sleep(5)
	if not os.path.exists("data/test2.pkl"):
		return []

	async with aiofiles.open("data/test2.pkl", "rb") as f:
		data = await f.read()
	return pkl.loads(data)


@router.post("/test2/data")
async def save_data(data: list):
	print(f"Saving {len(data)} data")
	data = pkl.dumps(data)
	async with aiofiles.open("data/test2.pkl", "wb") as f:
		await f.write(data)
