from ...utilities import installed_source_modules


def list_packages():
    """List installed source packages"""
    for m in installed_source_modules():
        print("-" * 50)
        print(f"{m.meta['name']} {m.meta['version']}")
        print("-" * 50)

        print(f"Sources")
        for s in m.sources:
            print(f"   {s}")
