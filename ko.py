# human_quicksort_app.py
import json
import random
from pathlib import Path
import streamlit as st

FILTERED_FILE = Path("names.json")
SORTED_FILE   = Path("sorted.json")

# -------------------- I/O --------------------
def load_filtered():
    if not FILTERED_FILE.exists():
        st.error(f"Missing {FILTERED_FILE}. Run your first app to create it.")
        st.stop()
    data = json.loads(FILTERED_FILE.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "names" in data:
        names = data["names"]
    elif isinstance(data, list):
        names = data
    else:
        st.error("filtered.json must be a list or an object with a 'names' field.")
        st.stop()
    # de-dup while keeping order
    seen, out = set(), []
    for n in names:
        if n not in seen:
            seen.add(n); out.append(n)
    return out

def save_sorted(names):
    SORTED_FILE.write_text(json.dumps({"names": names}, ensure_ascii=False, indent=2), encoding="utf-8")

# -------------------- State bootstrap --------------------
def init_state():
    if "stack" not in st.session_state:
        names = load_filtered()
        # Optional shuffle so comparisons feel varied; comment out if not wanted
        random.seed(42)
        random.shuffle(names)
        # "stack" holds subproblems to sort. Each is either:
        # - {"items": [...], "pivot": str, "i": int, "less": [], "greater": []}  (active partition)
        # - {"final": [...]} (already sorted chunk)
        st.session_state.stack = [{"items": names}]  # one big unsorted chunk
    if "output" not in st.session_state:
        st.session_state.output = []
    if "total" not in st.session_state:
        st.session_state.total = len(load_filtered())
    if "last_choice" not in st.session_state:
        st.session_state.last_choice = None  # for tiny feedback toast

def ensure_top_task_initialized():
    """If the top stack task is a raw 'items' list, initialize its pivot/partition state."""
    while st.session_state.stack:
        top = st.session_state.stack[-1]

        # If it's a final chunk, flush it to output and pop.
        if "final" in top:
            st.session_state.output.extend(top["final"])
            st.session_state.stack.pop()
            continue

        # If it's a plain items list, turn it into a partition task or finalize immediately.
        if "items" in top and "pivot" not in top:
            items = top["items"]
            if len(items) <= 1:
                st.session_state.stack[-1] = {"final": items}
                continue
            # Initialize a partition: choose middle element as pivot for balance
            mid = len(items) // 2
            pivot = items[mid]
            st.session_state.stack[-1] = {
                "items": items,
                "pivot": pivot,
                "i": 0,               # index of the candidate being compared
                "less": [],           # items ranked LOWER than pivot (less close)
                "greater": []         # items ranked HIGHER than pivot (more close)
            }
            continue
        break  # top task is ready for comparison or is a partition in progress

def current_comparison():
    """
    Returns (left, right, meta) where user picks who is closer.
    We show pivot on the LEFT, candidate on the RIGHT.
    """
    if not st.session_state.stack:
        return None, None, None

    task = st.session_state.stack[-1]
    if "pivot" not in task:
        return None, None, None

    items = task["items"]
    pivot = task["pivot"]

    # advance 'i' until we land on an item that isn't the pivot itself
    while task["i"] < len(items) and items[task["i"]] == pivot:
        task["i"] += 1

    if task["i"] >= len(items):
        return pivot, None, task  # partition finished; no comparison left

    candidate = items[task["i"]]
    return pivot, candidate, task

def finish_partition(task):
    """When all comparisons vs. pivot are done, split and push subproblems."""
    items = task["items"]
    pivot = task["pivot"]
    less = task["less"]
    greater = task["greater"]

    # Remove the partition task
    st.session_state.stack.pop()

    # Order for descending closeness (most preferred first):
    # greater (better than pivot), pivot, less (worse than pivot)
    if less:
        st.session_state.stack.append({"items": less})
    # pivot as final chunk
    st.session_state.stack.append({"final": [pivot]})
    if greater:
        st.session_state.stack.append({"items": greater})

# -------------------- UI --------------------
st.set_page_config(page_title="Human QuickSort", page_icon="🎯", layout="centered")
st.title("🎯 Human-Driven QuickSort")
init_state()
ensure_top_task_initialized()

# Progress
remaining_in_stack = sum(
    (len(t.get("items", [])) if "items" in t else len(t.get("final", [])))
    for t in st.session_state.stack
)
done = len(st.session_state.output)
total = st.session_state.total
st.caption(f"Progress: **{done}/{total}** placed · Remaining (incl. pending): **{remaining_in_stack}**")

# Current comparison
pivot, candidate, task = current_comparison()

if st.session_state.stack and task and candidate is None:
    # Partition finished; dispatch subproblems
    finish_partition(task)
    st.rerun()

elif not st.session_state.stack:
    st.success("All done! You’ve ranked everyone 🎉")
    st.write("Top → bottom = closest → farthest")
    st.json({"names": st.session_state.output})
    if st.button("Save"):
        save_sorted(st.session_state.output)
        st.success(f"Saved to {SORTED_FILE}")
else:
    # Show comparison UI
    st.subheader("Who is **closer** to you?")
    left, right = st.columns(2)
    with left:
        st.markdown(f"### 🧑‍🤝‍🧑 {pivot}")
        if st.button("👈 Pick Left (closer)"):
            # Left means pivot is closer → candidate goes to LESS (worse than pivot)
            task["less"].append(task["items"][task["i"]])
            task["i"] += 1
            st.session_state.last_choice = f"Picked {pivot}"
            st.rerun()
    with right:
        st.markdown(f"### 🧑‍🤝‍🧑 {candidate}")
        if st.button("Pick Right (closer) 👉"):
            # Right means candidate is closer → goes to GREATER (better than pivot)
            task["greater"].append(task["items"][task["i"]])
            task["i"] += 1
            st.session_state.last_choice = f"Picked {candidate}"
            st.rerun()

    st.divider()
    # Utility buttons
    util1, util2, util3 = st.columns(3)
    with util1:
        if st.button("💾 Save now (partial)"):
            # Save what’s fully ordered so far + unresolved pivot partition best guess
            # For safety, just save the placed part; you can resume later.
            save_sorted(st.session_state.output)
            st.success(f"Partial order saved to {SORTED_FILE}")
    with util2:
        if st.button("🔄 Restart from scratch"):
            for k in ["stack", "output", "total", "last_choice"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()
    with util3:
        st.write("")  # spacer
        st.caption(st.session_state.last_choice or "")

# Footer hint
st.caption("Sorting rule: you’re the comparator. "
           "Choosing **Left** keeps the pivot higher; choosing **Right** promotes the candidate above pivot. "
           "Final list is descending by closeness.")