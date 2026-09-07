from enum import StrEnum

import taskflow
import taskflow.engines
from taskflow.patterns import graph_flow as gf
from taskflow import task
from taskflow import exceptions as exc

from .router import router


class Outcome(StrEnum):
    SUCCESS = "success"
    FAIL = "fail"
    CANCEL = "cancel"


class TaskA(task.Task):
    def execute(self):
        return ("Task A completed",)

    def revert(self, result, flow_failures):
        print(f"Reverting TaskA: {result}")


class TaskB(task.Task):
    def execute(self):
        return ("Task B completed",)

    def revert(self, result, flow_failures):
        print(f"Reverting TaskB: {result}")


class TaskC(task.Task):
    def __init__(self, outcome, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outcome = outcome

    def execute(self, a_result, b_result):
        print(f"Received from A: {a_result}")
        print(f"Received from B: {b_result}")

        if self.outcome == Outcome.SUCCESS:
            return ("Task C completed successfully",)
        elif self.outcome == Outcome.FAIL:
            raise exc.NotFound("Task C failed intentionally")
        else:
            raise exc.InvalidState("Task C canceled intentionally")

    def revert(self, result, flow_failures):
        print(f"Reverting TaskC: {result}")


@router.get("/test5/{outcome}")
async def test5_endpoint(outcome: Outcome):
    print(f"Outcome: {outcome}")

    flow = gf.Flow("test5_flow")

    # Create tasks
    a = TaskA(name="task_a", provides=["a_result"])
    b = TaskB(name="task_b", provides=["b_result"])
    c = TaskC(outcome=outcome, name="task_c")

    # Add tasks to flow
    flow.add(a, b, c)

    # Set up dependencies
    flow.link(a, c)
    flow.link(b, c)

    try:
        engine = taskflow.engines.load(flow, engine="parallel")
        engine.run()

        return {
            "status": "Flow completed",
            "details": engine.storage.fetch_all(),
        }
    except exc.NotFound as e:
        return {
            "status": "Flow failed",
            "error": str(e),
        }
    except exc.InvalidState as e:
        return {
            "status": "Flow canceled",
            "error": str(e),
        }
    except Exception as e:
        return {
            "status": "Flow error",
            "error": str(e),
        }
