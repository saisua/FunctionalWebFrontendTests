def media(**kwargs):
	def _media_wrapper(cls):
		features = " and ".join(
			f"{key}: {val}"
			for key, val in kwargs.items()
		)

		cls._wrapper_start = f'@media ({features}){{'
		cls._wrapper_end = '}'

		return cls

	return _media_wrapper
