"""Check your code in student_code.py. No drone needed.

    python check.py

It runs your functions on known examples and tells you what passes and what still
needs work. Green PASS means the drone will use your version. TODO means you have not
written that one yet.
"""
import student_code as s

ALLOWED_ACTIONS = {"photograph", "celebrate", "dance", "nothing"}


def run_cases(name, cases):
    """cases is a list of (args, expected). Returns True if all pass."""
    fn = getattr(s, name)
    try:
        fn(*cases[0][0])
    except NotImplementedError:
        print(f"{name}\n  [TODO] not written yet")
        return False
    except Exception as exc:
        print(f"{name}\n  [ERROR] your code crashed: {exc}")
        return False
    all_ok = True
    print(name)
    for args, expected in cases:
        try:
            got = fn(*args)
        except Exception as exc:
            print(f"  [ERROR] {name}{args} crashed: {exc}")
            all_ok = False
            continue
        ok = got == expected
        all_ok = all_ok and ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}{args} = {got!r}   (want {expected!r})")
    return all_ok


def check_decide_action():
    """decide_action is yours to design, so we only check it returns a valid word."""
    name = "decide_action"
    try:
        s.decide_action(10)
    except NotImplementedError:
        print(f"{name}\n  [TODO] not written yet")
        return False
    except Exception as exc:
        print(f"{name}\n  [ERROR] your code crashed: {exc}")
        return False
    print(name)
    ok = True
    for marker in (10, 20, 30, 40, 42):
        got = s.decide_action(marker)
        valid = got in ALLOWED_ACTIONS
        ok = ok and valid
        note = "" if valid else f"   (must be one of {sorted(ALLOWED_ACTIONS)})"
        print(f"  [{'PASS' if valid else 'FAIL'}] decide_action({marker}) = {got!r}{note}")
    return ok


def main():
    print("Checking your code in student_code.py\n")
    results = []
    results.append(run_cases("clamp", [
        ((12, 0, 10), 10), ((-3, 0, 10), 0), ((5, 0, 10), 5), ((10, 0, 10), 10),
    ]))
    results.append(run_cases("centering_error", [
        ((400, 360), 40), ((300, 360), -60), ((360, 360), 0),
    ]))
    results.append(run_cases("steer_speed", [
        ((100, 0.1, 20), 10.0), ((500, 0.1, 20), 20), ((-500, 0.1, 20), -20), ((0, 0.1, 20), 0.0),
    ]))
    results.append(run_cases("is_aligned", [
        ((5, -3, 2, 35, 18), True), ((50, 0, 0, 35, 18), False), ((0, 0, 40, 35, 18), False),
        ((-50, 0, 0, 35, 18), False), ((0, -50, 0, 35, 18), False), ((0, 0, -40, 35, 18), False),
    ]))
    results.append(check_decide_action())

    done = sum(1 for r in results if r)
    print(f"\nScore: {done} of {len(results)} functions done.", end=" ")
    print("All done, great work." if done == len(results) else "Keep going.")


if __name__ == "__main__":
    main()
