def pretty(model: dict):
    """
    Pretty prints the ALC interpretation model (ℐ = (Δᴵ, ⋅ᴵ)).
    """
    print("\nModel Interpretation (ℐ):")
    domain_str = f"{{{', '.join(sorted(model['domain']))}}}"
    print(f"  Δᴵ (Domain): {domain_str}")

    print("  Concepts Interpretation (⋅ᴵ):")
    for concept, individuals in sorted(model['concepts'].items()):
        print(f"    {concept}ᴵ = {{{', '.join(sorted(individuals))}}}")

    print("  Roles Interpretation (⋅ᴵ):")
    for role, pairs in sorted(model['roles'].items()):
        formatted_pairs = ", ".join([f"({s}, {t})" for s, t in sorted(pairs)])
        print(f"    {role}ᴵ = {{{formatted_pairs}}}")

    if 'tbox' in model and model['tbox']:
        print("  TBox Satisfaction (𝒯ᴵ):")
        for rule in sorted(model['tbox'], key=lambda r: str(r)):
            # In ALC, for an interpretation to be a model of T, 
            # every individual must satisfy every rule in T.
            print(f"    ∀x ∈ Δᴵ x satisfies {rule}")
