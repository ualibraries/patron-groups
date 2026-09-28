# LDAP query tutorial

This is a practical guide to writing LDAP search filters for this project's
directory (UA's Enterprise Directory Service, "EDS"), and to using the two
tools in this repo that consume them:

- [`petl.ini`](../src/patron_groups/config/petl.ini) — the static, per-group
  queries that the `petl` sync script runs on a schedule.
- [`ldap_builder.py`](../src/patron_groups/scripts/ldap_builder.py) — an
  interactive tool for building, testing, and cross-referencing ad hoc
  queries against the groups defined in `petl.ini`.

It assumes no prior LDAP experience.

## 1. What a filter is

An LDAP search filter is a boolean expression that matches directory entries
(in this directory, people) by their attributes. It's always fully
parenthesized, and it always puts the operator *inside* the parentheses,
which trips up people coming from most other languages:

```
(eduPersonPrimaryAffiliation=faculty)
```

Read this as "match any entry where the `eduPersonPrimaryAffiliation`
attribute equals `faculty`". Each such `(attribute<op>value)` term is called
a *clause*.

## 2. Operators

| Operator | Meaning                          | Example                          |
|----------|-----------------------------------|-----------------------------------|
| `=`      | equals                            | `(employeeStatus=R)`             |
| `~=`     | approximately equals              | `(sn~=Smith)`                    |
| `>=`     | greater than or equal             | `(uaidCreated>=20200101)`        |
| `<=`     | less than or equal                | `(uaidCreated<=20201231)`        |
| `=*`     | present (attribute has any value) | `(mail=*)`                       |
| `*`      | wildcard, inside a value          | `(studentcpp=*:*:UGRD:*:*:*:*:AC:*:*)` |

The last two are easy to confuse. `(mail=*)` asks "does this person have a
`mail` attribute at all?" A `*` *inside* a value is a substring wildcard —
`(studentcpp=*:*:UGRD:*:*:*:*:AC:*:*)` matches a colon-delimited value where
the third field is `UGRD` and the eighth is `AC`, whatever else is in the
other fields.

`ldap_builder.py` exposes these same five choices when you build a clause
from a prompt (its `*` operator choice means "present").

## 3. Combining clauses: `&`, `|`, `!`

Boolean operators are *prefix* and go inside their own parentheses, wrapping
the clauses they combine:

- `(&(A)(B))` — AND: both `A` and `B` must match.
- `(|(A)(B))` — OR: either `A` or `B` matches.
- `(!(A))` — NOT: `A` must not match.

You can nest these freely. This is the entire `faculty-base` query from
`petl.ini`:

```
(eduPersonPrimaryAffiliation=faculty)
```

And here's `staff-base` ANDed with a hypothetical department restriction:

```
(&
    (eduPersonPrimaryAffiliation=staff)
    (employeePrimaryDept=1701)
)
```

Compare that to the real `hsl-base` query in `petl.ini`, which is many of
these nested `&`/`|` blocks concatenated together — it's built the same way,
just with more branches (faculty-or-qualifying-staff, AND-ed with a long
`|` list of department codes, OR-ed with the equivalent for students, DCCs,
and retirees).

**Common mistake:** forgetting that `&` and `|` need their *own* enclosing
parentheses even when combining just two clauses. `&(A)(B)` (no outer
parens) is not a valid filter; it must be `(&(A)(B))`.

## 4. Attributes used in this directory

These are the attributes the existing `petl.ini` groups query against. Use
`ldap_builder.py`'s option 6 (see §6) to see the actual values for any
attribute among a set of matched people if you're unsure what to filter on.

| Attribute                      | Meaning                                                                 |
|---------------------------------|--------------------------------------------------------------------------|
| `uaid`                          | The person's UA ID — the only attribute pulled back for sync purposes.  |
| `eduPersonPrimaryAffiliation`   | Primary affiliation, e.g. `faculty`, `staff`.                           |
| `eduPersonAffiliation`          | Any affiliation (multi-valued), e.g. `retiree`, `emeritus`.             |
| `employeeStatus`                | `A` active, `L` on leave, `P` paid leave, `W` ..., `R` retiree.         |
| `employeeType`                  | Single-character employee type code.                                   |
| `employeePrimaryDept`           | Primary home department code.                                          |
| `studentcpp`                    | Colon-delimited "career/plan/program" record; see §5.                  |
| `studenthonorsactive`           | `y`/`n` — active Honors College student.                                |
| `dccPrimaryStatus`               | `A` for an active DCC (designated campus colleague).                    |
| `dccPrimaryType`                 | DCC type code.                                                           |
| `dccPrimaryDept`                 | DCC's home department code.                                             |

## 5. Reading `studentcpp`

`studentcpp` is the attribute you'll spend the most time squinting at. It's
a colon-delimited value with 10 fields, and only a few of them are used in
practice:

```
*:*:UGRD:*:*:*:*:AC:*:*
      ^                ^
      career/program   status
      (field 3)        (field 8)
```

Field 3 is the academic career/program code (`UGRD` undergraduate, `GRAD`
graduate, `CORR`, `MEDS`, `PHRM`, `PROF`, `VETM`, `LAW`, etc. — see the
`grads-base` group for the full graduate-equivalent list). Field 8 is the
enrollment status, where `AC` means active. The unused fields are always
wildcarded with `*`.

Because a person can have multiple career/program records, `studentcpp` is
multi-valued, and the `*` wildcards mean these matches happen per-value —
you don't need multiple clauses to allow for other fields varying.

To match a particular degree/major code rather than a whole career, put it
in field 5, as the `finearts-base` and `hsl-base` groups do, e.g.:

```
(studentCPP=*:*:*:*:MUS*:*:*:AC:*:*)
```

(matches any active program whose plan code starts with `MUS`, e.g. music).

## 6. Building and testing a query with `ldap_builder.py`

Run it from the project root with Poetry:

```sh
poetry run python src/patron_groups/scripts/ldap_builder.py
```

It reads `PGRPS_LDAP_PASSWD` from `.env` and the connection settings and
group definitions from `petl.ini` automatically; pass `--env` / `--config`
to point at different files.

The menu:

1. **List configured groups** — every section name from `petl.ini`.
2. **Show a group's query** — pretty-prints one group's filter so you can
   see its structure before reusing or adapting it.
3. **Build a query from attributes** — prompts you for an attribute, an
   operator, and one or more values (OR-ed together), lets you negate the
   result, and repeats until you're done, joining everything with AND/OR.
   This is the easiest way to compose a filter without hand-balancing
   parentheses.
4. **Combine with configured groups** — pick one or more existing groups
   from `petl.ini` (by number or name) and AND/OR them together, optionally
   merging into whatever you already built.
5. **Show current query** — pretty-prints the filter you've built so far.
6. **Run and cross-reference** — runs your current query against the live
   directory, then lets you pick existing groups to compare it to. For each
   group it reports the group's size, the overlap with your query, that
   overlap as a percentage of your query's matches, and counts unique to
   each side — handy for sanity-checking a new group definition against
   related ones (e.g., does my new "college of X" query overlap the way I
   expect with `staff-base` and `faculty-base`?). You can also list extra
   attributes to get a breakdown of their most common values among your
   matches (e.g., see the department-code distribution of a query's
   results), and save the matched UA IDs to a file.
7. **Enter a raw filter** — paste a complete filter string directly, e.g.
   one built by hand or copied from `petl.ini`.

A typical session: use option 3 to build a draft filter, option 5 to review
it, option 6 to run it and compare it against related groups and inspect a
department-code breakdown, then iterate with option 3 or 7 until the
overlap numbers look right.

## 7. Worked example

Suppose you want everyone in an active `MUS` (music) program, active or on
leave, who is *not* also already in `finearts-base`.

1. In `ldap_builder.py`, option 3:
   - Attribute: `studentcpp`, operator `=`, value
     `*:*:*:*:MUS*:*:*:AC:*:*` → adds
     `(studentcpp=*:*:*:*:MUS*:*:*:AC:*:*)`.
   - Attribute blank to finish; only one clause, so no AND/OR prompt.
2. Option 6, run it, and cross-reference against `finearts-base`. The
   report's "overlap" count is how many of your matches are already
   covered; "only in query" is the new people you'd be adding.
3. If you specifically want to *exclude* the overlap, go back to option 3,
   build a second clause reusing `finearts-base`'s filter via option 4, wrap
   it in a negation... or more simply, use option 7 to hand-write:

   ```
   (&
       (studentcpp=*:*:*:*:MUS*:*:*:AC:*:*)
       (!(<finearts-base filter from option 2>))
   )
   ```

   pasting in whatever option 2 printed for `finearts-base`.

## 8. Adding a query to `petl.ini` for real syncing

Once a filter is validated with `ldap_builder.py`, promote it into
`petl.ini` as a new section:

```ini
[my-new-group-base]
ldap_query        =
    (studentcpp=*:*:*:*:MUS*:*:*:AC:*:*)
grouper_group     = ual-my-new-group-base
batch_size        = 1000
batch_timeout     = 900
```

Indentation of the continued `ldap_query` value doesn't matter to the
parser — it's whitespace-collapsed — but keeping it indented and one
clause per line, as the existing sections do, keeps it readable for the
next person.
