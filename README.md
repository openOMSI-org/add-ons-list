# openOMSI add-ons list

The list of projects other people make for [openOMSI](https://github.com/openOMSI-org/openOMSI):
tools, companions, content collections. The launcher's **Content → Add-ons** page shows what is
here, each entry a card with a link to the project's own website.

The page is a directory of links. The launcher downloads, installs and runs nothing of an
add-on, and an add-on is not part of openOMSI: the maintainers do not vouch for it.

Projects come in through pull requests: see [CONTRIBUTING.md](CONTRIBUTING.md).

## How it works

* `addons/<id>/` holds an entry: `addon.json` (name, author, description, homepage, tags) and,
  if it has one, its `icon.svg` or `icon.png`.
* `addons.json` lists every entry, with the size and the SHA-256 of its icon. It is made by
  `python3 tools/build_list.py`, and the checks fail when it is out of date.
* The launcher reads `addons.json` from this repository's `main` branch each time the Add-ons
  page opens, so a merged entry shows up for everyone, and a removed one disappears, without a
  new openOMSI release. It downloads an icon from the same branch and shows it only when its
  size and SHA-256 match. Without an internet connection the page says the list could not be
  loaded.

## Licence

The tools and the files of this repository are AGPL-3.0-only ([LICENSE](LICENSE)); an icon is
its author's, shared for this list (see CONTRIBUTING.md).
