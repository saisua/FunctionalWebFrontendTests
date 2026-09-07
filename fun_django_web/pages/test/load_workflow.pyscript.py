from dataclasses import dataclass

from workflows import load, depends
from notifications import show_notification


@dataclass
class LoadWorkflow:
	counter_value: "Element"  # noqa: F821
	dcounter_value: "Element"  # noqa: F821
	data: dict = None

	@load("state.pkl", fail="_no_data_to_load")
	async def _verify_data(self, data):
		print("verify_data", data)
		if (
			data is None or  # noqa: W504
			not isinstance(data, dict) or  # noqa: W504
			"counter" not in data or  # noqa: W504
			"dcounter" not in data or  # noqa: W504
			not isinstance(data["counter"], int) or  # noqa: W504
			not isinstance(data["dcounter"], int)
		):
			raise ValueError("Invalid data")

		self.data = data

	async def _no_data_to_load(self, data, algo):
		print("no_data_to_load", data, algo)
		show_notification("Failed to load data")

	@depends("_verify_data")
	async def load(self):
		print("load", self.data)
		self.counter_value.innerText = str(self.data["counter"])
		self.dcounter_value.innerText = str(self.data["dcounter"])
