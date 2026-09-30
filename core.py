import json


def new_game():
    return {"items": {}, "load": 0, "capacity": 2, "stock": 100, "metric": 100, "day": 1, "id": 0, "fault": False, "resource": 10, "rate": 2, "clock": 0, "paused": False, "settled": False}


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    return json.loads(text)


def _locked(state):
    return bool(state.get("settled"))


def add(state, item_id, amount):
    if _locked(state):
        return False
    if item_id in state["items"]:
        return False
    if amount <= 0 or amount > state["stock"]:
        return False
    state["items"][item_id] = amount
    state["stock"] -= amount
    return True


def receive(state, item_id):
    if _locked(state):
        return False
    if item_id not in state["items"]:
        return False
    if state["load"] >= state["capacity"]:
        return False
    state["load"] += 1
    return True


def fee(state, item_id, end_day):
    days = end_day - state["day"]
    if days < 0:
        days = 0
    return days * state["rate"]


def cancel(state, item_id):
    if _locked(state):
        return False
    amount = state["items"].pop(item_id, None)
    if amount is None:
        return False
    state["stock"] += amount
    return True


def produce(state, amount):
    if _locked(state):
        return False
    if state["fault"]:
        return False
    return True


def event(state):
    if _locked(state):
        return state["metric"]
    state["metric"] -= 10
    return state["metric"]


def guard(state, item_id):
    return state["stock"] > 0 and state["resource"] > 0


def tick(state):
    if state["paused"]:
        return state["clock"]
    state["clock"] += 1
    return state["clock"]


def settle(state):
    state["settled"] = True
    return True


def main():
    print("命令: add/receive/fee/cancel/produce/event/guard/tick/settle/quit")
    state = new_game()
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        parts = raw.split()
        cmd, args = parts[0], parts[1:]
        try:
            if cmd == "add":
                print(add(state, int(args[0]), int(args[1])))
            elif cmd == "receive":
                print(receive(state, int(args[0])))
            elif cmd == "fee":
                print(fee(state, int(args[0]), int(args[1])))
            elif cmd == "cancel":
                print(cancel(state, int(args[0])))
            elif cmd == "produce":
                print(produce(state, int(args[0])))
            elif cmd == "event":
                print(event(state))
            elif cmd == "guard":
                print(guard(state, int(args[0])))
            elif cmd == "tick":
                print(tick(state))
            elif cmd == "settle":
                print(settle(state))
            else:
                print("unknown")
        except (IndexError, ValueError):
            print("bad args")


if __name__ == "__main__":
    main()
