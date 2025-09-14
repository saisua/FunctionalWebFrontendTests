import os

import aiofiles

from django.http import HttpResponse
from django.conf import settings


async def get_pyscript_file(request):
	relative_path = request.GET.get('path', '')

	if not relative_path.endswith('.pyscript.py'):
		return HttpResponse("File not found", status=404)

	base_dir = settings.BASE_DIR
	full_path = os.path.normpath(os.path.join(base_dir, relative_path))

	if not full_path.startswith(str(base_dir)) or not os.path.isfile(full_path):
		return HttpResponse("File not found", status=404)

	try:
		async with aiofiles.open(full_path, 'r') as f:
			content = await f.read()
		return HttpResponse(content, content_type='text/plain')
	except Exception as e:
		return HttpResponse(f"Error reading file: {str(e)}", status=500)
