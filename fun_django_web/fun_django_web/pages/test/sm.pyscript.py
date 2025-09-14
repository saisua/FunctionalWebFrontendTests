import asyncio

from pyscript import document, window

from state_machine import StateMachine, State, transition

from workflows import store

from load_workflow import LoadWorkflow

loop = asyncio.get_running_loop()

status_value = document.getElementById("statusValue")
counter_value = document.getElementById("counterValue")
dcounter_value = document.getElementById("dcounterValue")

load_workflow = LoadWorkflow(
    counter_value,
    dcounter_value,
)

initial_state = "disabled"
if 'state=' in window.location.search:
    initial_state = window.location.search.split('state=')[1].split('&')[0]


@store("state.pkl")
async def _store_data(data):
    print("store_data", data)
    return data


class MyMachine(StateMachine):
    _current = 0
    _dcurrent = 0

    enabled = State('enabled', initial=initial_state == "enabled")
    disabled = State('disabled', initial=initial_state == "disabled")
    incremented = State('incremented')
    decremented = State('decremented')
    dincremented = State('dincremented')
    saved = State('saved')
    loaded = State('loaded')
    reseted = State('reseted')

    enable = (
        disabled.to(enabled)
        | dincremented.to(enabled)  # noqa: W503
    )
    disable = (
        enabled.to(disabled)
        | incremented.to(disabled)  # noqa: W503
        | decremented.to(disabled)  # noqa: W503
        | saved.to(disabled)  # noqa: W503
        | loaded.to(disabled)  # noqa: W503
        | reseted.to(disabled)  # noqa: W503
    )
    increment = (
        enabled.to(incremented)
        | incremented.to.itself()  # noqa: W503
        | disabled.to(dincremented)  # noqa: W503
        | dincremented.to.itself()  # noqa: W503
        | decremented.to(incremented)  # noqa: W503
    )
    decrement = (
        enabled.to(decremented)
        | decremented.to.itself()  # noqa: W503
        | incremented.to(decremented)  # noqa: W503
    )
    save = (
        enabled.to(saved)
        | incremented.to(saved)  # noqa: W503
        | decremented.to(saved)  # noqa: W503
    )
    load = (
        enabled.to(loaded)
        | incremented.to(loaded)  # noqa: W503
        | decremented.to(loaded)  # noqa: W503
    )
    leave = (
        disabled.to.outside("/test2")
        | dincremented.to.outside("/test2", "dincremented")  # noqa: W503
    )
    reset = (
        enabled.to(reseted)
        | disabled.to(reseted)  # noqa: W503
        | incremented.to(reseted)  # noqa: W503
        | decremented.to(reseted)  # noqa: W503
        | dincremented.to(reseted)  # noqa: W503
    )

    def on_enter_enabled(self):
        status_value.innerText = "Enabled"

        self.current += self.dcurrent
        self.dcurrent = 0

    def on_enter_disabled(self):
        status_value.innerText = "Disabled"

    def on_enter_incremented(self):
        self.current += 1

        if self.current % 3 == 0:
            self.disable()

    def on_enter_decremented(self):
        self.current -= 1

    def on_enter_dincremented(self):
        self.dcurrent += 1

    def on_enter_saved(self):
        loop.create_task(_store_data({
            "counter": self.current,
            "dcounter": self.dcurrent,
        }))

        self.disable()

    async def _update_values(self):
        await asyncio.sleep(0.1)

        self.current = int(counter_value.innerText)
        self.dcurrent = int(dcounter_value.innerText)

    def on_enter_loaded(self):
        loop.create_task(load_workflow.load())
        loop.create_task(self._update_values())

        self.disable()

    def on_enter_reseted(self):
        self.current = 0
        self.dcurrent = 0

        self.disable()

    @property
    def current(self):
        return self._current

    @property
    def dcurrent(self):
        return self._dcurrent

    @current.setter
    def current(self, value):
        self._current = value
        counter_value.innerText = str(self._current)

    @dcurrent.setter
    def dcurrent(self, value):
        self._dcurrent = value
        dcounter_value.innerText = str(self._dcurrent)


sm = None


def init():
    global sm
    sm = MyMachine()


init()


@transition
def increment(e):
    global sm
    sm.increment()


@transition
def decrement(e):
    global sm
    sm.decrement()


@transition
def enable(e):
    global sm
    sm.enable()


@transition
def disable(e):
    global sm
    sm.disable()


@transition
def save(e):
    global sm
    sm.save()


@transition
def reset(e):
    global sm
    sm.reset()


@transition
def load(e):
    global sm
    sm.load()


@transition
def leave(e):
    global sm
    sm.leave()
