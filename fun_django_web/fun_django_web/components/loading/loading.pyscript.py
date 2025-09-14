from pyscript import document, window, ffi


loading_overlay = document.getElementById('loading-overlay')
loading_spinner = document.getElementById('loading-spinner')


@ffi.create_proxy
def disable_loading(_):
	loading_overlay.style.display = 'none'
	loading_spinner.style.display = 'none'


window.addEventListener('py:all-done', disable_loading)
