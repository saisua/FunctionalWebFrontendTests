class var:
	def __getattr__(self, var_name: str):
		return f'--{var_name}'
