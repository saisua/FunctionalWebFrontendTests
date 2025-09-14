from datetime import datetime

from pyscript import document, ffi


body = document.body
sidebar_toggle_btn = document.getElementById('collapseBtn')
year = document.getElementById('year')


@ffi.create_proxy
def toggle_sidebar(_):
	collapsed = body.classList.toggle('is-collapsed')
	sidebar_toggle_btn.innerText = '>>' if collapsed else '<<'

	sidebar_toggle_btn.setAttribute('aria-pressed', str(collapsed))


@ffi.create_proxy
def keydown_handler(event):
	match event.key:
		case 'Escape':
			body.classList.remove('is-open')
			sidebar_toggle_btn.setAttribute(
				'aria-expanded',
				'false',
			)


if sidebar_toggle_btn:
	sidebar_toggle_btn.addEventListener('click', toggle_sidebar)

if year:
	year.textContent = datetime.now().year
