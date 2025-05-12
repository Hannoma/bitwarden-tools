from data.bitwarden import BitwardenEntry
from utils.cache import cache
from utils.url import normalise_domain
from utils.logger import logger, CONSOLE
from rich.prompt import Prompt, Confirm
from rich.table import Table


def _extract_domains(item: BitwardenEntry) -> list[str]:
    """Extract domains from a Bitwarden item."""
    return [normalise_domain(uri_entry.uri) for uri_entry in item.login.uris]


def _show_group_table(group: list[BitwardenEntry]) -> None:
    tbl = Table(title="Shared credentials", header_style="bold magenta")
    tbl.add_column("Idx", justify="right")
    tbl.add_column("ID", no_wrap=True)
    tbl.add_column("Name")
    tbl.add_column("Domains")
    for idx, item in enumerate(group):
        tbl.add_row(str(idx), item.id, item.name, ", ".join(sorted(_extract_domains(item))) or "<no uri>")
    CONSOLE.print(tbl)


def handle_common_credentials(items: list[BitwardenEntry]):
    credential_groups: dict[tuple[str, str], list[BitwardenEntry]] = {}
    # in the first pass, group items by username/password
    for item in items:
        if item.type != 1:
            continue

        key = (item.login.username, item.login.password)
        if key not in credential_groups:
            credential_groups[key] = []
        credential_groups[key].append(item)

    # in the second pass, show groups with more than one item
    for (username, password), group in credential_groups.items():
        if len(group) <= 1:
            continue

        logger.info("[bold cyan]Credentials:[/bold cyan] '%s' / '%s' used in %d entries", username, password, len(group))

        # check the merge cache to replay previous merges
        replayed = [False] * len(group)
        for idx, item in enumerate(group):
            if cache.replay(item, items):
                replayed[idx] = True
        if sum(replayed) >= len(group) - 1:
            logger.info("All items in this group have been merged before")
            continue

        _show_group_table(group)
        if not Confirm.ask("Merge this group?", default=False):
            continue
        tgt_idx = int(Prompt.ask("Choose target idx", choices=[str(i) for i in range(len(group))]))
        target = group[tgt_idx]
        for idx, item in enumerate(group):
            if item is target:
                continue
            if Confirm.ask(f"Merge idx {idx} into target?", default=True):
                cache.add(item, target)
                target.merge(item)
                items.remove(item)
        logger.info("Group complete – target now has %d URIs", len(target.login.uris))
    return items