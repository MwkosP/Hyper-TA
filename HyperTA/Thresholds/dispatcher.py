"""User-facing threshold composition entrypoints."""


def mixThresholds(df, configs, mode="and", search="grid"):
    """
    Routes to the correct Combinatorial Search engine.
    """
    from HyperTA.Search.combinatorialSearch import (
        combinatorialGridSearch,
        combinatorialRandomSearch,
        combinatorialBayesianSearch,
    )

    if search == "grid":
        print("🚀 Dispatching to Combinatorial GRID Search...")
        return combinatorialGridSearch(df, configs, mode=mode)

    elif search == "random":
        print("🚀 Dispatching to Combinatorial RANDOM Search...")
        return combinatorialRandomSearch(df, configs, n_iter=300, mode=mode)

    elif search == "bayesian":
        print("🚀 Dispatching to Combinatorial BAYESIAN Search...")
        return combinatorialBayesianSearch(df, configs, n_iter=300, mode=mode)

    else:
        raise ValueError(f"Unknown search type: {search}")
