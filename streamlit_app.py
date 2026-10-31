"""
streamlit_app.py - web app for the ancient Aryabhatiya algorithms.
Run locally:  streamlit run streamlit_app.py
"""
import streamlit as st

from ancient_algorithms import (kuttaka, kuttaka_modular_inverse,
                                aryabhata_square_root, aryabhata_cube_root)
from modern_checks import modern_inverse, modern_sqrt, modern_cbrt

MAX_DIGITS = 60

CHOICES = {
    "Kuttaka (modular inverse)": "kuttaka",
    "Square Root (Varga method)": "sqrt",
    "Cube Root (Ghana method)": "cbrt",
}

EXPLAIN = {
    "kuttaka": [
        "Keep dividing the bigger number by the smaller one and write down each "
        "quotient. This list of quotients is the **Valli** (chain).",
        "Stop when the remainder becomes 0. The last non-zero remainder is the GCD.",
        "Now walk **backwards** through the same chain, building two numbers x and y "
        "step by step.",
        "When you reach the top of the chain, x and y satisfy a*x + b*y = 1, "
        "and y (taken mod a) is the **modular inverse** of b.",
        "Think of it as retracing your footsteps up a staircase you built on the "
        "way down.",
    ],
    "sqrt": [
        "Group the digits in **pairs** from the right (55225 becomes 5 | 52 | 25).",
        "Take the left-most group and find the biggest digit whose square fits "
        "inside it. That is the first digit of the answer.",
        "'Bring down' the next pair of digits, like long division, and test digits "
        "0 to 9 to find the biggest one that still fits.",
        "Repeat until every pair has been used. The digits collected **are** the "
        "square root.",
    ],
    "cbrt": [
        "Group the digits in **triples** from the right (1771561 becomes 1 | 771 | 561).",
        "Take the left-most group and find the biggest digit whose cube fits inside it.",
        "Bring down the next triple and test digits 0 to 9 again.",
        "This program compares against the full running total every time, so the "
        "'carry' mistake that older computer versions made cannot happen.",
        "When all triples are used, the digits collected **are** the cube root.",
    ],
}


def parse_int(text, name, min_value):
    """Turn user text into an int, or raise ValueError with a friendly message."""
    cleaned = text.strip().replace(",", "").replace(" ", "")
    try:
        value = int(cleaned)
    except ValueError:
        raise ValueError(f"{name} must be a whole number (digits only).")
    if len(cleaned) > MAX_DIGITS:
        raise ValueError(f"{name} is too long (maximum {MAX_DIGITS} digits).")
    if value < min_value:
        raise ValueError(f"{name} must be at least {min_value}.")
    return value


def show_steps(steps):
    st.markdown("**Step-by-step working (ancient method):**")
    st.code("\n".join(steps), language="text")


def run_kuttaka(b_text, a_text):
    b = parse_int(b_text, "b", 1)
    a = parse_int(a_text, "a", 2)
    try:
        inv, steps = kuttaka_modular_inverse(b, a)
    except ValueError as err:
        _, _, _, steps = kuttaka(a, b)
        show_steps(steps)
        st.error(str(err))
        return
    show_steps(steps)
    st.success(f"Final answer: the modular inverse of {b} mod {a} is **{inv}**")
    check = modern_inverse(b, a)
    if inv == check:
        st.info(f"Modern check: Python pow({b}, -1, {a}) = {check}  -> MATCH")
    else:
        st.warning(f"Modern check gave {check} -> MISMATCH")


def run_sqrt(n_text):
    n = parse_int(n_text, "n", 0)
    root, rem, steps = aryabhata_square_root(n)
    show_steps(steps)
    st.success(f"Final answer: square root of {n} = **{root}** (remainder {rem})")
    check = modern_sqrt(n)
    if root == check:
        st.info(f"Modern check: math.isqrt({n}) = {check}  -> MATCH")
    else:
        st.warning(f"Modern check gave {check} -> MISMATCH")


def run_cbrt(n_text):
    n = parse_int(n_text, "n", 0)
    root, rem, steps = aryabhata_cube_root(n)
    show_steps(steps)
    st.success(f"Final answer: cube root of {n} = **{root}** (remainder {rem})")
    check = modern_cbrt(n)
    if root == check:
        st.info(f"Modern check: integer cube root of {n} = {check}  -> MATCH")
    else:
        st.warning(f"Modern check gave {check} -> MISMATCH")


# ---------------- page layout ----------------
st.set_page_config(page_title="Aryabhatiya Algorithms")

st.title("Aryabhatiya Computational Algorithms")
st.caption("Try the real ancient methods from the Aryabhatiya (499 CE), "
           "step by step, with simple explanations.")

st.header("Step 1 - Choose an algorithm")
label = st.radio("Which algorithm do you want to try?", list(CHOICES.keys()))
algo = CHOICES[label]

st.header("Step 2 - Enter your numbers")
if algo == "kuttaka":
    st.write("Finds the number x such that (b x x) leaves remainder 1 when divided by a.")
    col1, col2 = st.columns(2)
    b_text = col1.text_input("b (number to invert)", value="45")
    a_text = col2.text_input("a (modulus)", value="157")
elif algo == "sqrt":
    n_text = st.text_input("Number n", value="4782969")
else:
    n_text = st.text_input("Number n", value="12812904")

with st.expander("How does this calculation work? (in simple points)", expanded=True):
    for point in EXPLAIN[algo]:
        st.markdown(f"- {point}")

st.header("Step 3 - Solve")
if st.button("Solve using the ancient method", type="primary"):
    try:
        if algo == "kuttaka":
            run_kuttaka(b_text, a_text)
        elif algo == "sqrt":
            run_sqrt(n_text)
        else:
            run_cbrt(n_text)
    except ValueError as err:
        st.error(str(err))

st.divider()
st.header("Older research vs. this new model - in simple points")
with st.expander("How the earlier (older) work was done"):
    st.markdown(
        "- Earlier researchers mostly wrote about these algorithms **on paper**, "
        "with a few hand-worked examples.\n"
        "- Separate papers covered separate algorithms; nobody put them together.\n"
        "- Very few turned the methods into runnable code anyone could try.\n"
        "- Results were rarely checked against modern functions.\n"
        "- One study found an earlier computer version of the cube-root method could "
        "give a **wrong answer** when a 'carry' was mishandled.")
with st.expander("How this new model works differently"):
    st.markdown(
        "- All three algorithms live in **one program**.\n"
        "- Every step of the calculation is shown - nothing is hidden in a black box.\n"
        "- It never uses a modern shortcut to *produce* the answer; it always follows "
        "the ancient steps.\n"
        "- After solving, it **double-checks** the answer with a modern function.\n"
        "- Anyone can use it from a web page - no coding needed.")
with st.expander("Why this matters"):
    st.markdown(
        "- A 1,500-year-old method still gives correct answers, even for very large "
        "numbers.\n"
        "- People can *use and see* the ancient method working, not just read about it.\n"
        "- It closes the gap between 'old paper description' and 'modern working software'.")

st.caption("Third Year IKS Project - Aryabhatiya and Computational Algorithms")
