import streamlit as st


def select_item(
    items: list,
    key: str,
    label: str,
) -> object:
    """
    Generic selector that keeps Streamlit session state and query params in sync.

    Args:
        items: list of selectable objects (must have .name attribute)
        key: short name used for query param and session key ("subject", "level", etc.)
        label: label shown above the selectbox

    Returns:
        The selected object.
    """
    query_value = st.query_params.get(key, None)

    session_key = f"selected_{key}"
    # --- Sync query param → session state ---
    if query_value and query_value in [i.name for i in items]:
        matched = next(i for i in items if i.name == query_value)
        st.session_state[session_key] = matched
    elif session_key not in st.session_state:
        st.session_state[session_key] = items[0]

    # --- Selectbox bound to session state ---
    selected = st.selectbox(
        f"Select {key}",
        items,
        format_func=lambda i: i.name,
    )

    # --- Sync session state → query param ---
    if query_value != selected.name:
        st.query_params[key] = selected.name
        st.rerun()

    st.session_state[session_key] = selected

    return selected
