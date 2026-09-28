No fun, I don't like frontend

The idea is to have a Python web frontend framework with declarative syntax,
state machines and workflow DAGs.

The idea is to build a graph of possible website states and have its transitions
be processing DAGs. This would imply you can render the website use as a graph to explore
and be safer due to the mandatory fallback cases on requests and other external events.

You define the states, which define 

# TODOs

1. Create a native DAG way of processing steps with dependencies
1. Make into a Django plugin
1. Integrate processing workflows with declarative stuff
1. Add more declarative events
1. Maybe realocate declarative events? Not so declarative
1. Parse conditions to get explicit dependencies to integrate reactivity with declarativity
