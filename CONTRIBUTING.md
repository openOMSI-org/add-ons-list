# Adding or changing an add-on

1. Fork this repository and make a folder `addons/<id>/`. The id is 2 to 40 characters of
   `a-z`, `0-9` and `-`.
2. Add `addons/<id>/addon.json`:

   ```json
   {
     "id": "my-addon",
     "name": "My add-on",
     "author": "Your name",
     "description": "What it does, in one or two plain sentences.",
     "translations": { "de": "Was es tut, in ein oder zwei Sätzen." },
     "homepage": "https://example.org/my-addon",
     "icon": "icon.svg",
     "tags": ["tools"]
   }
   ```

3. Optionally put your icon beside it as `icon.svg` or `icon.png`.
4. Run `python3 tools/build_list.py` and commit `addons.json` with the entry.
5. Open a pull request that changes only your entry. The checks must pass.

## Fields

| Field | Required | Rules |
|---|---|---|
| `id` | yes | The folder's name: lowercase letters, digits and `-`, 2 to 40. |
| `name` | yes | At most 40 characters. |
| `author` | yes | A person, group or company, at most 40 characters. |
| `description` | yes | English, at most 200 characters. What it does, not why it is the best. |
| `translations` | no | The description in other languages, keyed by the game's language codes (`de`, `pt-pt`, `zh-tw`, ...), each at most 200 characters. |
| `homepage` | yes | See below. |
| `icon` | no | `icon.svg` or `icon.png` beside `addon.json`, square, at most 10 KB. An SVG holds no scripts, event handlers or links to other files. Without one the card shows a globe. |
| `tags` | no | Up to 5; lowercase letters, digits and `-`; at most 20 characters each. |

The `homepage` must be:

- an `https://` address of the project's own page on a named website, at most 200 characters;
- without a user name or password, a port, an IP address or `localhost`;
- without spaces, quotes, backslashes or `< > ^ { } |`.

An entry that breaks a rule is left out of the page.

## Review

Before merging, the maintainers check that:

- the homepage is a real project page for openOMSI: it says what the add-on does, who makes it
  and how to get it, and it works;
- there is no advertising, no tracking pixels or link shorteners, and no paid-only teaser
  without a word of what it costs;
- nothing harms players or breaks the openOMSI project's contributing rules or trademark policy
  (`CONTRIBUTING.md` and `TRADEMARKS.md` in its repository). An add-on does not present itself
  as openOMSI;
- the icon is your own work, or one you may share for this list.

An entry is removed when its homepage is gone or no longer matches what the entry says. The
launcher stops showing it as soon as the removal is merged.
