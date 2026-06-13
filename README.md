# as215932.net

Informational website for [AS215932](https://www.peeringdb.com/asn/215932)
(Hyrule Networks). ASN facts, peering policy, network weathermap, prefix
allocations, and a stub for the upcoming Looking Glass.

Deliberately primitive: plain static HTML, one CSS file, no JavaScript,
no webfonts, no remote assets. Renders under Tor Browser "Safest" mode.
Soft 80-column target for the hacker/builder aesthetic.

## Layout

| file | purpose |
|------|---------|
| `index.html`    | Home — ASN facts + weathermap |
| `network.html`  | Full topology and routing stack |
| `peering.html`  | Peering policy, requirements, NOC contact |
| `prefixes.html` | IPv6 allocation, RPKI/IRR, external records |
| `lg.html`       | Looking Glass stub — real LG coming later |
| `style.css`     | Black background, white text, monospace, ~80ch |

## Deploy

The site is served by `nginx` on the `web` VM
(`2a0c:b641:b50:2::30`) on port `8081`, fronted by Caddy on the `proxy`
VM which terminates TLS for `as215932.net`. All nginx / Caddy / Knot /
Icinga configuration lives in the
[hyrule-infra](https://github.com/AS215932/network-operations)
repository — this repo only contains the site content.

```sh
./deploy.sh            # rsync + reload nginx on the web VM
```

`deploy.sh` is a thin wrapper around `rsync` — it touches only
`/var/www/as215932.net/` and reloads nginx. No other state is changed.

## Editing

Since pages share a nav / header / footer, changes to the menu must be
applied to all five HTML files. There is no template engine — that's
intentional, to keep the site buildable with nothing but a text editor.

When adding content, keep rendered lines at or under 80 columns where
possible (CSS wraps longer lines, but breaking manually keeps the
aesthetic).

## License

Same as the rest of the AS215932 public repositories.

---

*Part of [Hyrule Networks (AS215932)](https://github.com/AS215932).*
