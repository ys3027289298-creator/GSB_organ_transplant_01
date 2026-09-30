import json


def new_game():
    return {
        "items": {},
        "load": 0,
        "capacity": 2,
        "stock": 100,
        "metric": 100,
        "day": 1,
        "id": 0,
        "fault": False,
        "resource": 10,
        "rate": 2,
        "clock": 0,
        "paused": False,
        "settled": False,
        "received": {},
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    return json.loads(text)


def add(state, item_id, amount):
    if state["settled"]:
        return False
    if item_id in state["items"]:
        return False
    if amount <= 0 or amount > state["stock"]:
        return False
    state["items"][item_id] = amount
    state["stock"] -= amount
    return True


def receive(state, item_id):
    if state["settled"]:
        return False
    if item_id in state["received"]:
        return False
    if state["load"] >= state["capacity"]:
        return False
    state["received"][item_id] = True
    state["load"] += 1
    return True


def fee(state, item_id, end_day):
    days = end_day - state["day"]
    if days <= 0:
        return 0
    return days * state["rate"]


def cancel(state, item_id):
    if state["settled"]:
        return False
    amount = state["items"].pop(item_id, None)
    if amount is None:
        return False
    state["stock"] += amount
    if state["received"].pop(item_id, None) is not None:
        state["load"] -= 1
    return True


def produce(state, amount):
    if state["settled"]:
        return False
    if state["fault"]:
        return False
    if amount <= 0 or amount > state["resource"]:
        return False
    state["resource"] -= amount
    return True


def event(state):
    if state["settled"]:
        return state["metric"]
    state["metric"] -= 10
    return state["metric"]


def guard(state, item_id):
    if state["settled"]:
        return False
    amount = state["items"].get(item_id)
    return amount is not None and state["resource"] >= amount


def tick(state):
    if state["paused"] or state["settled"]:
        return state["clock"]
    state["clock"] += 1
    return state["clock"]


def settle(state):
    state["settled"] = True
    return True


def main():
    print("命令: add/receive/fee/cancel/produce/event/guard/tick/settle/quit")
    state = new_game()

    def cmd_add(args):
        return add(state, int(args[0]), int(args[1]))

    def cmd_one(func):
        return lambda args: func(state, int(args[0]))

    def cmd_produce(args):
        return produce(state, int(args[0]))

    def cmd_fee(args):
        return fee(state, int(args[0]), int(args[1]))

    def cmd_event(_args):
        return event(state)

    def cmd_tick(_args):
        return tick(state)

    def cmd_settle(_args):
        return settle(state)

    commands = {
        "add": cmd_add,
        "receive": cmd_one(receive),
        "fee": cmd_fee,
        "cancel": cmd_one(cancel),
        "produce": cmd_produce,
        "event": cmd_event,
        "guard": cmd_one(guard),
        "tick": cmd_tick,
        "settle": cmd_settle,
    }

    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        parts = raw.split()
        handler = commands.get(parts[0])
        if handler is None:
            print("unknown command")
            continue
        try:
            print(handler(parts[1:]))
        except (IndexError, ValueError):
            print("invalid arguments")


if __name__ == "__main__":
    main()
